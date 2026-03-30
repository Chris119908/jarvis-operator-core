from jarvis_operator.config import load_config

def main() -> int:
    config = load_config("config.example.yaml")
    if not config.provider.type:
        raise RuntimeError("Provider type missing")
    print("Smoke check passed")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
