from __future__ import annotations

"""Mirror benchmark helpers based on the Python standard library."""

import asyncio
import time
from typing import Any
from urllib import request


def benchmark_mirrors(mirrors: list[dict[str, str]], timeout: float = 3.0) -> list[dict[str, Any]]:
    """Benchmark mirrors synchronously through an asyncio runner.

    Args:
        mirrors: Mirror definitions containing `name` and `url`.
        timeout: Per-request timeout in seconds.

    Returns:
        list[dict[str, Any]]: Mirror results sorted by latency.

    References:
        - Async worker: `_benchmark_all()` in current file.
    """

    return asyncio.run(_benchmark_all(mirrors, timeout))


async def _benchmark_all(mirrors: list[dict[str, str]], timeout: float) -> list[dict[str, Any]]:
    """Benchmark all mirrors concurrently.

    Args:
        mirrors: Mirror definitions containing `name` and `url`.
        timeout: Per-request timeout in seconds.

    Returns:
        list[dict[str, Any]]: Ranked mirror results.

    References:
        - Network probe: `_probe_mirror()` in current file.
    """

    tasks = [asyncio.create_task(_probe_mirror(mirror, timeout)) for mirror in mirrors]
    results = await asyncio.gather(*tasks)
    return sorted(results, key=lambda item: (not item["ok"], item["latency_ms"]))


async def _probe_mirror(mirror: dict[str, str], timeout: float) -> dict[str, Any]:
    """Measure a single mirror latency.

    Args:
        mirror: Mirror definition containing `name` and `url`.
        timeout: Per-request timeout in seconds.

    Returns:
        dict[str, Any]: Measured mirror status.

    References:
        - Called by `_benchmark_all()` in current file.
    """

    def do_request() -> dict[str, Any]:
        start = time.perf_counter()
        try:
            req = request.Request(mirror["url"], method="HEAD")
            with request.urlopen(req, timeout=timeout) as response:
                response.read(0)
            latency_ms = round((time.perf_counter() - start) * 1000, 2)
            return {"name": mirror["name"], "url": mirror["url"], "latency_ms": latency_ms, "ok": True, "error": ""}
        except Exception as exc:
            return {"name": mirror["name"], "url": mirror["url"], "latency_ms": float("inf"), "ok": False, "error": str(exc)}

    return await asyncio.to_thread(do_request)
