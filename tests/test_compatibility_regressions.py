"""Regression tests for Python 3.6-compatible runtime behavior."""

import json

from aupt.core.config_manager import ConfigManager
from aupt.utils.mirror_speed_test import benchmark_mirrors
from aupt.utils.subprocess_wrapper import run_command


def test_empty_mirror_benchmark_is_supported() -> None:
    assert benchmark_mirrors([]) == []


def test_subprocess_capture_uses_text_output() -> None:
    result = run_command(["python", "-c", "print('ok')"])
    assert result.returncode == 0
    assert result.stdout.strip() == "ok"


def test_config_falls_back_when_path_is_unwritable(tmp_path) -> None:
    config_path = tmp_path / "config.json"
    manager = ConfigManager(config_path)
    manager.config_path = config_path / "nested" / "config.json"
    manager._memory_config = {"default_manager": "apt"}
    assert manager.load()["default_manager"] == "apt"


def test_config_round_trip(tmp_path) -> None:
    config_path = tmp_path / "config.json"
    manager = ConfigManager(config_path)
    manager.set("mirror.timeout", 5)
    payload = json.loads(config_path.read_text(encoding="utf-8"))
    assert payload["mirror"]["timeout"] == 5
