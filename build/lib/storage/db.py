import sqlite3
from pathlib import Path
from storage.models import ChunkAnalysis

DB_PATH = Path.home() / ".vulnviper.sqlite3"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_chunks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file TEXT,
            function_name TEXT,
            chunk_type TEXT,
            start_line INTEGER,
            end_line INTEGER,
            summary TEXT,
            vulnerabilities TEXT,
            dependencies TEXT,
            parent_module TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_analysis(analysis: ChunkAnalysis):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO audit_chunks (
            file, function_name, chunk_type, start_line, end_line,
            summary, vulnerabilities, dependencies, parent_module
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        analysis.file,
        analysis.function_name,
        analysis.chunk_type,
        analysis.start_line,
        analysis.end_line,
        analysis.summary,
        ','.join(analysis.vulnerabilities),
        ','.join(analysis.dependencies),
        analysis.parent_module
    ))
    conn.commit()
    conn.close()

def get_all_results():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM audit_chunks")
    rows = cursor.fetchall()
    conn.close()
    return [ChunkAnalysis.from_row(row) for row in rows]
