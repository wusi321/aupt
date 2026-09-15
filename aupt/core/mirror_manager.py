"""Mirror listing, benchmarking and switching support."""

from dataclasses import dataclass
import glob
import json
import os
from pathlib import Path
import shutil
import tempfile
from typing import Any, Dict, List, Optional

from aupt.core.distro_detector import DistroDetector
from aupt.utils.mirror_speed_test import benchmark_mirrors
from aupt.utils.subprocess_wrapper import CommandResult, run_command


@dataclass
class MirrorRecord:
    name: str
    url: str
    managers: List[str]


class MirrorManager:
    """Manage mirror discovery, benchmarking and switching."""

    def __init__(self, mirror_db_path: Path, distro_detector: DistroDetector) -> None:
        self.mirror_db_path = mirror_db_path
        self.distro_detector = distro_detector
        self.database = self._load_database()

    def _load_database(self) -> Dict[str, List[Dict[str, Any]]]:
        with self.mirror_db_path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
        if not isinstance(data, dict):
            raise ValueError("镜像数据库必须是对象")
        return data

    def list_mirrors(self, manager: Optional[str] = None) -> List[MirrorRecord]:
        manager = manager or self.distro_detector.guess_manager()
        mirrors = self.database.get(manager or "", [])
        return [
            MirrorRecord(name=item["name"], url=item["url"], managers=[manager or "unknown"])
            for item in mirrors
        ]

    def benchmark(self, manager: Optional[str] = None, timeout: float = 3.0) -> List[Dict[str, Any]]:
        mirrors = self.list_mirrors(manager)
        return benchmark_mirrors(
            [{"name": mirror.name, "url": mirror.url} for mirror in mirrors], timeout=timeout
        )

    def auto_switch(
        self, manager: Optional[str] = None, dry_run: bool = False, timeout: float = 3.0
    ) -> CommandResult:
        ranking = self.benchmark(manager, timeout=timeout)
        best = next((item for item in ranking if item["ok"]), None)
        if not best:
            return CommandResult(["mirror", "auto"], 1, "", "没有可用镜像测速结果")
        return self.switch_mirror(best["name"], manager=manager, dry_run=dry_run)

    def switch_mirror(
        self, mirror_name: str, manager: Optional[str] = None, dry_run: bool = False
    ) -> CommandResult:
        manager = manager or self.distro_detector.guess_manager()
        if not manager:
            return CommandResult(["mirror", "switch"], 1, "", "无法识别当前系统包管理器")

        candidates = self.database.get(manager, [])
        selected = next((item for item in candidates if item["name"] == mirror_name), None)
        if not selected:
            return CommandResult(["mirror", "switch"], 1, "", "未找到镜像: {}".format(mirror_name))

        known_urls = [item["url"] for item in candidates]
        touched = []
        for file_path in self._target_files_for_manager(manager):
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
                    result = self._write_mirror_config(path, original, updated)
                    if result.returncode != 0:
                        return result
        if not touched:
            return CommandResult(
                ["mirror", "switch"],
                0,
                "未找到可替换的镜像源文件，目标镜像: {}".format(mirror_name),
                "",
            )
        message = "" if dry_run else "已切换到镜像: {}".format(mirror_name)
        return CommandResult(["mirror", "switch"], 0, "\n".join(touched), message)

    def _target_files_for_manager(self, manager: str) -> List[str]:
        mapping = {
            "apt": ["/etc/apt/sources.list"] + glob.glob("/etc/apt/sources.list.d/*.list"),
            "pacman": ["/etc/pacman.d/mirrorlist"],
            "dnf": glob.glob("/etc/yum.repos.d/*.repo"),
            "zypper": glob.glob("/etc/zypp/repos.d/*.repo"),
        }
        return mapping.get(manager, [])

    def _write_mirror_config(self, path: Path, original: str, updated: str) -> CommandResult:
        """Write a config and backup, escalating only the copy operation when needed."""

        backup_path = path.with_suffix(path.suffix + ".aupt.bak")
        try:
            if os.access(str(path), os.W_OK) and os.access(str(path.parent), os.W_OK):
                backup_path.write_text(original, encoding="utf-8")
                path.write_text(updated, encoding="utf-8")
                return CommandResult(["mirror", "switch"], 0, "已更新: {}".format(path), "")

            if not shutil.which("sudo"):
                raise PermissionError("需要 root 权限，且系统中未找到 sudo")
            with tempfile.TemporaryDirectory() as temp_dir:
                backup_tmp = Path(temp_dir) / "backup"
                content_tmp = Path(temp_dir) / "content"
                backup_tmp.write_text(original, encoding="utf-8")
                content_tmp.write_text(updated, encoding="utf-8")
                result = run_command(["sudo", "cp", str(backup_tmp), str(backup_path)])
                if result.returncode != 0:
                    return result
                result = run_command(["sudo", "cp", str(content_tmp), str(path)])
                if result.returncode != 0:
                    return result
            return CommandResult(["mirror", "switch"], 0, "已更新: {}".format(path), "")
        except OSError as exc:
            hint = (
                "无法修改系统文件: {}\n错误: {}\n\n"
                "请使用 root 用户运行 `aupt mirror auto`，或先执行 `aupt mirror auto --dry-run`。"
            ).format(path, exc)
            return CommandResult(["mirror", "switch"], 1, "", hint)
