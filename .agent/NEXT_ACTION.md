# Next Action

Verify the `state_store` contract for the smallest missing case:

- add a unit test proving `StateStore.load_state()` returns an empty dict when `STATE.json` is missing
- run the relevant unit tests
- update `.agent/STATE.json`, `.agent/SUMMARY.md`, and `.agent/NEXT_ACTION.md`
