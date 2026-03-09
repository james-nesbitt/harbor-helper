"""
Ollama-based interpreter.
Implements the 'Embedded LLM' requirement using Pydantic for safety.
"""

import requests
from pydantic import BaseModel
from typing import Dict, Any, List
from .models import ProposedAction, ActionKind


class LLMResponse(BaseModel):
    kind: ActionKind
    target_id: str
    summary: str
    details: str
    reasoning: str
    payload: Dict[str, Any]


class OllamaInterpreter:
    def __init__(
        self,
        model: str = "mistral",
        url: str = "http://localhost:11434/api/chat",
        available_targets: List[str] = None,
        verbose: bool = False,
    ):
        self.model = model
        self.url = url
        self.available_targets = available_targets or ["default"]
        self.verbose = verbose

    def interpret(self, raw_text: str) -> ProposedAction:
        targets_str = ", ".join([f"'{t}'" for t in self.available_targets])
        prompt = f"""
        Interpret this request for a Harbor OCI registry: "{raw_text}"
        
        Available target registries: {targets_str}

        Return ONLY valid JSON matching this schema:
        {{
            "kind": "harbor-manage-projects" or "harbor-new-robot",
            "target_id": one of {targets_str},
            "summary": "short string",
            "details": "longer string describing the plan",
            "reasoning": "why you chose this action and this target",
            "payload": {{ 
                "project_name": "string (required for harbor-manage-projects)",
                "name": "string (required for harbor-new-robot)",
                "level": "system" or "project" (optional, for robots)
            }}
        }}
        """

        if self.verbose:
            print(f"\n--- LLM PROMPT ---\n{prompt.strip()}\n------------------\n")

        try:
            response = requests.post(
                self.url,
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "stream": False,
                    "format": "json",
                },
                timeout=120,
            )
            response.raise_for_status()
            content = response.json().get("message", {}).get("content", "")

            if self.verbose:
                print(
                    f"--- LLM RAW RESPONSE ---\n{content.strip()}\n------------------------\n"
                )

            # Use Pydantic to validate the LLM's output - Fail Closed if invalid
            validated = LLMResponse.model_validate_json(content)

            return ProposedAction(
                kind=validated.kind,
                target_id=validated.target_id,
                summary=validated.summary,
                details=validated.details,
                reasoning=validated.reasoning,
                payload=validated.payload,
            )
        except Exception as e:
            # INTENT: Fail Closed
            raise ValueError(f"LLM Interpretation failed to produce a safe plan: {e}")
