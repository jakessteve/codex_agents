---
name: senior-architect
description: Make major technical decisions with explicit tradeoff analysis and Architecture Decision Records (ADRs).
---

# Senior Architect

## Purpose
Make major technical decisions by comparing options, recording tradeoffs, and writing ADRs when the decision is material.

## When to Use
- Choosing between architectural patterns
- Selecting frameworks or libraries
- Designing data models or APIs
- Making decisions that affect multiple components
- Any decision that would be expensive to reverse

## Steps

### 1. Define the Decision
- What decision needs to be made?
- What are the constraints?
- What is the time frame?
- Who are the stakeholders?

### 2. Enumerate Options
- Generate at least 2 viable alternatives
- For each option, analyze:
  - Performance implications
  - Maintainability impact
  - Extensibility considerations
  - Risk assessment
  - Cost (implementation time, infrastructure)

### 3. Record Tradeoffs
- Use `tradeoff_analyst` agent for formal analysis
- Or record manually:
  ```yaml
  tradeoffs:
    - option: <name>
      pros: <list>
      cons: <list>
      risk: <assessment>
      cost: <estimate>
  ```

### 4. Write ADR (for Material Decisions)
- For decisions that affect multiple components or are expensive to reverse:
  ```yaml
  adr:
    id: <ADR-NNN>
    title: <decision title>
    status: <proposed|accepted|deprecated|superseded>
    date: <ISO date>
    context: <why this decision is needed>
    decision: <what was decided>
    consequences:
      - positive: <benefits>
      - negative: <drawbacks>
      - neutral: <side effects>
    alternatives_considered: <list>
  ```

### 5. Record in Knowledge Graph
- Use `codex_knowledge_graph_upsert` to link the decision to affected components
- Use `codex_knowledge_knowledge_capture` to store the ADR
