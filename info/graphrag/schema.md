# Graph Schema

status: scaffold
owner: librarian
summary: Define the graph entities and relations used for requirements, stories, decisions, traces, and evidence.

## Core Nodes

| Node | Meaning |
|---|---|
| project | Root project identity and scope. |
| document | Any durable project artifact. |
| requirement | Business, product, or technical requirement. |
| epic | Bounded delivery slice. |
| story | User facing or implementation story. |
| task | Atomic execution item. |
| agent | A role that produced or reviewed an artifact. |
| contract | PM, agent, subagent, or Oracle contract. |
| test | A validation action or suite. |
| evidence | Captured proof of execution. |
| decision | ADR or routing decision. |
| trace | Durable execution or observability record. |

## Core Edges

| Edge | Meaning |
|---|---|
| derives_from | A lower level artifact came from a higher level source. |
| implements | A task or story implements an approved requirement. |
| validates | A test or evidence item validates an artifact. |
| approves | Oracle or PM approval of a gate result. |
| references | A soft reference to supporting context. |
| owns | A role or agent owns a file or contract. |
| traces_to | A trace or evidence item connects to a source artifact. |
