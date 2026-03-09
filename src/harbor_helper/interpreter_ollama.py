"""
Ollama-based interpreter.
Implements the 'Embedded LLM' requirement using Pydantic for safety.
"""

import requests
from pydantic import BaseModel
from typing import Dict, Any
from .models import ProposedAction, ActionKind


class LLMResponse(BaseModel):
    kind: ActionKind
    summary: str
    details: str
    reasoning: str
    payload: Dict[str, Any]


class OllamaInterpreter:
    def __init__(
        self, model: str = "mistral", url: str = "http://localhost:11434/api/chat"
    ):
        self.model = model
        self.url = url

    def interpret(self, raw_text: str) -> ProposedAction:
        prompt = f"""
        Interpret this request for a Harbor OCI registry: "{raw_text}"
        
        Return ONLY valid JSON matching this schema:
        {{
            "kind": "harbor-manage-projects" or "harbor-new-robot",
            "summary": "short string",
            "details": "longer string describing the plan",
            "reasoning": "why you chose this action",
            "payload": {{ ... action specific params ... }}
        }}
        """

        try:
            response = requests.post(
                self.url,
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "stream": False,
                    "format": "json",
                },
                timeout=30,
            )
            response.raise_for_status()
            content = response.json().get("message", {}).get("content", "")

            # Use Pydantic to validate the LLM's output - Fail Closed if invalid
            validated = LLMResponse.model_validate_json(content)

            return ProposedAction(
                kind=validated.kind,
                summary=validated.summary,
                details=validated.details,
                reasoning=validated.reasoning,
                payload=validated.payload,
            )
        except Exception as e:
            # INTENT: Fail Closed
            raise ValueError(f"LLM Interpretation failed to produce a safe plan: {e}")
