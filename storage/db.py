import sqlite3
from pathlib import Path
from storage.models import ChunkAnalysis

DB_PATH = Path(".vulnviper.sqlite3")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_chunks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file TEXT,
            chunk_name TEXT,
            chunk_type TEXT,
            start_line INTEGER,
            end_line INTEGER,
            summary TEXT,
            vulnerabilities TEXT,
            recommendations TEXT,
            dependencies TEXT,
            parent_module TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_analysis(analysis: ChunkAnalysis):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    db_row_tuple = analysis.to_db_row()

    cursor.execute("""
        INSERT INTO audit_chunks (
            file, chunk_name, chunk_type, start_line, end_line,
            summary, vulnerabilities, recommendations, dependencies, parent_module
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, db_row_tuple)
    conn.commit()
    conn.close()

def get_all_results():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM audit_chunks")
    rows = cursor.fetchall()
    conn.close()
    return [ChunkAnalysis.from_db_row(row) for row in rows]
