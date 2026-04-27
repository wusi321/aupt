"""Backend implementations for AUPT."""

from aupt.backends.apt_backend import AptBackend
from aupt.backends.dnf_backend import DnfBackend
from aupt.backends.flatpak_backend import FlatpakBackend
from aupt.backends.pacman_backend import PacmanBackend
from aupt.backends.snap_backend import SnapBackend
from aupt.backends.zypper_backend import ZypperBackend

__all__ = [
    "AptBackend",
    "PacmanBackend",
    "DnfBackend",
    "ZypperBackend",
    "FlatpakBackend",
    "SnapBackend",
]
