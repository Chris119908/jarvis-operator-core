# PROJECT_TARGET_SPEC.md
## Jarvis Operator Core v1

### 1. Vision
Jarvis Operator Core is a local, installable agent system that translates natural language into concrete computer tasks, executes them through controlled tools, validates results, and manages persistent state.

### 2. Scope (V1)
Build a functioning product that:
- installs locally
- is controlled via CLI
- works with swappable LLM backends
- executes real tasks reliably
- tests each function automatically
- validates results instead of claiming them

### 3. Non-Goals (V1)
Not part of V1:
- Voice interface
- GUI automation / vision RPA
- Multi-agent swarms
- Smart-home integration
- Active self-extension
- Unrestricted internet access
- Automatic software installation
- Complex UI

### 4. Target User
A technical single user running the system locally.

### 5. Fixed V1 Use Cases
1. Create a Python project scaffold
2. Analyze log files
3. Run tests and explain failures
4. Generate file structures from a specification

### 6. Functional Requirements
The system must support:
- CLI task intake
- tools: read_file, write_file, list_dir, safe_cli_run, optional fetch_url, state_store
- multi-step execution
- validation
- persistent state under .agent/
- transparent reporting of actions, tools, results, uncertainties

### 7. Non-Functional Requirements
- Security: whitelist-based CLI only, no shell injection, timeouts required
- Testability: each feature must be testable and tested
- Stability: no silent failures
- Extensibility: modular structure
- Logging: actions, tools, errors, results

### 8. LLM Requirements
Must support:
- Ollama
- OpenAI-compatible API
- Mock provider

### 9. Target Architecture
CLI -> Orchestrator -> Agent Logic (Coordinator, Executor, Validator) -> Tool Layer -> State Layer -> LLM Provider

### 10. Install Target
Must be installable with:
```bash
pip install -e .
cp config.example.yaml config.yaml
jarvis-operator doctor
jarvis-operator run "task"
```

### 11. Testing Strategy
Required:
- Unit tests
- Integration tests
- End-to-end tests
- Smoke tests

Rule:
No feature without test = not done.

### 12. Definition of Done
V1 is done when:
- all 4 use cases run
- all tests pass
- installation works
- CLI works
- state works
- logging exists
- LLM backend is swappable
- no critical security holes remain

### 13. Anti-Drift Rules
Codex must not:
- expand scope
- invent new systems
- build untested features
- use uncontrolled CLI
- bloat architecture
- activate self-extension in V1
