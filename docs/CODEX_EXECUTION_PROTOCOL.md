# CODEX_EXECUTION_PROTOCOL.md

## Required Read Order
Before making changes, read:
1. docs/PROJECT_TARGET_SPEC.md
2. docs/TOOL_CONTRACTS.md
3. docs/LLM_PROVIDER_SPEC.md
4. docs/STATE_MODEL.md
5. docs/TESTING_STRATEGY.md
6. .agent/STATE.json
7. .agent/NEXT_ACTION.md
8. AGENTS.md

## Loop
For each iteration:
1. read context
2. select the smallest next task
3. implement only that task
4. add or update tests
5. run relevant tests
6. update .agent/STATE.json
7. update .agent/SUMMARY.md
8. update .agent/NEXT_ACTION.md
9. record unresolved failures in .agent/KNOWN_ISSUES.md

## Hard Rules
- do not expand scope
- do not invent new subsystems
- do not mark features complete without evidence
- do not skip tests
- do not silently change architecture beyond the spec
