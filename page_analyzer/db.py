"""Database utilities for page analyzer."""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
from urllib.parse import urlparse


def get_connection():
    """Get database connection."""
    DATABASE_URL = os.getenv('DATABASE_URL')
    return psycopg2.connect(DATABASE_URL)


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
        cur.execute("""
            CREATE TABLE IF NOT EXISTS url_checks (
                id SERIAL PRIMARY KEY,
                url_id INTEGER NOT NULL REFERENCES urls(id) ON DELETE CASCADE,
                status_code INTEGER,
                h1 TEXT,
                title TEXT,
                description TEXT,
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


def get_all_urls_with_last_check():
    """Get all URLs with last check date."""
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("""
        SELECT 
            u.id, 
            u.name, 
            u.created_at,
            MAX(uc.created_at) as last_check_at
        FROM urls u
        LEFT JOIN url_checks uc ON u.id = uc.url_id
        GROUP BY u.id, u.name, u.created_at
        ORDER BY u.created_at DESC
    """)
    urls = cur.fetchall()
    cur.close()
    conn.close()
    return urls


def get_checks_for_url(url_id):
    """Get all checks for a specific URL."""
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute(
        "SELECT id, status_code, h1, title, description, created_at "
        "FROM url_checks WHERE url_id = %s "
        "ORDER BY created_at DESC",
        (url_id,)
    )
    checks = cur.fetchall()
    cur.close()
    conn.close()
    return checks


def add_check(url_id, status_code=None, h1=None, title=None, description=None):
    """Add a check for a URL."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO url_checks (url_id, status_code, h1, title, description, created_at) "
        "VALUES (%s, %s, %s, %s, %s, %s)",
        (url_id, status_code, h1, title, description, datetime.now())
    )
    conn.commit()
    check_id = cur.fetchone()[0] if cur.rowcount else None
    cur.close()
    conn.close()
    return check_id
