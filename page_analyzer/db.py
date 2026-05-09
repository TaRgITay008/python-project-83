"""Database utilities for page analyzer."""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
from urllib.parse import urlparse


def get_connection():
    """Get database connection."""
    DATABASE_URL = os.getenv('DATABASE_URL')
    conn = psycopg2.connect(DATABASE_URL)
    return conn


def init_db():
    """Create tables if not exist."""
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS urls (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL UNIQUE,
                created_at TIMESTAMP NOT NULL DEFAULT NOW()
            );
        """)
        conn.commit()
    conn.close()


def normalize_url(url):
    """Normalize URL: scheme + netloc only."""
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}"


def add_url(url):
    """Add URL to database, return id and whether it's new."""
    normalized = normalize_url(url)
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO urls (name, created_at) VALUES (%s, %s) RETURNING id",
            (normalized, datetime.now())
        )
        url_id = cur.fetchone()[0]
        conn.commit()
        return url_id, True
    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        cur.execute("SELECT id FROM urls WHERE name = %s", (normalized,))
        url_id = cur.fetchone()[0]
        return url_id, False
    finally:
        cur.close()
        conn.close()


def get_url(url_id):
    """Get URL by id."""
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT id, name, created_at FROM urls WHERE id = %s", (url_id,))
    url = cur.fetchone()
    cur.close()
    conn.close()
    return url


def get_all_urls():
    """Get all URLs ordered by created_at desc."""
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT id, name, created_at FROM urls ORDER BY created_at DESC")
    urls = cur.fetchall()
    cur.close()
    conn.close()
    return urls
