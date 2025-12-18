#!/usr/bin/env python3
from __future__ import annotations
import argparse, sqlite3, pandas as pd
from pathlib import Path

def ensure_schema(db: Path, schema_sql: Path) -> None:
    con = sqlite3.connect(db)
    try:
        con.executescript(schema_sql.read_text(encoding="utf-8"))
    finally:
        con.close()

def load_csv_into_db(csv_path: Path, db: Path) -> int:
    df = pd.read_csv(csv_path, parse_dates=["date"])
    df["date"] = df["date"].dt.date.astype(str)
    num_cols = ["impressions","clicks","conversions","avg_dwell_sec","bounce_rate"]
    for c in num_cols:
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)

    con = sqlite3.connect(db)
    con.execute("PRAGMA foreign_keys = ON;")
    try:
        for _, r in df.iterrows():
            con.execute("DELETE FROM content_daily WHERE date=? AND content_id=?", (r["date"], r["content_id"]))
            con.execute(
                """INSERT INTO content_daily
                (date,content_id,title,category,impressions,clicks,conversions,avg_dwell_sec,bounce_rate)
                VALUES (?,?,?,?,?,?,?,?,?)""",
                (r["date"], r["content_id"], r["title"], r["category"],
                 int(r["impressions"]), int(r["clicks"]), int(r["conversions"]),
                 float(r["avg_dwell_sec"]), float(r["bounce_rate"]))
            )
        con.commit()
    finally:
        con.close()
    return len(df)

def main():
    ap = argparse.ArgumentParser(description="Ingest CSV → SQLite (content KPIs).")
    ap.add_argument("--csv", default="data/raw_metrics.csv")
    ap.add_argument("--db", default="data/content_kpi.db")
    ap.add_argument("--schema", default="sql/schema.sql")
    args = ap.parse_args()

    db, schema, csv = Path(args.db), Path(args.schema), Path(args.csv)
    db.parent.mkdir(parents=True, exist_ok=True)

    ensure_schema(db, schema)
    n = load_csv_into_db(csv, db)
    print(f"✅ Ingested {n} rows → {db}")

if __name__ == "__main__":
    main()
