---
name: meta-evolution
description: Review and improve the agent evolution procedure. Use when tracking optimization stability, modifying agent harnesses, or verifying system performance trends.
---

# Skill: Meta Evolution (System Self-Optimization & Safety)

## Purpose
Oversee the processes by which the agent system adapts, learns from retrospectives, and updates its skills, rules, and prompts.

## Key Performance Indicators (KPIs)
Ensure evolution tracks and optimizes the following metrics:
- **Harness Stability**: Zero runtime compilation failures after updates.
- **Cache Efficiency**: Maximize `cache_hit_rate` and `plan_cache_hit_rate` to minimize cost and latency.
- **Repetition Rate**: Analyze loop logs via `codex_knowledge_graph_query` to eliminate redundant steps.

## Operational Protocol
- **Analyze Retrospectives**: Inspect learning records and retrospectives to identify structural gaps.
- **Validate Harness Changes**: Before proposing updates to agents' system prompts or core configs, verify changes against existing regression benchmarks.
- **Enforce Contracts**: Harness changes must be explicitly approved and accompanied by a task contract to prevent drift.
