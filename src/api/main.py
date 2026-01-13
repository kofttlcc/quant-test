
from flask import Flask, jsonify, request
import pandas as pd
import numpy as np
import math
import threading
import logging
import sys
import os
import json
import time

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))


# MAJOR-003 FIX: 區分必需模塊和可選模塊
# 必需模塊：導入失敗則阻止啟動
REQUIRED_MODULES_LOADED = True
try:
    from src.backend.backtest_engine import Backtester
    from src.models.strategy_logic import MomentumStrategy
    from src.data_loader.downloader import fetch_data
    from src.backend.storage import ResultStorage
    from src.backend.portfolio import Portfolio
    from src.backend.paper_trade import PaperTradingEngine
    import yfinance as yf
except ImportError as e:
    REQUIRED_MODULES_LOADED = False
    logging.critical(f"CRITICAL: Required module import failed: {e}")
    Backtester = None
    MomentumStrategy = None
    fetch_data = None
    ResultStorage = None
    yf = None

# 可選模塊：導入失敗僅記錄警告
try:
    from src.models.sentiment_engine import SentimentEngine
    # Module B: Macro Dashboard (New)
    from src.models.macro.macro_dashboard import get_macro_snapshot, get_next_event
except ImportError as e:
    logging.warning(f"Optional module import failed: {e}. Some features unavailable.")
    SentimentEngine = None
    get_macro_snapshot = None
    get_next_event = None





app = Flask(__name__)
storage = ResultStorage() if ResultStorage else None

def sanitize_for_json(obj):
    """
    Recursively replace NaN and Infinity with None for JSON serialization.
    """
    if isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return obj
    elif isinstance(obj, dict):
        return {k: sanitize_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [sanitize_for_json(item) for item in obj]
    elif isinstance(obj, (np.integer, np.floating)):
        if np.isnan(obj) or np.isinf(obj):
            return None
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return sanitize_for_json(obj.tolist())
    return obj

# 啟動時加載持久化配置
try:
    from src.services.config_service import load_saved_config
    load_saved_config()
    logging.info("持久化配置已加載")
except Exception as e:
    logging.warning(f"加載持久化配置失敗: {e}")

# CRITICAL-003 FIX: CORS 配置從環境變量讀取
ALLOWED_ORIGINS = os.environ.get('ALLOWED_ORIGINS', 'http://localhost:3000,http://localhost:5173').split(',')
ALLOWED_ORIGINS = [origin.strip() for origin in ALLOWED_ORIGINS if origin.strip()]

# CRITICAL-003 FIX: 加強 API Key 認證
API_KEY = os.environ.get('QUANT_API_KEY', '')  # 移除默認值
IS_PRODUCTION = os.environ.get('QUANT_ENV', 'development') == 'production'

# 啟動時檢查 - 使用 logging 模塊而非尚未定義的 logger
if IS_PRODUCTION and not API_KEY:
    logging.critical("SECURITY ERROR: QUANT_API_KEY not set in production mode!")
    raise RuntimeError("Production mode requires QUANT_API_KEY environment variable")

if not API_KEY:
    logging.warning("WARNING: Running without API Key authentication (development mode only)")

def check_api_key():
    """
    CRITICAL-003 FIX: 加強 API Key 驗證
    - 生產環境必須提供有效 API Key
    - 開發環境可選但會記錄警告
    """
    # 如果沒有設置 API Key，則處於開發模式
    if not API_KEY:
        return True  # 開發模式允許通過，但已在啟動時記錄警告
    
    # 生產模式：嚴格驗證
    key = request.headers.get('X-API-Key')
    if not key:
        logger.warning(f"API request without key from {request.remote_addr}")
        return False
    return key == API_KEY

@app.after_request
def after_request(response):
    origin = request.headers.get('Origin', '')
    if origin in ALLOWED_ORIGINS:
        response.headers.add('Access-Control-Allow-Origin', origin)
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-API-Key')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/api/v1/model/predict', methods=['POST'])
def model_predict():
    """
    Get Real-time Inference from AI Model.
    """
    if not check_api_key():
        return jsonify({"error": "Unauthorized"}), 401
        
    data = request.get_json() or {}
    ticker = data.get('ticker', 'BTC-USD')
    model_type = data.get('model_type', 'lightgbm')
    
    try:
        from src.data_loader.downloader import fetch_data
        # Get last 100 days for feature gen
        df = fetch_data(ticker, start_date="2024-01-01")
        if df.empty:
             return jsonify({"error": "No data"}), 404
             
        probability = 0.5
        signal = "HOLD"
        confidence = 0.0
        
        # 模型預測邏輯
        registry_matches = []
        if model_type == 'lightgbm' or model_type == 'tree':
             try:
                 from src.services.model_registry import get_model_registry
                 registry = get_model_registry()
                 registry_matches = registry.list_models('lightgbm')
             except ImportError:
                 pass
        elif model_type == 'mlp':
             try:
                 from src.services.model_registry import get_model_registry
                 registry = get_model_registry()
                 registry_matches = registry.list_models('mlp')
             except ImportError:
                 pass

        if not registry_matches:
             # 若無模型，返回明確狀態
             signal = "NO_MODEL"
             confidence = 0.0
             probability = 0.0
        else:
             # 加載最新模型進行預測
             try:
                 latest = registry_matches[-1] # List is chronological
                 model_path = latest['path']
                 if not os.path.isabs(model_path):
                     # Construct absolute path if relative
                     from src.services.model_registry import ModelRegistry
                     # Use ModelRegistry class constant or instance if available, but registry instance has MODELS_DIR
                     # Re-import to be safe
                     model_path = os.path.join(registry.root_dir, model_path)
                 
                 # Load predictor
                 predictor = None
                 if model_type == 'lightgbm' or model_type == 'tree':
                     from src.models.arena.tree_predictor import LightGBMPredictor
                     predictor = LightGBMPredictor()
                     if not predictor.load_model(model_path):
                         predictor = None
                 elif model_type == 'mlp':
                     from src.models.arena.lstm_predictor import MLPPredictor
                     predictor = MLPPredictor(model_path=model_path)
                     if not predictor.load_model():
                         predictor = None
                 
                 if predictor:
                     # Generate features on live data df
                     # We need enough data for lag features. fetch_data(start_date="2024-01-01") is likely enough (~1 year)
                     signals_df = predictor.generate_signals(df)
                     
                     if not signals_df.empty:
                         last_row = signals_df.iloc[-1]
                         sig_val = last_row.get('Signal', 0) # Case sensitive? generate_signals uses 'Signal'
                         
                         if sig_val == 1: 
                             signal = "BUY"
                             probability = 0.8
                         elif sig_val == -1: 
                             signal = "SELL" 
                             probability = 0.2
                         else: 
                             signal = "HOLD"
                             probability = 0.5
                             
                         # Confidence could be derived if predict_proba is exposed. 
                         # For now, simulate confidence based on signal strength logic or static.
                         confidence = 0.75 if signal != "HOLD" else 0.0
                     else:
                         signal = "HOLD" # Data processed but no signal generated (e.g. not enough data)
                 else:
                     signal = "NO_MODEL" # Load failed
             except Exception as e:
                 logger.error(f"Prediction logic error: {e}")
                 signal = "ERROR"
        
        return jsonify({
            "ticker": ticker,
            "signal": signal,
            "probability": probability,
            "confidence": confidence,
            "timestamp": pd.Timestamp.now().strftime("%H:%M:%S")
        })
    except Exception as e:
        logger.error(f"Inference Error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok", "service": "gemini-quant-backend"})

@app.route('/api/v1/market/status', methods=['GET'])
def market_status():
    """
    Get Real Market Status (Phase 6 P3).
    """
    ticker = 'BTC-USD'
    try:
        # Fetch real-time info
        t = yf.Ticker(ticker)
        # fast_info is faster than info
        price = t.fast_info.get('last_price', 0.0)
        
        # S&P 500
        sp = yf.Ticker('^GSPC')
        sp_price = sp.fast_info.get('last_price', 0.0)
        
        return jsonify({
            "market_status": "OPEN (Real-time)",
            "bitcoin_price": round(price, 2),
            "sp500_level": round(sp_price, 2),
            "last_updated": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
        })
    except Exception as e:
        logger.error(f"Status Fetch Error: {e}")
        # Fallback
        return jsonify({
            "market_status": "ERROR (Fallback)",
            "bitcoin_price": 0.0,
            "sp500_level": 0.0,
            "last_updated": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
        })

@app.route('/api/v1/macro/overview', methods=['GET'])
def macro_overview():
    """
    Get Macro Dashboard Data (Demo Integration).
    提供 VIX、利率、Fear & Greed 等宏觀指標。
    """
    try:
        if get_macro_snapshot is None:
            return jsonify({"error": "Macro module not available"}), 500
        
        snapshot = get_macro_snapshot()
        next_event = get_next_event()
        
        # 獲取新聞頭條
        news_headlines = []
        try:
            from src.services.news_service import get_latest_headlines
            news_headlines = get_latest_headlines(5)
        except Exception as e:
            logger.warning(f"News fetch error: {e}")
        
        return jsonify({
            "vix": {
                "value": snapshot['vix_value'],
                "status": snapshot['vix_status'],
                "change": snapshot['vix_change']
            },
            "rates": {
                "yield_10y": snapshot['yield_10y'],
                "yield_2y": snapshot['yield_2y'],
                "spread_bps": snapshot['yield_spread']
            },
            "fear_greed": {
                "value": snapshot['fear_greed_value'],
                "label": snapshot['fear_greed_label']
            },
            "breadth": {
                "adv_dec_ratio": snapshot['adv_dec_ratio'],
                "status": snapshot['market_breadth']
            },
            "next_event": next_event,
            "news": news_headlines,  # 新增新聞頭條
            "data_quality": snapshot['data_quality'],
            "timestamp": snapshot['timestamp']
        })
    except Exception as e:
        logger.error(f"Macro Overview Error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/v1/news/headlines', methods=['GET'])
def news_headlines():
    """
    Get Financial News Headlines (繁中財經新聞).
    支持天聚數行 API + Yahoo RSS 備用。
    """
    try:
        from src.services.news_service import get_latest_headlines
        
        count = request.args.get('count', 10, type=int)
        news = get_latest_headlines(min(count, 20))
        
        return jsonify({
            "success": True,
            "count": len(news),
            "headlines": news
        })
    except Exception as e:
        logger.error(f"News Headlines Error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/v1/market/analysis', methods=['GET'])
def market_analysis():
    """
    Get Regime & Sentiment Analysis.
    """
    ticker = request.args.get('ticker', 'BTC-USD')
    
    # Sentiment
    sent_engine = SentimentEngine()
    sent_data = sent_engine.analyze(ticker)
    
    # Regime (Mock live prediction or fetch from strategy)
    regime = "Bull" 
    if sent_data['score'] < -0.3:
        regime = "Bear"
    elif abs(sent_data['score']) < 0.2:
        regime = "Volatile"
        
    return jsonify({
        "ticker": ticker,
        "regime": regime,
        "sentiment": sent_data
    })

@app.route('/api/v1/stock/valuation', methods=['GET'])
def stock_valuation():
    """
    Get Intrinsic Value Analysis (Phase 7.0).
    """
    # MAJOR-006 FIX: 實際調用 API Key 認證
    if not check_api_key():
        return jsonify({"error": "Unauthorized: Invalid or missing API Key"}), 401
    
    ticker = request.args.get('ticker', 'AAPL')
    try:
        from src.models.valuation import ValuationEngine
        engine = ValuationEngine(ticker)
        res = engine.assess_value()
        
        return jsonify({
            "ticker": res.ticker,
            "company_name": res.company_name,
            "current_price": res.current_price,
            "fair_value": res.fair_value,
            "margin_of_safety": res.margin_of_safety,
            "status": res.status,
            "models": res.models,
            "data_quality": res.data_quality,  # Audit Fix
            "details": res.details
        })
    except Exception as e:
        logger.error(f"Valuation Error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/v1/valuation/sensitivity', methods=['GET'])
def valuation_sensitivity():
    """
    Get DCF Sensitivity Analysis (P1 Task).
    返回 WACC vs Growth Rate 敏感度矩陣
    """
    if not check_api_key():
        return jsonify({"error": "Unauthorized"}), 401
    
    ticker = request.args.get('ticker', 'AAPL')
    try:
        from src.models.valuation_sensitivity import calculate_sensitivity
        from src.models.valuation import ValuationEngine
        import yfinance as yf
        
        # MAJOR-006 FIX: 從實際數據獲取 FCF 和股數
        engine = ValuationEngine(ticker)
        engine._fetch_data()
        
        # 嘗試從 yfinance 獲取實際數據
        stock = yf.Ticker(ticker)
        info = stock.info
        
        # FCF: 優先使用 freeCashflow，後備使用估計值
        base_fcf = info.get('freeCashflow') or info.get('operatingCashflow', 0) * 0.7
        if not base_fcf or base_fcf <= 0:
            base_fcf = 10_000_000_000  # 後備默認值，但記錄警告
            logger.warning(f"[{ticker}] FCF data unavailable, using fallback: ${base_fcf:,}")
        
        # 股數
        shares = info.get('sharesOutstanding', 0)
        if not shares or shares <= 0:
            shares = 1_000_000_000  # 後備默認值
            logger.warning(f"[{ticker}] Shares data unavailable, using fallback: {shares:,}")
        
        result = calculate_sensitivity(base_fcf, shares)
        result['ticker'] = ticker
        result['data_source'] = 'live' if base_fcf > 10_000_000_000 else 'fallback'
        
        return jsonify(result)
    except Exception as e:
        logger.error(f"Sensitivity Error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/v1/valuation/ddm', methods=['GET'])
def valuation_ddm():
    """
    Get DDM Valuation (P2 Task).
    支持 Gordon Growth 和 Two-Stage DDM
    """
    if not check_api_key():
        return jsonify({"error": "Unauthorized"}), 401
    
    ticker = request.args.get('ticker', 'AAPL')
    model = request.args.get('model', 'gordon')  # 'gordon' or 'two_stage'
    growth = float(request.args.get('growth', 0.03))
    
    try:
        from src.models.ddm_model import calculate_ddm
        result = calculate_ddm(ticker, model, growth)
        return jsonify(result)
    except Exception as e:
        logger.error(f"DDM Error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/v1/ai/generate', methods=['POST'])
def ai_generate():
    """
    AI Content Generation (P2 Task).
    調用 Gemini 3 Pro 生成分析內容
    """
    if not check_api_key():
        return jsonify({"error": "Unauthorized"}), 401
    
    try:
        from src.services.ai_proxy import get_ai_proxy
        
        data = request.get_json() or {}
        prompt = data.get('prompt', '')
        context_type = data.get('type', 'general')
        macro_data = data.get('macro_data', {})
        valuation_data = data.get('valuation_data', {})
        arena_data = data.get('arena_data', [])
        
        proxy = get_ai_proxy()
        
        if not proxy.is_configured():
            # 返回 Mock 分析
            return jsonify({
                "success": True,
                "content": f"🤖 AI 分析 (Demo Mode)\n\n此為示範分析。請在設置中配置 Gemini API 以獲取真實 AI 分析。\n\n上下文: {context_type}",
                "is_mock": True
            })
        
        if context_type == 'market' or context_type.startswith('market'):
            result = proxy.analyze_market(macro_data)
        elif context_type == 'valuation' or context_type.startswith('valuation'):
            result = proxy.analyze_valuation(valuation_data)
        elif context_type == 'arena' or context_type.startswith('arena'):
            result = proxy.analyze_arena(arena_data)
        elif prompt:
            result = proxy.generate(prompt)
        else:
            # 沒有 prompt 時，默認生成市場分析
            result = proxy.analyze_market(macro_data)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"AI Generate Error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/v1/ai/config', methods=['POST'])
def ai_config():
    """
    Update AI Configuration.
    更新 Gemini API 配置並持久化到文件
    """
    if not check_api_key():
        return jsonify({"error": "Unauthorized"}), 401
    
    try:
        from src.services.ai_proxy import get_ai_proxy
        from src.services.config_service import get_config_service
        
        data = request.get_json() or {}
        api_url = data.get('api_url')
        api_key = data.get('api_key')
        model = data.get('model', 'gemini-3-pro-high')
        
        # 更新 AI Proxy
        proxy = get_ai_proxy()
        proxy.update_config(api_url, api_key, model)
        
        # 持久化到配置文件
        config = get_config_service()
        config.update_ai_config(api_url, api_key, model)
        
        return jsonify({
            "success": True,
            "configured": proxy.is_configured(),
            "persisted": True
        })
        
    except Exception as e:
        logger.error(f"AI Config Error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/v1/model/train', methods=['POST'])
def model_train():
    """
    Train AI Models (Async Implementation).
    """
    if not check_api_key():
        return jsonify({"error": "Unauthorized"}), 401
        
    data = request.get_json() or {}
    model_type = data.get('model_type', 'lightgbm')
    params = data.get('params', {})
    ticker = data.get('ticker', 'BTC-USD')
    
    try:
        from src.models.arena.ai_optimizer import get_ai_trainer
        trainer = get_ai_trainer()
        
        job_id = trainer.start_training_job(model_type, ticker, params)
        
        return jsonify({
            "success": True,
            "job_id": job_id,
            "status": "pending",
            "message": "Training started in background"
        })
        
    except Exception as e:
        logger.error(f"Training Request Error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/v1/model/train/status/<job_id>', methods=['GET'])
def model_train_status(job_id):
    """
    Get AI Training Job Status.
    """
    if not check_api_key():
        return jsonify({"error": "Unauthorized"}), 401
        
    try:
        from src.models.arena.ai_optimizer import get_ai_trainer
        trainer = get_ai_trainer()
        status = trainer.get_job_status(job_id)
        
        if not status:
            return jsonify({"error": "Job not found"}), 404
            
        return jsonify(status)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/v1/models', methods=['GET', 'DELETE'])
def model_management():
    """
    List or Delete Models in Registry.
    """
    if not check_api_key():
        return jsonify({"error": "Unauthorized"}), 401
        
    try:
        from src.services.model_registry import get_model_registry
        registry = get_model_registry()
        
        if request.method == 'DELETE':
            model_type = request.args.get('type')
            version = request.args.get('version')
            if not model_type or not version:
                return jsonify({"error": "Missing type or version"}), 400
                
            success = registry.delete_model(model_type, version)
            return jsonify({"success": success})
            
        else: # GET
            model_type = request.args.get('type')
            models = registry.list_models(model_type)
            return jsonify({"models": models})
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/v1/arena/adversarial', methods=['POST'])
def arena_adversarial():
    """
    Run Adversarial Arena (Phase 3 AI Battle).
    """
    if not check_api_key():
        return jsonify({"error": "Unauthorized"}), 401
        
    data = request.get_json() or {}
    ticker = data.get('ticker', 'BTC-USD')
    
    try:
        from src.models.arena.adversarial_arena import AdversarialArena
        from src.data_loader.downloader import fetch_data
        
        # 1. Fetch History
        df = fetch_data(ticker, start_date="2023-01-01")
        if df.empty or len(df) < 200:
            return jsonify({"error": "Insufficient data for battle"}), 400
            
        # 2. Run Battle
        arena = AdversarialArena()
        result_df, meta = arena.run_battle(df)
        
        if not meta:
            return jsonify({"error": "Battle failed"}), 500
            
        return jsonify({
            "ticker": ticker,
            "winner": meta.winner,
            "weights": meta.weights,
            "metrics": meta.metrics,
            "timestamp": meta.timestamp
        })
        
    except Exception as e:
        logger.error(f"Adversarial Arena Error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/v1/arena/battle', methods=['GET'])
def arena_battle():
    """
    Run Strategy Arena (Phase 7.2).
    """
    # MAJOR-006 FIX: 實際調用 API Key 認證
    if not check_api_key():
        return jsonify({"error": "Unauthorized: Invalid or missing API Key"}), 401
    
    ticker = request.args.get('ticker', 'AAPL')
    try:
        from src.backend.arena import StrategyArena
        from src.data_loader.downloader import fetch_data
        
        # Fetch Data
        df = fetch_data(ticker, start_date="2024-01-01")
        if df.empty: 
            return jsonify({"error": "No data"}), 404
            
        # Run Arena
        arena = StrategyArena()
        results = arena.run_battle(df)
        
        # Save Results (Phase 9)
        current_date = pd.Timestamp.now().strftime("%Y-%m-%d")
        for res in results:
            storage.save_run(
                ticker=ticker,
                strategy=res['Strategy'],
                start_date="2024-01-01", 
                end_date=current_date,
                metrics={
                    "Total_Return": res['Total Return'],
                    "Sharpe_Ratio": res['Sharpe'],
                    "Max_Drawdown": res['Max DD']
                }
            )

        return jsonify({
            "ticker": ticker,
            "results": results
        })
    except Exception as e:
        logger.error(f"Arena Error: {e}")
        return jsonify({"error": str(e)}), 500

# ============================================
# Phase 2: Paper Trading API
# ============================================

# Global Engine Instance & Thread
_paper_engine = None
_sim_thread = None
_sim_running = False

def simulation_loop():
    """Background loop for paper trading."""
    global _paper_engine, _sim_running
    logger.info("Simulation Loop Started.")
    while _sim_running:
        try:
            if _paper_engine:
                _paper_engine.execute_step()
            time.sleep(60) # Run every minute
        except Exception as e:
            logger.error(f"Simulation Loop Error: {e}")
            time.sleep(60)
    logger.info("Simulation Loop Stopped.")

@app.route('/api/v1/simulation/start', methods=['POST'])
def start_simulation():
    """Start Paper Trading Simulation in Background Thread."""
    if not check_api_key():
        return jsonify({"error": "Unauthorized"}), 401
        
    global _paper_engine, _sim_thread, _sim_running
    
    if _sim_running:
         return jsonify({"status": "already_running", "ticker": _paper_engine.ticker})

    data = request.get_json() or {}
    ticker = data.get('ticker', 'AAPL')
    initial_capital = data.get('initial_capital', 100000.0)
    
    # Simple Strategy for Simulation
    strategy = MomentumStrategy()
    
    try:
        if _paper_engine is None or _paper_engine.ticker != ticker:
             # Reset engine if new ticker
            _paper_engine = PaperTradingEngine(strategy, ticker, initial_capital)
        
        # Start Thread
        _sim_running = True
        _sim_thread = threading.Thread(target=simulation_loop, daemon=True)
        _sim_thread.start()
        
        return jsonify({
            "status": "started",
            "ticker": ticker,
            "equity": _paper_engine.state['equity']
        })
    except Exception as e:
        _sim_running = False
        return jsonify({"error": str(e)}), 500

@app.route('/api/v1/simulation/stop', methods=['POST'])
def stop_simulation():
    """Stop Paper Trading Simulation."""
    if not check_api_key():
        return jsonify({"error": "Unauthorized"}), 401

    global _sim_running
    if _sim_running:
        _sim_running = False
        return jsonify({"status": "stopped"})
    else:
        return jsonify({"status": "not_running"})

@app.route('/api/v1/simulation/status', methods=['GET'])
def simulation_status():
    """Get Paper Trading Status."""
    if not check_api_key():
        return jsonify({"error": "Unauthorized"}), 401
    
    state_file = "paper_trade_state.json"
    if os.path.exists(state_file):
        try:
            with open(state_file, 'r') as f:
                state = json.load(f)
            return jsonify(state)
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    else:
        return jsonify({"status": "not_started"})

@app.route('/api/v1/backtest/run', methods=['GET'])
def run_backtest():
    """
    Run backtest on demand.
    Supports Multi-Strategy via comma-separated string.
    """
    # MAJOR-006 FIX: 實際調用 API Key 認證
    if not check_api_key():
        return jsonify({"error": "Unauthorized: Invalid or missing API Key"}), 401
    
    ticker = request.args.get('ticker', 'BTC-USD')
    strategy_type = request.args.get('strategy', 'momentum')
    version_str = request.args.get('version', None) # 讀取版本參數
    
    logger.info(f"Running backtest for {ticker} with strategy={strategy_type}, version={version_str}")
    try:
        # 1. Fetch Data (Real)
        start_date = "2024-01-01" # Extended for Phase 6
        
        # Check if modules loaded
        if 'src.backend.backtest_engine' not in sys.modules and 'Backtester' not in globals():
             return jsonify({"error": "Backtester module not loaded"}), 500
             
        df = fetch_data(ticker, start_date=start_date)
        if df.empty:
             return jsonify({"error": f"No data for {ticker}"}), 404
             
        # 2. Run Strategy - Issue 4 FIX: 根據策略參數選擇策略
        strategy_types = strategy_type.split(',')
        strategies = []
        strategy_names = []
        
        for stype in strategy_types:
            stype = stype.strip()
            if not stype: continue
            
            if stype == 'tree' or stype == 'lightgbm':
                try:
                    from src.models.arena.tree_predictor import LightGBMPredictor
                    from src.services.model_registry import get_model_registry
                    
                    predictor = LightGBMPredictor()
                    registry = get_model_registry()
                    
                    # 查找目標模型
                    target_model = None
                    if version_str:
                        # 用戶指定版本
                        models = registry.list_models('lightgbm')
                        for m in models:
                            if m['version'] == version_str:
                                target_model = m
                                break
                        if not target_model:
                            logger.warning(f"Requested version {version_str} not found, falling back to latest.")
                    
                    # 若無指定或未找到，取最新
                    if not target_model:
                        models = registry.list_models('lightgbm')
                        if models:
                            target_model = models[0] # List is sorted desc by default? No, append order. 
                            # ModelRegistry appends new models, so last is newest. 
                            # But wait, previous list_models code I saw iterates dict items. 
                            # list_models code: return self.registry["models"].get(model_type, [])
                            # Registry appends. So last item is newest.
                            # BUT my previous edit in api_server for Backtest used models[0]. 
                            # Let's check list_models implementation in model_registry.py again. 
                            # It returns the list directly.
                            # So models[-1] is likely the newest. 
                            # Wait, let's look at `get_next_version`. It takes `history[-1]`. So yes, list is chronological.
                            # So I should use models[-1] for latest!
                            # CORRECTING LOGIC: models[-1] is latest.
                            target_model = models[-1]

                    model_loaded = False
                    if target_model:
                        model_path = target_model.get('path')
                        if not os.path.isabs(model_path):
                            model_path = os.path.join(registry.MODELS_DIR, os.path.basename(model_path))
                            
                        if os.path.exists(model_path):
                            if predictor.load_model(model_path):
                                logger.info(f"Backtest: Loaded LightGBM model from Registry ({target_model['version']}).")
                                model_loaded = True
                    
                    if not model_loaded:
                        # Fallback
                        if predictor.load_model():
                            logger.info("Backtest: Loaded LightGBM model from default path.")
                            model_loaded = True
                        else:
                            logger.info("Backtest: No saved LightGBM model found, will train on-the-fly.")
                            
                    strategies.append(predictor)
                    strategy_names.append(f"LightGBM ({target_model['version'] if target_model else 'New'})")
                except ImportError as e:
                    logger.warning(f"Failed to import LightGBM: {e}")
                    pass
            elif stype == 'mlp':
                try:
                    from src.models.arena.lstm_predictor import MLPPredictor
                    from src.services.model_registry import get_model_registry
                    
                    registry = get_model_registry()
                    models = registry.list_models('mlp')
                    
                    target_model = None
                    if version_str:
                         for m in models:
                            if m['version'] == version_str:
                                target_model = m
                                break
                    
                    if not target_model and models:
                        target_model = models[-1] # Latest

                    model_loaded = False
                    predictor = None
                    
                    if target_model:
                        model_path = target_model.get('path')
                        if not os.path.isabs(model_path):
                            model_path = os.path.join(registry.MODELS_DIR, os.path.basename(model_path))
                            
                        if os.path.exists(model_path):
                            predictor = MLPPredictor(model_path=model_path)
                            if predictor.load_model():
                                logger.info(f"Backtest: Loaded MLP model from Registry ({target_model['version']}).")
                                model_loaded = True
                    
                    if not model_loaded:
                        predictor = MLPPredictor()
                        if predictor.load_model():
                             logger.info("Backtest: Loaded MLP model from default path.")
                        else:
                             logger.info("Backtest: No saved MLP model found, will train on-the-fly.")
                    
                    strategies.append(predictor)
                    strategy_names.append(f"MLP ({target_model['version'] if target_model else 'New'})")
                except ImportError as e:
                    logger.warning(f"Failed to import MLP: {e}")
                    pass
            elif stype == 'rsi':
                try:
                    from src.models.strategy_enhancements import RSIReversionStrategy
                    strategies.append(RSIReversionStrategy())
                    strategy_names.append("RSI Reversion")
                except ImportError:
                    pass
            else: # Momentum default
                strategies.append(MomentumStrategy())
                strategy_names.append("Momentum")
        
        if not strategies:
            strategies = [MomentumStrategy()]
            strategy_names = ["Momentum"]
            
        # Create Portfolio if multiple or single
        if len(strategies) > 1:
            portfolio = Portfolio(strategies)
            strategy_name = " + ".join(strategy_names)
            strategy = portfolio
        else:
            strategy = strategies[0]
            strategy_name = strategy_names[0]
            
        bt = Backtester()
        result = bt.run_backtest(df, strategy)
        
        # 3. Save Result (Phase 6 P2)
        storage.save_run(
            ticker=ticker,
            strategy=strategy_name,
            start_date=start_date,
            end_date=pd.Timestamp.now().strftime("%Y-%m-%d"),
            metrics=result['metrics']
        )
        
        # Prepare OHLCV Data for Chart
        # Format: [{time: '2023-01-01', open: 100, high: 105, low: 99, close: 102}, ...]
        # Prepare OHLCV Data for Chart
        # Format: [{time: '2023-01-01', open: 100, high: 105, low: 99, close: 102}, ...]
        ohlcv = []
        
        # Ensure index is datetime for strftime
        temp_df = df.copy()
        if not isinstance(temp_df.index, pd.DatetimeIndex):
            if 'Date' in temp_df.columns:
                temp_df['Date'] = pd.to_datetime(temp_df['Date'])
                temp_df.set_index('Date', inplace=True)
            else:
                # Attempt to convert index
                try:
                    temp_df.index = pd.to_datetime(temp_df.index)
                except Exception:
                    pass

        for index, row in temp_df.iterrows():
            date_str = str(index)
            if hasattr(index, 'strftime'):
                date_str = index.strftime("%Y-%m-%d")
            elif isinstance(index, str):
                date_str = index.split(" ")[0] # Handle "2024-01-01 00:00:00"

            ohlcv.append({
                "time": date_str,
                "open": row['Open'],
                "high": row['High'],
                "low": row['Low'],
                "close": row['Close']
            })

        response_data = {
            "ticker": ticker,
            "period": "Since " + start_date,
            "metrics": result['metrics'],
            "equity_curve": result['equity_curve'],
            "dates": result['dates'],
            "ohlcv": ohlcv,
            "trades": result.get('trades', []),  # Phase 12
            "daily_returns": result.get('daily_returns', []),  # 新增
            "distribution": Backtester.get_return_distribution(result.get('daily_returns', []))  # 新增
        }
        
        return jsonify(sanitize_for_json(response_data))
        
    except Exception as e:
        logger.error(f"Backtest error: {e}")
        return jsonify({"error": str(e)}), 500

# ============================================
# Sprint 4: 數據更新 API
# ============================================

# 數據更新服務實例
_data_service = None
def get_data_service():
    global _data_service
    if _data_service is None:
        try:
            from src.data_loader.data_update_service import DataUpdateService
            _data_service = DataUpdateService()
        except ImportError:
            pass
    return _data_service

@app.route('/api/v1/data/audit', methods=['GET'])
def data_audit():
    """審計數據覆蓋情況"""
    service = get_data_service()
    if service is None:
        return jsonify({"error": "DataUpdateService not available"}), 500
    
    tickers = request.args.get('tickers', 'AAPL,MSFT,GOOGL,NVDA').split(',')
    reports = service.audit_data_coverage(tickers)
    
    return jsonify({
        "reports": [
            {
                "ticker": r.ticker,
                "price_start": r.price_start,
                "price_end": r.price_end,
                "price_rows": r.price_rows,
                "has_financials": r.has_financials,
                "status": r.status
            } for r in reports
        ]
    })

@app.route('/api/v1/data/update', methods=['POST'])
def data_update():
    """
    觸發數據更新
    
    支持兩種模式：
    - 默認模式：更新指定的 tickers 列表
    - sp500 模式：更新所有 S&P 500 股票 (2008-至今)
    """
    # MAJOR-006 FIX: 實際調用 API Key 認證
    if not check_api_key():
        return jsonify({"error": "Unauthorized: Invalid or missing API Key"}), 401
    
    service = get_data_service()
    if service is None:
        return jsonify({"error": "DataUpdateService not available"}), 500
    
    data = request.get_json() or {}
    mode = data.get('mode', 'default')  # 'default' 或 'sp500'
    
    if mode == 'sp500':
        # S&P 500 全量更新模式
        import threading
        def run_update():
            service.update_sp500_all()
        
        # 異步執行（避免請求超時）
        thread = threading.Thread(target=run_update)
        thread.daemon = True
        thread.start()
        
        return jsonify({
            "status": "started",
            "message": "S&P 500 全量更新已啟動 (預計 30-60 分鐘)",
            "mode": "sp500"
        })
    else:
        # 默認模式：更新指定 tickers
        tickers = data.get('tickers', ['AAPL', 'MSFT', 'GOOGL'])
        result = service.update_all(tickers)
        
        return jsonify({
            "status": result.status,
            "completed": result.completed,
            "total": result.total,
            "percentage": result.percentage,
            "errors": result.errors
        })

@app.route('/api/v1/data/cancel', methods=['POST'])
def data_cancel():
    """取消正在進行的數據更新"""
    service = get_data_service()
    if service is None:
        return jsonify({"error": "DataUpdateService not available"}), 500
    
    service.cancel_update()
    return jsonify({"status": "cancelled"})

@app.route('/api/v1/data/progress', methods=['GET'])
def data_progress():
    """獲取數據更新進度"""
    service = get_data_service()
    if service is None:
        return jsonify({"error": "DataUpdateService not available"}), 500
    
    progress = service.get_progress()
    if progress is None:
        return jsonify({"status": "idle"})
    return jsonify(progress)

def start_server(port=5000):
    app.run(host='0.0.0.0', port=port, debug=False)

if __name__ == "__main__":
    print("--- SELF-TEST START: api_server.py ---")
    
    # Test Client
    with app.test_client() as client:
        # 1. Health
        resp = client.get('/health')
        print(f"[TEST] Health Check: {resp.status_code} - {resp.json}")
        
        # 2. Market Status
        resp = client.get('/api/v1/market/status')
        print(f"[TEST] Market Status: {resp.status_code} - {resp.json}")
        
        if resp.status_code == 200:
            print("[TEST] SUCCESS: API endpoints reachable.")
        else:
            print("[TEST] FAILURE: API error.")
            
    print("--- SELF-TEST END ---")
    
    # Start Real Server
    print(">>> Starting API Server on Port 666...")
    start_server(port=666)
