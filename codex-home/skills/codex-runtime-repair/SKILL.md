---
name: codex-runtime-repair
description: Repair the Codex runtime or its launcher surface with minimal changes and clear evidence.
---

# Codex Runtime Repair

## Purpose
Repair the runtime with minimal changes and clear evidence. Use when MCP servers fail, configs break, or the launcher surface needs fixing.

## Steps

### 1. Reproduce the Failure
- Identify the exact command or action that triggers the failure
- Run the command and capture the full error output
- Verify the failure is reproducible (run at least twice)
- Check if the failure is environment-specific

### 2. Identify the Smallest Safe Repair
- Use `treesitter_summarize_path` on the affected file(s)
- Use `codex_knowledge_memory_query` for past runtime issues
- Determine the minimal change that fixes the issue
- Verify the change doesn't break other functionality

### 3. Validate the Fix
- Run the reproduction command again
- Run any available health checks
- Use `minimalist_review_change` to verify minimalism
- Record the fix in `codex_knowledge_knowledge_capture`

### 4. Common Runtime Issues
- **MCP server won't start**: Check `uv sync`, Python version, port conflicts
- **Config parse error**: Validate JSON syntax, check field types against schema
- **LSP server not responding**: Check binary path, initialization options
- **Permission denied**: Check file permissions and Codex approval policy

### 5. Output Format
```yaml
runtime_repair:
  issue: <description>
  reproduction: <exact command>
  root_cause: <diagnosis>
  fix: <what was changed>
  files_changed: <list>
  validation: <reproduction result after fix>
```
