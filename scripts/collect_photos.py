"""Collect real-world photos of oxygen concentrator nameplates and fronts for the photo-identification benchmark.

Tavily search with include_images returns image URLs from resale listings, refurbishers and product pages. Images are
fetched, decoded with Pillow (nothing else is ever opened or executed), re-encoded as JPEG and stored under
data/corpus/photos/ (gitignored: third-party photos are never redistributed). The manifest of source URLs is
committed so the set can be rebuilt. Ground truth is annotated by eye in data/external/photo_truth.json.

Run: python scripts/collect_photos.py
"""

from __future__ import annotations

import hashlib
import io
import json
import os
from pathlib import Path

import httpx
from PIL import Image
from tavily import TavilyClient

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data/corpus/photos"
MANIFEST = ROOT / "data/external/photo_manifest.json"
QUERIES = [
    "Philips Respironics EverFlo oxygen concentrator serial number label",
    "Respironics EverFlo oxygen concentrator front panel used",
    "DeVilbiss 525 oxygen concentrator label",
    "DeVilbiss 525DS oxygen concentrator used",
    "DeVilbiss 515 oxygen concentrator",
    "AirSep NewLife Elite oxygen concentrator label",
    "AirSep VisionAire oxygen concentrator used",
    "Invacare Platinum 10 oxygen concentrator label",
    "Nidek Nuvo Lite oxygen concentrator",
    "Nidek Mark 5 Nuvo oxygen concentrator label",
    "Longfian JAY-5 oxygen concentrator",
    "Yuwell 7F-5 oxygen concentrator",
    "Inogen One G3 portable oxygen concentrator",
    "Drive DeVilbiss 1025 oxygen concentrator",
    "CAIRE Companion 5 oxygen concentrator",
]


def main() -> None:
    c = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])
    OUT.mkdir(parents=True, exist_ok=True)
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8")) if MANIFEST.exists() else {"items": []}
    seen = {m["url"] for m in manifest["items"]}
    with httpx.Client(timeout=20, follow_redirects=True, headers={"User-Agent": "Mozilla/5.0 (research benchmark)"}) as http:
        for q in QUERIES:
            try:
                r = c.search(q, include_images=True, max_results=5)
            except Exception as e:  # noqa: BLE001
                print("search failed", q, type(e).__name__)
                continue
            got = 0
            for url in r.get("images", [])[:8]:
                url = url if isinstance(url, str) else url.get("url", "")
                if not url or url in seen:
                    continue
                seen.add(url)
                try:
                    resp = http.get(url)
                    if resp.status_code != 200 or len(resp.content) > 8_000_000:
                        continue
                    img = Image.open(io.BytesIO(resp.content))
                    img.load()
                    if min(img.size) < 200:
                        continue
                    img = img.convert("RGB")
                    img.thumbnail((1600, 1600))
                    name = hashlib.sha1(url.encode()).hexdigest()[:12] + ".jpg"
                    img.save(OUT / name, "JPEG", quality=88)
                    manifest["items"].append({"file": name, "url": url, "query": q, "size": list(img.size)})
                    got += 1
                except Exception as e:  # noqa: BLE001 - one bad image never stops the collection
                    print("  skipped", url[:80], type(e).__name__)
                    continue
            print(f"{q[:60]:60s} +{got}", flush=True)
    MANIFEST.write_text(json.dumps(manifest, indent=1), encoding="utf-8")
    print("images", len(manifest["items"]))


if __name__ == "__main__":
    main()
