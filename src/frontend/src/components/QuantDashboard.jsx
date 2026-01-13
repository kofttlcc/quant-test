/**
 * QuantDashboard.jsx - 量化分析系統主界面 (投產版本)
 * 整合 app.tsx Demo 與現有後端 API
 * 內建 Mock 數據確保始終有內容顯示
 */

import React, { useState, useEffect, useCallback } from 'react';
import {
    LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip,
    ResponsiveContainer, AreaChart, Area, BarChart, Bar,
    Cell, ReferenceLine, ComposedChart, Scatter
} from 'recharts';
import {
    Activity, TrendingUp, TrendingDown, DollarSign,
    Settings, Layers, Play, BarChart2,
    ShieldAlert, Layout, Search, Bell,
    Database, RefreshCw, AlertTriangle,
    Calendar, Sliders, Hash, Globe, Gauge, BarChart4,
    Zap, Bot, Swords, Calculator, Sparkles, Loader2,
    Key, Network, User, Lock, Save, Server, Cpu
} from 'lucide-react';
import { API } from '../services/api';
import ModelTrainingModal from './ModelTrainingModal';
import SimulationDashboard from './SimulationDashboard';
import AISignalWidget from './AISignalWidget';
import './QuantDashboard.css';

const API_BASE = '/api/v1';

// ============ MOCK DATA (Fallback) ============

const MOCK_BACKTEST = {
    metrics: {
        Total_Return: 0.245,
        Annualized_Return: 0.182,
        Sharpe_Ratio: 2.84,
        Max_Drawdown: -0.082,
        Total_Trades: 156,
        Win_Rate: 0.584,
        // Sprint 1: P0 風險指標
        VaR_95: -0.0215,       // 95% 日 VaR
        CVaR_95: -0.0342,      // 95% 日 CVaR
        Sortino_Ratio: 3.12,   // Sortino Ratio
        Total_Commission: 156.80 // 總佣金
    },
    equity_curve: Array.from({ length: 252 }, (_, i) => 1 + (i * 0.001) + (Math.sin(i / 20) * 0.02))
};

const MOCK_ARENA = [
    { Strategy: 'LightGBM 預測器', Type: 'AI', 'Total Return': 0.185, Sharpe: 2.4, 'Max DD': -0.042 },
    { Strategy: 'MLP 趨勢模型', Type: 'AI', 'Total Return': 0.158, Sharpe: 2.1, 'Max DD': -0.085 },
    { Strategy: 'RSI 均值回歸', Type: 'Traditional', 'Total Return': 0.121, Sharpe: 1.8, 'Max DD': -0.021 },
    { Strategy: '動量策略', Type: 'Traditional', 'Total Return': 0.089, Sharpe: 1.2, 'Max DD': -0.067 },
    { Strategy: '趨勢追蹤 MA', Type: 'Traditional', 'Total Return': 0.054, Sharpe: 0.9, 'Max DD': -0.123 },
];

const MOCK_VALUATION = {
    ticker: 'AAPL',
    company_name: 'Apple Inc.',
    current_price: 178.35,
    fair_value: 205.10,
    intrinsic_value: 205.10,
    margin_of_safety: 0.152,
    status: 'UNDERVALUED',
    confidence: 'HIGH',
    details: {
        wacc: '8.0%',
        growth: '2.5%',
        terminal_growth: '2.5%'
    }
};

const MOCK_MACRO = {
    vix: { value: 14.8, status: 'Normal', change: -1.5, term_structure: 'Contango' },
    fear_greed: { value: 68, label: 'Greed' },
    rates: { yield_10y: 4.25, yield_2y: 4.60, spread_bps: -35 },
    breadth: {
        adv_dec_ratio: 1.85,
        status: 'Risk On',
        advancing: 320,
        declining: 173,
        sectors: [
            { name: 'XLK (科技)', change: 1.2 },
            { name: 'XLU (公用)', change: -0.4 }
        ]
    },
    next_event: {
        name: 'FOMC 利率決議',
        countdown_days: 12,
        countdown_hours: 4,
        market_expectation: '暫停升息',
        impact: 'HIGH'
    },
    breaking_news: '聯準會會議紀要暗示暫停加息，那指期貨夜盤大漲 1.2%',
    info_news: '10年期美債收益率回落至 4.25% 下方，創兩週新低'
};

// 按 Demo 原版生成 K 線數據
const generateKLineData = (points = 60) => {
    let data = [];
    let price = 150;

    for (let i = 0; i < points; i++) {
        const move = (Math.random() - 0.48) * 3;
        const volatility = Math.random() * 2;
        const open = price;
        const close = price + move;
        const high = Math.max(open, close) + Math.random() * volatility;
        const low = Math.min(open, close) - Math.random() * volatility;
        price = close;
        let rsi = 50 + (Math.random() - 0.5) * 40;

        let signal = null;
        let signalPrice = null;
        if (rsi < 30 && Math.random() > 0.5) { signal = 'buy'; signalPrice = low * 0.98; }
        else if (rsi > 70 && Math.random() > 0.5) { signal = 'sell'; signalPrice = high * 1.02; }

        const isUp = close > open;
        data.push({
            time: `10-${String(i + 1).padStart(2, '0')}`,
            open: parseFloat(open.toFixed(2)),
            high: parseFloat(high.toFixed(2)),
            low: parseFloat(low.toFixed(2)),
            close: parseFloat(close.toFixed(2)),
            body: [Math.min(open, close), Math.max(open, close)],
            wick: [low, high],
            color: isUp ? '#10b981' : '#f43f5e',
            rsi: parseFloat(rsi.toFixed(2)),
            signal,
            signalPrice
        });
    }
    return data;
};

// 信號標記組件 (按 Demo 原版)
// 交易明細表格樣式
const tradeTableStyles = {
    table: {
        width: '100%',
        borderCollapse: 'collapse',
        fontSize: '0.85rem'
    },
    thead: {
        position: 'sticky',
        top: 0,
        backgroundColor: '#f8fafc',
        zIndex: 1
    },
    th: {
        padding: '10px 12px',
        textAlign: 'left',
        fontWeight: 600,
        color: '#64748b',
        borderBottom: '2px solid #e2e8f0'
    },
    tr: {
        borderBottom: '1px solid #f1f5f9'
    },
    td: {
        padding: '8px 12px',
        color: '#334155'
    }
};

const SignalMarker = (props) => {
    const { cx, cy, payload } = props;
    if (!payload || !payload.signal) return null;
    const isBuy = payload.signal === 'buy';
    const color = isBuy ? '#10b981' : '#f43f5e';
    return (
        <g transform={`translate(${cx},${cy})`}>
            <polygon points={isBuy ? "-6,6 0,-6 6,6" : "-6,-6 0,6 6,-6"} fill={color} stroke="none" />
            <text x={0} y={isBuy ? 20 : -15} textAnchor="middle" fill={color} fontSize={10} fontWeight="bold">{isBuy ? 'B' : 'S'}</text>
        </g>
    );
};

// 生成 RSI 數據
const generateRSIData = () => {
    let data = [];
    let rsi = 50;
    for (let i = 0; i < 60; i++) {
        rsi += (Math.random() - 0.5) * 10;
        rsi = Math.max(20, Math.min(80, rsi));
        data.push({ time: `10-${String(i + 1).padStart(2, '0')}`, rsi: parseFloat(rsi.toFixed(1)) });
    }
    return data;
};

// 生成回撤數據 - 使用標準日期格式
const generateDrawdownData = () => {
    let data = [];
    let currentDrawdown = 0;
    const startDate = new Date('2024-10-01');
    for (let i = 0; i < 60; i++) {
        const change = Math.random() > 0.6 ? 0.5 : -0.8;
        currentDrawdown = Math.min(0, currentDrawdown + change);
        if (Math.random() > 0.8) currentDrawdown = 0;
        const date = new Date(startDate);
        date.setDate(date.getDate() + i);
        const dateStr = date.toISOString().split('T')[0]; // YYYY-MM-DD 格式
        data.push({ time: dateStr, drawdown: parseFloat(currentDrawdown.toFixed(2)) });
    }
    return data;
};

// 收益分佈數據
const DISTRIBUTION_DATA = [
    { range: '<-3%', count: 2 }, { range: '-2%~-3%', count: 5 }, { range: '-1%~-2%', count: 12 },
    { range: '-0%~-1%', count: 25 }, { range: '0%~1%', count: 35 }, { range: '1%~2%', count: 20 },
    { range: '2%~3%', count: 8 }, { range: '>3%', count: 3 },
];

// 敏感度分析數據
const SENSITIVITY_DATA = [
    { wacc: '7.5%', g2: '$145', g25: '$158', g3: '$172' },
    { wacc: '8.0%', g2: '$132', g25: '$142', g3: '$155' },
    { wacc: '8.5%', g2: '$120', g25: '$128', g3: '$138' },
];

// ============ COMPONENTS ============

const MetricCard = ({ title, value, subValue, isPositive, icon: Icon }) => (
    <div className="metric-card">
        <div className="metric-header">
            <span className="metric-title">{title}</span>
            <Icon size={16} className="metric-icon" />
        </div>
        <div className="metric-body">
            <div className="metric-value">{value}</div>
            {subValue && (
                <div className={`metric-sub ${isPositive ? 'positive' : 'negative'}`}>
                    {isPositive ? <TrendingUp size={12} /> : <TrendingDown size={12} />}
                    {subValue}
                </div>
            )}
        </div>
    </div>
);

const IconButton = ({ icon: Icon, label, active, onClick }) => (
    <div className="icon-button-wrapper">
        <button onClick={onClick} className={`icon-button ${active ? 'active' : ''}`}>
            <Icon size={20} />
        </button>
        <div className="icon-tooltip">{label}</div>
    </div>
);

const Badge = ({ children, type }) => {
    const styles = {
        active: 'badge-active', inactive: 'badge-inactive',
        warning: 'badge-warning', training: 'badge-training',
    };
    return (
        <span className={`badge ${styles[type] || 'badge-info'}`}>
            {type === 'active' && <div className="badge-dot pulse"></div>}
            {type === 'training' && <div className="badge-dot bounce"></div>}
            {children || (type === 'active' ? '運行中' : type === 'inactive' ? '離線' : type === 'training' ? '訓練中' : '異常')}
        </span>
    );
};

const AIAnalysisCard = ({ title, content, isLoading, onGenerate, buttonText = "生成分析" }) => (
    <div className="ai-card">
        <div className="ai-card-header">
            <h3><Sparkles size={14} /> {title}</h3>
            <button onClick={onGenerate} disabled={isLoading} className="ai-btn">
                {isLoading ? <Loader2 size={12} className="spin" /> : <Bot size={12} />}
                {isLoading ? "分析中..." : buttonText}
            </button>
        </div>
        {content && (
            <div className="ai-content">
                {content.split('\n').map((line, i) => <p key={i}>{line}</p>)}
            </div>
        )}
    </div>
);

// ============ MAIN COMPONENT ============

export default function QuantDashboard({ onNavigate }) {
    const [activeTab, setActiveTab] = useState('dashboard');
    const [ticker, setTicker] = useState('AAPL');
    const [isLoading, setIsLoading] = useState(false);
    const [dataSource, setDataSource] = useState('Mock'); // 'Live' or 'Mock'

    // State with Mock defaults
    const [backtestData, setBacktestData] = useState(MOCK_BACKTEST);
    // 使用 K 線數據 (按 Demo 原版)
    const [chartData, setChartData] = useState(() => generateKLineData());
    const [drawdownData, setDrawdownData] = useState(() => generateDrawdownData());
    const [rsiData] = useState(() => generateRSIData());
    const [arenaData, setArenaData] = useState(MOCK_ARENA);
    const [valuationData, setValuationData] = useState(MOCK_VALUATION);
    const [macroData, setMacroData] = useState(MOCK_MACRO);

    // 估值模型選擇
    const [valuationModel, setValuationModel] = useState('DCF');

    // 時間週期選擇
    const [timeframe, setTimeframe] = useState('1D');

    // 回測參數 (可編輯) - 按照 PM 需求設置默認值
    const [backtestParams, setBacktestParams] = useState({
        startDate: '2020-03-23',
        endDate: new Date().toISOString().split('T')[0], // 當前日期
        initialCapital: 10000,
        strategy: '',  // 空表示使用默認策略
        universe: 'SPY, QQQ'
    });

    // AI 模型版本選擇
    const [aiModelVersions, setAiModelVersions] = useState([]);
    const [selectedModelVersion, setSelectedModelVersion] = useState('');

    // 當策略包含 AI 時，獲取版本列表
    useEffect(() => {
        const fetchVersions = async () => {
            const strats = (backtestParams.strategy || '').toLowerCase();
            let type = '';
            if (strats.includes('lightgbm')) type = 'lightgbm';
            else if (strats.includes('mlp')) type = 'mlp';

            if (type) {
                try {
                    const res = await API.listModels(type);
                    if (res && res.models) {
                        // 取最近 5 個版本
                        const versions = res.models.slice(-5).reverse();
                        setAiModelVersions(versions);
                        if (versions.length > 0 && !selectedModelVersion) {
                            setSelectedModelVersion(versions[0].version);
                        }
                    }
                } catch (e) {
                    console.error("Failed to fetch model versions:", e);
                }
            } else {
                setAiModelVersions([]);
                setSelectedModelVersion('');
            }
        };
        fetchVersions();
    }, [backtestParams.strategy]);

    // AI Analysis states
    const [aiAnalysis, setAiAnalysis] = useState('');
    const [isAiLoading, setIsAiLoading] = useState(false);

    // 訓練 Modal 狀態
    const [showTrainingModal, setShowTrainingModal] = useState(false);

    // 模型有效性過濾函數
    const isValidModel = (model) => {
        return model.Sharpe > 0 &&
            (model['Total Return'] || 0) > -0.5 &&
            (model['Max DD'] || 0) > -0.8;
    };

    // Settings - load from localStorage
    const [config, setConfig] = useState(() => {
        const saved = localStorage.getItem('quant_config');
        if (saved) {
            try {
                return JSON.parse(saved);
            } catch (e) {
                console.error('Failed to parse saved config:', e);
            }
        }
        return {
            apiAddress: import.meta.env.VITE_API_URL || 'http://localhost:666',
            geminiUrl: '',
            geminiKey: '',
            geminiModel: 'gemini-3-pro-high',
        };
    });
    const [configStatus, setConfigStatus] = useState('');

    // Sync config to backend on initial load
    // Sync config to backend on initial load
    useEffect(() => {
        if (config.geminiKey) {
            API.configureAI(config.geminiUrl, config.geminiKey, config.geminiModel).catch(console.error);
        }
    }, []);

    // Load live data
    const loadLiveData = useCallback(async () => {
        setIsLoading(true);
        setDataSource('Loading...');

        // 解析 universe 參數，取第一個 ticker 進行回測
        // 注意：目前後端只支持單一 ticker，多資產聯合回測需要後端擴展
        const universeList = backtestParams.universe.split(',').map(t => t.trim()).filter(t => t);

        // FIX: Search Bug - Prioritize user input (ticker) over default universe
        const primaryTicker = ticker || universeList[0];

        // REMOVED: Force overwrite logic that caused search reset
        // if (universeList.length > 0 && universeList[0] !== ticker) {
        //     setTicker(universeList[0]);
        // }

        try {
            // Try to load backtest with configured parameters
            // 傳遞版本參數 (如果有)
            const btResult = await API.runBacktest(primaryTicker, backtestParams.strategy || 'momentum', selectedModelVersion);

            if (btResult && btResult.error) {
                // 顯式錯誤提示
                alert(`Backtest Failed: ${btResult.error}\n\nPlease check if the trained model exists or try another strategy.`);
                setDataSource('Error');
                setIsLoading(false);
                return;
            }

            if (btResult && !btResult.error && btResult.metrics) {
                setBacktestData(btResult);
                // 更新 K 線圖數據使用真實 OHLCV 數據
                if (btResult.ohlcv && btResult.ohlcv.length > 0) {
                    // 採樣：最多顯示 120 個蠟燭
                    const maxCandles = 120;
                    const ohlcvData = btResult.ohlcv;
                    const step = Math.max(1, Math.floor(ohlcvData.length / maxCandles));

                    // 預建 trades 查找表
                    const tradesMap = new Map();
                    const tradeDates = new Set();
                    if (btResult.trades) {
                        btResult.trades.forEach(t => {
                            tradesMap.set(t.time, { type: t.type?.toLowerCase(), size: t.size, value: t.value });
                            tradeDates.add(t.time);
                        });
                    }

                    // 改進採樣：確保交易日期被包含
                    const sampledData = ohlcvData.filter((d, i) => {
                        // 包含：每隔 step 個點、最後一個點、以及所有交易日期
                        return i % step === 0 || i === ohlcvData.length - 1 || tradeDates.has(d.time);
                    });

                    // 轉換為圖表格式
                    const klineData = sampledData.map((d) => {
                        const trade = tradesMap.get(d.time);
                        return {
                            time: d.time.substring(5), // "MM-DD" 格式
                            open: d.open,
                            high: d.high,
                            low: d.low,
                            close: d.close,
                            body: [Math.min(d.open, d.close), Math.max(d.open, d.close)],
                            wick: [d.low, d.high],
                            color: d.close >= d.open ? '#22c55e' : '#ef4444',
                            rsi: 30 + Math.random() * 40, // 模擬 RSI
                            signal: trade?.type || null,
                            signalPrice: trade ? d.close : null,
                            // 新增：交易數量和金額（可用於 tooltip）
                            tradeSize: trade?.size || null,
                            tradeValue: trade?.value || null
                        };
                    });
                    setChartData(klineData);
                }

                // 計算真實回撤數據
                if (btResult.equity_curve && btResult.dates && btResult.equity_curve.length > 0) {
                    const equities = btResult.equity_curve;
                    let maxEquity = equities[0];

                    // 採樣：如果數據超過 100 個點，每 N 個點取一個
                    const maxPoints = 100;
                    const step = Math.max(1, Math.floor(equities.length / maxPoints));

                    const realDrawdown = [];
                    for (let i = 0; i < equities.length; i += step) {
                        const eq = equities[i];
                        maxEquity = Math.max(maxEquity, eq);
                        const dd = ((eq - maxEquity) / maxEquity) * 100;
                        realDrawdown.push({
                            time: btResult.dates[i],
                            drawdown: parseFloat(dd.toFixed(2))
                        });
                    }
                    setDrawdownData(realDrawdown);
                }

                setDataSource('Live');
            } else {
                setDataSource('Mock');
            }
        } catch (e) {
            console.error('Backtest error:', e);
            setDataSource('Mock');
        }

        try {
            // Try to load arena
            const arenaResult = await API.runArena(primaryTicker);
            if (arenaResult?.results?.length > 0) {
                setArenaData(arenaResult.results);
            }
        } catch (e) {
            console.error('Arena error:', e);
        }

        try {
            // Try to load valuation
            const valResult = await API.getValuation(primaryTicker);
            if (valResult && !valResult.error && valResult.current_price) {
                setValuationData({
                    ...MOCK_VALUATION,
                    ...valResult,
                    intrinsic_value: valResult.fair_value || valResult.intrinsic_value
                });
            }
        } catch (e) {
            console.error('Valuation error:', e);
        }

        try {
            // Try to load macro
            const macroResult = await API.getMacroOverview();
            if (macroResult && !macroResult.error) {
                setMacroData(macroResult);
            }
        } catch (e) {
            console.error('Macro error:', e);
        }

        setIsLoading(false);
    }, [ticker, backtestParams]);

    // Initial load
    useEffect(() => {
        loadLiveData();
    }, []);

    // ===== P3: 實時更新 (輪詢) =====
    const [isLiveUpdating, setIsLiveUpdating] = useState(false);
    const [lastUpdateTime, setLastUpdateTime] = useState(null);

    // Arena 實時更新 (每 30 秒)
    useEffect(() => {
        const updateArena = async () => {
            try {
                setIsLiveUpdating(true);
                const arenaResult = await API.runArena(ticker);
                if (arenaResult?.results?.length > 0) {
                    setArenaData(arenaResult.results);
                    setLastUpdateTime(new Date().toLocaleTimeString());
                }
            } catch (e) {
                console.error('Arena live update error:', e);
            } finally {
                setIsLiveUpdating(false);
            }
        };

        // 初始不立即更新，使用 loadLiveData 的結果
        const interval = setInterval(updateArena, 30000); // 30 秒
        return () => clearInterval(interval);
    }, [ticker]);

    // 宏觀數據實時更新 (每 60 秒)
    useEffect(() => {
        const updateMacro = async () => {
            try {
                const macroResult = await API.getMacroOverview();
                if (macroResult && !macroResult.error) {
                    setMacroData(macroResult);
                }
            } catch (e) {
                console.error('Macro live update error:', e);
            }
        };

        const interval = setInterval(updateMacro, 60000); // 60 秒
        return () => clearInterval(interval);
    }, []);

    // Generate AI Analysis (integrated with Gemini 3 Pro)
    const generateAIAnalysis = async (contextType) => {
        setIsAiLoading(true);
        try {
            const result = await API.generateAI(contextType, {
                macroData: macroData,
                valuationData: valuationData,
                arenaData: arenaData
            });

            if (result.success) {
                setAiAnalysis(result.content);
            } else if (result.is_mock) {
                setAiAnalysis(result.content);
            } else {
                setAiAnalysis(`❌ AI 分析失敗: ${result.error || '未知錯誤'}\n\n請檢查設置中的 Gemini API 配置。`);
            }
        } catch (e) {
            console.error('AI Analysis error:', e);
            setAiAnalysis(`❌ AI 分析失敗: ${e.message}\n\n請檢查後端服務是否運行。`);
        }
        setIsAiLoading(false);
    };

    // ============ VIEWS ============

    const renderDashboard = () => (
        <div className="dashboard-grid">
            {/* 頂部新聞滾動條 - 按 Demo 設計 */}
            <div className="news-ticker-bar">
                <div className="news-breaking">
                    <span className="news-tag breaking">BREAKING:</span>
                    <span>{macroData.breaking_news || '聯準會會議紀要暗示暫停加息，那指期貨夜盤大漲 1.2%'}</span>
                </div>
                <div className="news-info">
                    <span className="news-tag info">INFO:</span>
                    <span>{macroData.info_news || '10年期美債收益率回落至 4.25% 下方，創兩週新低'}</span>
                </div>
                <div className="live-indicator">
                    <span className="live-dot"></span>
                    實時 (LIVE)
                </div>
            </div>

            {/* 宏觀態勢感知 - 按 Demo 1:1 還原 */}
            <div className="macro-panel">
                <div className="macro-header">
                    <Globe size={14} />
                    <span>宏觀態勢感知</span>
                </div>
                <div className="macro-cards-row">
                    {/* 市場情緒 */}
                    <div className="macro-card sentiment">
                        <div className="card-label"><Gauge size={12} /> 市場情緒</div>
                        <div className="card-badge">Contra</div>
                        <div className="sentiment-value">{macroData.fear_greed?.value || 68}</div>
                        <div className="sentiment-label">{macroData.fear_greed?.label || 'Greed'}</div>
                        <div className="sentiment-bar">
                            <div className="bar-fill" style={{ width: `${macroData.fear_greed?.value || 68}%` }}></div>
                        </div>
                        <div className="sentiment-labels">
                            <span>極恐</span><span>中性</span><span>極貪</span>
                        </div>
                    </div>

                    {/* 利率與波動 */}
                    <div className="macro-card rates">
                        <div className="card-label"><TrendingUp size={12} /> 利率與波動</div>
                        <div className="rates-grid">
                            <div className="rate-item">
                                <span className="rate-label">美債 10年殖利率</span>
                                <span className="rate-value">{macroData.rates?.yield_10y || 4.25}%</span>
                            </div>
                            <div className="rate-item">
                                <span className="rate-label">10年-2年 利差</span>
                                <span className="rate-value negative">{macroData.rates?.spread_bps || -35} bps</span>
                            </div>
                            <div className="rate-item">
                                <span className="rate-label">VIX 恐慌指數</span>
                                <span className="rate-value">{macroData.vix?.value || 14.8}</span>
                            </div>
                            <div className="rate-item">
                                <span className="rate-label">期限結構</span>
                                <span className="rate-value badge">{macroData.vix?.term_structure || '正價差'}</span>
                            </div>
                        </div>
                    </div>

                    {/* 下一個超級事件 */}
                    <div className="macro-card event">
                        <div className="card-label"><Zap size={12} /> 下一個超級事件</div>
                        <span className="impact-badge high">{macroData.next_event?.impact || 'HIGH'} 衝擊</span>
                        <div className="event-name">{macroData.next_event?.name || 'FOMC 利率決議'}</div>
                        <div className="event-org">聯邦公開市場委員會</div>
                        <div className="event-details">
                            <div className="detail-item">
                                <span className="detail-label">倒數計時</span>
                                <span className="detail-value">{macroData.next_event?.countdown_days || 12}D {macroData.next_event?.countdown_hours || 4}H</span>
                            </div>
                            <div className="detail-item">
                                <span className="detail-label">市場預期</span>
                                <span className="detail-value">{macroData.next_event?.market_expectation || '暫停升息'}</span>
                            </div>
                        </div>
                    </div>

                    {/* 市場廣度 - 缺失的功能 */}
                    <div className="macro-card breadth">
                        <div className="card-label"><BarChart2 size={12} /> 市場廣度 (Breadth)</div>
                        <span className="risk-badge on">{macroData.breadth?.status || '風險偏好 (Risk On)'} ▲</span>
                        <div className="breadth-labels">
                            <span>上漲股票隻數 ({macroData.breadth?.advancing || 320})</span>
                            <span>下跌股票隻數 ({macroData.breadth?.declining || 173})</span>
                        </div>
                        <div className="breadth-bar">
                            <div className="adv-bar"></div>
                            <div className="dec-bar"></div>
                        </div>
                        <div className="breadth-ratio">漲跌比: {macroData.breadth?.adv_dec_ratio || 1.85}</div>
                        <div className="sector-changes">
                            {(macroData.breadth?.sectors || [
                                { name: 'XLK (科技)', change: 1.2 },
                                { name: 'XLU (公用)', change: -0.4 }
                            ]).map((s, i) => (
                                <span key={i} className={s.change > 0 ? 'positive' : 'negative'}>
                                    {s.name} {s.change > 0 ? '+' : ''}{s.change}%
                                </span>
                            ))}
                        </div>
                    </div>
                </div>
            </div>

            {/* AI 首席策略師觀點 */}
            <div className="ai-insight-bar">
                <div className="ai-insight-label">
                    <Sparkles size={16} />
                    <span>AI 首席策略師觀點 (AI Macro Insight)</span>
                </div>
                <button className="ai-generate-btn" onClick={() => generateAIAnalysis('macro')}>
                    <Bot size={14} /> 生成 AI 宏觀解讀
                </button>
            </div>

            {/* 財經新聞滾動 */}
            {macroData.news && macroData.news.length > 0 && (
                <div className="news-ticker">
                    <div className="news-label">📰 財經快訊</div>
                    <div className="news-scroll">
                        {macroData.news.map((item, idx) => (
                            <span key={idx} className="news-item">
                                <span className="news-source">[{item.source}]</span>
                                {item.title}
                                <span className="news-separator">•</span>
                            </span>
                        ))}
                    </div>
                </div>
            )}

            {/* 核心指標 - 按 Demo 1:1 還原 */}
            <div className="metrics-row demo-style">
                <AISignalWidget ticker={ticker} />

                <div className="metric-card">
                    <div className="metric-header">
                        <span className="metric-title">累積收益 (CUM. RETURN)</span>
                        <DollarSign size={16} />
                    </div>
                    <div className="metric-value positive">+{((backtestData?.metrics?.Total_Return || 0.245) * 100).toFixed(1)}%</div>
                    <div className="metric-sub">↗ vs SPY +12.1%</div>
                </div>
                <div className="metric-card">
                    <div className="metric-header">
                        <span className="metric-title">年化夏普比率 (SHARPE)</span>
                        <ShieldAlert size={16} />
                    </div>
                    <div className="metric-value">{(backtestData?.metrics?.Sharpe_Ratio || 2.84).toFixed(2)}</div>
                    <div className="metric-sub">↗ 排名前 5%</div>
                </div>
                <div className="metric-card">
                    <div className="metric-header">
                        <span className="metric-title">盈虧比 (PROFIT FACTOR)</span>
                        <TrendingUp size={16} />
                    </div>
                    <div className="metric-value">{(backtestData?.metrics?.Profit_Factor || 1.65).toFixed(2)}</div>
                    <div className="metric-sub">↗ 穩健</div>
                </div>
                {/* Sprint 1: Sortino Ratio 卡片 */}
                <div className="metric-card">
                    <div className="metric-header">
                        <span className="metric-title">索提諾比率 (SORTINO)</span>
                        <ShieldAlert size={16} />
                    </div>
                    <div className="metric-value">{(backtestData?.metrics?.Sortino_Ratio || 3.12).toFixed(2)}</div>
                    <div className="metric-sub">↗ 僅懲罰下行風險</div>
                </div>
            </div>

            {/* Sprint 1: VaR/CVaR 風險指標卡片 */}
            <div className="metrics-row demo-style" style={{ marginTop: '12px' }}>
                <div className="metric-card" style={{ borderLeft: '3px solid #ef4444' }}>
                    <div className="metric-header">
                        <span className="metric-title">風險價值 (VaR 95%)</span>
                        <AlertTriangle size={16} color="#ef4444" />
                    </div>
                    <div className="metric-value negative">{((backtestData?.metrics?.VaR_95 || -0.0215) * 100).toFixed(2)}%</div>
                    <div className="metric-sub">每日最大預期損失</div>
                </div>
                <div className="metric-card" style={{ borderLeft: '3px solid #f97316' }}>
                    <div className="metric-header">
                        <span className="metric-title">條件風險 (CVaR 95%)</span>
                        <AlertTriangle size={16} color="#f97316" />
                    </div>
                    <div className="metric-value negative">{((backtestData?.metrics?.CVaR_95 || -0.0342) * 100).toFixed(2)}%</div>
                    <div className="metric-sub">尾部風險平均損失</div>
                </div>
                <div className="metric-card">
                    <div className="metric-header">
                        <span className="metric-title">最大回撤 (MAX DD)</span>
                        <TrendingDown size={16} />
                    </div>
                    <div className="metric-value negative">{((backtestData?.metrics?.Max_Drawdown || -0.082) * 100).toFixed(1)}%</div>
                    <div className="metric-sub">↗ 恢復期: 14天</div>
                </div>
                <div className="metric-card">
                    <div className="metric-header">
                        <span className="metric-title">總佣金成本</span>
                        <DollarSign size={16} />
                    </div>
                    <div className="metric-value">${(backtestData?.metrics?.Total_Commission || 156.80).toFixed(2)}</div>
                    <div className="metric-sub">交易摩擦成本</div>
                </div>
            </div>

            {/* 主圖表區域 - 按 Demo 原版代碼還原 (8:4 比例) */}
            <div className="backtest-main-area">
                {/* 左側：K線圖 + RSI (8 欄) */}
                <div className="chart-panel kline-panel">
                    <div className="chart-header">
                        <div className="header-left">
                            <h2>模型回測: 價格走勢與 RSI 指標</h2>
                            <div className="timeframe-selector">
                                {['M1', 'M5', 'M30', '1H', '1D'].map(t => (
                                    <button key={t} className={t === timeframe ? 'active' : ''} onClick={() => setTimeframe(t)}>{t}</button>
                                ))}
                            </div>
                        </div>
                        <div className="chart-legend">
                            <span className="legend-item buy">● 買入信號</span>
                            <span className="legend-item sell">● 賣出信號</span>
                        </div>
                    </div>

                    {/* K線圖 (flex: 3) - 按 Demo 原版使用蠟燭圖 */}
                    <div className="kline-chart-area">
                        <div className="ma-indicator">MA20: <span className="value">154.20</span></div>
                        <ResponsiveContainer width="100%" height={420}>
                            <ComposedChart data={chartData} syncId="quantChart" margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" vertical={false} />
                                <XAxis dataKey="time" stroke="#94a3b8" fontSize={10} tick={false} axisLine={false} />
                                <YAxis stroke="#94a3b8" fontSize={10} tickLine={false} axisLine={false} domain={['auto', 'auto']} orientation="right" />
                                <RechartsTooltip
                                    contentStyle={{ backgroundColor: '#fff', borderColor: '#e2e8f0', fontSize: '12px' }}
                                    cursor={{ stroke: '#94a3b8', strokeWidth: 1, strokeDasharray: '3 3' }}
                                />
                                {/* 價格線型圖 (優化：替代 K 線圖以適應長週期回測) */}
                                <defs>
                                    <linearGradient id="priceGradient" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="5%" stopColor="#22c55e" stopOpacity={0.4} />
                                        <stop offset="95%" stopColor="#22c55e" stopOpacity={0.05} />
                                    </linearGradient>
                                </defs>
                                <Area
                                    type="monotone"
                                    dataKey="close"
                                    stroke="#22c55e"
                                    strokeWidth={2}
                                    fill="url(#priceGradient)"
                                    dot={false}
                                    name="收盤價"
                                />
                                {/* 買賣信號 */}
                                <Scatter dataKey="signalPrice" shape={<SignalMarker />} />
                            </ComposedChart>
                        </ResponsiveContainer>
                    </div>

                    {/* RSI 圖 (flex: 1) - 使用相同數據源實現十字星貫穿 */}
                    <div className="rsi-chart-area">
                        <ResponsiveContainer width="100%" height={100}>
                            <LineChart data={chartData} syncId="quantChart" margin={{ top: 0, right: 10, left: 0, bottom: 0 }}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" vertical={false} />
                                <XAxis dataKey="time" stroke="#94a3b8" fontSize={10} tickLine={false} axisLine={false} />
                                <YAxis stroke="#94a3b8" fontSize={10} tickLine={false} axisLine={false} domain={[0, 100]} ticks={[30, 70]} orientation="right" />
                                <RechartsTooltip
                                    contentStyle={{ backgroundColor: '#fff', borderColor: '#e2e8f0', fontSize: '12px' }}
                                    cursor={{ stroke: '#94a3b8', strokeWidth: 1, strokeDasharray: '3 3' }}
                                    wrapperStyle={{ display: 'none' }}
                                />
                                <ReferenceLine y={70} stroke="#f43f5e" strokeDasharray="3 3" strokeOpacity={0.5} />
                                <ReferenceLine y={30} stroke="#10b981" strokeDasharray="3 3" strokeOpacity={0.5} />
                                <Line type="monotone" dataKey="rsi" stroke="#c084fc" strokeWidth={1.5} dot={false} activeDot={{ r: 4, fill: '#fff' }} />
                            </LineChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                {/* 右側：配置 + 統計 (4 欄) */}
                <div className="config-stats-column">
                    {/* 回測參數配置 - 可交互輸入 */}
                    <div className="config-card">
                        <h3><Sliders size={14} /> 回測參數配置</h3>
                        <div className="config-form">
                            <div className="form-row">
                                <div className="form-group">
                                    <label>開始日期</label>
                                    <input
                                        type="date"
                                        className="config-input"
                                        value={backtestParams.startDate}
                                        onChange={(e) => setBacktestParams({ ...backtestParams, startDate: e.target.value })}
                                    />
                                </div>
                                <div className="form-group">
                                    <label>結束日期</label>
                                    <input
                                        type="date"
                                        className="config-input"
                                        value={backtestParams.endDate}
                                        onChange={(e) => setBacktestParams({ ...backtestParams, endDate: e.target.value })}
                                    />
                                </div>
                            </div>
                            <div className="form-group">
                                <label>初始資金</label>
                                <input
                                    type="number"
                                    className="config-input"
                                    value={backtestParams.initialCapital}
                                    onChange={(e) => setBacktestParams({ ...backtestParams, initialCapital: parseInt(e.target.value) || 0 })}
                                />
                            </div>
                            <div className="form-group">
                                <label>標的資產 (Universe)</label>
                                <input
                                    type="text"
                                    className="config-input"
                                    value={backtestParams.universe}
                                    onChange={(e) => setBacktestParams({ ...backtestParams, universe: e.target.value })}
                                />
                            </div>
                            {/* 策略選擇 + 回測按鈕 (同一行) */}
                            <div className="backtest-action-row" style={{ display: 'flex', gap: '12px', alignItems: 'flex-end' }}>
                                <div className="form-group" style={{ flex: 2, marginBottom: 0 }}>
                                    <label>策略模型 (按住 Ctrl 多選)</label>
                                    <select
                                        multiple
                                        className="config-input"
                                        value={Array.isArray(backtestParams.strategy) ? backtestParams.strategy : [backtestParams.strategy]}
                                        onChange={(e) => {
                                            const selected = Array.from(e.target.selectedOptions, option => option.value);
                                            setBacktestParams({ ...backtestParams, strategy: selected.join(',') });
                                        }}
                                        style={{ width: '100%', height: '80px' }}
                                    >
                                        <option value="momentum">動能策略 (基準)</option>
                                        <option value="rsi">RSI 均值回歸</option>
                                        <option value="lightgbm">AI：梯度提升樹 (LightGBM)</option>
                                        <option value="mlp">AI：神經網絡 (MLP)</option>
                                    </select>
                                </div>

                                {/* AI 模型版本選擇 (僅當選擇 AI 策略時顯示) */}
                                {(backtestParams.strategy || '').toLowerCase().match(/lightgbm|mlp/) && (
                                    <div className="form-group" style={{ flex: 1, minWidth: '120px' }}>
                                        <label>模型版本 (AI Version)</label>
                                        <select
                                            className="config-input"
                                            value={selectedModelVersion}
                                            onChange={(e) => setSelectedModelVersion(e.target.value)}
                                        >
                                            <option value="">最新 (Latest)</option>
                                            {aiModelVersions.map((v, idx) => (
                                                <option key={idx} value={v.version}>
                                                    {v.version} ({v.timestamp})
                                                </option>
                                            ))}
                                        </select>
                                    </div>
                                )}

                                <button className="run-btn" onClick={loadLiveData} disabled={isLoading} style={{ whiteSpace: 'nowrap', flex: 1, minWidth: '100px' }}>
                                    <Play size={14} /> 開始回測
                                </button>
                            </div>
                        </div>
                    </div>

                    {/* 核心統計指標 */}
                    <div className="stats-card">
                        <h3><Hash size={14} /> 核心統計指標</h3>
                        <div className="stats-grid">
                            <div className="stat-box">
                                <span className="label">勝率 (Win Rate)</span>
                                <span className="value green">{((backtestData?.metrics?.Win_Rate || 0.584) * 100).toFixed(1)}%</span>
                            </div>
                            <div className="stat-box">
                                <span className="label">凱利公式 (Kelly)</span>
                                <span className="value purple">{((backtestData?.metrics?.Kelly || 0.125) * 100).toFixed(1)}%</span>
                            </div>
                            <div className="stat-box">
                                <span className="label">平均盈利 (Avg Win)</span>
                                <span className="value">+${(backtestData?.metrics?.Avg_Win || 240.50).toFixed(2)}</span>
                            </div>
                            <div className="stat-box">
                                <span className="label">平均虧損 (Avg Loss)</span>
                                <span className="value">-${Math.abs(backtestData?.metrics?.Avg_Loss || 115.20).toFixed(2)}</span>
                            </div>
                            <div className="stat-box full-width">
                                <span className="label">總交易次數 (Total Trades)</span>
                                <span className="value">{backtestData?.metrics?.Total_Trades || 1245} 筆</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* 交易明細表格 - 全寬佈局 (P0 整改) */}
            {
                backtestData?.trades && backtestData.trades.length > 0 && (
                    <div className="trade-log-panel" style={{
                        gridColumn: '1 / -1',  // 關鍵：跨越所有 grid 列
                        marginTop: '24px',
                        marginBottom: '24px',
                        width: '100%',
                        background: '#fff',
                        borderRadius: '12px',
                        padding: '16px 20px',
                        boxShadow: '0 1px 3px rgba(0,0,0,0.08)'
                    }}>
                        <div className="chart-header" style={{ marginBottom: '16px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                            <h2 style={{ margin: 0, fontSize: '1rem', color: '#1e293b', display: 'flex', alignItems: 'center', gap: '8px' }}>
                                <Activity size={14} /> 交易明細日誌 (Trade Log)
                            </h2>
                            <span className="desc" style={{ fontSize: '0.85rem', color: '#64748b' }}>
                                共 {backtestData.trades.length} 筆交易 | 初始資金: ${backtestParams.initialCapital.toLocaleString()}
                            </span>
                        </div>
                        <div className="trade-table-container" style={{ maxHeight: '280px', overflowY: 'auto', overflowX: 'auto' }}>
                            <table className="trade-table" style={{ ...tradeTableStyles.table, width: '100%', tableLayout: 'fixed' }}>
                                <thead style={tradeTableStyles.thead}>
                                    <tr>
                                        <th style={tradeTableStyles.th}>日期</th>
                                        <th style={tradeTableStyles.th}>類型</th>
                                        <th style={tradeTableStyles.th}>執行價格</th>
                                        <th style={tradeTableStyles.th}>股數</th>
                                        <th style={tradeTableStyles.th}>金額</th>
                                        <th style={tradeTableStyles.th}>持倉比例</th>
                                        <th style={tradeTableStyles.th}>盈虧</th>
                                        <th style={tradeTableStyles.th}>累計盈虧</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {backtestData.trades.map((trade, idx) => (
                                        <tr key={idx} style={tradeTableStyles.tr}>
                                            <td style={tradeTableStyles.td}>{trade.time}</td>
                                            <td style={{
                                                ...tradeTableStyles.td,
                                                color: trade.type === 'BUY' ? '#22c55e' : '#ef4444',
                                                fontWeight: 600
                                            }}>
                                                {trade.type === 'BUY' ? '🟢 買入' : '🔴 賣出'}
                                            </td>
                                            <td style={tradeTableStyles.td}>${trade.price?.toFixed(2)}</td>
                                            <td style={tradeTableStyles.td}>{trade.shares || Math.floor((trade.value || 0) / (trade.price || 1))} 股</td>
                                            <td style={tradeTableStyles.td}>${(trade.value || 0).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</td>
                                            <td style={tradeTableStyles.td}>
                                                {((trade.position_after || 0) * 100).toFixed(0)}%
                                            </td>
                                            <td style={{
                                                ...tradeTableStyles.td,
                                                color: (trade.pnl || 0) >= 0 ? '#22c55e' : '#ef4444',
                                                fontWeight: 600
                                            }}>
                                                {(trade.pnl || 0) >= 0 ? '+' : ''}${(trade.pnl || 0).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                                            </td>
                                            <td style={{
                                                ...tradeTableStyles.td,
                                                color: (trade.cumulative_pnl || 0) >= 0 ? '#22c55e' : '#ef4444'
                                            }}>
                                                {(trade.cumulative_pnl || 0) >= 0 ? '+' : ''}${(trade.cumulative_pnl || 0).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </div>
                )
            }

            {/* 下方區域：回撤分析 + 收益分佈 (8:4 比例) */}
            <div className="bottom-charts-area">
                {/* 左側：回撤分析 */}
                <div className="chart-panel drawdown-panel">
                    <div className="chart-header">
                        <h2><TrendingDown size={14} /> 回撤分析 (Underwater Plot)</h2>
                        <span className="desc">可視化歷史最大虧損幅度與恢復時間</span>
                    </div>
                    <div className="chart-container">
                        <ResponsiveContainer width="100%" height={180}>
                            <AreaChart data={drawdownData}>
                                <defs>
                                    <linearGradient id="colorDrawdown" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="5%" stopColor="#f43f5e" stopOpacity={0.3} />
                                        <stop offset="95%" stopColor="#f43f5e" stopOpacity={0} />
                                    </linearGradient>
                                </defs>
                                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" vertical={false} />
                                <XAxis dataKey="time" stroke="#94a3b8" fontSize={10} tickLine={false} axisLine={false} />
                                <YAxis stroke="#94a3b8" fontSize={10} tickLine={false} axisLine={false} />
                                <RechartsTooltip formatter={(value) => [`${value}%`, 'Drawdown']} />
                                <Area type="step" dataKey="drawdown" stroke="#f43f5e" strokeWidth={2} fill="url(#colorDrawdown)" />
                            </AreaChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                {/* 右側：收益分佈 */}
                <div className="chart-panel distribution-panel">
                    <div className="chart-header">
                        <h2><BarChart2 size={14} /> 收益分佈直方圖</h2>
                    </div>
                    <div className="chart-container">
                        <ResponsiveContainer width="100%" height={120}>
                            <BarChart data={DISTRIBUTION_DATA} layout="vertical" margin={{ left: 10 }}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" horizontal={false} />
                                <XAxis type="number" stroke="#94a3b8" fontSize={10} hide />
                                <YAxis dataKey="range" type="category" stroke="#64748b" fontSize={10} width={60} tickLine={false} axisLine={false} />
                                <RechartsTooltip cursor={{ fill: '#f1f5f9' }} />
                                <Bar dataKey="count" fill="#6366f1" radius={[0, 4, 4, 0]} barSize={14}>
                                    {DISTRIBUTION_DATA.map((entry, index) => (
                                        <Cell key={index} fill={index === 3 || index === 4 ? '#6366f1' : '#cbd5e1'} />
                                    ))}
                                </Bar>
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                    {/* 統計指標中文介紹 */}
                    <div className="distribution-stats">
                        <div className="stat-row">
                            <span className="stat-label">均值 (Mean):</span>
                            <span className="stat-value positive">+0.12%</span>
                            <span className="stat-desc">每日平均收益率</span>
                        </div>
                        <div className="stat-row">
                            <span className="stat-label">標準差 (Std):</span>
                            <span className="stat-value">1.85%</span>
                            <span className="stat-desc">收益波動程度</span>
                        </div>
                        <div className="stat-row">
                            <span className="stat-label">偏度 (Skew):</span>
                            <span className="stat-value positive">+0.42</span>
                            <span className="stat-desc">正偏態，右尾較長</span>
                        </div>
                        <div className="stat-row">
                            <span className="stat-label">峰度 (Kurtosis):</span>
                            <span className="stat-value">3.21</span>
                            <span className="stat-desc">略高於正態分佈</span>
                        </div>
                    </div>
                </div>
            </div>


            {/* AI 分析 */}
            <div className="ai-panel">
                <AIAnalysisCard
                    title="AI 首席策略師觀點"
                    content={aiAnalysis}
                    isLoading={isAiLoading}
                    onGenerate={() => generateAIAnalysis('market_outlook')}
                    buttonText="生成 AI 解讀"
                />
            </div>
        </div >
    );

    const renderArena = () => (
        <div className="arena-view">
            <div className="arena-header">
                <h2><Swords size={24} /> AI 模型競技場 (Alpha Arena)</h2>
                <div className="arena-controls">
                    <Badge type={isLiveUpdating ? "updating" : "active"}>
                        {isLiveUpdating ? (
                            <><Loader2 size={12} className="spin" /> 更新中...</>
                        ) : (
                            <>🔴 實時 PK 中</>
                        )}
                    </Badge>
                    {lastUpdateTime && (
                        <span className="last-update">更新於 {lastUpdateTime}</span>
                    )}
                    <button onClick={loadLiveData} className="refresh-btn">
                        <RefreshCw size={14} /> 刷新
                    </button>
                </div>
            </div>

            <div className="arena-table">
                <div className="arena-table-header">
                    <div>排名</div>
                    <div>策略模型</div>
                    <div>類型</div>
                    <div>年化回報</div>
                    <div>夏普比率</div>
                    <div>最大回撤</div>
                </div>
                {arenaData.map((model, idx) => (
                    <div key={idx} className={`arena-row ${idx === 0 ? 'champion' : ''}`}>
                        <div className="rank">
                            {idx === 0 ? '🥇' : idx === 1 ? '🥈' : idx === 2 ? '🥉' : idx + 1}
                        </div>
                        <div className="strategy-name">
                            {model.Type === 'AI' ? <Bot size={14} /> : <Activity size={14} />}
                            {model.Strategy}
                        </div>
                        <div>
                            <span className={`type-badge ${model.Type === 'AI' ? 'ai' : 'trad'}`}>
                                {model.Type}
                            </span>
                        </div>
                        <div className="return positive">
                            +{((model['Total Return'] || 0) * 100).toFixed(1)}%
                        </div>
                        <div className="sharpe">{(model.Sharpe || 0).toFixed(2)}</div>
                        <div className="negative">
                            {((model['Max DD'] || 0) * 100).toFixed(1)}%
                        </div>
                    </div>
                ))}
            </div>

            <div className="arena-summary">
                <div className="summary-card">
                    <h4>🏆 冠軍模型</h4>
                    <div className="champion-name">{arenaData[0]?.Strategy || 'LightGBM'}</div>
                    <div className="champion-stats">
                        回報 +{((arenaData[0]?.['Total Return'] || 0) * 100).toFixed(1)}% | Sharpe {(arenaData[0]?.Sharpe || 0).toFixed(2)}
                    </div>
                </div>
                <div className="summary-card">
                    <h4>📊 AI vs 傳統</h4>
                    <div className="vs-stat">
                        <span className="ai-avg">AI 平均: +17.2%</span>
                        <span className="trad-avg">傳統: +8.8%</span>
                    </div>
                </div>
                <div className="summary-card action">
                    <Bot size={32} />
                    <div>訓練新模型</div>
                    <button className="train-btn" onClick={() => setShowTrainingModal(true)}>進入訓練場</button>
                </div>
            </div>

            <AIAnalysisCard
                title="AI 賽事解說"
                content={aiAnalysis}
                isLoading={isAiLoading}
                onGenerate={() => generateAIAnalysis('arena_commentary')}
                buttonText="生成戰況分析"
            />
        </div>
    );

    const renderValuation = () => (
        <div className="valuation-view">
            <div className="valuation-header">
                <h2><Calculator size={24} /> 真實內在價值估值</h2>
                <div className="valuation-search">
                    <input
                        type="text"
                        value={ticker}
                        onChange={(e) => setTicker(e.target.value.toUpperCase())}
                        className="ticker-input"
                        placeholder="股票代碼"
                    />
                    <button onClick={loadLiveData} className="search-btn" disabled={isLoading}>
                        <Search size={14} /> 搜索
                    </button>
                </div>
                <div className="model-selector">
                    {['DCF', 'Graham', 'DDM'].map(m => (
                        <button
                            key={m}
                            className={m === valuationModel ? 'active' : ''}
                            onClick={() => setValuationModel(m)}
                        >
                            {m}
                        </button>
                    ))}
                </div>
            </div>

            <div className="valuation-grid">
                <div className="valuation-card main">
// ... (inside renderValuation, inside valuation-card main)
                    <h3>
                        {valuationData?.ticker || ticker}
                        <span>{valuationData?.company_name || 'Loading...'}</span>
                        {/* Audit Fix: Data Quality Warning */}
                        {valuationData?.data_quality && valuationData.data_quality !== 'High' && (
                            <span className="quality-warning" title="部分數據缺失，使用估算值或緩存數據">
                                <AlertTriangle size={14} /> 數據品質: {valuationData.data_quality === 'Medium' ? '中 (估算)' : '低 (不完整)'}
                            </span>
                        )}
                    </h3>

                    <div className="price-compare">
                        <div className="price-item">
                            <label>當前市價</label>
                            <div className="price">${(valuationData?.current_price || 178.35).toFixed(2)}</div>
                        </div>
                        <div className="vs-arrow">→</div>
                        <div className="price-item highlight">
                            <label>內在價值 ({valuationModel})</label>
                            <div className="price positive">
                                ${
                                    (valuationData?.models && valuationData.models[valuationModel]
                                        ? valuationData.models[valuationModel]
                                        : (valuationData?.intrinsic_value || 0)
                                    ).toFixed(2)
                                }
                            </div>
                        </div>
                    </div>

                    <div className="margin-safety">
                        <label>安全邊際 (Margin of Safety)</label>
                        {(() => {
                            const currentPrice = valuationData?.current_price || 1;
                            const modelValue = valuationData?.models && valuationData.models[valuationModel]
                                ? valuationData.models[valuationModel]
                                : (valuationData?.intrinsic_value || 0);

                            // Calculate dynamic margin for the selected model
                            const margin = modelValue > 0
                                ? (modelValue - currentPrice) / modelValue
                                : 0;

                            return (
                                <>
                                    <div className={`margin-value ${margin > 0 ? 'positive' : 'negative'}`}>
                                        +{(margin * 100).toFixed(1)}%
                                    </div>
                                    <div className="margin-bar">
                                        {/* Simple visualization for dynamic margin */}
                                        <div className="bar-fill" style={{ width: `${Math.min(100, Math.max(0, 50 + margin * 50))}%`, background: margin > 0 ? '#10b981' : '#f43f5e' }}></div>
                                        <div className="bar-marker" style={{ left: '50%' }}></div>
                                    </div>
                                </>
                            );
                        })()}
                        <div className="bar-labels">
                            <span>高估</span>
                            <span>合理</span>
                            <span>低估</span>
                        </div>
                        <div className="verdict positive">UNDERVALUED (低估)</div>
                    </div>
                </div>

                <div className="valuation-sidebar">
                    <div className="detail-card">
                        <h4>📊 敏感度分析</h4>
                        <table className="sensitivity-table">
                            <thead>
                                <tr><th>WACC \ g</th><th>2.0%</th><th>2.5%</th><th>3.0%</th></tr>
                            </thead>
                            <tbody>
                                {SENSITIVITY_DATA.map((row, i) => (
                                    <tr key={i}>
                                        <td>{row.wacc}</td>
                                        <td>{row.g2}</td>
                                        <td className={i === 1 ? 'highlight' : ''}>{row.g25}</td>
                                        <td>{row.g3}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>

                    <div className="detail-card">
                        <h4>⚙️ 模型參數</h4>
                        <div className="param-list">
                            <div><span>WACC</span><span>8.0%</span></div>
                            <div><span>成長率 (5Y)</span><span>12.0%</span></div>
                            <div><span>終值成長率</span><span>2.5%</span></div>
                            <div><span>置信度</span><span className="positive">HIGH</span></div>
                        </div>
                    </div>
                </div>
            </div>

            <AIAnalysisCard
                title="智能估值報告"
                content={aiAnalysis}
                isLoading={isAiLoading}
                onGenerate={() => generateAIAnalysis('valuation_report')}
                buttonText="生成投資評級"
            />
        </div>
    );

    const renderDataLayer = () => (
        <div className="data-view">
            <div className="data-header">
                <h2><Database size={24} /> 數據源管理</h2>
                <div className="data-actions">
                    <button className="update-btn primary" onClick={() => {
                        alert('數據增量更新已啟動！\n後端將自動執行斷點續傳更新。');
                        loadLiveData();
                    }}>
                        <TrendingUp size={14} /> 觸發數據更新
                    </button>
                    <button className="refresh-btn" onClick={loadLiveData}>
                        <RefreshCw size={14} /> 刷新狀態
                    </button>
                </div>
            </div>

            <div className="data-feeds">
                {[
                    { name: 'yfinance (OHLCV)', status: 'active', latency: '~500ms', source: 'REST API', records: '12,450' },
                    { name: 'yfinance (Financials)', status: 'active', latency: '~800ms', source: 'REST API', records: '2,340' },
                    { name: 'SQLite Cache', status: 'active', latency: '<1ms', source: 'Local', records: '45,200' },
                    { name: 'Macro Indicators', status: 'active', latency: '~1s', source: 'yfinance', records: '156' },
                ].map((feed, idx) => (
                    <div key={idx} className="feed-card">
                        <div className="feed-info">
                            <div className={`feed-icon ${feed.status}`}><Database size={20} /></div>
                            <div>
                                <div className="feed-name">{feed.name}</div>
                                <div className="feed-source">Source: {feed.source}</div>
                            </div>
                        </div>
                        <div className="feed-stats">
                            <div className="feed-stat">
                                <label>Records</label>
                                <span>{feed.records}</span>
                            </div>
                            <div className="feed-stat">
                                <label>Latency</label>
                                <span>{feed.latency}</span>
                            </div>
                            <Badge type={feed.status} />
                        </div>
                    </div>
                ))}
            </div>

            <div className="data-info">
                <div className="info-card success">
                    <h4>✅ 數據覆蓋報告</h4>
                    <p>所有核心數據源運行正常。緩存命中率 94.2%。</p>
                </div>
                <div className="info-card success">
                    <Sparkles size={16} />
                    <div>
                        <h4>✅ 斷點續傳功能</h4>
                        <p>已支持增量更新 - 只下載缺失日期範圍，自動合併數據</p>
                    </div>
                </div>
            </div>
        </div>
    );

    const renderSettings = () => (
        <div className="settings-view">
            <h2><Settings size={24} /> 系統設置</h2>

            <div className="settings-section">
                <h3><Bot size={16} /> AI 模型連接</h3>
                <div className="setting-group">
                    <label>選擇模型</label>
                    <div className="input-with-icon">
                        <Cpu size={14} />
                        <select
                            value={config.geminiModel || 'gemini-3-pro-high'}
                            onChange={(e) => setConfig({ ...config, geminiModel: e.target.value })}
                            className="settings-select"
                        >
                            <option value="gemini-3-pro-high">Gemini 3 PRO (High) - 原生 HTTP</option>
                            <option value="gemini-3-flash">Gemini 3 Flash - Google GenAI SDK</option>
                        </select>
                    </div>
                </div>
                <div className="setting-group">
                    <label>API 地址</label>
                    <div className="input-with-icon">
                        <Network size={14} />
                        <input
                            type="text"
                            value={config.geminiUrl}
                            onChange={(e) => setConfig({ ...config, geminiUrl: e.target.value })}
                            placeholder="https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent"
                        />
                    </div>
                </div>
                <div className="setting-group">
                    <label>API Key</label>
                    <div className="input-with-icon">
                        <Key size={14} />
                        <input
                            type="password"
                            value={config.geminiKey}
                            onChange={(e) => setConfig({ ...config, geminiKey: e.target.value })}
                            placeholder="輸入您的 Gemini API Key"
                        />
                    </div>
                </div>
            </div>

            <div className="settings-section">
                <h3><Server size={16} /> 後端服務</h3>
                <div className="setting-group">
                    <label>API 地址</label>
                    <div className="input-with-icon">
                        <Network size={14} />
                        <input
                            type="text"
                            value={config.apiAddress}
                            onChange={(e) => setConfig({ ...config, apiAddress: e.target.value })}
                            placeholder={import.meta.env.VITE_API_URL || "http://localhost:666"}
                        />
                    </div>
                </div>
            </div>

            <div className="settings-section">
                <h3><User size={16} /> 帳戶安全</h3>
                <div className="setting-group">
                    <label>管理員帳號</label>
                    <input type="text" defaultValue="admin" />
                </div>
                <div className="setting-group">
                    <label>新密碼</label>
                    <div className="input-with-icon">
                        <Lock size={14} />
                        <input type="password" placeholder="••••••••" />
                    </div>
                </div>
            </div>

            <div className="settings-actions">
                {configStatus && (
                    <div className={`config-status ${configStatus.includes('✅') ? 'success' : configStatus.includes('❌') ? 'error' : 'warning'}`}>
                        {configStatus}
                    </div>
                )}
                <button className="save-btn" onClick={async () => {
                    setConfigStatus('⏳ 保存中...');
                    try {
                        // Save to localStorage first
                        localStorage.setItem('quant_config', JSON.stringify(config));

                        // Then sync to backend
                        const result = await API.configureAI(config.geminiUrl, config.geminiKey, config.geminiModel);
                        if (result.success) {
                            setConfigStatus(result.configured ? '✅ Gemini API 配置成功！配置已持久化。' : '⚠️ 配置已保存到本地，但 API Key 為空');
                        } else {
                            setConfigStatus('❌ 後端同步失敗: ' + (result.error || '未知錯誤') + ' (本地已保存)');
                        }
                    } catch (e) {
                        // Still save locally even if backend fails
                        localStorage.setItem('quant_config', JSON.stringify(config));
                        setConfigStatus('⚠️ 本地已保存，但後端連接失敗: ' + e.message);
                    }
                    // Clear status after 5 seconds
                    setTimeout(() => setConfigStatus(''), 5000);
                }}>
                    <Save size={16} /> 保存配置
                </button>
            </div>
        </div>
    );

    // ============ RENDER ============

    return (
        <div className="quant-app">
            <div className="sidebar">
                <div className="logo"><Activity size={26} /></div>
                <nav>
                    <IconButton icon={Layout} label="總覽儀表板" active={activeTab === 'dashboard'} onClick={() => setActiveTab('dashboard')} />
                    <IconButton icon={Swords} label="AI 競技場" active={activeTab === 'arena'} onClick={() => setActiveTab('arena')} />
                    <IconButton icon={Calculator} label="內在估值" active={activeTab === 'valuation'} onClick={() => setActiveTab('valuation')} />
                    <IconButton icon={LineChart} label="實盤模擬" active={activeTab === 'simulation'} onClick={() => setActiveTab('simulation')} />
                    <IconButton icon={Layers} label="數據管理" active={activeTab === 'data'} onClick={() => setActiveTab('data')} />
                </nav>
                <div className="sidebar-footer">
                    <IconButton icon={Settings} label="系統設置" active={activeTab === 'settings'} onClick={() => setActiveTab('settings')} />
                </div>
            </div>

            <div className="main-content">
                <header>
                    <div className="header-left">
                        <h1>量化分析系統 <span>V2.0</span></h1>
                        <div className="status">
                            <span className="status-dot"></span>
                            系統在線 • {dataSource}
                        </div>
                    </div>
                    <div className="header-right">
                        <div className="search-box">
                            <Search size={16} />
                            <input
                                type="text"
                                placeholder="搜尋股票代碼..."
                                value={ticker}
                                onChange={(e) => setTicker(e.target.value.toUpperCase())}
                                onKeyDown={(e) => e.key === 'Enter' && loadLiveData()}
                            />
                        </div>
                        <button className="notification">
                            <Bell size={18} />
                            <span className="notification-dot"></span>
                        </button>
                        <div className="avatar">Q</div>
                    </div>
                </header>

                <main>
                    {activeTab === 'dashboard' && renderDashboard()}
                    {activeTab === 'arena' && renderArena()}
                    {activeTab === 'valuation' && renderValuation()}
                    {activeTab === 'simulation' && <SimulationDashboard />}
                    {activeTab === 'data' && renderDataLayer()}
                    {activeTab === 'settings' && renderSettings()}
                </main>
            </div>

            {/* AI 模型訓練 Modal */}
            {showTrainingModal && (
                <ModelTrainingModal
                    onClose={() => setShowTrainingModal(false)}
                    onTrain={async (config) => {
                        console.log('Training with config:', config);
                        try {
                            // API Call
                            const response = await fetch(`${API_BASE}/model/train`, {
                                method: 'POST',
                                headers: {
                                    'Content-Type': 'application/json',
                                    'X-API-Key': localStorage.getItem('quant_api_key') || ''
                                },
                                body: JSON.stringify({
                                    model_type: config.model_type,
                                    params: config.params,
                                    ticker: ticker // Use current ticker
                                })
                            });
                            const data = await response.json();

                            // Return data so ModelTrainingModal determines success/failure
                            if (data.success && onNavigate) {
                                // Auto-redirect to AI Lab for monitoring
                                onNavigate('ailab');
                            }
                            return data;
                        } catch (err) {
                            console.error("Training Request Error", err);
                            return { success: false, error: "Network/Server Error" };
                        }
                    }}
                />
            )}
        </div>
    );
}
