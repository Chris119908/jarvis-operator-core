from __future__ import annotations

from pathlib import Path
from pydantic import BaseModel
import yaml


class ProviderConfig(BaseModel):
    type: str
    model: str
    base_url: str | None = None
    api_key_env: str | None = None


class RuntimeConfig(BaseModel):
    state_dir: str
    workspace_root: str
    log_dir: str
    log_level: str


class SafeCLIConfig(BaseModel):
    allowed_commands: list[str]
    default_timeout_seconds: int


class ToolsConfig(BaseModel):
    allowed_workspaces: list[str]
    safe_cli: SafeCLIConfig


class AppConfig(BaseModel):
    provider: ProviderConfig
    runtime: RuntimeConfig
    tools: ToolsConfig


def load_config(path: str | Path) -> AppConfig:
    config_path = Path(path).resolve()
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with config_path.open("r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)

    if not isinstance(raw, dict):
        raise ValueError("Config file must contain a YAML mapping.")

    config_root = config_path.parent
    runtime = raw.get("runtime", {})
    tools = raw.get("tools", {})

    runtime_workspace_root = Path(runtime.get("workspace_root", "."))
    if not runtime_workspace_root.is_absolute():
        runtime["workspace_root"] = str((config_root / runtime_workspace_root).resolve())

    normalized_allowed_workspaces: list[str] = []
    for workspace in tools.get("allowed_workspaces", []):
        workspace_path = Path(workspace)
        if workspace_path.is_absolute():
            normalized_allowed_workspaces.append(str(workspace_path.resolve()))
        else:
            normalized_allowed_workspaces.append(
                str((config_root / workspace_path).resolve())
            )
    tools["allowed_workspaces"] = normalized_allowed_workspaces

    return AppConfig.model_validate(raw)
