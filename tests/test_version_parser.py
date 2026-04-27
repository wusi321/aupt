from aupt.utils.version_parser import parse_package_spec


def test_parse_equality_version() -> None:
    """验证 `==` 版本表达式可以被正确解析。

    Args:
        None.

    Returns:
        None.

    References:
        - 被测函数: `aupt/utils/version_parser.py`
    """

    parsed = parse_package_spec("gcc==9")
    assert parsed.name == "gcc"
    assert parsed.operator == "=="
    assert parsed.version == "9"


def test_parse_at_version() -> None:
    """验证 `@` 版本表达式可以被正确解析。

    Args:
        None.

    Returns:
        None.

    References:
        - 被测函数: `aupt/utils/version_parser.py`
    """

    parsed = parse_package_spec("python@3.10")
    assert parsed.name == "python"
    assert parsed.operator == "@"
    assert parsed.version == "3.10"
