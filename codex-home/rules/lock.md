# Lock Rules

- Acquire a writer lock before editing.
- Do not edit while the other runtime holds the write lock.
- Release the lock on exit.
