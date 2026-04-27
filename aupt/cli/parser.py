from __future__ import annotations

"""CLI argument parsing utilities."""

import argparse
from typing import Sequence

SUPPORTED_MANAGERS = ("apt", "pacman", "dnf", "zypper", "flatpak", "snap")
SUPPORTED_ACTIONS = (
    "install",
    "remove",
    "update",
    "upgrade",
    "search",
    "info",
    "mirror",
    "doctor",
    "clean",
    "config",
    "benchmark",
    "update-db",
)


def build_action_parser(action: str) -> argparse.ArgumentParser:
    """Create an action-specific argument parser.

    Args:
        action: Target CLI action name.

    Returns:
        argparse.ArgumentParser: Configured parser for the action.

    References:
        - Action list: `SUPPORTED_ACTIONS` in current file.
    """

    parser = argparse.ArgumentParser(prog=f"aupt {action}")
    parser.add_argument("--dry-run", action="store_true", help="仅显示即将执行的命令")

    if action == "install":
        parser.add_argument("package", help="要安装的包名")
    elif action == "remove":
        parser.add_argument("package", help="要卸载的包名")
    elif action == "search":
        parser.add_argument("keyword", help="搜索关键字")
    elif action == "info":
        parser.add_argument("package", help="要查询的信息包名")
    elif action == "mirror":
        parser.add_argument("mirror_action", choices=("auto", "list", "switch"), help="镜像子命令")
        parser.add_argument("mirror_name", nargs="?", help="镜像名称，仅 switch 时使用")
    elif action == "config":
        parser.add_argument("config_action", nargs="?", choices=("show", "get", "set"), default="show")
        parser.add_argument("key", nargs="?", help="配置键，支持点路径")
        parser.add_argument("value", nargs="?", help="配置值")
    elif action == "benchmark":
        parser.add_argument("--runs", type=int, default=3, help="基准执行次数")
    return parser


def parse_cli_args(argv: Sequence[str]) -> argparse.Namespace:
    """Parse CLI arguments with optional explicit manager prefix.

    Args:
        argv: Raw argument list excluding the executable name.

    Returns:
        argparse.Namespace: Parsed arguments namespace.

    References:
        - Supported managers: `SUPPORTED_MANAGERS` in current file.
        - Supported actions: `SUPPORTED_ACTIONS` in current file.
    """

    if not argv:
        raise SystemExit("用法: aupt <manager?> <action> [args] [--dry-run]")

    explicit_manager = None
    tokens = list(argv)
    if tokens[0] in SUPPORTED_MANAGERS:
        explicit_manager = tokens.pop(0)

    if not tokens:
        raise SystemExit("缺少 action 参数")

    action = tokens.pop(0)
    if action not in SUPPORTED_ACTIONS:
        raise SystemExit(f"不支持的 action: {action}")

    parser = build_action_parser(action)
    parsed = parser.parse_args(tokens)
    parsed.action = action
    parsed.explicit_manager = explicit_manager
    return parsed
