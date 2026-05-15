from __future__ import annotations

"""Interactive mirror selection menu with timeout fallback."""

import select
import sys
from typing import Any

from aupt.core.mirror_manager import MirrorManager, MirrorRecord
from aupt.utils.subprocess_wrapper import CommandResult

MENU_TIMEOUT_SECONDS = 15


def select_mirror_interactive(
    mirror_manager: MirrorManager,
    manager: str | None = None,
    timeout_seconds: int = MENU_TIMEOUT_SECONDS,
) -> str | None:
    """Display an interactive mirror selection menu and return the chosen mirror name.

    Args:
        mirror_manager: Mirror manager instance to query mirrors.
        manager: Optional backend manager name. When omitted, use detected manager.
        timeout_seconds: Seconds to wait for user input before auto-selecting option 1.

    Returns:
        str | None: Selected mirror name, or None when cancelled.

    References:
        - Mirror manager: `aupt/core/mirror_manager.py`
    """

    mirrors = mirror_manager.list_mirrors(manager)
    if not mirrors:
        print("\n当前系统没有可用镜像源，跳过镜像选择。")
        return None

    manager_name = manager or (mirrors[0].managers[0] if mirrors else "未知")

    print(f"\n{'=' * 52}")
    print(f"  镜像源选择 - {manager_name}")
    print(f"{'=' * 52}")
    print(f"  [1] 自动测速并选择最佳镜像源 (推荐，{timeout_seconds}s 后自动执行)")
    for idx, mirror in enumerate(mirrors, start=2):
        print(f"  [{idx}] {mirror.name:12s} {mirror.url}")
    cancel_idx = len(mirrors) + 2
    print(f"  [{cancel_idx}] 跳过，不做修改")
    print(f"{'=' * 52}")

    choice = _read_choice_with_timeout(len(mirrors), timeout_seconds)

    if choice is None or choice == 0:
        return None
    if choice == 1:
        return "__auto__"
    if 2 <= choice <= len(mirrors) + 1:
        return mirrors[choice - 2].name
    return None


def _read_choice_with_timeout(mirror_count: int, timeout_seconds: int) -> int | None:
    """Read a single-digit menu choice with a timeout.

    Args:
        mirror_count: Number of mirror entries.
        timeout_seconds: Seconds to wait before returning default (1).

    Returns:
        int | None: 0 means cancel, 1 means auto, 2..N+1 means mirror index, None means skip.

    References:
        - Called by `select_mirror_interactive()` in current file.
    """

    cancel_idx = mirror_count + 2
    prompt = f"请输入选项 [1-{cancel_idx}]，{timeout_seconds}s 内无输入自动执行 [1]: "

    if not sys.stdin.isatty():
        print(f"非交互终端，自动执行 [1] 自动测速并选择最佳镜像源")
        return 1

    print(prompt, end="", flush=True)

    rlist, _, _ = select.select([sys.stdin], [], [], timeout_seconds)
    if not rlist:
        print("\n超时，自动执行 [1] 自动测速并选择最佳镜像源")
        return 1

    raw = sys.stdin.readline().strip()
    if not raw:
        print("无输入，自动执行 [1] 自动测速并选择最佳镜像源")
        return 1

    try:
        num = int(raw)
    except ValueError:
        print(f"无效输入 '{raw}'，自动执行 [1]")
        return 1

    if num == cancel_idx:
        print("已取消，跳过镜像源修改。")
        return 0
    if 1 <= num <= mirror_count + 1:
        return num

    print(f"无效选项 {num}，自动执行 [1]")
    return 1


def apply_mirror_selection(
    mirror_manager: MirrorManager,
    manager: str | None = None,
    dry_run: bool = False,
    timeout_seconds: int = MENU_TIMEOUT_SECONDS,
) -> CommandResult:
    """Full mirror selection flow: show menu, handle choice, apply switch.

    Args:
        mirror_manager: Mirror manager instance.
        manager: Optional backend manager name.
        dry_run: Whether to simulate without writing files.
        timeout_seconds: Menu timeout in seconds.

    Returns:
        CommandResult: Result of the mirror switch operation or a skip result.

    References:
        - Menu display: `select_mirror_interactive()` in current file.
        - Mirror switcher: `MirrorManager.switch_mirror()` / `auto_switch()`
    """

    selected = select_mirror_interactive(mirror_manager, manager, timeout_seconds)
    if selected is None:
        return CommandResult(["mirror", "select"], 0, "已跳过镜像源选择", "")

    if selected == "__auto__":
        config = mirror_manager.distro_detector.guess_manager()
        timeout = getattr(mirror_manager, "_default_timeout", 3.0)
        print("\n正在测速并选择最佳镜像源...")
        return mirror_manager.auto_switch(manager, dry_run=dry_run, timeout=timeout)

    print(f"\n正在切换到镜像源: {selected}")
    return mirror_manager.switch_mirror(selected, manager=manager, dry_run=dry_run)
