from __future__ import annotations

"""Snap backend implementation."""

from aupt.backends.base_backend import BackendCommand, BaseBackend


class SnapBackend(BaseBackend):
    """Provide Snap package management commands."""

    name = "snap"
    executable = "snap"

    def build_install_command(self, package: str, version: str | None = None) -> BackendCommand:
        """Build a Snap install command.

        Args:
            package: Snap package name.
            version: Optional channel string.

        Returns:
            BackendCommand: Prepared command object.

        References:
            - Unified interface: `aupt/backends/base_backend.py`
        """

        argv = ["snap", "install", package]
        if version:
            argv.extend(["--channel", version])
        return BackendCommand(argv, requires_root=True)

    def build_remove_command(self, package: str) -> BackendCommand:
        """Build a Snap remove command.

        Args:
            package: Snap package name.

        Returns:
            BackendCommand: Prepared command object.

        References:
            - Unified interface: `aupt/backends/base_backend.py`
        """

        return BackendCommand(["snap", "remove", package], requires_root=True)

    def build_update_command(self) -> BackendCommand:
        """Build a Snap refresh command.

        Args:
            None.

        Returns:
            BackendCommand: Prepared command object.

        References:
            - Unified interface: `aupt/backends/base_backend.py`
        """

        return BackendCommand(["snap", "refresh"], requires_root=True)

    def build_upgrade_command(self) -> BackendCommand:
        """Build a Snap upgrade command.

        Args:
            None.

        Returns:
            BackendCommand: Prepared command object.

        References:
            - Unified interface: `aupt/backends/base_backend.py`
        """

        return self.build_update_command()

    def build_search_command(self, keyword: str) -> BackendCommand:
        """Build a Snap search command.

        Args:
            keyword: Search keyword.

        Returns:
            BackendCommand: Prepared command object.

        References:
            - Unified interface: `aupt/backends/base_backend.py`
        """

        return BackendCommand(["snap", "find", keyword])

    def build_info_command(self, package: str) -> BackendCommand:
        """Build a Snap info command.

        Args:
            package: Snap package name.

        Returns:
            BackendCommand: Prepared command object.

        References:
            - Unified interface: `aupt/backends/base_backend.py`
        """

        return BackendCommand(["snap", "info", package])

    def build_clean_command(self) -> BackendCommand:
        """Build a Snap clean command.

        Args:
            None.

        Returns:
            BackendCommand: Prepared command object.

        References:
            - Unified interface: `aupt/backends/base_backend.py`
        """

        return BackendCommand(["snap", "set", "system", "refresh.retain=2"], requires_root=True)
