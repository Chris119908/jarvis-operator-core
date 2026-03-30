# TOOL_CONTRACTS.md

## Principles
Each tool must have:
- a single clear responsibility
- explicit inputs
- explicit outputs
- explicit error behavior
- tests
- security boundaries

## read_file
Purpose: read a text file from an allowed workspace.

Input:
- path: string

Output:
- content: string

Errors:
- FileNotFoundError
- PermissionError
- UnicodeDecodeError

Tests:
- reads normal file
- fails on missing file

## write_file
Purpose: write a text file into an allowed workspace.

Input:
- path: string
- content: string

Output:
- success: boolean
- bytes_written: integer

Errors:
- PermissionError
- ValueError for invalid paths

Tests:
- writes new file
- overwrites existing file
- blocks invalid path

## list_dir
Purpose: list entries in an allowed directory.

Input:
- path: string

Output:
- entries: list[string]

Errors:
- FileNotFoundError
- PermissionError

Tests:
- lists files
- handles empty directory

## safe_cli_run
Purpose: run allowlisted commands in allowlisted workspaces.

Input:
- command: list[string]
- cwd: string
- timeout_seconds: integer optional

Output:
- returncode: integer
- stdout: string
- stderr: string
- timed_out: boolean

Rules:
- only allow command[0] in allowlist
- no shell=True
- no command chaining
- cwd must be within allowed workspace
- timeout mandatory by default

Errors:
- PermissionError
- ValueError
- TimeoutExpired converted to timed_out=true

Tests:
- allowed command succeeds
- forbidden command blocked
- disallowed cwd blocked

## state_store
Purpose: persist and load .agent/STATE.json

Input:
- state_dir: string
- data: dict for save

Output:
- load_state(): dict
- save_state(): None

Errors:
- JSONDecodeError for broken file

Tests:
- save/load roundtrip
- empty state if file missing
