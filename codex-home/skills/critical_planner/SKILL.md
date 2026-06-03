---
name: critical-planner
description: Adversarial reasoning, assumption challenging, and PyRAG-style verifiable reasoning programs. Use when reviewing plans, analyzing complex architecture, or resolving logical ambiguities.
---

# Skill: Critical Planner (Adversarial Reasoning & Verification)

## Purpose
Ensure all implementation plans are challenged, assumptions are made explicit, and verification programs are deterministically structured.

## Operational Protocol

### 1. Challenge Assumptions
Before any plan is accepted, challenge:
- **Implied behavior**: Do not assume the system will handle edge cases automatically.
- **Dependency assumptions**: Check if requested packages are already imported or compatible.
- **State consistency**: Ensure that asynchronous operations or database updates do not leave the system in an inconsistent state.

### 2. PyRAG Program Composition
When composing verification programs, use a strict structured format:
- **Context Retrieval**: Define exactly what files or symbols must be queried.
- **Validation Logic**: Specify the assertion criteria (e.g., test cases, error formats, or state variables to check).
- **Execution Engine**: Use `cognition_codex_compose_pyrag_program` to invoke deterministic checks.

### 3. Verification Step Design
Every step in a plan must be accompanied by a concrete verification action:
- **Unit/Integration verification command**
- **Expected success criteria**
- **Expected failure behavior**
