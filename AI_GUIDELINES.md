# AI Development Guidelines

This project employs an AI-assisted "Spec and Intent-driven" development methodology. These rules guide how AI agents should interact with the codebase and the user.

**Primary references:** `INTENT.md` (vision, values), `SPEC.md` (requirements, scope).

## Core Directives for AI Agents

1. **Context is King:** Before writing any code, always read or refer to `INTENT.md` and `SPEC.md`. Ensure that your proposed solutions, architectural choices, and code implementations strictly align with the documented vision and requirements.
2. **Document-First Workflow:** When the user requests a significant new feature or a change in direction, first propose updating `SPEC.md` or `INTENT.md` to reflect this change *before* or *alongside* writing the implementation code. Prefer updating the docs in the same change (or a dedicated doc-only change) and mention the doc updates when proposing implementation. 
3. **Seek Clarification on Ambiguity:** If a user's request is ambiguous, lacks detail, or appears to contradict the established `INTENT.md` or `SPEC.md`, **stop and ask for clarification**. Do not make broad assumptions that could derail the project's architecture.
4. **Iterative and Small Steps:** Propose changes in small, logical, and testable increments. Avoid massive, sprawling rewrites unless explicitly commanded.
5. **Explain the "Why":** When proposing a solution, briefly explain *why* it fits the project's intent and how it fulfills the specific requirement in the spec.
6. **Self-Correction:** If you realize a previously implemented feature violates the core intent or spec, proactively point it out to the user and suggest a correction.
7. **Sparse or Missing Docs:** If `INTENT.md` or `SPEC.md` is missing or very sparse, say so and suggest minimal content before implementing; do not infer a full vision or spec.
8. **Document–Code Drift:** If the codebase no longer matches INTENT or SPEC, flag it and suggest either updating the docs or the code to restore alignment.
9. **Testing:** Testing and distribution should follow SPEC.md non-functional requirements (tests, mocks, packaging). When adding features, propose tests that match the spec.

## How to Use This Setup (For the User)

1. **Flesh out the Docs:** Start by filling in the details in `INTENT.md` and `SPEC.md`. The more detail you provide, the better the AI can assist you.
2. **Prompt with Reference:** When asking the AI to build something, you can say things like:
   - "Based on the User Stories in `SPEC.md`, let's implement the first feature."
   - "I want to add [Feature X]. Does this align with our `INTENT.md`? If so, please update the spec and draft the code."
3. **Review and Iterate:** Treat the AI as a pair programmer who relies heavily on the documentation you provide.
4. **When Docs Conflict:** If INTENT and SPEC conflict, clarify which takes precedence (typically INTENT for "why," SPEC for "what" and scope).