"""Database utilities for page analyzer."""

import os
import sqlite3
from datetime import datetime
from urllib.parse import urlparse


def get_connection():
    """Get database connection."""
    db_path = os.getenv('DATABASE_URL', 'sqlite:///database.db').replace('sqlite:///', '')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def normalize_url(url):
    """Normalize URL: scheme + netloc only."""
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}"


def add_url(url):
    """Add URL to database, return id."""
    normalized = normalize_url(url)
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO urls (name, created_at) VALUES (?, ?)",
            (normalized, datetime.now())
        )
        url_id = cur.lastrowid
        conn.commit()
        return url_id, True
    except sqlite3.IntegrityError:
        conn.rollback()
        cur.execute("SELECT id FROM urls WHERE name = ?", (normalized,))
        url_id = cur.fetchone()[0]
        return url_id, False
    finally:
        cur.close()
        conn.close()


def get_url(url_id):
    """Get URL by id."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name, created_at FROM urls WHERE id = ?", (url_id,))
    url = cur.fetchone()
    cur.close()
    conn.close()
    return url


def get_all_urls():
    """Get all URLs ordered by created_at desc."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name, created_at FROM urls ORDER BY created_at DESC")
    urls = cur.fetchall()
    cur.close()
    conn.close()
    return urls
