from __future__ import annotations

from typing import Any

try:
    from mcp.server.fastmcp import FastMCP
except Exception as exc:  # pragma: no cover
    raise SystemExit("Missing MCP runtime dependency. Run uv sync in mcp/minimalist.") from exc

mcp = FastMCP("minimalist")


def _count(lines: list[str], prefix: str) -> int:
    return sum(1 for line in lines if line.startswith(prefix))


@mcp.tool()
def review_change(
    change_summary: str,
    file_count: int = 0,
    added_lines: int = 0,
    removed_lines: int = 0,
    tests: list[str] | None = None,
) -> dict[str, Any]:
    """Review a change for minimalism and diff size."""
    total_lines = added_lines + removed_lines
    risk = "low"
    suggestions: list[str] = []
    if file_count > 5 or total_lines > 400:
        risk = "high"
        suggestions.append("split the change into smaller story-sized pieces")
    elif file_count > 2 or total_lines > 120:
        risk = "medium"
        suggestions.append("verify the change can be reduced to the approved task contract")
    if not tests:
        suggestions.append("add the smallest required test bundle before merge")
    else:
        test_count = len(tests)
        if test_count < 2:
            suggestions.append("add one regression-style check to protect the main path")
    return {
        "change_summary": change_summary,
        "file_count": file_count,
        "added_lines": added_lines,
        "removed_lines": removed_lines,
        "risk": risk,
        "suggestions": suggestions,
    }


@mcp.tool()
def diff_budget(
    planned_files: list[str],
    actual_files: list[str],
    allowed_slack: int = 1,
) -> dict[str, Any]:
    """Compare planned and actual file counts."""
    planned = len(planned_files)
    actual = len(actual_files)
    delta = abs(actual - planned)
    within_budget = delta <= allowed_slack
    return {
        "planned_files": planned_files,
        "actual_files": actual_files,
        "planned_count": planned,
        "actual_count": actual,
        "delta": delta,
        "within_budget": within_budget,
    }


@mcp.tool()
def simplification_notes(
    scope: str,
    duplicate_terms: list[str] | None = None,
    new_dependencies: list[str] | None = None,
) -> dict[str, Any]:
    """Return compact simplification guidance."""
    notes: list[str] = []
    if duplicate_terms:
        notes.append(f"merge repeated concepts: {', '.join(duplicate_terms)}")
    if new_dependencies:
        notes.append(f"avoid new dependencies where possible: {', '.join(new_dependencies)}")
    if not notes:
        notes.append("keep the implementation aligned to the approved task contract")
    return {"scope": scope, "notes": notes}


if __name__ == "__main__":
    mcp.run(transport="stdio")
