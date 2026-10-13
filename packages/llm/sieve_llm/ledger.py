from __future__ import annotations

import sqlite3
import time
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass
class CallRecord:
    trace_id: str
    tier: str
    model: str
    model_id: str
    purpose: str
    tokens_in: int
    tokens_out: int
    usd: float
    latency_ms: int
    ts: float = 0.0


class Ledger:
    """Append-only record of every model call. Feeds the Trace panel and the README cost table."""

    def __init__(self, path: str | Path = "data/ledger.db"):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(self.path, check_same_thread=False)
        self._conn.execute(
            """CREATE TABLE IF NOT EXISTS calls (
                ts REAL, trace_id TEXT, tier TEXT, model TEXT, model_id TEXT, purpose TEXT,
                tokens_in INTEGER, tokens_out INTEGER, usd REAL, latency_ms INTEGER)"""
        )
        self._conn.commit()

    def record(self, rec: CallRecord) -> None:
        rec.ts = rec.ts or time.time()
        d = asdict(rec)
        self._conn.execute(
            "INSERT INTO calls VALUES (:ts,:trace_id,:tier,:model,:model_id,:purpose,:tokens_in,:tokens_out,:usd,:latency_ms)",
            d,
        )
        self._conn.commit()

    def trace(self, trace_id: str) -> list[dict]:
        cur = self._conn.execute(
            "SELECT ts,tier,model,model_id,purpose,tokens_in,tokens_out,usd,latency_ms FROM calls WHERE trace_id=? ORDER BY ts",
            (trace_id,),
        )
        cols = ["ts", "tier", "model", "model_id", "purpose", "tokens_in", "tokens_out", "usd", "latency_ms"]
        return [dict(zip(cols, row, strict=True)) for row in cur.fetchall()]

    def totals(self) -> dict:
        cur = self._conn.execute(
            "SELECT model, COUNT(*), SUM(tokens_in), SUM(tokens_out), SUM(usd) FROM calls GROUP BY model"
        )
        return {
            row[0]: {"calls": row[1], "tokens_in": row[2], "tokens_out": row[3], "usd": round(row[4] or 0, 4)}
            for row in cur.fetchall()
        }
