from __future__ import annotations

"""Central command dispatcher."""

from argparse import Namespace
import json
from pathlib import Path
import time

from aupt.backends import AptBackend, DnfBackend, FlatpakBackend, PacmanBackend, SnapBackend, ZypperBackend
from aupt.core.config_manager import ConfigManager
from aupt.core.distro_detector import DistroDetector
from aupt.core.mirror_manager import MirrorManager
from aupt.core.package_resolver import PackageResolver
from aupt.utils.subprocess_wrapper import CommandResult
from aupt.utils.version_parser import parse_package_spec


class Dispatcher:
    """Coordinate CLI requests and backend execution."""

    def __init__(
        self,
        distro_detector: DistroDetector,
        package_resolver: PackageResolver,
        config_manager: ConfigManager,
        mirror_manager: MirrorManager,
    ) -> None:
        """Initialize the dispatcher.

        Args:
            distro_detector: Distro detection service.
            package_resolver: Package alias resolution service.
            config_manager: User config service.
            mirror_manager: Mirror management service.

        Returns:
            None.

        References:
            - Services live in `aupt/core/`.
        """

        self.distro_detector = distro_detector
        self.package_resolver = package_resolver
        self.config_manager = config_manager
        self.mirror_manager = mirror_manager
        self.backends = {
            "apt": AptBackend(),
            "pacman": PacmanBackend(),
            "dnf": DnfBackend(),
            "zypper": ZypperBackend(),
            "flatpak": FlatpakBackend(),
            "snap": SnapBackend(),
        }

    def handle(self, args: Namespace) -> CommandResult:
        """Dispatch a parsed CLI namespace to the matching handler.

        Args:
            args: Parsed CLI namespace.

        Returns:
            CommandResult: Final execution result.

        References:
            - CLI parser: `aupt/cli/parser.py`
        """

        if args.action == "mirror":
            return self._handle_mirror(args)
        if args.action == "doctor":
            return self._handle_doctor()
        if args.action == "config":
            return self._handle_config(args)
        if args.action == "benchmark":
            return self._handle_benchmark(args)
        if args.action == "update-db":
            return self._handle_update_db()
        return self._handle_backend_action(args)

    def _handle_backend_action(self, args: Namespace) -> CommandResult:
        """Execute backend-backed package operations.

        Args:
            args: Parsed CLI namespace.

        Returns:
            CommandResult: Final execution result.

        References:
            - Backend registry: `self.backends` in current class.
            - Version parser: `aupt/utils/version_parser.py`
        """

        chain = self._resolve_backend_chain(args.explicit_manager)
        if not chain:
            return CommandResult([args.action], 1, "", "未找到可用包管理器")

        package_spec = getattr(args, "package", None)
        version = None
        requested_name = None
        if package_spec:
            parsed = parse_package_spec(package_spec)
            requested_name = parsed.name
            version = parsed.version

        keyword = getattr(args, "keyword", None)
        failures: list[str] = []
        for manager in chain:
            backend = self.backends[manager]
            try:
                if args.action in {"install", "remove", "info"}:
                    resolved_name = self.package_resolver.resolve(requested_name or "", manager)
                else:
                    resolved_name = requested_name
                result = self._invoke_backend(backend, args.action, resolved_name, version, keyword, args.dry_run)
            except Exception as exc:
                failures.append(f"{manager}: {exc}")
                continue
            if result.returncode == 0 or args.explicit_manager or args.action in {"update", "upgrade", "clean"}:
                return result
            failures.append(f"{manager}: {result.stderr.strip() or result.stdout.strip() or '失败'}")
        return CommandResult([args.action], 1, "", "\n".join(failures))

    def _invoke_backend(
        self,
        backend: object,
        action: str,
        package: str | None,
        version: str | None,
        keyword: str | None,
        dry_run: bool,
    ) -> CommandResult:
        """Call a concrete backend method.

        Args:
            backend: Concrete backend instance.
            action: Target action.
            package: Optional resolved package name.
            version: Optional parsed version string.
            keyword: Optional search keyword.
            dry_run: Whether to avoid command execution.

        Returns:
            CommandResult: Backend execution result.

        References:
            - Backends: `aupt/backends/`
        """

        if action == "install":
            return backend.install(package or "", version=version, dry_run=dry_run)
        if action == "remove":
            return backend.remove(package or "", dry_run=dry_run)
        if action == "update":
            return backend.update(dry_run=dry_run)
        if action == "upgrade":
            return backend.upgrade(dry_run=dry_run)
        if action == "search":
            return backend.search(keyword or "", dry_run=dry_run)
        if action == "info":
            return backend.info(package or "", dry_run=dry_run)
        if action == "clean":
            return backend.clean(dry_run=dry_run)
        raise ValueError(f"不支持的后端动作: {action}")

    def _resolve_backend_chain(self, explicit_manager: str | None) -> list[str]:
        """Determine backend priority chain.

        Args:
            explicit_manager: Optional manager specified by user.

        Returns:
            list[str]: Available backend names in priority order.

        References:
            - Config manager: `self.config_manager` in current class.
            - Distro detector: `self.distro_detector` in current class.
        """

        if explicit_manager:
            backend = self.backends.get(explicit_manager)
            return [explicit_manager] if backend and backend.is_available() else []

        config = self.config_manager.load()
        detected = self.distro_detector.guess_manager()
        preferred = []
        default_manager = config.get("default_manager", "auto")
        if default_manager != "auto":
            preferred.append(default_manager)
        if detected:
            preferred.append(detected)
        preferred.extend(config.get("priority", []))
        preferred.extend(["flatpak", "snap"])

        deduped: list[str] = []
        for manager in preferred:
            if manager not in deduped and manager in self.backends and self.backends[manager].is_available():
                deduped.append(manager)
        return deduped

    def _handle_mirror(self, args: Namespace) -> CommandResult:
        """Process mirror subcommands.

        Args:
            args: Parsed CLI namespace.

        Returns:
            CommandResult: Synthetic operation result.

        References:
            - Mirror manager: `aupt/core/mirror_manager.py`
        """

        config = self.config_manager.load()
        timeout = float(config.get("mirror", {}).get("timeout", 3.0))
        if args.mirror_action == "list":
            mirrors = self.mirror_manager.list_mirrors(args.explicit_manager)
            output = "\n".join(f"{item.name}\t{item.url}" for item in mirrors) or "没有可用镜像"
            return CommandResult(["mirror", "list"], 0, output, "")
        if args.mirror_action == "auto":
            return self.mirror_manager.auto_switch(args.explicit_manager, dry_run=args.dry_run, timeout=timeout)
        if args.mirror_action == "switch":
            if not args.mirror_name:
                return CommandResult(["mirror", "switch"], 1, "", "mirror switch 需要指定镜像名称")
            return self.mirror_manager.switch_mirror(args.mirror_name, manager=args.explicit_manager, dry_run=args.dry_run)
        return CommandResult(["mirror"], 1, "", "未知镜像动作")

    def _handle_doctor(self) -> CommandResult:
        """Run environment diagnostics.

        Args:
            None.

        Returns:
            CommandResult: Diagnostic report.

        References:
            - Distro detector: `self.distro_detector` in current class.
        """

        distro = self.distro_detector.detect()
        manager = self.distro_detector.guess_manager(distro)
        available = self.distro_detector.available_managers()
        report = {
            "distro": distro.name,
            "distro_id": distro.distro_id,
            "id_like": distro.id_like,
            "primary_manager": manager,
            "available_managers": available,
            "config_path": str(self.config_manager.config_path),
        }
        return CommandResult(["doctor"], 0, json.dumps(report, indent=2, ensure_ascii=False), "")

    def _handle_config(self, args: Namespace) -> CommandResult:
        """Show or edit persisted configuration.

        Args:
            args: Parsed CLI namespace.

        Returns:
            CommandResult: Synthetic operation result.

        References:
            - Config manager: `aupt/core/config_manager.py`
        """

        if args.config_action == "show":
            return CommandResult(["config", "show"], 0, json.dumps(self.config_manager.get(), indent=2, ensure_ascii=False), "")
        if args.config_action == "get":
            if not args.key:
                return CommandResult(["config", "get"], 1, "", "config get 需要指定 key")
            return CommandResult(["config", "get"], 0, json.dumps(self.config_manager.get(args.key), ensure_ascii=False), "")
        if args.config_action == "set":
            if not args.key or args.value is None:
                return CommandResult(["config", "set"], 1, "", "config set 需要指定 key 和 value")
            value = self._coerce_value(args.value)
            updated = self.config_manager.set(args.key, value)
            return CommandResult(["config", "set"], 0, json.dumps(updated, indent=2, ensure_ascii=False), "")
        return CommandResult(["config"], 1, "", "未知配置动作")

    def _handle_benchmark(self, args: Namespace) -> CommandResult:
        """Benchmark local selection and mirror metadata calls.

        Args:
            args: Parsed CLI namespace.

        Returns:
            CommandResult: Synthetic benchmark result.

        References:
            - Distro detector: `self.distro_detector` in current class.
            - Mirror manager: `self.mirror_manager` in current class.
        """

        runs = max(1, args.runs)
        samples: list[float] = []
        for _ in range(runs):
            start = time.perf_counter()
            self.distro_detector.detect()
            self._resolve_backend_chain(None)
            self.mirror_manager.list_mirrors()
            samples.append(time.perf_counter() - start)
        summary = {
            "runs": runs,
            "min_seconds": min(samples),
            "max_seconds": max(samples),
            "avg_seconds": sum(samples) / len(samples),
        }
        return CommandResult(["benchmark"], 0, json.dumps(summary, indent=2, ensure_ascii=False), "")

    def _handle_update_db(self) -> CommandResult:
        """Refresh lightweight cache data for future queries.

        Args:
            None.

        Returns:
            CommandResult: Synthetic cache update result.

        References:
            - Config manager: `self.config_manager` in current class.
        """

        cache_dir = Path.home() / ".aupt" / "cache"
        cache_dir.mkdir(parents=True, exist_ok=True)
        distro = self.distro_detector.detect()
        payload = {
            "distro": {
                "id": distro.distro_id,
                "id_like": distro.id_like,
                "name": distro.name,
                "version_codename": distro.version_codename,
            },
            "available_managers": self.distro_detector.available_managers(),
        }
        (cache_dir / "distro.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        return CommandResult(["update-db"], 0, str(cache_dir / "distro.json"), "")

    def _coerce_value(self, raw_value: str) -> object:
        """Convert a string CLI value into a basic Python object.

        Args:
            raw_value: Raw string from CLI.

        Returns:
            object: Parsed scalar or structured value.

        References:
            - Called by `_handle_config()` in current file.
        """

        try:
            return json.loads(raw_value)
        except json.JSONDecodeError:
            lowered = raw_value.lower()
            if lowered in {"true", "false"}:
                return lowered == "true"
            return raw_value
