"""SQLite database fallback for Windows (replaces Replit PostgreSQL dependency).

Automatically creates local database if PostgreSQL is unavailable.
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional

DB_PATH = Path(__file__).parent / "data" / "predictions.db"
DB_PATH.parent.mkdir(exist_ok=True)

class SQLitePredictionDB:
    """Local SQLite database for predictions."""
    
    def __init__(self):
        self.conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
        self._init_tables()
        
    def _init_tables(self):
        """Create tables if they don't exist."""
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                symbol TEXT NOT NULL,
                direction TEXT NOT NULL,
                confidence REAL,
                target_price REAL,
                actual_direction TEXT,
                correct INTEGER,
                prediction_data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS key_value_store (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        self.conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_predictions_date 
            ON predictions(date DESC)
        """)
        
        self.conn.commit()
    
    def store_prediction(self, prediction: Dict):
        """Store a prediction."""
        self.conn.execute("""
            INSERT INTO predictions 
            (date, symbol, direction, confidence, target_price, prediction_data)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            prediction.get('target_date', datetime.now().date().isoformat()),
            prediction.get('symbol', 'AMD'),
            prediction['direction'],
            prediction.get('confidence', 0),
            prediction.get('target_price', 0),
            json.dumps(prediction)
        ))
        self.conn.commit()
    
    def update_outcome(self, date: str, actual_direction: str):
        """Update actual outcome for a prediction."""
        cursor = self.conn.execute(
            "SELECT id, direction FROM predictions WHERE date = ? ORDER BY created_at DESC LIMIT 1",
            (date,)
        )
        row = cursor.fetchone()
        
        if row:
            pred_id, predicted = row
            correct = 1 if predicted == actual_direction else 0
            self.conn.execute("""
                UPDATE predictions 
                SET actual_direction = ?, correct = ?
                WHERE id = ?
            """, (actual_direction, correct, pred_id))
            self.conn.commit()
    
    def get_recent_predictions(self, limit=20) -> list:
        """Get recent predictions."""
        cursor = self.conn.execute("""
            SELECT date, direction, confidence, actual_direction, correct
            FROM predictions
            ORDER BY date DESC
            LIMIT ?
        """, (limit,))
        
        return [{
            'date': row[0],
            'predicted': row[1],
            'confidence': row[2],
            'actual': row[3],
            'correct': row[4]
        } for row in cursor.fetchall()]
    
    def get_accuracy(self, days=30) -> float:
        """Calculate accuracy over last N days."""
        cursor = self.conn.execute("""
            SELECT AVG(correct) 
            FROM predictions 
            WHERE correct IS NOT NULL AND date >= date('now', '-' || ? || ' days')
        """, (days,))
        
        result = cursor.fetchone()[0]
        return result if result is not None else 0.5
    
    def store_kv(self, key: str, value: str):
        """Store key-value pair."""
        self.conn.execute("""
            INSERT OR REPLACE INTO key_value_store (key, value, updated_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
        """, (key, value))
        self.conn.commit()
    
    def get_kv(self, key: str) -> Optional[str]:
        """Get value by key."""
        cursor = self.conn.execute("SELECT value FROM key_value_store WHERE key = ?", (key,))
        row = cursor.fetchone()
        return row[0] if row else None
    
    def close(self):
        """Close database connection."""
        self.conn.close()

# Global instance
db = SQLitePredictionDB()

if __name__ == "__main__":
    print(f"📊 SQLite Database: {DB_PATH}")
    print(f"✅ Tables initialized")
    print(f"📈 Recent accuracy: {db.get_accuracy(30):.1%}")
    
    recent = db.get_recent_predictions(5)
    print(f"📋 Last 5 predictions:")
    for p in recent:
        print(f"   {p['date']}: {p['predicted']} ({p.get('confidence', 0):.0%})")
