from __future__ import annotations

"""Abstract backend interface and shared command execution helpers."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Iterable, Sequence
import shutil

from aupt.utils.subprocess_wrapper import CommandResult, run_command


@dataclass
class BackendCommand:
    """Represent a prepared backend command.

    Args:
        argv: Subprocess argument vector.
        requires_root: Whether the command should be prefixed with sudo.

    Returns:
        None.

    References:
        - Command execution: `aupt/utils/subprocess_wrapper.py`
    """

    argv: list[str]
    requires_root: bool = False


class BaseBackend(ABC):
    """Define the unified backend interface for package managers."""

    name = "base"
    executable = ""

    def is_available(self) -> bool:
        """Check whether the backend executable exists on the current system.

        Args:
            None.

        Returns:
            bool: True when the package manager executable is available.

        References:
            - Backend executable declaration: current class attributes.
        """

        return bool(self.executable and shutil.which(self.executable))

    def execute(self, command: BackendCommand, dry_run: bool = False, stream: bool = False) -> CommandResult:
        """Execute a prepared backend command.

        Args:
            command: Prepared backend command object.
            dry_run: Whether to only print the command without executing it.
            stream: When True, output flows to terminal in real-time (for long commands).

        Returns:
            CommandResult: Process execution result.

        References:
            - Command wrapper: `aupt/utils/subprocess_wrapper.py`
        """

        argv = list(command.argv)
        if command.requires_root and shutil.which("sudo"):
            argv = ["sudo", *argv]
        return run_command(argv, dry_run=dry_run, stream=stream)

    def install(self, package: str, version: str | None = None, dry_run: bool = False) -> CommandResult:
        """Install a package through the backend.

        Args:
            package: Resolved package name.
            version: Optional requested version string.
            dry_run: Whether to only print the command.

        Returns:
            CommandResult: Process execution result.

        References:
            - Builder hook: `build_install_command()` in current class.
        """

        return self.execute(self.build_install_command(package, version), dry_run=dry_run, stream=not dry_run)

    def remove(self, package: str, dry_run: bool = False) -> CommandResult:
        """Remove a package through the backend.

        Args:
            package: Resolved package name.
            dry_run: Whether to only print the command.

        Returns:
            CommandResult: Process execution result.

        References:
            - Builder hook: `build_remove_command()` in current class.
        """

        return self.execute(self.build_remove_command(package), dry_run=dry_run, stream=not dry_run)

    def update(self, dry_run: bool = False) -> CommandResult:
        """Refresh package index through the backend.

        Args:
            dry_run: Whether to only print the command.

        Returns:
            CommandResult: Process execution result.

        References:
            - Builder hook: `build_update_command()` in current class.
        """

        return self.execute(self.build_update_command(), dry_run=dry_run, stream=not dry_run)

    def upgrade(self, dry_run: bool = False) -> CommandResult:
        """Upgrade installed packages through the backend.

        Args:
            dry_run: Whether to only print the command.

        Returns:
            CommandResult: Process execution result.

        References:
            - Builder hook: `build_upgrade_command()` in current class.
        """

        return self.execute(self.build_upgrade_command(), dry_run=dry_run, stream=not dry_run)

    def search(self, keyword: str, dry_run: bool = False) -> CommandResult:
        """Search packages through the backend.

        Args:
            keyword: Search keyword.
            dry_run: Whether to only print the command.

        Returns:
            CommandResult: Process execution result.

        References:
            - Builder hook: `build_search_command()` in current class.
        """

        return self.execute(self.build_search_command(keyword), dry_run=dry_run)

    def info(self, package: str, dry_run: bool = False) -> CommandResult:
        """Show package metadata through the backend.

        Args:
            package: Resolved package name.
            dry_run: Whether to only print the command.

        Returns:
            CommandResult: Process execution result.

        References:
            - Builder hook: `build_info_command()` in current class.
        """

        return self.execute(self.build_info_command(package), dry_run=dry_run)

    def clean(self, dry_run: bool = False) -> CommandResult:
        """Clean local package caches through the backend.

        Args:
            dry_run: Whether to only print the command.

        Returns:
            CommandResult: Process execution result.

        References:
            - Builder hook: `build_clean_command()` in current class.
        """

        return self.execute(self.build_clean_command(), dry_run=dry_run, stream=not dry_run)

    @abstractmethod
    def build_install_command(self, package: str, version: str | None = None) -> BackendCommand:
        """Build the install command for the concrete backend.

        Args:
            package: Resolved package name.
            version: Optional requested version string.

        Returns:
            BackendCommand: Prepared command.

        References:
            - Called by `install()` in current file.
        """

    @abstractmethod
    def build_remove_command(self, package: str) -> BackendCommand:
        """Build the remove command for the concrete backend.

        Args:
            package: Resolved package name.

        Returns:
            BackendCommand: Prepared command.

        References:
            - Called by `remove()` in current file.
        """

    @abstractmethod
    def build_update_command(self) -> BackendCommand:
        """Build the update command for the concrete backend.

        Args:
            None.

        Returns:
            BackendCommand: Prepared command.

        References:
            - Called by `update()` in current file.
        """

    @abstractmethod
    def build_upgrade_command(self) -> BackendCommand:
        """Build the upgrade command for the concrete backend.

        Args:
            None.

        Returns:
            BackendCommand: Prepared command.

        References:
            - Called by `upgrade()` in current file.
        """

    @abstractmethod
    def build_search_command(self, keyword: str) -> BackendCommand:
        """Build the search command for the concrete backend.

        Args:
            keyword: Search keyword.

        Returns:
            BackendCommand: Prepared command.

        References:
            - Called by `search()` in current file.
        """

    @abstractmethod
    def build_info_command(self, package: str) -> BackendCommand:
        """Build the info command for the concrete backend.

        Args:
            package: Resolved package name.

        Returns:
            BackendCommand: Prepared command.

        References:
            - Called by `info()` in current file.
        """

    @abstractmethod
    def build_clean_command(self) -> BackendCommand:
        """Build the clean command for the concrete backend.

        Args:
            None.

        Returns:
            BackendCommand: Prepared command.

        References:
            - Called by `clean()` in current file.
        """
