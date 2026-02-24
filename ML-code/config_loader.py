from pathlib import Path

import yaml


def load_config() -> dict:
    """Load config from config.yaml (same dir as this file)."""
    base_dir = Path(__file__).resolve().parent
    config_path = base_dir / "config.yaml"
    if not config_path.exists():
        raise FileNotFoundError(f"config.yaml not found at {config_path}")
    with config_path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    if not isinstance(data, dict):
        raise ValueError("config.yaml must contain a mapping at the top level.")
    return data

