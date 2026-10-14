"""Recall watch: an always-on job for Hermes cron.

Every week, pull the latest openFDA recalls for oxygen concentrators, compare with the fleet's devices, and
write a short message for the district engineer. Hermes cron runs it and `hermes send` delivers it to WhatsApp,
Telegram or Slack. Donated machines never receive manufacturer recall letters; this closes that gap.

Register (once):   hermes cron add --name sieve-recall-watch --schedule "0 8 * * 1" --command "uv run python scripts/recall_watch.py"
Run by hand:       uv run python scripts/recall_watch.py
"""

from __future__ import annotations

import json
import sys
from datetime import UTC, datetime
from pathlib import Path

import httpx


def _root() -> Path:
    """Repo root: honour SIEVE_ROOT, then the current directory (Hermes cron --workdir), then this file's parent."""
    import os

    for cand in [os.environ.get("SIEVE_ROOT"), os.getcwd(), str(Path(__file__).resolve().parents[1])]:
        if cand and (Path(cand) / "packages/core/sieve_core/data/devices.yaml").exists():
            return Path(cand)
    return Path(__file__).resolve().parents[1]


ROOT = _root()
STATE = ROOT / "data/recall_watch_state.json"
RECORDS = ROOT / "data/records.jsonl"
REGISTRY = ROOT / "packages/core/sieve_core/data/devices.yaml"


def fleet_keys() -> set[str]:
    import yaml

    keys: set[str] = set()
    devs = {d["id"]: d for d in yaml.safe_load(REGISTRY.read_text(encoding="utf-8"))["devices"]}
    if RECORDS.exists():
        for line in RECORDS.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            r = json.loads(line)
            d = devs.get(r.get("device_id"))
            if d:
                keys.update(a.lower() for a in d.get("model_aliases", []))
                keys.add(d["manufacturer"].split()[0].lower())
    return keys


def main() -> int:
    r = httpx.get("https://api.fda.gov/device/recall.json", params={"search": 'product_description:"oxygen concentrator"', "limit": 100}, timeout=60)
    r.raise_for_status()
    recalls = r.json().get("results", [])
    seen = set(json.loads(STATE.read_text(encoding="utf-8")).get("seen", [])) if STATE.exists() else set()
    keys = fleet_keys()
    new_relevant = []
    for rc in recalls:
        rid = rc.get("product_res_number") or rc.get("res_event_number") or json.dumps(rc)[:40]
        blob = json.dumps(rc).lower()
        if rid not in seen and any(k in blob for k in keys):
            new_relevant.append((rid, rc))
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps({"seen": sorted(seen | {rid for rid, _ in new_relevant}), "checked_at": datetime.now(UTC).isoformat(), "total_recalls_seen": len(recalls)}), encoding="utf-8")
    if not new_relevant:
        print(f"Sieve recall watch: {len(recalls)} recalls checked, none new for the fleet.")
        return 0
    lines = [f"Sieve recall watch: {len(new_relevant)} new recall(s) match devices in the fleet."]
    for rid, rc in new_relevant[:5]:
        lines.append(f"- {rc.get('event_date_initiated')}: {(rc.get('product_description') or '')[:80]}. Reason: {(rc.get('reason_for_recall') or '')[:140]}. Source: openFDA {rid}")
    msg = "\n".join(lines)
    print(msg)
    return 0


if __name__ == "__main__":
    sys.exit(main())
