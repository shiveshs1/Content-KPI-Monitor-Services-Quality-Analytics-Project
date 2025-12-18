#!/usr/bin/env python3
from __future__ import annotations
import csv, random
from pathlib import Path
from datetime import date, timedelta

def main() -> None:
    out = Path("data/raw_metrics.csv")
    out.parent.mkdir(parents=True, exist_ok=True)

    titles = [
        ("A101","10 Tips to Brew Coffee","Lifestyle"),
        ("A102","Best Cameras 2025","Electronics"),
        ("A103","Healthy Breakfast Ideas","Lifestyle"),
        ("A104","Travel Hacks Europe","Travel"),
        ("A105","Beginner’s Guide to Python","Education"),
    ]
    start = date(2025, 9, 1)
    days = 30

    rows = []
    for d in range(days):
        day = start + timedelta(days=d)
        for cid, title, cat in titles:
            impr = random.randint(400, 2200)
            clk  = int(impr * random.uniform(0.08, 0.22))
            conv = int(clk  * random.uniform(0.07, 0.20))
            dwell = round(random.uniform(25, 90), 1)
            bounce = round(random.uniform(0.25, 0.6), 2)
            rows.append([day.isoformat(), cid, title, cat, impr, clk, conv, dwell, bounce])

    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["date","content_id","title","category","impressions","clicks","conversions","avg_dwell_sec","bounce_rate"])
        w.writerows(rows)

    print(f"✅ Wrote sample CSV with {len(rows)} rows → {out}")

if __name__ == "__main__":
    main()
