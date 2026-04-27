from __future__ import annotations

"""DNF backend implementation."""

from aupt.backends.base_backend import BackendCommand, BaseBackend


class DnfBackend(BaseBackend):
    """Provide Fedora-family package management commands."""

    name = "dnf"
    executable = "dnf"

    def build_install_command(self, package: str, version: str | None = None) -> BackendCommand:
        """Build a DNF install command.

        Args:
            package: Package name resolved for DNF.
            version: Optional version string.

        Returns:
            BackendCommand: Prepared command object.

        References:
            - Unified interface: `aupt/backends/base_backend.py`
        """

        target = f"{package}-{version}" if version else package
        return BackendCommand(["dnf", "install", "-y", target], requires_root=True)

    def build_remove_command(self, package: str) -> BackendCommand:
        """Build a DNF remove command.

        Args:
            package: Package name resolved for DNF.

        Returns:
            BackendCommand: Prepared command object.

        References:
            - Unified interface: `aupt/backends/base_backend.py`
        """

        return BackendCommand(["dnf", "remove", "-y", package], requires_root=True)

    def build_update_command(self) -> BackendCommand:
        """Build a DNF update command.

        Args:
            None.

        Returns:
            BackendCommand: Prepared command object.

        References:
            - Unified interface: `aupt/backends/base_backend.py`
        """

        return BackendCommand(["dnf", "makecache"], requires_root=True)

    def build_upgrade_command(self) -> BackendCommand:
        """Build a DNF upgrade command.

        Args:
            None.

        Returns:
            BackendCommand: Prepared command object.

        References:
            - Unified interface: `aupt/backends/base_backend.py`
        """

        return BackendCommand(["dnf", "upgrade", "-y"], requires_root=True)

    def build_search_command(self, keyword: str) -> BackendCommand:
        """Build a DNF search command.

        Args:
            keyword: Search keyword.

        Returns:
            BackendCommand: Prepared command object.

        References:
            - Unified interface: `aupt/backends/base_backend.py`
        """

        return BackendCommand(["dnf", "search", keyword])

    def build_info_command(self, package: str) -> BackendCommand:
        """Build a DNF info command.

        Args:
            package: Package name resolved for DNF.

        Returns:
            BackendCommand: Prepared command object.

        References:
            - Unified interface: `aupt/backends/base_backend.py`
        """

        return BackendCommand(["dnf", "info", package])

    def build_clean_command(self) -> BackendCommand:
        """Build a DNF clean command.

        Args:
            None.

        Returns:
            BackendCommand: Prepared command object.

        References:
            - Unified interface: `aupt/backends/base_backend.py`
        """

        return BackendCommand(["dnf", "clean", "all"], requires_root=True)
