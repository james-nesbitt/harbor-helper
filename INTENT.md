# Project Intent

This document outlines the overarching "Why" of this project. It should serve as the North Star for all development decisions, both for human contributors and AI agents.

## 1. Vision

Reduce or replace *manual* effort in responding to requests for project and robot management on two corporate Harbor OCI registries (e.g., by automating approval flows and safe execution so that most simple requests do not require manual steps).

## 2. Target Audience

The project is meant to listen to engineers inside the organization who need resources and access on the corporate registries.

## 3. Core Values & Principles

* **Safety is most important**: The software created should never create or destroy resources on Harbor without being certain that the operation is correct and approved.
* **Fail Closed**: If the LLM interpretation contains any ambiguity, or if the connection to JIRA/Harbor/Slack is unstable, the system must halt and request manual intervention rather than attempting to guess the user's intent.
* **Clear Communication**: Detail what is being done to fulfill the request. The "Why" is as important as the "What": The system must record exactly why it understood a request in a certain way (the LLM's reasoning) and who approved it.
* **Auditability**: An engineer should be able to look at a JIRA ticket later and reconstruct the entire decision-making process.
* **Efficiency**: Use available SDK and API toolkits where available instead of writing new ones.
* **Living Documentation**: Keep `INTENT.md` and `SPEC.md` as the source of truth; update them when direction or scope changes.

## 4. Problem Statement

This tool should reduce the effort that Operations engineers need to put in to respond to simple requests (initially CRUD on Projects and Robots) within two corporate registries.

## 5. Success Criteria

The tool is successful if it can correctly and safely resolve reported change requests to the connected services (e.g. Harbor registries) with user approval and without creating or destroying resources in error.

---
*Note to AI: Before proposing complex architectural changes or new features, review this document to ensure the proposal aligns with the core vision and values. If a proposal improves safety or clarity of communication, that aligns with core values even if not spelled out in SPEC.*
