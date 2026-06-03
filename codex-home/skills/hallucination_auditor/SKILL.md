---
name: hallucination-auditor
description: Audits agent outputs for hallucinations, scope drift, and logical inconsistencies. Use when reviewing code changes, generated text, or before final completion gates.
---

# Skill: Hallucination Auditor (Verification of Truth & Scope)

## Purpose
Examine agent outputs to verify that all code changes, CLI commands, and design claims are mathematically and structurally sound and backed by real repository files.

## Audit Taxonomy (AgentHallu)
Classify any detected inconsistencies into one of these types:
1. **Fabricated Reference**: Referencing functions, classes, files, or packages that do not exist.
2. **State Divergence**: Claiming a test has passed or a service is running without actually executing it or checking its logs.
3. **Scope Creep**: Implementing features or modifying files outside of the Scope Lock task contract.
4. **Command Invention**: Proposing shell commands that are invalid, uninstalled, or unsupported.

## Operational Protocol
- **Cross-Reference Claims**: Match every modified file, function call, and library update against actual files in the workspace.
- **Diagnostics Check**: Review Tree-sitter AST nodes and language server diagnostics to confirm there are no unresolved compile/lint issues.
- **Generate Report**: List all audit findings sorted by severity (Blocker, Warning, Info) with direct file and line references.
