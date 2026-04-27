from __future__ import annotations

"""Zypper backend implementation."""

from aupt.backends.base_backend import BackendCommand, BaseBackend


class ZypperBackend(BaseBackend):
    """Provide openSUSE package management commands."""

    name = "zypper"
    executable = "zypper"

    def build_install_command(self, package: str, version: str | None = None) -> BackendCommand:
        """Build a zypper install command.

        Args:
            package: Package name resolved for zypper.
            version: Optional version string.

        Returns:
            BackendCommand: Prepared command object.

        References:
            - Unified interface: `aupt/backends/base_backend.py`
        """

        target = f"{package}={version}" if version else package
        return BackendCommand(["zypper", "--non-interactive", "install", target], requires_root=True)

    def build_remove_command(self, package: str) -> BackendCommand:
        """Build a zypper remove command.

        Args:
            package: Package name resolved for zypper.

        Returns:
            BackendCommand: Prepared command object.

        References:
            - Unified interface: `aupt/backends/base_backend.py`
        """

        return BackendCommand(["zypper", "--non-interactive", "remove", package], requires_root=True)

    def build_update_command(self) -> BackendCommand:
        """Build a zypper refresh command.

        Args:
            None.

        Returns:
            BackendCommand: Prepared command object.

        References:
            - Unified interface: `aupt/backends/base_backend.py`
        """

        return BackendCommand(["zypper", "refresh"], requires_root=True)

    def build_upgrade_command(self) -> BackendCommand:
        """Build a zypper upgrade command.

        Args:
            None.

        Returns:
            BackendCommand: Prepared command object.

        References:
            - Unified interface: `aupt/backends/base_backend.py`
        """

        return BackendCommand(["zypper", "--non-interactive", "update"], requires_root=True)

    def build_search_command(self, keyword: str) -> BackendCommand:
        """Build a zypper search command.

        Args:
            keyword: Search keyword.

        Returns:
            BackendCommand: Prepared command object.

        References:
            - Unified interface: `aupt/backends/base_backend.py`
        """

        return BackendCommand(["zypper", "search", keyword])

    def build_info_command(self, package: str) -> BackendCommand:
        """Build a zypper info command.

        Args:
            package: Package name resolved for zypper.

        Returns:
            BackendCommand: Prepared command object.

        References:
            - Unified interface: `aupt/backends/base_backend.py`
        """

        return BackendCommand(["zypper", "info", package])

    def build_clean_command(self) -> BackendCommand:
        """Build a zypper clean command.

        Args:
            None.

        Returns:
            BackendCommand: Prepared command object.

        References:
            - Unified interface: `aupt/backends/base_backend.py`
        """

        return BackendCommand(["zypper", "clean", "--all"], requires_root=True)
