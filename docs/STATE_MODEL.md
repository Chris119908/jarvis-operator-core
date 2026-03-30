# STATE_MODEL.md

## Purpose
Persistent state prevents context loss across Codex iterations.

## Files under .agent/
- STATE.json: machine-readable state
- SUMMARY.md: human-readable short status
- NEXT_ACTION.md: exactly one next concrete step
- KNOWN_ISSUES.md: open issues and blockers
- DECISIONS.md: architecture and scope decisions

## Minimum STATE.json fields
- project_name
- version_target
- current_goal
- current_status
- current_step
- completed_steps
- pending_steps
- known_blockers
- created_artifacts
- selected_provider
- last_validation_status

## Update Rules
After each meaningful development iteration:
- STATE.json must be updated
- SUMMARY.md must be refreshed
- NEXT_ACTION.md must point to the smallest next task
- KNOWN_ISSUES.md must track unresolved failures
