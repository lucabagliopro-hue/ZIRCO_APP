import sqlite3
import os
from pathlib import Path
from kernel.contracts import FactClaim

class MemoryKernel:
    def __init__(self, db_path: str = "memory_data/jarvis_memory.db", vault_path: str = "memory_data/vault"):
        self.db_path = db_path
        self.vault_path = vault_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        os.makedirs(self.vault_path, exist_ok=True)
        self._init_db()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS facts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    predicate TEXT NOT NULL,
                    category TEXT NOT NULL,
                    content TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    status TEXT DEFAULT 'active',
                    source_session TEXT,
                    timestamp TEXT NOT NULL
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS fact_observations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    fact_id INTEGER,
                    timestamp TEXT NOT NULL,
                    FOREIGN KEY(fact_id) REFERENCES facts(id)
                )
            """)
            conn.commit()

    def ingest_fact(self, claim: FactClaim) -> int:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO facts (predicate, category, content, confidence, status, source_session, timestamp)
                VALUES (?, ?, ?, ?, 'active', ?, ?)
            """, (claim.predicate, claim.category, claim.content, claim.confidence, claim.source_session, claim.timestamp.isoformat()))
            fact_id = cursor.lastrowid
            conn.commit()
        self._sync_markdown_mirror(claim.category)
        return fact_id

    def _sync_markdown_mirror(self, category: str):
        file_path = Path(self.vault_path) / f"{category}.md"
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT content, confidence, timestamp FROM facts WHERE category = ? AND status = 'active'", (category,))
            rows = cursor.fetchall()

        lines = [f"# Miroir Mémoire : {category.upper()}", ""]
        for row in rows:
            lines.append(f"- **{row[0]}** (Confiance: {row[1]}, Enregistré: {row[2]})")
        
        file_path.write_text("\n".join(lines), encoding="utf-8")