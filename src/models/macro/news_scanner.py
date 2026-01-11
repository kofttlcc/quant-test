
import logging
from typing import List, Dict, Tuple
import datetime
import random # Fallback simulation

logger = logging.getLogger(__name__)

class NewsScanner:
    """
    Module B: Macro Intelligence News Scanner
    Role: Analyze Financial News & Sentiment
    """
    
    def __init__(self):
        self.keywords_bullish = [
            "surge", "jump", "rally", "beat", "optimism", "growth", "record", 
            "bull", "gain", "profit", "upgrade", "recovery"
        ]
        self.keywords_bearish = [
            "cloud", "drop", "plunge", "crash", "miss", "concern", "recession", 
            "inflation", "bear", "loss", "downgrade", "warn", "crisis", "war"
        ]
        
    def fetch_and_analyze(self, tickers: List[str] = ["SPY", "QQQ", "^GSPC"]) -> Tuple[float, str]:
        """
        Fetch news and calculate sentiment score (-1.0 to 1.0).
        """
        import yfinance as yf
        
        all_news = []
        for t in tickers:
            try:
                tick = yf.Ticker(t)
                news = tick.news
                if news:
                    all_news.extend(news)
            except Exception as e:
                logger.warning(f"News fetch error for {t}: {e}")
                
        if not all_news:
            logger.warning("No live news found. Using Simulation.")
            return self._simulate_sentiment()
            
        # Analyze
        score = 0.0
        count = 0
        
        for article in all_news:
            title = article.get('title', '').lower()
            if not title: continue
            
            s = 0
            for w in self.keywords_bullish:
                if w in title: s += 1
            for w in self.keywords_bearish:
                if w in title: s -= 1
            
            score += s
            count += 1
            
        final_score = (score / count) if count > 0 else 0.0
        # Normalize to -1 to 1 (Assuming a max word hit of 3 per title roughly)
        normalized = max(-1.0, min(1.0, final_score))
        
        return normalized, "Live"

    def _simulate_sentiment(self) -> Tuple[float, str]:
        """Simulation for dev environment"""
        # Randomly drift sentiment
        # In a real app, this should clearly state IT IS FAKE.
        return random.uniform(-0.5, 0.5), "Simulated"
