"""Allow running AUPT as a module."""

from aupt.cli.commands import main


if __name__ == "__main__":
    raise SystemExit(main())
