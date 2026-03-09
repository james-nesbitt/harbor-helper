# Project Specification

This project is a Mirantis corporate application used to automate dev-ops operations.

This project will allow approved engineers to interact with an AI Agent to make change requests to various services maintained by the organization. Only approved ops engineers can trigger changes; other users are out of scope for now.

## 0. Definitions

1. communication platform: common communication platform tools used by Mirantis which will be used to interact with the project. Currently this includes only "slack" 
2. Backend service: a Mirantis service that the application can interact with over API calls, for which requests to the project can be made.

## 1. Functional Requirements

- Listen for requests from specific engineers on common communication platforms;
- interpret the requests using an embedded agent.
- respond to requests by interacting with various systems through various service APIs;
- comment on and update related JIRA tickets.

Feature set 1: Harbor OCI registries: various Harbor registries will be modified by the project

- Feature 1-1: harbor-manage-projects
    - respond to requests related to projects, and manage Harbor projects in the corporate registries
- Feature 1-2: harbor-new-robot
    - respond to requests related to robot accounts, and manage robots and their project access

## 2. Non-Functional Requirements
- Requirement 1: The project should never create/modify/delete resources on the Harbor registries without being sure that the operation is authorized and correct;
- Requirement 2: The project should always describe what changes will be implemented before making the change;
- Requirement 3: The project should always seek approval for the change details before making the change. By default, this requires a 'Peer Review' model where the approver in Slack must be a different 'Approved Ops Engineer' than the requester;
- Requirement 4: The project should never send credentials over group communication. Credentials (robot tokens) must ONLY be sent via a direct Slack DM to the requester;
- Requirement 5: the project should include an app, tests for the app, a distribution for the app and tooling for building, packaging and distribution the app;
- Requirement 6: The project should include unit and functional testing;
- Requirement 7: All communication and API interactions should be testable using API mocks.
- Requirement 8: Only JIRA tickets within the "PRODENG" or "IT" projects shall be managed or updated by the application. Requests referencing tickets in other projects must be rejected.
- Requirement 9: All code generated and maintained in this project should be linted and formatted according to industry standards. Tooling for this should be included.
- Requirement 10: `uv` shall be used as the primary tool for Python environment management, dependency resolution, and tool execution.
- Requirement 11: The root `README.md` shall be developer-oriented (installation, build instructions, development workflow). End-user and administrative usage documentation shall be stored in a dedicated `/docs` directory.
- Requirement 12: The project should provide local development tooling to simulate the application's behavior. This tooling should allow running the agency's interpretation and approval workflow using mocks for Slack, JIRA, and Harbor.

## 3. User Stories / Use Cases

Users interact via supported communication platforms (e.g., Slack); the system may update related JIRA tickets. User stories:

1. As an "approved ops engineer" I want to ask for a new Harbor project, so that I can deliver new resources to an engineering team.
2. As an "approved ops engineer" I want to ask for a new Harbor robot account, so that I can provide an engineering team CI/CD automation with access to the Harbor registry.

## 4. Data Models & Entities

- **Approved DevOps Engineer**: A communication entity which the project knows is allowed to make requests.
- **Approver**: An Approved DevOps Engineer who confirms a request. In 'Peer Review' mode, this must be different from the Requester.
- **Harbor Project**: A project in a corporate Harbor registry, manageable via the Harbor API.
- **Robot Account**: A robot account in Harbor with configurable project access.
- **Request**: An incoming change request, from an approved communication platform, to be interpreted and fulfilled.
- **Approval**: Confirmation that the requested change is authorized and correct before execution.
- **Request Status**: One of `PENDING_INTERPRETATION`, `AWAITING_APPROVAL`, `APPROVED`, `EXECUTING`, `COMPLETED`, `FAILED`.

## 5. Workflow

1. **Request**: User makes a request in Slack.
2. **Ticket Association**: Every request MUST be associated with an existing JIRA ticket from the 'PRODENG' or 'IT' projects. The system will NOT create new JIRA tickets. If no Ticket ID is provided, or if the provided ID belongs to a different project, the request must be rejected.
3. **Interpretation**: The LLM interprets the request. The reasoning and planned change details are posted to the JIRA ticket as a comment.
4. **Approval**: The system posts the plan to Slack and waits for an Approver.
5. **Execution**: Once approved, the system executes the change in Harbor, updates the JIRA ticket status, and sends credentials via Slack DM.

## 6. Technology Stack & Constraints

- Harbor API 2.4.0: https://goharbor.io/docs/2.4.0/working-with-projects/using-api-explorer/
- Slack API
- Atlassian JIRA API

## 7. Distribution and Packaging

- the project should include packaging and distribution tooling for kubernetes
- any OCI artifacts generated should be pushed to oci://registry.ci.mirantis.com/jnesbitt/ for dev and registry.mirantis.com/jnesbitt/ for production
- podman should be the preferred tool for OCI image building

## 8. Out of scope

- Other registries beyond the two corporate Harbor OCI registries (at this time)
- Direct database or filesystem access to Harbor.
 - Complex network configuration, registry mirroring, or user permission management beyond robots.

---
*Note to AI: Use this document to determine the scope of work. Do not implement features outside of this specification unless explicitly requested by the user. If a requested feature conflicts with these specs, ask for clarification. Tests, distribution, and mocks (NFRs 5–7) apply to the app and tooling for this project.*
