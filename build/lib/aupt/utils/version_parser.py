from __future__ import annotations

"""Package version expression parser."""

from dataclasses import dataclass
import re

_VERSION_PATTERN = re.compile(r"^(?P<name>[A-Za-z0-9._+-]+?)(?:(?P<op>==|>=|<=|>|<|@)(?P<version>.+))?$")


@dataclass
class ParsedPackageSpec:
    """Represent a user package specification.

    Args:
        raw: Original user input.
        name: Parsed package name.
        operator: Optional version operator.
        version: Optional version string.

    Returns:
        None.

    References:
        - Parser: `parse_package_spec()` in current file.
    """

    raw: str
    name: str
    operator: str | None
    version: str | None


def parse_package_spec(spec: str) -> ParsedPackageSpec:
    """Parse package text such as `gcc==9` or `python@3.10`.

    Args:
        spec: Raw package spec string.

    Returns:
        ParsedPackageSpec: Structured package specification.

    References:
        - Pattern: `_VERSION_PATTERN` in current file.
    """

    match = _VERSION_PATTERN.match(spec.strip())
    if not match:
        raise ValueError(f"非法包描述: {spec}")
    data = match.groupdict()
    return ParsedPackageSpec(
        raw=spec,
        name=data["name"],
        operator=data.get("op"),
        version=data.get("version"),
    )
