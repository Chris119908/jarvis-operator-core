# AGENTS.md

This repository is developed under strict scope and testing discipline.

Before making any change, always read:
1. docs/PROJECT_TARGET_SPEC.md
2. docs/CODEX_EXECUTION_PROTOCOL.md
3. .agent/STATE.json
4. .agent/NEXT_ACTION.md

Rules:
- Work only on the smallest next task.
- Do not expand scope.
- Do not invent architecture beyond the spec.
- No feature is complete without tests.
- After every meaningful change:
  - update or add tests
  - run relevant tests
  - update .agent/STATE.json
  - update .agent/SUMMARY.md
  - update .agent/NEXT_ACTION.md

Priority:
1. correctness
2. testability
3. simplicity
4. extensibility

Never mark work as done without evidence.
