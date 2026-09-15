"""Subprocess execution wrapper."""

from dataclasses import dataclass
import subprocess
from typing import List, Sequence


@dataclass
class CommandResult:
    """Wrap subprocess execution output."""

    command: List[str]
    returncode: int
    stdout: str
    stderr: str


def run_command(argv: Sequence[str], dry_run: bool = False, timeout: int = 600, stream: bool = False) -> CommandResult:
    """Run a subprocess without shell interpolation on Python 3.6+."""

    command = list(argv)
    if dry_run:
        return CommandResult(command, 0, "DRY-RUN: " + " ".join(command), "")
    try:
        if stream:
            completed = subprocess.run(command, check=False, timeout=timeout)
            return CommandResult(command, completed.returncode, "", "")
        completed = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            check=False,
            timeout=timeout,
        )
        return CommandResult(command, completed.returncode, completed.stdout or "", completed.stderr or "")
    except KeyboardInterrupt:
        return CommandResult(command, 130, "", "用户取消了操作 (Ctrl+C)")
    except FileNotFoundError as exc:
        return CommandResult(command, 127, "", str(exc))
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout or ""
        stderr = exc.stderr or ""
        if isinstance(stdout, bytes):
            stdout = stdout.decode(errors="replace")
        if isinstance(stderr, bytes):
            stderr = stderr.decode(errors="replace")
        return CommandResult(command, 124, stdout, stderr or "命令执行超时: {}".format(exc))
