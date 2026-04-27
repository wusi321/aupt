from __future__ import annotations

"""Pacman backend implementation."""

from aupt.backends.base_backend import BackendCommand, BaseBackend


class PacmanBackend(BaseBackend):
    """Provide Arch-family package management commands."""

    name = "pacman"
    executable = "pacman"

    def build_install_command(self, package: str, version: str | None = None) -> BackendCommand:
        """Build a pacman install command.

        Args:
            package: Package name resolved for pacman.
            version: Optional version string, currently unsupported.

        Returns:
            BackendCommand: Prepared command object.

        References:
            - Unified interface: `aupt/backends/base_backend.py`
        """

        if version:
            raise ValueError("pacman backend 暂不支持直接指定历史版本安装")
        return BackendCommand(["pacman", "-S", "--noconfirm", package], requires_root=True)

    def build_remove_command(self, package: str) -> BackendCommand:
        """Build a pacman remove command.

        Args:
            package: Package name resolved for pacman.

        Returns:
            BackendCommand: Prepared command object.

        References:
            - Unified interface: `aupt/backends/base_backend.py`
        """

        return BackendCommand(["pacman", "-R", "--noconfirm", package], requires_root=True)

    def build_update_command(self) -> BackendCommand:
        """Build a pacman update command.

        Args:
            None.

        Returns:
            BackendCommand: Prepared command object.

        References:
            - Unified interface: `aupt/backends/base_backend.py`
        """

        return BackendCommand(["pacman", "-Sy"], requires_root=True)

    def build_upgrade_command(self) -> BackendCommand:
        """Build a pacman upgrade command.

        Args:
            None.

        Returns:
            BackendCommand: Prepared command object.

        References:
            - Unified interface: `aupt/backends/base_backend.py`
        """

        return BackendCommand(["pacman", "-Syu", "--noconfirm"], requires_root=True)

    def build_search_command(self, keyword: str) -> BackendCommand:
        """Build a pacman search command.

        Args:
            keyword: Search keyword.

        Returns:
            BackendCommand: Prepared command object.

        References:
            - Unified interface: `aupt/backends/base_backend.py`
        """

        return BackendCommand(["pacman", "-Ss", keyword])

    def build_info_command(self, package: str) -> BackendCommand:
        """Build a pacman info command.

        Args:
            package: Package name resolved for pacman.

        Returns:
            BackendCommand: Prepared command object.

        References:
            - Unified interface: `aupt/backends/base_backend.py`
        """

        return BackendCommand(["pacman", "-Si", package])

    def build_clean_command(self) -> BackendCommand:
        """Build a pacman clean command.

        Args:
            None.

        Returns:
            BackendCommand: Prepared command object.

        References:
            - Unified interface: `aupt/backends/base_backend.py`
        """

        return BackendCommand(["pacman", "-Scc", "--noconfirm"], requires_root=True)
