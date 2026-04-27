from aupt.cli.parser import parse_cli_args


def test_parse_explicit_manager_install() -> None:
    """验证显式包管理器前缀的 install 命令解析。

    Args:
        None.

    Returns:
        None.

    References:
        - 被测函数: `aupt/cli/parser.py`
    """

    parsed = parse_cli_args(["apt", "install", "vim"])
    assert parsed.explicit_manager == "apt"
    assert parsed.action == "install"
    assert parsed.package == "vim"


def test_parse_mirror_switch() -> None:
    """验证 mirror switch 命令解析。

    Args:
        None.

    Returns:
        None.

    References:
        - 被测函数: `aupt/cli/parser.py`
    """

    parsed = parse_cli_args(["mirror", "switch", "tuna"])
    assert parsed.action == "mirror"
    assert parsed.mirror_action == "switch"
    assert parsed.mirror_name == "tuna"
