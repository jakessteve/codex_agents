---
name: structured-validation
description: Convert command output into compact pass/fail summaries with actionable failure details. Avoid large logs in conversation.
---

# Structured Validation

## Purpose
Reduce raw command output into compact, actionable evidence that is easy to verify and hand off. Never paste large logs into the conversation.

## Steps

### 1. Run the Required Validation Command
- Execute the test, build, or type-check command
- Capture the full output for processing

### 2. Reduce to Pass/Fail Summary
- Count passing and failing tests
- Identify the specific failures
- Categorize failures by type (assertion, timeout, compilation, runtime)

### 3. Keep Failures Actionable
- For each failure, include:
  - Test name or error location
  - Error message (truncated to key information)
  - Suggested fix (if obvious)
- Do NOT include full stack traces or large log outputs

### 4. Avoid Large Logs
- Never paste more than 20 lines of raw output
- Summarize: "50 tests passed, 3 failed" instead of pasting all 53 lines
- For build errors, list only the error lines, not the full build log

### 5. Output Format
```yaml
validation:
  command: <command run>
  total: <count>
  passed: <count>
  failed: <count>
  failures:
    - test: <test name or file:line>
      error: <key error message>
      fix: <suggested fix or "investigate">
  summary: <one-line summary>
```
