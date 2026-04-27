from __future__ import annotations

"""Package alias resolution service."""

import json
from pathlib import Path


class PackageResolver:
    """Resolve logical package names into manager-specific names."""

    def __init__(self, alias_path: Path) -> None:
        """Initialize the package resolver.

        Args:
            alias_path: JSON alias database path.

        Returns:
            None.

        References:
            - Alias file: `aupt/database/package_alias.json`
        """

        self.alias_path = alias_path
        self.aliases = self._load_aliases()

    def _load_aliases(self) -> dict[str, dict[str, str]]:
        """Load alias mapping from disk.

        Args:
            None.

        Returns:
            dict[str, dict[str, str]]: Alias database.

        References:
            - Called by `__init__()` in current file.
        """

        with self.alias_path.open("r", encoding="utf-8") as handle:
            return json.load(handle)

    def resolve(self, requested_name: str, manager: str) -> str:
        """Resolve a user-facing package name for a specific backend.

        Args:
            requested_name: Original package name from user input.
            manager: Target backend manager name.

        Returns:
            str: Backend-specific package name.

        References:
            - Alias table: `self.aliases` in current class.
        """

        key = requested_name.lower()
        manager_alias = self.aliases.get(key, {})
        return manager_alias.get(manager, requested_name)
