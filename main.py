#!/usr/bin/env python3
"""Repository-level executable entrypoint for AUPT."""

from aupt.cli.commands import main


if __name__ == "__main__":
    raise SystemExit(main())
