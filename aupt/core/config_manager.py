from __future__ import annotations

"""Configuration loading and persistence utilities."""

from copy import deepcopy
import json
from pathlib import Path
from typing import Any

DEFAULT_CONFIG = {
    "default_manager": "auto",
    "priority": ["apt", "pacman", "dnf", "zypper", "flatpak", "snap"],
    "mirror": {"auto_select": True, "timeout": 3.0},
    "cache": {"enabled": True},
}


class ConfigManager:
    """Manage user configuration stored in a YAML-compatible JSON file."""

    def __init__(self, config_path: Path | None = None) -> None:
        """Initialize the config manager.

        Args:
            config_path: Optional explicit config file path.

        Returns:
            None.

        References:
            - Default config: `DEFAULT_CONFIG` in current file.
        """

        self.config_path = config_path or Path.home() / ".config" / "aupt" / "config.yaml"

    def ensure_exists(self) -> None:
        """Create the default config file when it does not exist.

        Args:
            None.

        Returns:
            None.

        References:
            - Save method: `save()` in current file.
        """

        if not self.config_path.exists():
            self.save(deepcopy(DEFAULT_CONFIG))

    def load(self) -> dict[str, Any]:
        """Load configuration from disk.

        Args:
            None.

        Returns:
            dict[str, Any]: Configuration dictionary.

        References:
            - Default config: `DEFAULT_CONFIG` in current file.
        """

        self.ensure_exists()
        with self.config_path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
        merged = deepcopy(DEFAULT_CONFIG)
        self._deep_merge(merged, data)
        return merged

    def save(self, config: dict[str, Any]) -> None:
        """Persist configuration to disk.

        Args:
            config: Configuration dictionary to write.

        Returns:
            None.

        References:
            - Config path: `self.config_path` in current class.
        """

        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with self.config_path.open("w", encoding="utf-8") as handle:
            json.dump(config, handle, indent=2, ensure_ascii=False)
            handle.write("\n")

    def get(self, key_path: str | None = None) -> Any:
        """Read a configuration value.

        Args:
            key_path: Optional dot-separated key path.

        Returns:
            Any: Entire config or a single key value.

        References:
            - Loader: `load()` in current file.
        """

        config = self.load()
        if not key_path:
            return config
        current: Any = config
        for key in key_path.split("."):
            current = current[key]
        return current

    def set(self, key_path: str, value: Any) -> dict[str, Any]:
        """Set a configuration value and save it.

        Args:
            key_path: Dot-separated key path.
            value: Value to write.

        Returns:
            dict[str, Any]: Updated configuration.

        References:
            - Saver: `save()` in current file.
        """

        config = self.load()
        current = config
        keys = key_path.split(".")
        for key in keys[:-1]:
            current = current.setdefault(key, {})
        current[keys[-1]] = value
        self.save(config)
        return config

    def _deep_merge(self, base: dict[str, Any], new_data: dict[str, Any]) -> None:
        """Merge a user config into defaults recursively.

        Args:
            base: Mutable base dictionary.
            new_data: User-provided overrides.

        Returns:
            None.

        References:
            - Called by `load()` in current file.
        """

        for key, value in new_data.items():
            if isinstance(value, dict) and isinstance(base.get(key), dict):
                self._deep_merge(base[key], value)
            else:
                base[key] = value
