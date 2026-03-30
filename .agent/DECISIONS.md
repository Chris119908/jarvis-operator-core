# Decisions

## Initial architectural decisions

- V1 is CLI-first.
- V1 uses a provider abstraction layer.
- V1 must support a MockProvider for deterministic tests.
- V1 must keep persistent state in .agent/.
- V1 must not implement active self-extension.
- V1 must prioritize testability over feature breadth.
