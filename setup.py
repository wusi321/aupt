"""Legacy setuptools entry point for Python 3.6-compatible builds."""

from pathlib import Path

from setuptools import find_packages, setup


readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

setup(
    name="aupt",
    version="0.1.0",
    description="Advanced Unified Package Tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    python_requires=">=3.6",
    packages=find_packages(include=["aupt", "aupt.*"]),
    include_package_data=True,
    package_data={"aupt.database": ["*.json"]},
    install_requires=["dataclasses; python_version < '3.7'"],
    entry_points={"console_scripts": ["aupt=aupt.cli.commands:main"]},
)
