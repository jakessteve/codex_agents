from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from mcp.server.fastmcp import FastMCP
except Exception as exc:  # pragma: no cover
    raise SystemExit("Missing MCP runtime dependency. Run uv sync in mcp/cognition_codex.") from exc

mcp = FastMCP("cognition_codex")
ROOT = Path(__file__).resolve().parent
STATE_PATH = ROOT / "state" / "cognition_codex.json"

NEGATIONS = {"not", "no", "never", "without", "cannot", "can't", "won't", "deny", "denies", "denied"}
STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "be",
    "by",
    "for",
    "from",
    "in",
    "is",
    "it",
    "of",
    "on",
    "or",
    "the",
    "to",
    "with",
    "must",
    "should",
    "need",
    "needs",
    "required",
    "require",
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _ensure_state() -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)


def _default_state() -> dict[str, Any]:
    return {"events": [], "concepts": [], "intents": [], "dreams": []}


def _load_state() -> dict[str, Any]:
    _ensure_state()
    if not STATE_PATH.exists():
        return _default_state()
    try:
        data = json.loads(STATE_PATH.read_text(encoding="utf-8"))
    except Exception:
        return _default_state()
    state = _default_state()
    if isinstance(data, dict):
        for key in state:
            value = data.get(key, [])
            if isinstance(value, list):
                state[key] = value
    return state


def _save_state(state: dict[str, Any]) -> None:
    _ensure_state()
    tmp_path = STATE_PATH.with_suffix(".json.tmp")
    tmp_path.write_text(json.dumps(state, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    tmp_path.replace(STATE_PATH)


def _slug(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")
    return slug or "item"


def _normalise_items(values: list[Any] | None) -> list[str]:
    if not values:
        return []
    items: list[str] = []
    for value in values:
        if isinstance(value, str):
            text = value.strip()
        elif isinstance(value, dict):
            text = str(value.get("text") or value.get("label") or value.get("value") or "").strip()
        else:
            text = str(value).strip()
        if text:
            items.append(text)
    return items


def _dedupe_preserve_order(values: list[str]) -> list[str]:
    seen: set[str] = set()
    deduped: list[str] = []
    for value in values:
        key = value.lower()
        if key in seen:
            continue
        seen.add(key)
        deduped.append(value)
    return deduped


def _canonicalize(text: str) -> tuple[str, bool]:
    tokens = re.findall(r"[a-z0-9]+", text.lower())
    negated = any(token in NEGATIONS for token in tokens)
    filtered = [token for token in tokens if token not in NEGATIONS and token not in STOPWORDS]
    return " ".join(filtered), negated


def _upsert_summary(state: dict[str, Any], bucket: str, label: str, evidence: list[str]) -> None:
    label_key = _slug(label)
    collection = state[bucket]
    for entry in collection:
      if isinstance(entry, dict) and entry.get("label_key") == label_key:
            entry["occurrences"] = int(entry.get("occurrences", 0)) + 1
            entry["evidence"] = _dedupe_preserve_order([*entry.get("evidence", []), *evidence])
            entry["updated_at"] = _now()
            return
    collection.append(
        {
            "label": label.strip(),
            "label_key": label_key,
            "occurrences": 1,
            "evidence": _dedupe_preserve_order(evidence),
            "created_at": _now(),
            "updated_at": _now(),
        }
    )


def _top_entries(entries: list[dict[str, Any]], limit: int = 5) -> list[dict[str, Any]]:
    ranked = sorted(entries, key=lambda entry: (-int(entry.get("occurrences", 0)), str(entry.get("label", ""))))
    return ranked[:limit]


@mcp.tool()
def status() -> dict[str, Any]:
    """Return service and stored state status."""
    state = _load_state()
    return {
        "service": "cognition_codex",
        "backend": "json_state",
        "state_path": str(STATE_PATH),
        "event_count": len(state["events"]),
        "concept_count": len(state["concepts"]),
        "intent_count": len(state["intents"]),
        "dream_count": len(state["dreams"]),
    }


@mcp.tool()
def compose_pyrag_program(
    goal: str,
    retrieval_sources: list[str] | None = None,
    constraints: list[str] | None = None,
    max_steps: int = 5,
    repair_loop: bool = True,
) -> dict[str, Any]:
    """Compose a deterministic PyRAG-style execution plan."""
    sources = _dedupe_preserve_order(_normalise_items(retrieval_sources) or ["graph", "treesitter", "tests"])
    constraint_list = _dedupe_preserve_order(_normalise_items(constraints))
    program_name = _slug(goal)
    steps = [
        {
            "step": 1,
            "action": "capture_goal",
            "details": goal.strip(),
        },
        {
            "step": 2,
            "action": "retrieve_evidence",
            "sources": sources,
        },
        {
            "step": 3,
            "action": "compose_candidate",
            "details": "Build the smallest candidate plan from the retrieved evidence.",
        },
        {
            "step": 4,
            "action": "execute_and_validate",
            "details": "Run the candidate against the task constraints and required checks.",
        },
    ]
    if repair_loop:
        steps.append(
            {
                "step": 5,
                "action": "repair_if_needed",
                "details": "Revise the candidate deterministically if validation fails.",
            }
        )
    python_program = "\n".join(
        [
            f"def run_{program_name}():",
            f"    goal = {goal!r}",
            f"    sources = {sources!r}",
            f"    constraints = {constraint_list!r}",
            "    evidence = []",
            "    for source in sources:",
            "        evidence.append(f'retrieve:{source}:{goal}')",
            "    candidate = {'goal': goal, 'evidence': evidence, 'constraints': constraints}",
            "    validated = True",
            "    if constraints:",
            "        validated = all(bool(item.strip()) for item in constraints)",
            "    if not validated:",
            "        candidate['repair'] = 'tighten constraints and retry retrieval'",
            "    return candidate",
        ]
    )
    return {
        "goal": goal.strip(),
        "sources": sources,
        "constraints": constraint_list,
        "max_steps": max_steps,
        "repair_loop": repair_loop,
        "steps": steps[: max(1, max_steps)],
        "program": python_program,
        "execution_hints": [
            "keep variables explicit",
            "prefer executable evidence over prose-only claims",
            "repair only after validation failure is observed",
        ],
    }


@mcp.tool()
def parallel_multisearch(
    query: str,
    perspectives: list[str] | None = None,
    limit: int = 3,
) -> dict[str, Any]:
    """Generate parallel query variants and a merge strategy."""
    query_text = query.strip()
    perspective_list = _dedupe_preserve_order(_normalise_items(perspectives) or ["rephrase", "expand", "decompose"])
    variants: list[dict[str, Any]] = []
    for perspective in perspective_list[: max(1, limit)]:
        variants.append(
            {
                "perspective": perspective,
                "query": f"{query_text} ({perspective})",
                "purpose": f"search from the {perspective} angle",
            }
        )
    return {
        "query": query_text,
        "variants": variants,
        "merge_strategy": {
            "step": "normalize",
            "step_2": "consolidate",
            "step_3": "select_highest_signal",
        },
        "merge_keys": ["shared_terms", "evidence_strength", "constraint_coverage"],
    }


@mcp.tool()
def fold_cognifold(
    events: list[Any] | None = None,
    concepts: list[str] | None = None,
    intents: list[str] | None = None,
    source: str = "manual",
) -> dict[str, Any]:
    """Fold event/concept/intent inputs into a compact persistent memory store."""
    state = _load_state()
    event_records: list[dict[str, Any]] = []
    for event in events or []:
        if isinstance(event, dict):
            text = str(event.get("text") or event.get("content") or event.get("label") or "").strip()
            kind = str(event.get("kind") or "event").strip()
        else:
            text = str(event).strip()
            kind = "event"
        if not text:
            continue
        record = {
            "kind": kind,
            "text": text,
            "source": source,
            "created_at": _now(),
        }
        state["events"].append(record)
        event_records.append(record)

    for concept in _dedupe_preserve_order(_normalise_items(concepts)):
        _upsert_summary(state, "concepts", concept, [item["text"] for item in event_records] or [concept])

    for intent in _dedupe_preserve_order(_normalise_items(intents)):
        _upsert_summary(state, "intents", intent, [item["text"] for item in event_records] or [intent])

    _save_state(state)
    return {
        "stored_events": len(event_records),
        "concept_count": len(state["concepts"]),
        "intent_count": len(state["intents"]),
        "top_concepts": _top_entries(state["concepts"]),
        "top_intents": _top_entries(state["intents"]),
        "state_path": str(STATE_PATH),
    }


@mcp.tool()
def check_aop_consistency(
    claims: list[str] | None = None,
    relations: list[dict[str, Any]] | None = None,
    rules: list[str] | None = None,
) -> dict[str, Any]:
    """Check for simple logical conflicts and return crystallisation guidance."""
    claim_items = _dedupe_preserve_order(_normalise_items(claims))
    relation_items = relations or []
    rule_items = _dedupe_preserve_order(_normalise_items(rules))

    violations: list[str] = []
    seen_claims: dict[str, bool] = {}
    for claim in claim_items:
        canonical, negated = _canonicalize(claim)
        if not canonical:
            continue
        if canonical in seen_claims and seen_claims[canonical] != negated:
            violations.append(f"claim conflict on '{canonical}'")
        seen_claims[canonical] = negated

    seen_relations: dict[tuple[str, str, str], bool] = {}
    for relation in relation_items:
        if not isinstance(relation, dict):
            continue
        subject = str(relation.get("subject") or relation.get("from") or "").strip()
        rel = str(relation.get("relation") or relation.get("type") or "").strip()
        target = str(relation.get("target") or relation.get("to") or "").strip()
        if not subject or not rel or not target:
            continue
        negated = any(token in NEGATIONS for token in re.findall(r"[a-z0-9]+", f"{subject} {rel} {target}".lower()))
        key = (subject.lower(), rel.lower(), target.lower())
        if key in seen_relations and seen_relations[key] != negated:
            violations.append(f"relation conflict on {subject} {rel} {target}")
        seen_relations[key] = negated

    score = max(0, 100 - (len(violations) * 25) - (len(rule_items) * 2))
    status = "consistent" if not violations and score >= 80 else "needs_recrystallization"
    repair_prompt = "strengthen the boundary conditions and re-check for contradictions"
    if violations:
        repair_prompt = "remove contradictory claims, rewrite relations, then re-run the verifier"
    return {
        "status": status,
        "crystallisation_score": score,
        "claims": claim_items,
        "relations": relation_items,
        "rules": rule_items,
        "violations": violations,
        "repair_prompt": repair_prompt,
    }


@mcp.tool()
def consolidate_dreaming(
    traces: list[str] | None = None,
    lessons: list[str] | None = None,
    patterns: list[str] | None = None,
    max_items: int = 8,
) -> dict[str, Any]:
    """Consolidate traces and lessons into durable memory and next actions."""
    state = _load_state()
    trace_items = _dedupe_preserve_order(_normalise_items(traces))
    lesson_items = _dedupe_preserve_order(_normalise_items(lessons))
    pattern_items = _dedupe_preserve_order(_normalise_items(patterns))

    combined_signals = trace_items + lesson_items + pattern_items
    dream_record = {
        "created_at": _now(),
        "traces": trace_items[:max_items],
        "lessons": lesson_items[:max_items],
        "patterns": pattern_items[:max_items],
        "summary": " | ".join((lesson_items[:2] + pattern_items[:2]) or trace_items[:2]),
    }
    state["dreams"].append(dream_record)

    for item in lesson_items:
        _upsert_summary(state, "concepts", item, combined_signals or [item])
    for item in pattern_items:
        _upsert_summary(state, "intents", item, combined_signals or [item])

    _save_state(state)

    recurring = []
    for entry in _top_entries(state["intents"], limit=max_items):
        if int(entry.get("occurrences", 0)) > 1:
            recurring.append(entry["label"])

    next_actions = [
        "tighten the smallest recurring guardrails",
        "promote high-frequency lessons into skills or prompts",
        "route the strongest patterns back to the evolution loop",
    ]
    if any("verbosity" in signal.lower() for signal in combined_signals):
        next_actions.insert(0, "strengthen the minimalism guardrails")
    if any("drift" in signal.lower() for signal in combined_signals):
        next_actions.insert(0, "review scope drift controls")

    return {
        "dream_count": len(state["dreams"]),
        "stored_traces": trace_items[:max_items],
        "consolidated_lessons": lesson_items[:max_items],
        "consolidated_patterns": pattern_items[:max_items],
        "recurring_themes": recurring[:max_items],
        "next_actions": _dedupe_preserve_order(next_actions)[:max_items],
        "state_path": str(STATE_PATH),
    }


if __name__ == "__main__":
    mcp.run(transport="stdio")
