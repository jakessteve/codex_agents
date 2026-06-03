---
name: requirement-interviewer
description: Elicit and clarify vague, underspecified, or scope-ambiguous requests through focused questioning.
---

# Requirement Interviewer

## Purpose
Transform vague requests into clear, validated requirements by asking focused questions and removing ambiguity before planning begins.

## Steps

### 1. Analyze the Request
- What is explicitly stated?
- What is implied but not stated?
- What is ambiguous or could be interpreted multiple ways?
- What decisions need to be made?

### 2. Identify Question Types
- **Clarification questions**: What did you mean by X?
- **Scope questions**: Should Y be included or excluded?
- **Priority questions**: Which is more important, A or B?
- **Constraint questions**: Are there technical or business constraints?
- **Validation questions**: Can you confirm that Z is correct?

### 3. Ask Focused Questions
- Ask one question at a time
- Provide options when possible (not open-ended)
- Use `question` tool for structured input
- Record all answers

### 4. Remove Ambiguity
- Replace vague terms with specific definitions
- Replace "etc." with explicit lists
- Replace "should" with "must" or "may"
- Replace "fast" with measurable thresholds

### 5. Output Format
```yaml
requirement_interview:
  original_request: <user's exact words>
  clarified_requirements:
    - requirement: <clarified statement>
      source: <user confirmation or inference>
      priority: <must_have|should_have|nice_to_have>
  ambiguities_resolved:
    - ambiguity: <what was unclear>
      resolution: <how it was resolved>
  decisions_needed:
    - decision: <what still needs user input>
      options: <list of options>
  scope_boundary:
    in_scope: <explicitly included>
    out_of_scope: <explicitly excluded>
```
