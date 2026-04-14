import os
from contextlib import contextmanager

import psycopg2
from psycopg2 import pool
from dotenv import load_dotenv

load_dotenv()

_pool: pool.SimpleConnectionPool | None = None


def get_pool() -> pool.SimpleConnectionPool:
    global _pool
    if _pool is None:
        _pool = pool.SimpleConnectionPool(1, 10, dsn=os.environ["DATABASE_URL"])
    return _pool


@contextmanager
def get_conn():C
    """Yield a psycopg2 connection from the pool; commit on success, rollback on error."""
    p = get_pool()
    conn = p.getconn()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        p.putconn(conn)


def init_schema():
    """Create pgvector extension and all tables if they don't exist. Called once at startup."""
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            cur.execute("""
                CREATE TABLE IF NOT EXISTS datasets (
                    id   SERIAL PRIMARY KEY,
                    name TEXT NOT NULL UNIQUE
                );
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS chunks (
                    id         SERIAL PRIMARY KEY,
                    dataset_id INTEGER NOT NULL REFERENCES datasets(id) ON DELETE CASCADE,
                    chunk_idx  INTEGER NOT NULL,
                    text       TEXT    NOT NULL,
                    embedding  vector(1024) NOT NULL,
                    UNIQUE (dataset_id, chunk_idx)
                );
            """)
            cur.execute("""
                CREATE INDEX IF NOT EXISTS chunks_embedding_idx
                    ON chunks USING ivfflat (embedding vector_l2_ops)
                    WITH (lists = 100);
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS chunk_edges (
                    id         SERIAL PRIMARY KEY,
                    dataset_id INTEGER NOT NULL REFERENCES datasets(id) ON DELETE CASCADE,
                    src_idx    INTEGER NOT NULL,
                    dst_idx    INTEGER NOT NULL,
                    weight     FLOAT   NOT NULL,
                    UNIQUE (dataset_id, src_idx, dst_idx)
                );
            """)
