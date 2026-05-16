from __future__ import annotations

"""CLI command entrypoint and output formatting."""

from pathlib import Path
from typing import Sequence

from aupt.cli.parser import parse_cli_args
from aupt.core.config_manager import ConfigManager
from aupt.core.dispatcher import Dispatcher
from aupt.core.distro_detector import DistroDetector
from aupt.core.mirror_manager import MirrorManager
from aupt.core.package_resolver import PackageResolver
from aupt.utils.logger import get_logger
from aupt.utils.subprocess_wrapper import CommandResult


def format_result(result: CommandResult) -> str:
    """Convert a command result into printable text.

    Args:
        result: Command execution result.

    Returns:
        str: User-facing text output.

    References:
        - Result type: `aupt/utils/subprocess_wrapper.py`
    """

    chunks: list[str] = []
    if result.stdout.strip():
        chunks.append(result.stdout.strip())
    if result.stderr.strip():
        chunks.append(result.stderr.strip())
    if not chunks:
        chunks.append(f"命令执行完成，退出码: {result.returncode}")
    return "\n".join(chunks)


def build_dispatcher(project_root: Path | None = None) -> Dispatcher:
    """Construct the main dispatcher with all core services.

    Args:
        project_root: Optional repository root path. When omitted, use installed package root.

    Returns:
        Dispatcher: Ready-to-use dispatcher instance.

    References:
        - Config manager: `aupt/core/config_manager.py`
        - Distro detector: `aupt/core/distro_detector.py`
        - Package resolver: `aupt/core/package_resolver.py`
        - Mirror manager: `aupt/core/mirror_manager.py`
    """

    package_root = project_root / "aupt" if project_root is not None else Path(__file__).resolve().parents[1]
    database_dir = package_root / "database"

    config_manager = ConfigManager()
    distro_detector = DistroDetector(database_dir / "distro_map.json")
    package_resolver = PackageResolver(database_dir / "package_alias.json")
    mirror_manager = MirrorManager(database_dir / "mirror_list.json", distro_detector)
    return Dispatcher(
        distro_detector=distro_detector,
        package_resolver=package_resolver,
        config_manager=config_manager,
        mirror_manager=mirror_manager,
    )


def main(argv: Sequence[str] | None = None) -> int:
    """Run the AUPT command-line entrypoint.

    Args:
        argv: Optional argument list excluding executable name.

    Returns:
        int: Process exit code.

    References:
        - Parser: `aupt/cli/parser.py`
        - Dispatcher: `aupt/core/dispatcher.py`
    """

    import sys

    try:
        args = parse_cli_args(list(argv) if argv is not None else sys.argv[1:])
        project_root = Path(__file__).resolve().parents[2]
        logger = get_logger()
        dispatcher = build_dispatcher(project_root)
        logger.debug("开始处理命令: %s", args)
        result = dispatcher.handle(args)
        print(format_result(result))
        return result.returncode
    except KeyboardInterrupt:
        print("\n操作已取消。", file=sys.stderr)
        return 130
