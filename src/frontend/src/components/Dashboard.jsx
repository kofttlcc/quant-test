
import React, { useState, useEffect } from 'react';
import { API } from '../services/api';
import { TradingChart } from './TradingChart';
import { ArenaView } from './ArenaView';

const CN_MAP = {
    "Bull": "牛市",
    "Bear": "熊市",
    "Volatile": "震盪",
    "Unknown": "未知",
    "Undervalued (Strong)": "嚴重低估",
    "Undervalued": "低估",
    "Overvalued": "高估",
    "Fair Value": "合理",
    "Elevated": "風險升高",
    "Critical": "極度危險",
    "Low Risk": "低風險"
};

const t = (text) => CN_MAP[text] || text;

export const Dashboard = () => {
    const [ticker, setTicker] = useState('AAPL');
    const [strategy, setStrategy] = useState('momentum');
    const [loading, setLoading] = useState(false);

    // Sprint 3: 回測時間選擇
    const [startDate, setStartDate] = useState('2024-01-01');
    const [endDate, setEndDate] = useState(new Date().toISOString().split('T')[0]);

    // Sprint 4: 數據更新狀態
    const [updateProgress, setUpdateProgress] = useState(null);
    const [updateLogs, setUpdateLogs] = useState([]);

    // Data State
    const [analysis, setAnalysis] = useState(null);
    const [valuation, setValuation] = useState(null);
    const [backtest, setBacktest] = useState(null);
    const [arenaResults, setArenaResults] = useState(null);

    // Chart State
    const [chartData, setChartData] = useState([]);
    const [lineData, setLineData] = useState([]);
    const [markers, setMarkers] = useState([]);
    const [trades, setTrades] = useState([]);
    const [rsiData, setRsiData] = useState([]);  // Sprint 3: RSI 數據

    // Sprint 4: 一鍵更新數據
    const handleDataUpdate = async () => {
        setUpdateLogs([{ time: new Date().toLocaleTimeString(), msg: '🚀 開始更新數據...' }]);
        setUpdateProgress({ percentage: 0, status: 'running' });

        try {
            setUpdateLogs(prev => [...prev, { time: new Date().toLocaleTimeString(), msg: '📡 連接後端 API...' }]);

            const result = await API.updateData(['AAPL', 'MSFT', 'GOOGL', 'NVDA']);

            if (result.error) {
                setUpdateLogs(prev => [...prev, { time: new Date().toLocaleTimeString(), msg: `❌ 後端錯誤: ${result.error}` }]);
                setUpdateProgress({ percentage: 0, status: 'failed' });
                return;
            }

            setUpdateProgress({ percentage: result.percentage || 100, status: result.status || 'completed' });
            setUpdateLogs(prev => [...prev,
            { time: new Date().toLocaleTimeString(), msg: `✅ 完成: ${result.completed || 0}/${result.total || 0} 項目` },
            ...(result.errors || []).map(e => ({ time: new Date().toLocaleTimeString(), msg: `⚠️ ${e}` }))
            ]);
        } catch (e) {
            setUpdateLogs(prev => [...prev,
            { time: new Date().toLocaleTimeString(), msg: `❌ 網絡錯誤: ${e.message}` },
            { time: new Date().toLocaleTimeString(), msg: `💡 提示: 請確認後端服務已啟動` }
            ]);
            setUpdateProgress({ percentage: 0, status: 'failed' });
        }
    };

    // S&P 500 全量更新
    const handleSP500Update = async () => {
        const confirmed = window.confirm(
            '⚠️ S&P 500 全量更新\n\n' +
            '這將下載所有 500 只股票的歷史數據 (2008-至今)。\n' +
            '預計耗時：30-60 分鐘\n\n' +
            '確定要開始嗎？'
        );
        if (!confirmed) return;

        setUpdateLogs([{ time: new Date().toLocaleTimeString(), msg: '🚀 啟動 S&P 500 全量更新...' }]);
        setUpdateProgress({ percentage: 0, status: 'running' });

        try {
            // apiAddress removed, relying on proxy or relative path
            const res = await fetch('/api/v1/data/update', {
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ mode: 'sp500' })
            });
            const result = await res.json();

            setUpdateLogs(prev => [...prev,
            { time: new Date().toLocaleTimeString(), msg: `✅ ${result.message || 'S&P 500 更新已啟動'}` },
            { time: new Date().toLocaleTimeString(), msg: '📊 查看進度請刷新頁面...' }
            ]);

            // 開始輪詢進度
            pollProgress();
        } catch (e) {
            setUpdateLogs(prev => [...prev, { time: new Date().toLocaleTimeString(), msg: `❌ 錯誤: ${e.message}` }]);
            setUpdateProgress({ percentage: 0, status: 'failed' });
        }
    };

    // 輪詢進度
    const pollProgress = () => {
        const intervalId = setInterval(async () => {
            try {
                const progress = await API.getUpdateProgress();
                if (progress.status === 'idle' || progress.status === 'completed' || progress.status === 'failed' || progress.status === 'cancelled') {
                    clearInterval(intervalId);
                }
                if (progress.percentage !== undefined) {
                    setUpdateProgress(progress);
                    setUpdateLogs(prev => [...prev.slice(-10), {
                        time: new Date().toLocaleTimeString(),
                        msg: `📊 ${progress.current_ticker || ''} (${progress.percentage?.toFixed(0) || 0}%)`
                    }]);
                }
            } catch (e) {
                // 忽略輪詢錯誤
            }
        }, 3000);
    };

    // Auto Load
    useEffect(() => {
        handleRun();
    }, []);

    const fetchSidePanels = async (sym) => {
        const ana = await API.getAnalysis(sym);
        if (!ana.error) setAnalysis(ana);

        const val = await API.getValuation(sym);
        if (!val.error) setValuation(val);
    };

    const handleRun = async () => {
        setLoading(true);
        try {
            await fetchSidePanels(ticker);

            if (strategy === 'arena') {
                const res = await API.runArena(ticker);
                if (!res.error) {
                    setArenaResults(res.results);
                    setBacktest(null);
                } else {
                    alert(res.error);
                }
            } else {
                const res = await API.runBacktest(ticker, strategy);
                if (!res.error) {
                    setBacktest(res);
                    setArenaResults(null);

                    if (res.ohlcv && Array.isArray(res.ohlcv)) setChartData(res.ohlcv);
                    if (res.dates && res.equity_curve) {
                        const ld = res.dates.map((d, i) => ({ time: d, value: res.equity_curve[i] }));
                        setLineData(ld);
                    }

                    // Process Trades for Markers
                    // Trade: { time, type: "BUY"|"SELL", price }
                    const rawTrades = res.trades || [];
                    setTrades(rawTrades);

                    const chartMarkers = rawTrades.map(tr => ({
                        time: tr.time,
                        position: tr.type === 'BUY' ? 'belowBar' : 'aboveBar',
                        color: tr.type === 'BUY' ? '#00c853' : '#ff3d00',
                        shape: tr.type === 'BUY' ? 'arrowUp' : 'arrowDown',
                        text: tr.type === 'BUY' ? 'B' : 'S'
                    }));
                    setMarkers(chartMarkers);

                    // 計算 RSI 數據 (從 OHLCV 計算) - 改進算法
                    if (res.ohlcv && res.ohlcv.length > 14) {
                        const closes = res.ohlcv.map(c => c.close);
                        const period = 14;
                        const rsiValues = [];

                        // 使用 Wilder 平滑法計算 RSI
                        let avgGain = 0;
                        let avgLoss = 0;

                        for (let i = 0; i < closes.length; i++) {
                            if (i === 0) {
                                rsiValues.push(null);
                                continue;
                            }

                            const change = closes[i] - closes[i - 1];
                            const gain = change > 0 ? change : 0;
                            const loss = change < 0 ? -change : 0;

                            if (i < period) {
                                avgGain += gain / period;
                                avgLoss += loss / period;
                                rsiValues.push(null);
                            } else if (i === period) {
                                avgGain += gain / period;
                                avgLoss += loss / period;
                                const rs = avgLoss === 0 ? 100 : avgGain / avgLoss;
                                rsiValues.push(100 - (100 / (1 + rs)));
                            } else {
                                // Wilder 平滑
                                avgGain = (avgGain * (period - 1) + gain) / period;
                                avgLoss = (avgLoss * (period - 1) + loss) / period;
                                const rs = avgLoss === 0 ? 100 : avgGain / avgLoss;
                                rsiValues.push(100 - (100 / (1 + rs)));
                            }
                        }

                        // 過濾 null 值並構建圖表數據 - Issue 5 FIX: 過濾無效時間
                        const rsiChartData = res.ohlcv
                            .map((c, i) => ({
                                time: c.time,
                                value: rsiValues[i]
                            }))
                            .filter(d => {
                                // 過濾無效數據
                                if (d.value === null || isNaN(d.value)) return false;
                                // 過濾無效時間 (必須是有效的日期字符串)
                                if (!d.time || d.time === 0 || d.time === '0') return false;
                                if (typeof d.time === 'string' && d.time.length < 8) return false;
                                return true;
                            });

                        console.log('RSI Data generated:', rsiChartData.length, 'points');
                        if (rsiChartData.length > 0) {
                            console.log('RSI sample:', rsiChartData[0]);
                        }
                        setRsiData(rsiChartData);
                    }

                } else {
                    alert(res.error);
                }
            }
        } catch (e) {
            console.error(e);
            alert("System Error");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="dashboard-grid">
            <header>
                <div className="logo">Gemini Quant <span style={{ fontSize: '0.6em', opacity: 0.7 }}>Phase 12 (Pro)</span></div>
                <div className="status-pill online">系統連線正常</div>
            </header>

            <aside>
                <div className="card input-group">
                    <label>交易代碼 (Ticker)</label>
                    <input value={ticker} onChange={e => setTicker(e.target.value.toUpperCase())} />
                </div>
                <div className="card input-group">
                    <label>策略選擇 (Strategy)</label>
                    <select value={strategy} onChange={e => setStrategy(e.target.value)}>
                        <option value="momentum">Momentum (動能模型)</option>
                        <option value="tree">LightGBM (AI 樹模型)</option>
                        <option value="rsi">RSI Reversion (均值回歸)</option>
                        <option value="arena">⚔️ 策略競技場</option>
                    </select>
                </div>
                <div className="card input-group">
                    <label>回測起始日期</label>
                    <input type="date" value={startDate} onChange={e => setStartDate(e.target.value)} />
                </div>
                <div className="card input-group">
                    <label>回測結束日期</label>
                    <input type="date" value={endDate} onChange={e => setEndDate(e.target.value)} />
                </div>
                <div style={{ fontSize: '0.8em', color: '#888', marginBottom: '10px', padding: '0 5px' }}>
                    {strategy === 'momentum' && "ℹ️ 捕捉市場趨勢，突破買入。"}
                    {strategy === 'tree' && "ℹ️ LightGBM 樹模型，特徵可解釋。"}
                    {strategy === 'rsi' && "ℹ️ RSI 超賣買入，超買賣出。"}
                    {strategy === 'arena' && "ℹ️ 多策略實時對決，選出最強Alpha。"}
                </div>
                <button className="primary" onClick={handleRun} disabled={loading}>
                    {loading ? "計算中..." : "執行回測"}
                </button>

                {/* Sprint 4: 一鍵更新數據 */}
                <div className="card" style={{ marginTop: '15px' }}>
                    <h3>📊 數據更新</h3>
                    <button
                        className="secondary"
                        onClick={handleDataUpdate}
                        disabled={updateProgress?.status === 'running'}
                        style={{ width: '100%', marginBottom: '8px' }}
                    >
                        {updateProgress?.status === 'running' ? '更新中...' : '🔄 快速更新 (Top 10)'}
                    </button>
                    <button
                        className="primary"
                        onClick={handleSP500Update}
                        disabled={updateProgress?.status === 'running'}
                        style={{ width: '100%', marginBottom: '10px' }}
                    >
                        📈 S&P 500 全量更新 (2008-至今)
                    </button>
                    <div style={{ fontSize: '0.75em', color: '#666', marginBottom: '10px' }}>
                        ⏱️ 全量更新預計 30-60 分鐘
                    </div>

                    {/* 進度條 */}
                    {updateProgress && (
                        <div style={{ marginBottom: '10px' }}>
                            <div style={{
                                background: '#333',
                                borderRadius: '4px',
                                overflow: 'hidden',
                                height: '8px'
                            }}>
                                <div style={{
                                    width: `${updateProgress.percentage || 0}%`,
                                    background: updateProgress.status === 'completed' ? 'var(--success)' : 'var(--primary)',
                                    height: '100%',
                                    transition: 'width 0.3s'
                                }} />
                            </div>
                            <div style={{ fontSize: '0.8em', color: '#888', marginTop: '5px' }}>
                                {updateProgress.percentage?.toFixed(0) || 0}% - {updateProgress.status}
                            </div>
                        </div>
                    )}

                    {/* 日誌輸出 */}
                    {updateLogs.length > 0 && (
                        <div style={{
                            maxHeight: '100px',
                            overflowY: 'auto',
                            fontSize: '0.75em',
                            background: '#111',
                            borderRadius: '4px',
                            fontFamily: 'monospace'
                        }}>
                            {updateLogs.map((log, i) => (
                                <div key={i} style={{ color: log.msg.includes('❌') ? 'var(--danger)' : '#aaa' }}>
                                    [{log.time}] {log.msg}
                                </div>
                            ))}
                        </div>
                    )}
                </div>

                {backtest && backtest.metrics && (
                    <div className="card">
                        <h3>回測績效</h3>
                        <div className="metric-row">
                            <span>總回報率</span>
                            <span className="metric-val" style={{ color: backtest.metrics.Total_Return > 0 ? 'var(--success)' : 'var(--danger)' }}>
                                {(backtest.metrics.Total_Return * 100).toFixed(2)}%
                            </span>
                        </div>
                        <div className="metric-row">
                            <span>夏普比率</span>
                            <span className="metric-val">{backtest.metrics.Sharpe_Ratio.toFixed(2)}</span>
                        </div>
                        <div className="metric-row">
                            <span>交易次數</span>
                            <span className="metric-val">{trades.length}</span>
                        </div>
                    </div>
                )}
            </aside>

            <main className="card" style={{ padding: 0, overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>
                {arenaResults ? (
                    <ArenaView results={arenaResults} />
                ) : (
                    <>
                        <div style={{ flex: 1, position: 'relative' }}>
                            <TradingChart data={chartData} lineData={lineData} markers={markers} rsiData={rsiData} />
                        </div>
                        {/* Trade Log Panel */}
                        <div style={{ height: '150px', borderTop: '1px solid #333', overflowY: 'auto', padding: '10px' }}>
                            <h4 style={{ margin: '0 0 10px 0' }}>交易流水 (Trade Log)</h4>
                            <table style={{ width: '100%', fontSize: '0.85em', textAlign: 'left', borderCollapse: 'collapse' }}>
                                <thead style={{ position: 'sticky', top: 0, background: '#1e1e1e' }}>
                                    <tr>
                                        <th>日期</th>
                                        <th>類型</th>
                                        <th>價格</th>
                                        <th>數量</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {trades.map((t, i) => {
                                        // 格式化日期為 YYYY-MM-DD
                                        const formatDate = (time) => {
                                            if (!time) return '---';
                                            if (typeof time === 'string') {
                                                // 已是字符串格式，直接返回日期部分
                                                return time.split(' ')[0].split('T')[0];
                                            }
                                            if (typeof time === 'number') {
                                                // Unix 時間戳轉換
                                                const d = new Date(time * 1000);
                                                return d.toISOString().split('T')[0];
                                            }
                                            return String(time);
                                        };

                                        return (
                                            <tr key={i} style={{ borderBottom: '1px solid #222' }}>
                                                <td>{formatDate(t.time)}</td>
                                                <td style={{ color: t.type === 'BUY' ? 'var(--success)' : 'var(--danger)' }}>{t.type}</td>
                                                <td>${t.price?.toFixed(2) || '---'}</td>
                                                <td>{t.size?.toFixed(4) || '---'}</td>
                                            </tr>
                                        );
                                    })}
                                </tbody>
                            </table>
                        </div>
                    </>
                )}
            </main>

            <div className="right-panel">
                <div className="card">
                    <h3>真實價值 (Alpha)</h3>
                    {valuation ? (
                        <>
                            <div style={{ fontSize: '2em', fontWeight: 'bold' }}>${valuation.fair_value?.toFixed(2) || '---'}</div>
                            <div style={{ color: valuation.status?.includes('Under') ? 'var(--success)' : 'var(--danger)' }}>
                                {t(valuation.status)}
                            </div>
                            <div style={{ fontSize: '0.8em', marginTop: '10px', color: '#888' }}>
                                DCF: ${valuation.models?.DCF} | Graham: ${valuation.models?.Graham}
                            </div>
                        </>
                    ) : (<div>載入中...</div>)}
                </div>

                <div className="card">
                    <h3>市場狀態 (AI)</h3>
                    {analysis ? (
                        <div className="defcon-widget">
                            <div className="defcon-circle" style={{
                                borderColor: analysis.regime === 'Bull' ? 'var(--success)' : (analysis.regime === 'Bear' ? 'var(--danger)' : 'var(--warning)'),
                                color: analysis.regime === 'Bull' ? 'var(--success)' : (analysis.regime === 'Bear' ? 'var(--danger)' : 'var(--warning)'),
                                boxShadow: `0 0 15px ${analysis.regime === 'Bull' ? '#00c85340' : '#ffab0040'}`
                            }}>
                                {analysis.regime === 'Bull' ? 5 : (analysis.regime === 'Bear' ? 1 : 3)}
                            </div>
                            <div>
                                <div style={{ fontWeight: 'bold', fontSize: '1.2em' }}>{t(analysis.regime)}</div>
                                <div style={{ fontSize: '0.9em', color: '#aaa' }}>{analysis.regime === 'Bull' ? '市場環境有利' : '檢測到市場波動'}</div>
                            </div>
                        </div>
                    ) : (<div>載入中...</div>)}
                </div>

                <div className="card">
                    <h3>情緒分析 (Sentiment)</h3>
                    {analysis && analysis.sentiment ? (
                        <>
                            <div className="metric-row">
                                <span>情緒分數</span>
                                <span className="metric-val" style={{ color: analysis.sentiment.score > 0 ? 'var(--success)' : 'var(--danger)' }}>
                                    {analysis.sentiment.score.toFixed(2)}
                                </span>
                            </div>
                            <div style={{ fontSize: '0.9em', color: '#aaa', marginTop: '5px' }}>
                                {analysis.sentiment.description}
                            </div>
                        </>
                    ) : (<div>載入中...</div>)}
                </div>
            </div>
        </div>
    );
};
