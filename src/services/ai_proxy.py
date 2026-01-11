"""
ai_proxy.py - Gemini AI Proxy 服務
====================================
版本: v3.0 (直接 HTTP 調用，繞過系統代理)
功能: 代理 Gemini API 調用，支持 Antigravity 本地代理

重要: 使用 requests 直接調用，禁用系統代理
"""

import os
import logging
import requests
from typing import Dict, Any, Optional
from dataclasses import dataclass
try:
    import google.generativeai as genai
except ImportError:
    genai = None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class AIConfig:
    """AI 配置"""
    api_url: str = "http://127.0.0.1:8045"
    api_key: str = ""
    model_name: str = "gemini-3-pro-high"
    timeout: int = 60


class GeminiProxy:
    """
    Gemini AI 代理服務 (直接 HTTP 版本)
    
    重要: 禁用系統代理，直接連接到 Antigravity 代理
    """
    
    def __init__(self, config: AIConfig = None):
        self.config = config or AIConfig()
        self._load_config_from_env()
    
    def _load_config_from_env(self):
        """從環境變量加載配置"""
        env_key = os.environ.get('GEMINI_API_KEY')
        if env_key:
            self.config.api_key = env_key
        
        env_url = os.environ.get('GEMINI_API_URL')
        if env_url:
            self.config.api_url = env_url
    
    def update_config(self, api_url: str = None, api_key: str = None, model_name: str = None):
        """更新配置"""
        if api_url:
            self.config.api_url = api_url.rstrip('/')
        if api_key:
            self.config.api_key = api_key
        if model_name:
            self.config.model_name = model_name
        
        logger.info(f"AI Config updated: url={self.config.api_url}, model={self.config.model_name}")
    
    def is_configured(self) -> bool:
        """檢查是否已配置"""
        return bool(self.config.api_key)
    
    def generate(self, prompt: str, system_prompt: str = None) -> Dict[str, Any]:
        """
        調用 Gemini API 生成內容 (直接 HTTP)
        
        重要: 使用 proxies={'http': None, 'https': None} 繞過系統代理
        
        Args:
            prompt: 用戶提示
            system_prompt: 系統提示 (可選)
        
        Returns:
            {"success": bool, "content": str, "error": str}
        """
        if not self.config.api_key:
            return {
                "success": False,
                "content": "",
                "error": "Gemini API 未配置。請在設置中填入 API Key。"
            }
        
        if self.config.model_name == 'gemini-3-flash':
            return self._generate_via_google_genai(prompt, system_prompt)
        
        # Default: Gemini 3 Pro (Direct HTTP)
        try:
            # 構建 URL
            base_url = self.config.api_url.rstrip('/')
            url = f"{base_url}/v1beta/models/{self.config.model_name}:generateContent"
            
            # Headers
            headers = {
                "Content-Type": "application/json",
                "x-goog-api-key": self.config.api_key
            }
            
            # 構建內容
            full_prompt = prompt
            if system_prompt:
                full_prompt = f"[System Instructions]\n{system_prompt}\n\n[User Request]\n{prompt}"
            
            payload = {
                "contents": [
                    {"parts": [{"text": full_prompt}]}
                ],
                "generationConfig": {
                    "temperature": 0.7,
                    "maxOutputTokens": 2048
                }
            }
            
            logger.info(f"Calling Gemini API (HTTP): {url}")
            # ... (rest of request logic) ...
            
            # 關鍵: 禁用系統代理，直接連接
            response = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=self.config.timeout,
                proxies={'http': None, 'https': None}  # 繞過系統代理！
            )
            
            logger.info(f"Response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                content = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                return {"success": True, "content": content, "error": ""}
            elif response.status_code == 429:
                return {
                    "success": False,
                    "content": "",
                    "error": f"API 配額已用盡 (429)。請稍後再試或檢查配額。響應: {response.text[:200]}"
                }
            elif response.status_code == 401:
                return {
                    "success": False,
                    "content": "",
                    "error": f"API Key 無效 (401)。請檢查 API Key 是否正確。"
                }
            else:
                return {
                    "success": False,
                    "content": "",
                    "error": f"API Error ({response.status_code}): {response.text[:300]}"
                }
                
        except requests.Timeout:
            logger.error(f"Timeout calling {self.config.api_url}")
            return {
                "success": False,
                "content": "",
                "error": f"請求超時。請確認代理服務 {self.config.api_url} 正在運行。"
            }
        except requests.ConnectionError as e:
            logger.error(f"Connection error: {e}")
            return {
                "success": False,
                "content": "",
                "error": f"連接失敗: {str(e)[:100]}"
            }
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return {"success": False, "content": "", "error": str(e)}

    def _generate_via_google_genai(self, prompt: str, system_prompt: str = None) -> Dict[str, Any]:
        """使用 Google Generative AI SDK (Gemini 3 Flash)"""
        if not genai:
            return {"success": False, "content": "", "error": "Module 'google.generativeai' not found. Please install it."}

        try:
            # 配置 SDK
            # User provided: 
            # genai.configure(api_key="...", transport='rest', client_options={'api_endpoint': '...'})
            
            # Ensure URL is clean (no path suffixes)
            api_endpoint = self.config.api_url
            if ':generateContent' in api_endpoint:
                 api_endpoint = api_endpoint.split(':generateContent')[0]
            if '/models/' in api_endpoint:
                 api_endpoint = api_endpoint.split('/models/')[0]
            api_endpoint = api_endpoint.rstrip('/')
            
            # Note: The user specific request implies using this for the Antigravity proxy usually running on 127.0.0.1:8045
            # We respect the config.api_url which should come from settings
            
            logger.info(f"Configuring Google GenAI SDK: endpoint={api_endpoint}")
            
            genai.configure(
                api_key=self.config.api_key,
                transport='rest',
                client_options={'api_endpoint': api_endpoint}
            )
            
            # Creating model
            generation_config = None
            if system_prompt:
                model = genai.GenerativeModel(
                    self.config.model_name,
                    system_instruction=system_prompt
                )
            else:
                model = genai.GenerativeModel(self.config.model_name)
            
            logger.info(f"Generating content with model: {self.config.model_name}")
            response = model.generate_content(prompt)
            
            return {"success": True, "content": response.text, "error": ""}
            
        except Exception as e:
            logger.error(f"Google GenAI SDK Error: {e}")
            return {"success": False, "content": "", "error": str(e)}
    
    def analyze_market(self, macro_data: Dict[str, Any]) -> Dict[str, Any]:
        """生成市場分析報告"""
        system_prompt = """你是一位專業的量化分析師，使用繁體中文回覆。分析風格：客觀、數據驅動、提供清晰的市場觀點、給出可執行的建議。"""

        prompt = f"""根據以下宏觀市場數據，生成簡潔的市場分析報告：

VIX 指數: {macro_data.get('vix', {}).get('value', 'N/A')} ({macro_data.get('vix', {}).get('status', 'N/A')})
Fear & Greed: {macro_data.get('fear_greed', {}).get('value', 'N/A')} ({macro_data.get('fear_greed', {}).get('label', 'N/A')})
10Y 國債收益率: {macro_data.get('rates', {}).get('yield_10y', 'N/A')}%
收益率曲線: {macro_data.get('rates', {}).get('spread_bps', 'N/A')} bps

請提供：1. 市場狀態總結 2. 風險偏好建議 3. 關注重點"""

        return self.generate(prompt, system_prompt)
    
    def analyze_valuation(self, valuation_data: Dict[str, Any]) -> Dict[str, Any]:
        """生成估值分析報告"""
        system_prompt = """你是一位專業的價值投資分析師，使用繁體中文回覆。"""

        prompt = f"""根據以下估值數據，生成投資評級報告：

股票: {valuation_data.get('ticker', 'N/A')}
當前股價: ${valuation_data.get('current_price', 'N/A')}
內在價值: ${valuation_data.get('intrinsic_value', 'N/A')}
安全邊際: {valuation_data.get('margin_of_safety', 'N/A')}

請提供：1. 投資評級 2. 核心理由 3. 主要風險"""

        return self.generate(prompt, system_prompt)
    
    def analyze_arena(self, arena_results: list) -> Dict[str, Any]:
        """生成競技場戰況分析"""
        system_prompt = """你是一位量化策略評論員，使用繁體中文，風格生動有趣。"""

        strategies_text = "\n".join([
            f"#{i+1} {r.get('Strategy', 'N/A')} ({r.get('Type', 'N/A')}): "
            f"回報 {r.get('Total Return', 0)*100:.1f}%, Sharpe {r.get('Sharpe', 0):.2f}"
            for i, r in enumerate(arena_results[:5])
        ]) if arena_results else "暫無數據"

        prompt = f"""策略競技場對戰結果：

{strategies_text}

請以體育賽事解說的風格，生成戰況分析。"""

        return self.generate(prompt, system_prompt)


# 單例
_proxy = GeminiProxy()


def get_ai_proxy() -> GeminiProxy:
    """獲取 AI Proxy 單例"""
    return _proxy


def generate_ai_content(prompt: str, context_type: str = "general") -> Dict[str, Any]:
    """便捷函數: 生成 AI 內容"""
    return _proxy.generate(prompt)


if __name__ == "__main__":
    print("--- SELF-TEST: ai_proxy.py v3.0 ---")
    print("使用直接 HTTP 調用，禁用系統代理")
    
    proxy = GeminiProxy()
    proxy.update_config(
        api_url="http://127.0.0.1:8045",
        api_key="sk-b6dd1a56f6be48a9997d29fdebb244f9"
    )
    
    print(f"\nAPI URL: {proxy.config.api_url}")
    print(f"Model: {proxy.config.model_name}")
    print(f"Configured: {proxy.is_configured()}")
    
    print("\n[TEST] Generating content...")
    result = proxy.generate("Say hello in one sentence")
    
    if result["success"]:
        print(f"✅ Success: {result['content'][:200]}")
    else:
        print(f"❌ Error: {result['error']}")
    
    print("\n--- SELF-TEST COMPLETE ---")
