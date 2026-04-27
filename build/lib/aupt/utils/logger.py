from __future__ import annotations

"""Project logger factory."""

import logging
from pathlib import Path


def get_logger(name: str = "aupt") -> logging.Logger:
    """Create or return a configured logger instance.

    Args:
        name: Logger name.

    Returns:
        logging.Logger: Configured logger.

    References:
        - Log path: `~/.local/state/aupt/aupt.log`
    """

    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)
    logger.propagate = False
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    log_path = Path.home() / ".local" / "state" / "aupt" / "aupt.log"
    try:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_path, encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except OSError:
        # Keep CLI usable on read-only or restricted filesystems.
        logger.debug("日志文件不可写，已回退为仅控制台输出。")
    return logger
