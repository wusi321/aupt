from __future__ import annotations

"""APT backend implementation."""

from aupt.backends.base_backend import BackendCommand, BaseBackend


class AptBackend(BaseBackend):
    """Provide Debian-family package management commands."""

    name = "apt"
    executable = "apt-get"

    def build_install_command(self, package: str, version: str | None = None) -> BackendCommand:
        """Build an APT install command.

        Args:
            package: Package name resolved for APT.
            version: Optional APT version string.

        Returns:
            BackendCommand: Prepared command object.

        References:
            - Unified interface: `aupt/backends/base_backend.py`
        """

        target = f"{package}={version}" if version else package
        return BackendCommand(["apt-get", "install", "-y", target], requires_root=True)

    def build_remove_command(self, package: str) -> BackendCommand:
        """Build an APT remove command.

        Args:
            package: Package name resolved for APT.

        Returns:
            BackendCommand: Prepared command object.

        References:
            - Unified interface: `aupt/backends/base_backend.py`
        """

        return BackendCommand(["apt-get", "remove", "-y", package], requires_root=True)

    def build_update_command(self) -> BackendCommand:
        """Build an APT update command.

        Args:
            None.

        Returns:
            BackendCommand: Prepared command object.

        References:
            - Unified interface: `aupt/backends/base_backend.py`
        """

        return BackendCommand(["apt-get", "update", "-y"], requires_root=True)

    def build_upgrade_command(self) -> BackendCommand:
        """Build an APT upgrade command.

        Args:
            None.

        Returns:
            BackendCommand: Prepared command object.

        References:
            - Unified interface: `aupt/backends/base_backend.py`
        """

        return BackendCommand(["apt-get", "upgrade", "-y"], requires_root=True)

    def build_search_command(self, keyword: str) -> BackendCommand:
        """Build an APT search command.

        Args:
            keyword: Search keyword.

        Returns:
            BackendCommand: Prepared command object.

        References:
            - Unified interface: `aupt/backends/base_backend.py`
        """

        return BackendCommand(["apt-cache", "search", keyword])

    def build_info_command(self, package: str) -> BackendCommand:
        """Build an APT info command.

        Args:
            package: Package name resolved for APT.

        Returns:
            BackendCommand: Prepared command object.

        References:
            - Unified interface: `aupt/backends/base_backend.py`
        """

        return BackendCommand(["apt-cache", "show", package])

    def build_clean_command(self) -> BackendCommand:
        """Build an APT clean command.

        Args:
            None.

        Returns:
            BackendCommand: Prepared command object.

        References:
            - Unified interface: `aupt/backends/base_backend.py`
        """

        return BackendCommand(["apt-get", "autoremove", "-y"], requires_root=True)
