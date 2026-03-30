from jarvis_operator.config import load_config

def run_doctor(config_path: str = "config.yaml") -> int:
    config = load_config(config_path)
    print("Doctor OK")
    print(f"Provider: {config.provider.type}")
    print(f"State dir: {config.runtime.state_dir}")
    return 0
