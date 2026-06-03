from __future__ import annotations

from typing import Any

try:
    from mcp.server.fastmcp import FastMCP
except Exception as exc:  # pragma: no cover
    raise SystemExit("Missing MCP runtime dependency. Run uv sync in mcp/planner.") from exc

mcp = FastMCP("planner")


def _normalize_complexity(complexity: str) -> str:
    value = complexity.strip().lower()
    if value in {"tiny", "small", "atomic"}:
        return "atomic"
    if value in {"medium", "standard"}:
        return "medium"
    if value in {"large", "epic"}:
        return "epic"
    if value in {"exploratory", "debugging", "self_healing", "self_evolving"}:
        return value
    return "unknown"


def _topology_for(task_type: str, complexity: str, file_count: int, domain_count: int) -> dict[str, Any]:
    comp = _normalize_complexity(complexity)
    if comp == "atomic" and file_count <= 3 and domain_count <= 1:
        return {
            "topology": "sequential_pipeline",
            "writers": 1,
            "reads": ["project_context", "task_contract"],
        }
    if comp in {"medium", "debugging", "self_healing"}:
        return {
            "topology": "sequential_pipeline",
            "writers": 1,
            "reads": ["project_context", "requirements", "oracle_review"],
        }
    if comp in {"epic", "self_evolving"} or file_count > 10 or domain_count > 2:
        return {
            "topology": "wave_execution",
            "writers": 1,
            "reads": ["project_context", "requirements", "architecture", "oracle_review"],
        }
    if comp == "exploratory":
        return {
            "topology": "independent_ensemble",
            "writers": 0,
            "reads": ["project_context", "problem_statement"],
        }
    return {
        "topology": "sequential_pipeline",
        "writers": 1,
        "reads": ["project_context"],
    }


def _missing(values: dict[str, Any], required: list[str]) -> list[str]:
    missing: list[str] = []
    for key in required:
        value = values.get(key)
        if value in (None, "", [], {}):
            missing.append(key)
    return missing


@mcp.tool()
def suggest_topology(
    task_type: str,
    complexity: str = "unknown",
    file_count: int = 0,
    domain_count: int = 1,
) -> dict[str, Any]:
    """Suggest a routing topology and gate sequence."""
    topology = _topology_for(task_type, complexity, file_count, domain_count)
    if topology["topology"] == "wave_execution":
        gates = ["preflight_gate", "oracle_plan_gate", "oracle_wave_gate", "oracle_release_gate"]
    elif topology["topology"] == "independent_ensemble":
        gates = ["preflight_gate", "oracle_merge_gate", "oracle_release_gate"]
    else:
        gates = ["preflight_gate", "oracle_plan_gate", "oracle_release_gate"]
    return {
        "task_type": task_type,
        "complexity": _normalize_complexity(complexity),
        "file_count": file_count,
        "domain_count": domain_count,
        "topology": topology["topology"],
        "writers": topology["writers"],
        "recommended_gates": gates,
        "read_context": topology["reads"],
    }


@mcp.tool()
def review_task_contract(
    original_user_request: str,
    validated_user_intent: str,
    task_type: str,
    complexity: str,
    selected_lifecycle_path: str,
    selected_topology: str,
    required_documents: list[str] | None = None,
    allowed_files: list[str] | None = None,
    required_tests: list[str] | None = None,
    scope_drift_budget_percent: int = 5,
) -> dict[str, Any]:
    """Review a PM task contract for completeness and routing readiness."""
    payload = {
        "original_user_request": original_user_request,
        "validated_user_intent": validated_user_intent,
        "task_type": task_type,
        "complexity": complexity,
        "selected_lifecycle_path": selected_lifecycle_path,
        "selected_topology": selected_topology,
        "required_documents": required_documents or [],
        "allowed_files": allowed_files or [],
        "required_tests": required_tests or [],
        "scope_drift_budget_percent": scope_drift_budget_percent,
    }
    required = [
        "original_user_request",
        "validated_user_intent",
        "task_type",
        "complexity",
        "selected_lifecycle_path",
        "selected_topology",
        "required_documents",
        "allowed_files",
        "required_tests",
    ]
    missing = _missing(payload, required)
    ready = not missing and scope_drift_budget_percent <= 5
    topology_hint = _topology_for(task_type, complexity, len(payload["allowed_files"]), len(payload["required_documents"]))
    return {
        "ready": ready,
        "missing": missing,
        "topology_hint": topology_hint["topology"],
        "gates": ["preflight_gate", "oracle_plan_gate"] if ready else ["request_enrichment", "pm_review"],
        "payload": payload,
    }


@mcp.tool()
def summarize_route(
    task_type: str,
    complexity: str,
    file_count: int = 0,
    domain_count: int = 1,
    confidence_score: int = 80,
) -> dict[str, Any]:
    """Return a compact routing summary for PM use."""
    topology = _topology_for(task_type, complexity, file_count, domain_count)
    confidence_bucket = "low" if confidence_score < 60 else "medium" if confidence_score < 85 else "high"
    return {
        "task_type": task_type,
        "complexity": _normalize_complexity(complexity),
        "confidence_score": confidence_score,
        "confidence_bucket": confidence_bucket,
        "topology": topology["topology"],
        "writer_count": topology["writers"],
    }


if __name__ == "__main__":
    mcp.run(transport="stdio")
