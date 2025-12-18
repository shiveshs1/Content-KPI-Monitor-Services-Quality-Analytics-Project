PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS content_daily (
  date           TEXT NOT NULL,             -- YYYY-MM-DD
  content_id     TEXT NOT NULL,
  title          TEXT NOT NULL,
  category       TEXT NOT NULL,
  impressions    INTEGER NOT NULL CHECK(impressions >= 0),
  clicks         INTEGER NOT NULL CHECK(clicks >= 0),
  conversions    INTEGER NOT NULL CHECK(conversions >= 0),
  avg_dwell_sec  REAL NOT NULL CHECK(avg_dwell_sec >= 0),
  bounce_rate    REAL NOT NULL CHECK(bounce_rate BETWEEN 0 AND 1),
  PRIMARY KEY (date, content_id)
);

CREATE VIEW IF NOT EXISTS v_content_kpi AS
SELECT
  date,
  content_id,
  title,
  category,
  impressions,
  clicks,
  conversions,
  avg_dwell_sec,
  bounce_rate,
  CASE WHEN impressions > 0 THEN 1.0 * clicks / impressions ELSE 0.0 END AS ctr,
  CASE WHEN clicks > 0 THEN 1.0 * conversions / clicks ELSE 0.0 END AS conversion_rate
FROM content_daily;
