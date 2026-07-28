"""
db.py — History & Storage Module
Handles all SQLite persistence for Growth GPT campaigns and simulation runs.
"""
import sqlite3
import json
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "growthgpt.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS campaigns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT NOT NULL,
            product_description TEXT,
            target_audience TEXT,
            campaign_message TEXT,
            objective TEXT,
            tone TEXT,
            budget TEXT,
            result_json TEXT NOT NULL,
            engagement_score REAL,
            conversion_probability REAL,
            growth_potential TEXT,
            created_at TEXT NOT NULL
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# Users / Authentication
# ---------------------------------------------------------------------------

def create_user(full_name: str, email: str, password_hash: str) -> int:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO users (full_name, email, password_hash, created_at)
        VALUES (?, ?, ?, ?)
    """, (full_name.strip(), email.strip().lower(), password_hash, datetime.utcnow().isoformat()))
    conn.commit()
    user_id = cur.lastrowid
    conn.close()
    return user_id


def get_user_by_email(email: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE email = ?", (email.strip().lower(),))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def get_user_by_id(user_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def save_campaign(data: dict, result: dict) -> int:
    conn = get_connection()
    cur = conn.cursor()
    
    predictions = result.get("predictions", {})
    if "engagement_score" in predictions and isinstance(predictions["engagement_score"], dict):
        engagement_score = predictions["engagement_score"].get("value")
    else:
        engagement_score = result.get("growth_prediction", {}).get("engagement_score")
        
    if "conversion_probability" in predictions and isinstance(predictions["conversion_probability"], dict):
        conversion_probability = predictions["conversion_probability"].get("value")
    else:
        conversion_probability = result.get("growth_prediction", {}).get("conversion_probability")
        
    growth_potential = result.get("readiness", {}).get("risk_level") or result.get("growth_prediction", {}).get("growth_potential")

    cur.execute("""
        INSERT INTO campaigns
        (product_name, product_description, target_audience, campaign_message,
         objective, tone, budget, result_json, engagement_score,
         conversion_probability, growth_potential, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data.get("product_name"),
        data.get("product_description"),
        data.get("target_audience"),
        data.get("campaign_message"),
        data.get("objective"),
        result.get("campaign_analysis", {}).get("tone", ""),
        data.get("budget"),
        json.dumps(result),
        engagement_score,
        conversion_probability,
        growth_potential,
        datetime.utcnow().isoformat()
    ))
    conn.commit()
    campaign_id = cur.lastrowid
    conn.close()
    return campaign_id


def get_campaign(campaign_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM campaigns WHERE id = ?", (campaign_id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return None
    record = dict(row)
    record["result"] = json.loads(record["result_json"])
    return record


def list_campaigns(limit: int = 50):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, product_name, objective, engagement_score,
               conversion_probability, growth_potential, created_at
        FROM campaigns ORDER BY id DESC LIMIT ?
    """, (limit,))
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def get_dashboard_stats():
    """Aggregate metrics across every saved campaign, for the Dashboard page."""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) AS n FROM campaigns")
    total = cur.fetchone()["n"]

    cur.execute("""
        SELECT AVG(engagement_score) AS avg_eng, AVG(conversion_probability) AS avg_conv
        FROM campaigns WHERE engagement_score IS NOT NULL
    """)
    row = cur.fetchone()
    avg_engagement = round(row["avg_eng"], 1) if row and row["avg_eng"] is not None else None
    avg_conversion = round(row["avg_conv"], 1) if row and row["avg_conv"] is not None else None

    cur.execute("""
        SELECT growth_potential, COUNT(*) AS n FROM campaigns
        WHERE growth_potential IS NOT NULL AND growth_potential != ''
        GROUP BY growth_potential
    """)
    growth_breakdown = {r["growth_potential"]: r["n"] for r in cur.fetchall()}

    cur.execute("""
        SELECT objective, COUNT(*) AS n FROM campaigns
        WHERE objective IS NOT NULL AND objective != ''
        GROUP BY objective ORDER BY n DESC
    """)
    objective_breakdown = [{"objective": r["objective"], "count": r["n"]} for r in cur.fetchall()]

    cur.execute("""
        SELECT id, product_name, objective, engagement_score, conversion_probability,
               growth_potential, created_at
        FROM campaigns ORDER BY id DESC LIMIT 8
    """)
    recent = [dict(r) for r in cur.fetchall()]

    cur.execute("""
        SELECT product_name, engagement_score, conversion_probability
        FROM campaigns WHERE engagement_score IS NOT NULL
        ORDER BY engagement_score DESC LIMIT 1
    """)
    top_row = cur.fetchone()
    top_campaign = dict(top_row) if top_row else None

    conn.close()
    return {
        "total_campaigns": total,
        "avg_engagement": avg_engagement,
        "avg_conversion": avg_conversion,
        "growth_breakdown": growth_breakdown,
        "objective_breakdown": objective_breakdown,
        "recent": recent,
        "top_campaign": top_campaign,
    }


def delete_campaign(campaign_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM campaigns WHERE id = ?", (campaign_id,))
    conn.commit()
    conn.close()
