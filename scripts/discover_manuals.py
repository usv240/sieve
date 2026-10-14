"""Self-updating corpus: Tavily map discovers new manual PDFs on the mirror site and proposes manifest entries.

`uv run python scripts/discover_manuals.py` maps the oxygen-concentrator, suction and oximeter category pages,
diffs the PDF links against what is already downloaded, and writes data/discovered.json. Run `make fetch-corpus`
afterwards to pull the new files. Uses Tavily extract on the category page (map returns no links for this plain-HTML HTTP site).
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
PAGES = {
    "oxygen_concentrators": "http://www.frankshospitalworkshop.com/equipment/oxygen_concentrators_service_manuals.html",
    "suction_pumps": "http://www.frankshospitalworkshop.com/equipment/suction_pumps_service_manuals.html",
    "pulse_oximeters": "http://www.frankshospitalworkshop.com/equipment/pulse_oximeter_service_manuals.html",
}


def main() -> int:
    for env in (ROOT / ".env", ROOT.parent / ".env"):
        if env.exists():
            for line in env.read_text(encoding="utf-8").splitlines():
                if "=" in line and not line.strip().startswith("#"):
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip())
    key = os.environ.get("TAVILY_API_KEY")
    if not key:
        print("TAVILY_API_KEY not set")
        return 1
    from tavily import TavilyClient

    c = TavilyClient(api_key=key)
    report: dict[str, dict] = {}
    for cls, url in PAGES.items():
        have = {p.name.lower() for p in (ROOT / "data/corpus" / cls).glob("*.pdf")}
        try:
            # Tavily map returns no links for this plain-HTML HTTP site, so use extract and read the anchors.
            ex = c.extract(urls=[url], extract_depth="basic")
            raw = (ex.get("results") or [{}])[0].get("raw_content") or ""
            import re
            from urllib.parse import urljoin

            links = [urljoin(url, href) for href in re.findall(r"\(([^)\s]+\.pdf)\)", raw, re.IGNORECASE)] + re.findall(r"https?://[^\s)]+\.pdf", raw, re.IGNORECASE)
            if not links:
                # Plain-HTML HTTP mirror: Tavily returns no anchors, so read the page directly (same links the fetch script uses).
                import httpx

                html = httpx.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=30, follow_redirects=True).text
                links = [urljoin(url, h) for h in re.findall(r'href="([^"]+\.pdf)"', html, re.IGNORECASE)]
        except Exception as e:  # noqa: BLE001
            report[cls] = {"error": type(e).__name__}
            continue
        pdfs = sorted({u for u in links if isinstance(u, str) and u.lower().endswith(".pdf")})
        new = [u for u in pdfs if unquote(u.rsplit("/", 1)[-1]).lower() not in have]
        report[cls] = {"mapped_pdfs": len(pdfs), "already_have": len(pdfs) - len(new), "new": new[:50]}
        print(f"{cls}: {len(pdfs)} PDFs mapped, {len(new)} new")
    (ROOT / "data/discovered.json").write_text(json.dumps(report, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
