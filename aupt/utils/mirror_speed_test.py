"""Mirror benchmark helpers based on the Python standard library."""

from concurrent.futures import ThreadPoolExecutor
import time
from typing import Any, Dict, List
from urllib import request


def benchmark_mirrors(mirrors: List[Dict[str, str]], timeout: float = 3.0) -> List[Dict[str, Any]]:
    """Benchmark mirrors concurrently using APIs available on Python 3.6+."""

    if not mirrors:
        return []
    with ThreadPoolExecutor(max_workers=min(8, len(mirrors))) as executor:
        results = list(executor.map(lambda item: _probe_mirror(item, timeout), mirrors))
    return sorted(results, key=lambda item: (not item["ok"], item["latency_ms"]))


def _probe_mirror(mirror: Dict[str, str], timeout: float) -> Dict[str, Any]:
    """Measure a single mirror latency with a tiny ranged request."""

    start = time.perf_counter()
    try:
        request_object = request.Request(mirror["url"], headers={"Range": "bytes=0-0"})
        with request.urlopen(request_object, timeout=timeout) as response:
            response.read(1)
        latency_ms = round((time.perf_counter() - start) * 1000, 2)
        return {
            "name": mirror["name"],
            "url": mirror["url"],
            "latency_ms": latency_ms,
            "ok": True,
            "error": "",
        }
    except Exception as exc:
        return {
            "name": mirror["name"],
            "url": mirror["url"],
            "latency_ms": float("inf"),
            "ok": False,
            "error": str(exc),
        }
