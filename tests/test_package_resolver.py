from pathlib import Path

from aupt.core.package_resolver import PackageResolver


def test_resolve_alias_for_apt() -> None:
    """验证包别名可以按管理器正确映射。

    Args:
        None.

    Returns:
        None.

    References:
        - 被测类: `aupt/core/package_resolver.py`
        - 数据库: `aupt/database/package_alias.json`
    """

    root = Path(__file__).resolve().parents[1]
    resolver = PackageResolver(root / "aupt" / "database" / "package_alias.json")
    assert resolver.resolve("opencv", "apt") == "python3-opencv"
