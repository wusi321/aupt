from __future__ import annotations

"""Mirror listing, benchmarking and switching support."""

from dataclasses import dataclass
import glob
import json
from pathlib import Path
from typing import Any

from aupt.core.distro_detector import DistroDetector
from aupt.utils.mirror_speed_test import benchmark_mirrors
from aupt.utils.subprocess_wrapper import CommandResult


@dataclass(slots=True)
class MirrorRecord:
    """Represent a mirror candidate.

    Args:
        name: Logical mirror name.
        url: Base mirror URL.
        managers: Supported package manager names.

    Returns:
        None.

    References:
        - Source database: `aupt/database/mirror_list.json`
    """

    name: str
    url: str
    managers: list[str]


class MirrorManager:
    """Manage mirror discovery, benchmark and switching."""

    def __init__(self, mirror_db_path: Path, distro_detector: DistroDetector) -> None:
        """Initialize the mirror manager.

        Args:
            mirror_db_path: Mirror database path.
            distro_detector: Distro detector dependency.

        Returns:
            None.

        References:
            - Detector class: `aupt/core/distro_detector.py`
        """

        self.mirror_db_path = mirror_db_path
        self.distro_detector = distro_detector
        self.database = self._load_database()

    def _load_database(self) -> dict[str, list[dict[str, Any]]]:
        """Load mirror metadata from disk.

        Args:
            None.

        Returns:
            dict[str, list[dict[str, Any]]]: Mirror metadata table.

        References:
            - Called by `__init__()` in current file.
        """

        with self.mirror_db_path.open("r", encoding="utf-8") as handle:
            return json.load(handle)

    def list_mirrors(self, manager: str | None = None) -> list[MirrorRecord]:
        """List available mirrors for a package manager.

        Args:
            manager: Optional manager name. When omitted, use detected manager.

        Returns:
            list[MirrorRecord]: Mirror candidates.

        References:
            - Detector dependency: `self.distro_detector` in current class.
        """

        if manager is None:
            manager = self.distro_detector.guess_manager()
        mirrors = self.database.get(manager or "", [])
        return [MirrorRecord(name=item["name"], url=item["url"], managers=[manager or "unknown"]) for item in mirrors]

    def benchmark(self, manager: str | None = None, timeout: float = 3.0) -> list[dict[str, Any]]:
        """Measure mirror latency and sort by speed.

        Args:
            manager: Optional manager name. When omitted, use detected manager.
            timeout: Network timeout in seconds.

        Returns:
            list[dict[str, Any]]: Ranked mirror benchmark results.

        References:
            - Benchmark helper: `aupt/utils/mirror_speed_test.py`
        """

        mirrors = self.list_mirrors(manager)
        return benchmark_mirrors([{"name": mirror.name, "url": mirror.url} for mirror in mirrors], timeout=timeout)

    def auto_switch(self, manager: str | None = None, dry_run: bool = False, timeout: float = 3.0) -> CommandResult:
        """Select the fastest mirror and switch to it.

        Args:
            manager: Optional manager name. When omitted, use detected manager.
            dry_run: Whether to avoid writing system files.
            timeout: Network timeout in seconds.

        Returns:
            CommandResult: Synthetic operation result.

        References:
            - Mirror switcher: `switch_mirror()` in current file.
        """

        ranking = self.benchmark(manager, timeout=timeout)
        best = next((item for item in ranking if item["ok"]), None)
        if not best:
            return CommandResult(["mirror", "auto"], 1, "", "没有可用镜像测速结果")
        return self.switch_mirror(best["name"], manager=manager, dry_run=dry_run)

    def switch_mirror(self, mirror_name: str, manager: str | None = None, dry_run: bool = False) -> CommandResult:
        """Switch repo files to the selected mirror by replacing known URLs.

        Args:
            mirror_name: Mirror alias to switch to.
            manager: Optional manager name. When omitted, use detected manager.
            dry_run: Whether to avoid writing system files.

        Returns:
            CommandResult: Synthetic operation result.

        References:
            - Mirror list: `list_mirrors()` in current file.
            - File mapping: `_target_files_for_manager()` in current file.
        """

        if manager is None:
            manager = self.distro_detector.guess_manager()
        if not manager:
            return CommandResult(["mirror", "switch"], 1, "", "无法识别当前系统包管理器")

        candidates = self.database.get(manager, [])
        selected = next((item for item in candidates if item["name"] == mirror_name), None)
        if not selected:
            return CommandResult(["mirror", "switch"], 1, "", f"未找到镜像: {mirror_name}")

        known_urls = [item["url"] for item in candidates]
        target_files = self._target_files_for_manager(manager)
        touched: list[str] = []
        for file_path in target_files:
            path = Path(file_path)
            if not path.exists():
                continue
            original = path.read_text(encoding="utf-8")
            updated = original
            for known_url in known_urls:
                updated = updated.replace(known_url, selected["url"])
            if updated != original:
                touched.append(str(path))
                if not dry_run:
                    backup_path = path.with_suffix(path.suffix + ".aupt.bak")
                    backup_path.write_text(original, encoding="utf-8")
                    path.write_text(updated, encoding="utf-8")
        if not touched:
            return CommandResult(["mirror", "switch"], 0, f"未找到可替换的镜像源文件，目标镜像: {mirror_name}", "")
        return CommandResult(["mirror", "switch"], 0, "\n".join(touched), "" if dry_run else f"已切换到镜像: {mirror_name}")

    def _target_files_for_manager(self, manager: str) -> list[str]:
        """Return repo file paths for a package manager.

        Args:
            manager: Target manager name.

        Returns:
            list[str]: Candidate configuration file paths.

        References:
            - Called by `switch_mirror()` in current file.
        """

        mapping = {
            "apt": ["/etc/apt/sources.list", *glob.glob("/etc/apt/sources.list.d/*.list")],
            "pacman": ["/etc/pacman.d/mirrorlist"],
            "dnf": glob.glob("/etc/yum.repos.d/*.repo"),
            "zypper": glob.glob("/etc/zypp/repos.d/*.repo"),
        }
        return mapping.get(manager, [])
