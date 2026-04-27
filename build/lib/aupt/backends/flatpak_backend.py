from __future__ import annotations

"""Flatpak backend implementation."""

from aupt.backends.base_backend import BackendCommand, BaseBackend


class FlatpakBackend(BaseBackend):
    """Provide Flatpak package management commands."""

    name = "flatpak"
    executable = "flatpak"

    def build_install_command(self, package: str, version: str | None = None) -> BackendCommand:
        """Build a Flatpak install command.

        Args:
            package: Package name or application id.
            version: Optional branch string.

        Returns:
            BackendCommand: Prepared command object.

        References:
            - Unified interface: `aupt/backends/base_backend.py`
        """

        argv = ["flatpak", "install", "-y", package]
        if version:
            argv.extend(["--branch", version])
        return BackendCommand(argv)

    def build_remove_command(self, package: str) -> BackendCommand:
        """Build a Flatpak remove command.

        Args:
            package: Package name or application id.

        Returns:
            BackendCommand: Prepared command object.

        References:
            - Unified interface: `aupt/backends/base_backend.py`
        """

        return BackendCommand(["flatpak", "uninstall", "-y", package])

    def build_update_command(self) -> BackendCommand:
        """Build a Flatpak update command.

        Args:
            None.

        Returns:
            BackendCommand: Prepared command object.

        References:
            - Unified interface: `aupt/backends/base_backend.py`
        """

        return BackendCommand(["flatpak", "update", "-y"])

    def build_upgrade_command(self) -> BackendCommand:
        """Build a Flatpak upgrade command.

        Args:
            None.

        Returns:
            BackendCommand: Prepared command object.

        References:
            - Unified interface: `aupt/backends/base_backend.py`
        """

        return self.build_update_command()

    def build_search_command(self, keyword: str) -> BackendCommand:
        """Build a Flatpak search command.

        Args:
            keyword: Search keyword.

        Returns:
            BackendCommand: Prepared command object.

        References:
            - Unified interface: `aupt/backends/base_backend.py`
        """

        return BackendCommand(["flatpak", "search", keyword])

    def build_info_command(self, package: str) -> BackendCommand:
        """Build a Flatpak info command.

        Args:
            package: Package name or application id.

        Returns:
            BackendCommand: Prepared command object.

        References:
            - Unified interface: `aupt/backends/base_backend.py`
        """

        return BackendCommand(["flatpak", "info", package])

    def build_clean_command(self) -> BackendCommand:
        """Build a Flatpak clean command.

        Args:
            None.

        Returns:
            BackendCommand: Prepared command object.

        References:
            - Unified interface: `aupt/backends/base_backend.py`
        """

        return BackendCommand(["flatpak", "uninstall", "--unused", "-y"])
