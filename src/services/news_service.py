"""
news_service.py - 繁中財經新聞服務
===================================
版本: v1.0
功能: 獲取繁體中文財經新聞用於宏觀面板

支持來源:
1. 天聚數行 TianAPI (每日100次免費)
2. Yahoo Finance 財經頭條 (備用)
"""

import os
import logging
import requests
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class NewsItem:
    """新聞項目"""
    title: str
    source: str
    time: str
    url: Optional[str] = None
    summary: Optional[str] = None
    category: str = "財經"


class NewsService:
    """
    繁中財經新聞服務
    
    支持多個新聞來源，自動降級
    """
    
    # 天聚數行 API (需要註冊獲取 key)
    TIANAPI_URL = "https://api.tianapi.com/caijing/index"
    
    # Yahoo Finance RSS (備用，繁中台灣)
    YAHOO_RSS_TW = "https://tw.stock.yahoo.com/rss/news/category/tw-market"
    
    def __init__(self, tianapi_key: str = None):
        self.tianapi_key = tianapi_key or os.environ.get('TIANAPI_KEY', '')
    
    def get_news(self, count: int = 5) -> List[NewsItem]:
        """
        獲取財經新聞
        
        Args:
            count: 獲取數量 (默認 5)
        
        Returns:
            新聞列表
        """
        news = []
        
        # 嘗試 TianAPI
        if self.tianapi_key:
            try:
                news = self._fetch_tianapi(count)
                if news:
                    logger.info(f"TianAPI: 獲取 {len(news)} 條新聞")
                    return news
            except Exception as e:
                logger.warning(f"TianAPI 獲取失敗: {e}")
        
        # 備用：Yahoo Finance RSS
        try:
            news = self._fetch_yahoo_rss(count)
            if news:
                logger.info(f"Yahoo RSS: 獲取 {len(news)} 條新聞")
                return news
        except Exception as e:
            logger.warning(f"Yahoo RSS 獲取失敗: {e}")
        
        # 最終備用：Mock 新聞
        return self._get_mock_news(count)
    
    def _fetch_tianapi(self, count: int) -> List[NewsItem]:
        """從天聚數行獲取新聞"""
        params = {
            "key": self.tianapi_key,
            "num": min(count, 10)  # API 限制
        }
        
        response = requests.get(self.TIANAPI_URL, params=params, timeout=10)
        data = response.json()
        
        if data.get("code") != 200:
            raise Exception(f"TianAPI error: {data.get('msg', 'Unknown')}")
        
        news = []
        for item in data.get("result", {}).get("newslist", [])[:count]:
            news.append(NewsItem(
                title=item.get("title", ""),
                source=item.get("source", "天聚數行"),
                time=item.get("ctime", datetime.now().strftime("%Y-%m-%d")),
                url=item.get("url"),
                summary=item.get("description", "")[:100] if item.get("description") else None
            ))
        
        return news
    
    def _fetch_yahoo_rss(self, count: int) -> List[NewsItem]:
        """從 Yahoo Finance RSS 獲取新聞 (台灣)"""
        import xml.etree.ElementTree as ET
        
        response = requests.get(self.YAHOO_RSS_TW, timeout=10)
        response.encoding = 'utf-8'
        
        root = ET.fromstring(response.text)
        channel = root.find('channel')
        
        news = []
        for item in channel.findall('item')[:count]:
            title = item.find('title')
            pub_date = item.find('pubDate')
            link = item.find('link')
            
            news.append(NewsItem(
                title=title.text if title is not None else "",
                source="Yahoo 財經",
                time=pub_date.text[:16] if pub_date is not None else datetime.now().strftime("%Y-%m-%d"),
                url=link.text if link is not None else None
            ))
        
        return news
    
    def _get_mock_news(self, count: int) -> List[NewsItem]:
        """獲取 Mock 新聞 (當所有來源失敗時)"""
        mock_headlines = [
            ("聯準會維持利率不變，市場關注下季展望", "Reuters"),
            ("台積電法說會後股價創新高", "經濟日報"),
            ("美股三大指數漲跌互見，科技股領漲", "Bloomberg"),
            ("港股恆指收漲 0.8%，金融股走強", "香港經濟日報"),
            ("比特幣突破 10 萬美元，創歷史新高", "CoinDesk"),
            ("油價受中東局勢影響小幅上揚", "路透社"),
            ("美國非農就業數據優於預期", "CNBC"),
        ]
        
        news = []
        for i, (title, source) in enumerate(mock_headlines[:count]):
            news.append(NewsItem(
                title=title,
                source=source,
                time=datetime.now().strftime("%Y-%m-%d %H:%M"),
                category="財經 (Demo)"
            ))
        
        return news
    
    def get_news_dict(self, count: int = 5) -> List[Dict[str, Any]]:
        """獲取新聞 (字典格式，用於 API)"""
        return [asdict(n) for n in self.get_news(count)]


# 單例
_service = NewsService()


def get_news_service() -> NewsService:
    """獲取新聞服務單例"""
    return _service


def get_latest_headlines(count: int = 5) -> List[Dict[str, Any]]:
    """便捷函數：獲取最新頭條"""
    return _service.get_news_dict(count)


if __name__ == "__main__":
    print("--- SELF-TEST: news_service.py ---")
    
    service = NewsService()
    
    print("\n[TEST] 獲取新聞 (Mock 模式，無 API Key)...")
    news = service.get_news(5)
    
    for i, item in enumerate(news, 1):
        print(f"  {i}. [{item.source}] {item.title}")
    
    print(f"\n獲取 {len(news)} 條新聞")
    
    print("\n--- SELF-TEST COMPLETE ---")
