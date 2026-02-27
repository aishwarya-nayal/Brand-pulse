import sqlite3
from datetime import datetime

DB_NAME = "brand_pulse.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            brand TEXT NOT NULL,
            subreddit TEXT,
            post_title TEXT,
            comment_body TEXT NOT NULL,
            polarity_score REAL,
            sentiment_label TEXT,
            scraped_at TEXT
        )
    """)

    conn.commit()
    conn.close()
    print("Database initialized.")

def insert_comment(brand, subreddit, post_title, comment_body, polarity_score, sentiment_label):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO comments (brand, subreddit, post_title, comment_body, polarity_score, sentiment_label, scraped_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (brand, subreddit, post_title, comment_body, polarity_score, sentiment_label, datetime.now().isoformat()))

    conn.commit()
    conn.close()

def fetch_all(brand=None):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    if brand:
        cursor.execute("SELECT * FROM comments WHERE brand = ?", (brand,))
    else:
        cursor.execute("SELECT * FROM comments")

    rows = cursor.fetchall()
    conn.close()
    return rows

def fetch_summary(brand):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT sentiment_label, COUNT(*) as count
        FROM comments
        WHERE brand = ?
        GROUP BY sentiment_label
    """, (brand,))

    rows = cursor.fetchall()
    conn.close()
    return rows

def fetch_sentiment_over_time(brand):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT DATE(scraped_at) as date, sentiment_label, COUNT(*) as count
        FROM comments
        WHERE brand = ?
        GROUP BY DATE(scraped_at), sentiment_label
        ORDER BY date ASC
    """, (brand,))

    rows = cursor.fetchall()
    conn.close()
    return rows

def is_data_stale(brand, days=7):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT MAX(scraped_at) FROM comments WHERE brand = ?
    """, (brand,))

    row = cursor.fetchone()
    conn.close()

    if not row or not row[0]:
        return True  # no data at all

    from datetime import datetime, timedelta
    try:
        last_scraped = datetime.fromisoformat(row[0])
        diff = datetime.now() - last_scraped
        return diff.days >= days
    except Exception as e:
        print(f"[Stale Check Error] {e}")
        return False 
if __name__ == "__main__":
    init_db()