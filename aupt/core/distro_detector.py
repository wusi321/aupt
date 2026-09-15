"""Linux distribution detection service."""

from dataclasses import dataclass
import json
from pathlib import Path
import shutil
from typing import Dict, List, Optional


@dataclass
class DistroInfo:
    """Describe the current Linux distribution.

    Args:
        distro_id: The primary ID field from `/etc/os-release`.
        id_like: Related distro families from `/etc/os-release`.
        name: Human-readable distribution name.
        version_codename: Optional release codename.

    Returns:
        None.

    References:
        - Detection source: `/etc/os-release`
    """

    distro_id: str
    id_like: List[str]
    name: str
    version_codename: Optional[str] = None


class DistroDetector:
    """Detect current distro and map it to the primary package manager."""

    def __init__(self, mapping_path: Path) -> None:
        """Initialize the distro detector.

        Args:
            mapping_path: JSON mapping file path.

        Returns:
            None.

        References:
            - Mapping file: `aupt/database/distro_map.json`
        """

        self.mapping_path = mapping_path
        self.mapping = self._load_mapping()

    def _load_mapping(self) -> Dict[str, str]:
        """Load distro-to-manager mapping from disk.

        Args:
            None.

        Returns:
            dict[str, str]: Mapping table.

        References:
            - Called by `__init__()` in current file.
        """

        with self.mapping_path.open("r", encoding="utf-8") as handle:
            return json.load(handle)

    def detect(self) -> DistroInfo:
        """Read `/etc/os-release` and build distro metadata.

        Args:
            None.

        Returns:
            DistroInfo: Parsed distribution information.

        References:
            - Mapping consumer: `guess_manager()` in current file.
        """

        os_release = Path("/etc/os-release")
        if not os_release.exists():
            os_release = Path("/usr/lib/os-release")
        if not os_release.exists():
            return DistroInfo("unknown", [], "Unknown Linux")
        values: Dict[str, str] = {}
        with os_release.open("r", encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if not line or "=" not in line:
                    continue
                key, value = line.split("=", 1)
                values[key] = value.strip().strip('"').strip("'")
        id_like = values.get("ID_LIKE", "").split()
        return DistroInfo(
            distro_id=values.get("ID", "unknown"),
            id_like=id_like,
            name=values.get("PRETTY_NAME", values.get("NAME", "Unknown Linux")),
            version_codename=values.get("VERSION_CODENAME"),
        )

    def guess_manager(self, distro: Optional[DistroInfo] = None) -> Optional[str]:
        """Infer the best primary manager from distro metadata.

        Args:
            distro: Optional pre-detected distro information.

        Returns:
            str | None: Manager name or None when undetermined.

        References:
            - Distro info type: `DistroInfo` in current file.
            - Mapping table: `self.mapping` in current class.
        """

        distro = distro or self.detect()
        candidates = [distro.distro_id, *distro.id_like]
        for candidate in candidates:
            manager = self.mapping.get(candidate)
            if manager:
                return manager
        return None

    def available_managers(self) -> List[str]:
        """List package managers that are installed on the host.

        Args:
            None.

        Returns:
            list[str]: Installed manager names.

        References:
            - Mapping table: `self.mapping` in current class.
        """

        managers = sorted(set(self.mapping.values()) | {"flatpak", "snap"})
        return [manager for manager in managers if shutil.which(manager)]
