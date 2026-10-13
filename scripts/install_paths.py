"""Make the in-repo packages importable from the virtualenv without packaging each one.

Writes a .pth file into site-packages listing packages/* and apps/api. Run by `make setup`.
"""

from __future__ import annotations

import sysconfig
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIRS = [ROOT / "apps" / "api", *sorted((ROOT / "packages").iterdir())]


def main() -> None:
    site = Path(sysconfig.get_paths()["purelib"])
    pth = site / "sieve_paths.pth"
    pth.write_text("\n".join(str(d) for d in DIRS if d.is_dir()) + "\n", encoding="utf-8")
    print(f"wrote {pth} with {sum(1 for d in DIRS if d.is_dir())} paths")


if __name__ == "__main__":
    main()
