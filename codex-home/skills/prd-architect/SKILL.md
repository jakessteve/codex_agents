---
name: prd-architect
description: Convert a validated request into a Product Requirements Document. Focus on what and why, not implementation details.
---

# PRD Architect

## Purpose
Convert a validated user request into a structured Product Requirements Document that defines what to build and why, without prescribing implementation details.

## Steps

### 1. Understand the Request
- Read the validated user intent from the task contract
- Use `codex_knowledge_project_context` to understand project constraints
- Use `codex_knowledge_graph_query` to understand related entities

### 2. Define the Problem
- What problem does this feature solve?
- Who are the users?
- What are the current pain points?

### 3. Define Requirements
- Functional requirements (what the system must do)
- Non-functional requirements (performance, security, accessibility)
- Constraints (technical, business, regulatory)
- Out of scope (explicitly list what is NOT included)

### 4. Define Acceptance Criteria
- Each requirement must have measurable acceptance criteria
- Use the format: "Given [context], when [action], then [result]"
- Criteria must be testable and unambiguous

### 5. Define Scope
- In scope: what is included in this release
- Out of scope: what is deferred to future releases
- Scope drift budget: maximum allowed deviation (default: 5%)

### 6. Output Format
```yaml
prd:
  title: <feature name>
  problem: <problem statement>
  users: <who will use this>
  functional_requirements:
    - id: <FR-001>
      description: <what the system must do>
      acceptance_criteria: <testable criteria>
  non_functional_requirements:
    - id: <NFR-001>
      description: <performance, security, etc.>
      acceptance_criteria: <testable criteria>
  constraints: <list of constraints>
  in_scope: <list of included features>
  out_of_scope: <list of excluded features>
  scope_drift_budget: <percentage>
```
