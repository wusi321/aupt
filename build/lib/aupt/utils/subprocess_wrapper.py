from __future__ import annotations

"""Subprocess execution wrapper."""

from dataclasses import dataclass
import subprocess
from typing import Sequence


@dataclass
class CommandResult:
    """Wrap subprocess execution output.

    Args:
        command: Executed command vector.
        returncode: Process exit code.
        stdout: Standard output text.
        stderr: Standard error text.

    Returns:
        None.

    References:
        - Producer: `run_command()` in current file.
    """

    command: list[str]
    returncode: int
    stdout: str
    stderr: str


def run_command(argv: Sequence[str], dry_run: bool = False, timeout: int = 600) -> CommandResult:
    """Run a subprocess command safely without shell interpolation.

    Args:
        argv: Process argument vector.
        dry_run: Whether to skip real execution.
        timeout: Execution timeout in seconds.

    Returns:
        CommandResult: Process execution result.

    References:
        - Result type: `CommandResult` in current file.
    """

    command = list(argv)
    if dry_run:
        return CommandResult(command, 0, "DRY-RUN: " + " ".join(command), "")
    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,
            timeout=timeout,
        )
        return CommandResult(command, completed.returncode, completed.stdout, completed.stderr)
    except KeyboardInterrupt:
        return CommandResult(command, 130, "", "用户取消了操作 (Ctrl+C)")
    except FileNotFoundError as exc:
        return CommandResult(command, 127, "", str(exc))
    except subprocess.TimeoutExpired as exc:
        return CommandResult(command, 124, exc.stdout or "", f"命令执行超时: {exc}")
