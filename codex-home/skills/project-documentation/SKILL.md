---
name: project-documentation
description: Convert a validated PRD or requirements set into traceable delivery documents, including architecture notes, epic specifications, user story specifications, and atomic task lists. Use when Codex needs to plan, decompose, or document work before implementation, or when a change needs the full PRD-to-delivery document chain to reduce hallucination.
---

# Project Documentation

Use this skill when the task needs an end-to-end document chain rather than a single prose artifact.

## Workflow
1. Read the current project context and the relevant indexes in order: requirement, architecture, and story.
2. Anchor on approved source docs only: PRD, SRS, architecture, design, ADRs, existing epics, existing stories, and existing task lists.
3. If the source set is incomplete, stop and ask PM or the user for the missing decision before inventing scope.
4. Produce the smallest sufficient set of documents:
   - PRD or requirements summary
   - architecture or design notes when needed
   - epic specification
   - user story specification
   - atomic task list
5. Keep each downstream artifact traceable back to the source docs and forward to the implementation work.
6. Prefer delta updates over rewrites. Preserve the repository's one-file-per-artifact layout.
7. Use `document-sync` and `obsidian-sot` after approval to update indexes and approved summaries.

## Guardrails
- Do not invent epics, stories, tasks, or acceptance criteria that are not grounded in approved source docs.
- Do not skip straight from PRD to code when the change needs decomposition.
- Do not expand scope just because the document structure allows it.
- Keep task lists actionable enough that implementation agents can execute without guessing.
