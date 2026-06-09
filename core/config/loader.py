# Configuration Loader

#default_config.yaml  (required, shipped with repo)
#config.yaml          (optional, user overrides)

from pathlib import Path
import yaml

DEFAULT_CONFIG_PATH = Path("core/config/default_config.yaml")
USER_CONFIG_PATH = Path("core/config/config.yaml")


def deep_merge(base: dict, override: dict) -> dict:
    """
    Recursively merge two dictionaries.
    Values in 'override' take precedence.
    """
    result = base.copy()
    for key, value in override.items():
        if (
            key in result
            and isinstance(result[key], dict)
            and isinstance(value, dict)
        ):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def load_yaml(path: Path) -> dict:
    """Load YAML safely, return {} if missing or empty."""
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def load_config() -> dict:
    """
    Load and merge default + user config.
    User config overrides defaults.
    """
    default_cfg = load_yaml(DEFAULT_CONFIG_PATH)
    user_cfg = load_yaml(USER_CONFIG_PATH)

    return deep_merge(default_cfg, user_cfg)
