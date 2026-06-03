from __future__ import annotations

import binascii
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from mcp.server.fastmcp import FastMCP
except Exception as exc:  # pragma: no cover
    raise SystemExit("Missing MCP runtime dependency. Run uv sync in mcp/trace_export.") from exc

mcp = FastMCP("trace_export")
ROOT = Path(__file__).resolve().parent
EXPORT_ROOT = ROOT / "exports"
EXPORT_FILE = EXPORT_ROOT / "trace_exports.jsonl"

PHOENIX_HOST = os.environ.get("PHOENIX_HOST", "127.0.0.1")
PHOENIX_PORT = int(os.environ.get("PHOENIX_PORT", "6006"))
PHOENIX_ENABLED = os.environ.get("PHOENIX_EXPORT_ENABLED", "true").lower() in {"true", "1", "yes"}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _generate_hex_id(length: int) -> str:
    byte_count = length // 2
    return binascii.hexlify(os.urandom(byte_count)).decode("ascii")


def _timestamp_ns(iso_timestamp: str) -> str:
    dt = datetime.fromisoformat(iso_timestamp)
    return str(int(dt.timestamp() * 1_000_000_000))


def _push_to_phoenix(record: dict[str, Any]) -> dict[str, Any]:
    phoenix_url = f"http://{PHOENIX_HOST}:{PHOENIX_PORT}/v1/traces"
    if not PHOENIX_ENABLED:
        return {"pushed": False, "phoenix_url": phoenix_url}

    trace_id = _generate_hex_id(32)
    span_id = _generate_hex_id(16)
    timestamp_ns = _timestamp_ns(record["timestamp"])
    name = f"{record['trace_class']}.{record['title']}"

    otlp_payload = {
        "resourceSpans": [
            {
                "resource": {
                    "attributes": [
                        {
                            "key": "service.name",
                            "value": {"stringValue": "codex-trace-export"},
                        }
                    ]
                },
                "scopeSpans": [
                    {
                        "scope": {"name": "codex"},
                        "spans": [
                            {
                                "traceId": trace_id,
                                "spanId": span_id,
                                "name": name,
                                "kind": 1,
                                "startTimeUnixNano": timestamp_ns,
                                "endTimeUnixNano": timestamp_ns,
                                "attributes": [
                                    {
                                        "key": "codex.trace_class",
                                        "value": {"stringValue": record["trace_class"]},
                                    },
                                    {
                                        "key": "codex.title",
                                        "value": {"stringValue": record["title"]},
                                    },
                                    {
                                        "key": "codex.source",
                                        "value": {"stringValue": record["source"]},
                                    },
                                    {
                                        "key": "codex.payload",
                                        "value": {
                                            "stringValue": json.dumps(record["payload"], ensure_ascii=True)
                                        },
                                    },
                                ],
                            }
                        ],
                    }
                ],
            }
        ]
    }

    try:
        data = json.dumps(otlp_payload, ensure_ascii=True).encode("utf-8")
        req = urllib.request.Request(
            phoenix_url,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            response.read()
        return {"pushed": True, "phoenix_url": phoenix_url}
    except Exception as exc:
        error_msg = f"Phoenix push failed: {exc}\n"
        sys.stderr.write(error_msg)
        return {"pushed": False, "phoenix_url": phoenix_url, "error": str(exc)}


@mcp.tool()
def record_trace(
    trace_class: str,
    title: str,
    payload: dict[str, Any],
    source: str = "manual",
) -> dict[str, Any]:
    """Append a trace export record for later review or upload."""
    EXPORT_ROOT.mkdir(parents=True, exist_ok=True)
    record = {
        "timestamp": _now(),
        "trace_class": trace_class,
        "title": title,
        "source": source,
        "payload": payload,
    }
    with EXPORT_FILE.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=True) + "\n")
    phoenix_result = _push_to_phoenix(record)
    return {
        "stored": True,
        "export_file": str(EXPORT_FILE),
        "record": record,
        "phoenix": phoenix_result,
    }


@mcp.tool()
def summarize_exports(limit: int = 20) -> dict[str, Any]:
    """Return a compact summary of stored trace exports."""
    if not EXPORT_FILE.exists():
        return {"export_file": str(EXPORT_FILE), "records": [], "count": 0}
    rows = EXPORT_FILE.read_text(encoding="utf-8", errors="ignore").splitlines()
    records = [json.loads(row) for row in rows if row.strip()]
    return {
        "export_file": str(EXPORT_FILE),
        "count": len(records),
        "records": records[-limit:],
    }


@mcp.tool()
def push_to_phoenix(
    trace_class: str | None = None,
    title: str | None = None,
) -> dict[str, Any]:
    """Manually push previously recorded traces to Phoenix by filter."""
    if not EXPORT_FILE.exists():
        return {"export_file": str(EXPORT_FILE), "pushed": 0, "results": []}
    rows = EXPORT_FILE.read_text(encoding="utf-8", errors="ignore").splitlines()
    records = [json.loads(row) for row in rows if row.strip()]

    matched = []
    for rec in records:
        if trace_class is not None and rec.get("trace_class") != trace_class:
            continue
        if title is not None and rec.get("title") != title:
            continue
        matched.append(rec)

    results = []
    for rec in matched:
        result = _push_to_phoenix(rec)
        results.append({"record": rec, "phoenix": result})

    return {
        "export_file": str(EXPORT_FILE),
        "pushed": len(results),
        "results": results,
    }


@mcp.tool()
def phoenix_status() -> dict[str, Any]:
    """Check if Phoenix is reachable."""
    health_url = f"http://{PHOENIX_HOST}:{PHOENIX_PORT}/health"
    try:
        req = urllib.request.Request(health_url, method="GET")
        with urllib.request.urlopen(req, timeout=10) as response:
            body = response.read().decode("utf-8", errors="ignore")
        return {"reachable": True, "url": health_url, "status": response.status, "body": body}
    except Exception as exc:
        return {"reachable": False, "url": health_url, "error": str(exc)}


if __name__ == "__main__":
    mcp.run(transport="stdio")
