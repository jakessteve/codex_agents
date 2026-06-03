from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from mcp.server.fastmcp import FastMCP
except Exception as exc:  # pragma: no cover
    raise SystemExit("Missing MCP runtime dependency. Run uv sync in mcp/evolution.") from exc

mcp = FastMCP("evolution")
ROOT = Path(__file__).resolve().parent
PROPOSAL_ROOT = ROOT / "proposals"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@mcp.tool()
def classify_repetition(
    failure_pattern: str,
    occurrences: int,
    notes: list[str] | None = None,
) -> dict[str, Any]:
    """Classify repeated failure patterns for evolution review."""
    severity = "low"
    if occurrences >= 5:
        severity = "high"
    elif occurrences >= 3:
        severity = "medium"
    proposal = {
        "failure_pattern": failure_pattern,
        "occurrences": occurrences,
        "severity": severity,
        "notes": notes or [],
        "next_step": "draft_harness_change" if severity != "low" else "record_lesson",
    }
    return proposal


@mcp.tool()
def propose_harness_change(
    trigger: str,
    evidence: list[str],
    desired_change: str,
    constraints: list[str] | None = None,
) -> dict[str, Any]:
    """Draft a harness evolution proposal manifest."""
    manifest = {
        "contract_type": "evolution_proposal",
        "created_at": _now(),
        "trigger": trigger,
        "evidence": evidence,
        "desired_change": desired_change,
        "constraints": constraints or [],
        "review_gates": ["oracle_proposal_gate", "human_approval", "oracle_adoption_gate"],
    }
    return manifest


@mcp.tool()
def record_retrospective(
    lesson: str,
    evidence: list[str] | None = None,
    action_items: list[str] | None = None,
) -> dict[str, Any]:
    """Return a compact retrospective payload for docs capture."""
    return {
        "lesson": lesson,
        "evidence": evidence or [],
        "action_items": action_items or [],
        "capture_target": str(PROPOSAL_ROOT),
    }


if __name__ == "__main__":
    mcp.run(transport="stdio")
