
import sqlite3
import pandas as pd
import json
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ResultStorage:
    """
    Persistence layer for Backtest Results.
    """
    def __init__(self, db_path='temp/results.db'):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_path = db_path
        self._init_db()
        
    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS backtest_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticker TEXT,
                strategy TEXT,
                total_return REAL,
                sharpe_ratio REAL,
                max_drawdown REAL,
                start_date TEXT,
                end_date TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                metrics_json TEXT
            )
        ''')
        conn.commit()
        conn.close()
        
    def save_run(self, ticker: str, strategy: str, start_date: str, end_date: str, metrics: dict):
        """Save a backtest run."""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            # Extract key metrics
            ret = metrics.get('Total_Return', 0.0)
            sharpe = metrics.get('Sharpe_Ratio', 0.0)
            dd = metrics.get('Max_Drawdown', 0.0)
            
            c.execute('''
                INSERT INTO backtest_runs 
                (ticker, strategy, total_return, sharpe_ratio, max_drawdown, start_date, end_date, metrics_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (ticker, strategy, ret, sharpe, dd, start_date, end_date, json.dumps(metrics)))
            
            conn.commit()
            logger.info(f"Saved Backtest Run for {ticker} (ID: {c.lastrowid})")
            conn.close()
            return c.lastrowid
        except Exception as e:
            logger.error(f"Error saving results: {e}")
            return None
            
    def get_recent_runs(self, limit=5):
        try:
            conn = sqlite3.connect(self.db_path)
            df = pd.read_sql(f"SELECT * FROM backtest_runs ORDER BY timestamp DESC LIMIT {limit}", conn)
            conn.close()
            return df.to_dict('records')
        except Exception as e:
            logger.error(f"Error fetching runs: {e}")
            return []
