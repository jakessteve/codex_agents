# Model Policy

- Use the smallest model that can safely complete the task.
- Keep Codex model profiles explicit and avoid hidden model routing.
- Match role class to the routing catalog before choosing a model.
- Prefer helper subagents for narrow or read-only work.

## Model Routing Catalog (Updated 2026-06-06)

### OpenAI Models (Codex CLI Native)
| Model | Role Class | Cost (Input/Output per 1M tok) | Profile |
|-------|-----------|--------------------------------|---------|
| gpt-5.5 | Premium reasoning | $5.00/$30.00 | deep, self-heal |
| gpt-5.4-mini | Standard reasoning | $0.75/$4.50 | default, review |
| gpt-5.4-nano | Budget/fast | $0.20/$1.25 | fast, batch, read-only |

### Profile Assignment Rationale
| Profile | Model | Reasoning | Rationale |
|---------|-------|-----------|-----------|
| default | gpt-5.4-mini | medium | Capable for most tasks, 6.7x cheaper than gpt-5.5 |
| fast | gpt-5.4-nano | low | Quick reads, summaries, narrow synthesis |
| deep | gpt-5.5 | xhigh | Complex reasoning, architecture, planning |
| review | gpt-5.4-mini | medium | Review doesn't need premium model |
| batch | gpt-5.4-nano | low | Batch tasks are typically mechanical |
| self-heal | gpt-5.5 | high | Self-healing needs strong reasoning |
| read-only | gpt-5.4-nano | low | Audit, exploration, no edits needed |

### Cost Savings
- Default profile: gpt-5.5 → gpt-5.4-mini = ~6.7x cheaper input, ~6.7x cheaper output
- Fast profile: gpt-5.4-mini → gpt-5.4-nano = ~3.75x cheaper input, ~3.6x cheaper output
- Review profile: gpt-5.5 → gpt-5.4-mini = ~6.7x cheaper input, ~6.7x cheaper output
- Batch profile: gpt-5.4-mini → gpt-5.4-nano = ~3.75x cheaper input, ~3.6x cheaper output
