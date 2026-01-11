import React, { useState, useEffect } from 'react';
import { Activity, Play, Pause, RefreshCw, Square, Info } from 'lucide-react';
import { ComposedChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Scatter } from 'recharts';

const SimulationDashboard = () => {
    const [status, setStatus] = useState(null);
    const [loading, setLoading] = useState(false);
    const [ticker, setTicker] = useState('AAPL');

    const fetchStatus = async () => {
        try {
            const res = await fetch('http://localhost:5001/api/v1/simulation/status');
            if (res.ok) {
                const data = await res.json();
                setStatus(data);
            }
        } catch (e) {
            console.error(e);
        }
    };

    useEffect(() => {
        fetchStatus();
        const interval = setInterval(fetchStatus, 5000);
        return () => clearInterval(interval);
    }, []);

    const startSimulation = async () => {
        setLoading(true);
        try {
            await fetch('http://localhost:5001/api/v1/simulation/start', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ ticker: ticker })
            });
            fetchStatus();
        } catch (e) {
            console.error(e);
        }
        setLoading(false);
    };

    const stopSimulation = async () => {
        try {
            await fetch('http://localhost:5001/api/v1/simulation/stop', { method: 'POST' });
            setStatus(prev => ({ ...prev, status: 'stopped' }));
        } catch (e) {
            console.error(e);
        }
    };

    // Custom Dot for Trades
    const renderTradeDot = (props) => {
        const { cx, cy, payload } = props;
        const trade = status?.history?.find(t => t.candle_time.startsWith(payload.time) || t.time.startsWith(payload.time));

        if (trade) {
            const color = trade.type === 'BUY' ? '#22c55e' : '#ef4444';
            const rotation = trade.type === 'BUY' ? 0 : 180;
            return (
                <svg x={cx - 6} y={cy - 6} width={12} height={12} fill={color} viewBox="0 0 1024 1024" style={{ transform: `rotate(${rotation}deg)` }}>
                    <path d="M512 0L128 768h768z" />
                </svg>
            );
        }
        return null;
    };

    return (
        <div className="simulation-view" style={{ padding: '24px', height: '100%', overflowY: 'auto' }}>
            <div className="simulation-header" style={{ marginBottom: '24px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <h2 style={{ fontSize: '1.25rem', fontWeight: 600, color: '#1e293b', display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <Activity size={24} /> 實盤模擬交易 (Paper Trading)
                </h2>
                <div style={{ display: 'flex', gap: '10px' }}>
                    <input
                        value={ticker}
                        onChange={e => setTicker(e.target.value)}
                        style={{ padding: '8px 12px', borderRadius: '6px', border: '1px solid #cbd5e1', fontSize: '14px' }}
                        placeholder="輸入代碼 (e.g. AAPL)"
                    />
                    <button
                        onClick={startSimulation}
                        disabled={loading}
                        className="update-btn primary"
                        style={{ display: 'flex', alignItems: 'center', gap: '6px' }}
                    >
                        {loading ? <RefreshCw size={14} className="spin" /> : <Play size={14} />}
                        開始模擬
                    </button>
                    <button
                        onClick={stopSimulation}
                        className="update-btn danger"
                        style={{ display: 'flex', alignItems: 'center', gap: '6px', background: '#ef4444', color: 'white', border: 'none', padding: '8px 12px', borderRadius: '6px', cursor: 'pointer' }}
                    >
                        <Square size={14} /> 停止
                    </button>
                </div>
            </div>

            {status && status.status !== 'not_started' ? (
                <>
                    <div className="metrics-row" style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px', marginBottom: '24px' }}>
                        <div className="metric-card">
                            <div className="metric-header">
                                <span className="metric-title">總資產 (Total Equity)</span>
                            </div>
                            <div className="metric-value">${status.equity?.toLocaleString(undefined, { minimumFractionDigits: 2 })}</div>
                        </div>
                        <div className="metric-card">
                            <div className="metric-header">
                                <span className="metric-title">現金 (Cash)</span>
                            </div>
                            <div className="metric-value">${status.cash?.toLocaleString(undefined, { minimumFractionDigits: 2 })}</div>
                        </div>
                        <div className="metric-card">
                            <div className="metric-header">
                                <span className="metric-title">持倉頭寸 (Positions)</span>
                            </div>
                            <div className="metric-value">{status.positions} 股</div>
                        </div>
                    </div>

                    {/* Chart Section */}
                    <div style={{ background: 'white', borderRadius: '12px', padding: '20px', marginBottom: '24px', boxShadow: '0 1px 3px rgba(0,0,0,0.08)' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '16px' }}>
                            <h3 style={{ fontSize: '1rem', color: '#334155' }}>實時權益曲線 (Live Performance)</h3>
                            {status.strategy_name && <span style={{ fontSize: '0.9rem', color: '#64748b', display: 'flex', alignItems: 'center', gap: '6px' }}><Info size={14} /> 運行模型: {status.strategy_name}</span>}
                        </div>

                        <div style={{ height: '300px', width: '100%' }}>
                            {status.market_history && status.market_history.length > 0 ? (
                                <ResponsiveContainer>
                                    <ComposedChart data={status.market_history}>
                                        <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" vertical={false} />
                                        <XAxis dataKey="time" hide={true} />
                                        <YAxis yAxisId="left" domain={['auto', 'auto']} label={{ value: 'Equity ($)', angle: -90, position: 'insideLeft' }} />
                                        <YAxis yAxisId="right" orientation="right" domain={['auto', 'auto']} label={{ value: 'Price', angle: 90, position: 'insideRight' }} />
                                        <Tooltip />
                                        <Legend />
                                        <Line yAxisId="left" type="monotone" dataKey="equity" stroke="#2563eb" dot={false} strokeWidth={2} name="Total Equity" />
                                        <Line yAxisId="right" type="monotone" dataKey="price" stroke="#94a3b8" dot={renderTradeDot} strokeWidth={1} strokeDasharray="3 3" name="Stock Price" />
                                    </ComposedChart>
                                </ResponsiveContainer>
                            ) : (
                                <div style={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#cbd5e1' }}>
                                    等待數據積累...
                                </div>
                            )}
                        </div>
                    </div>

                    <div className="trade-log-panel" style={{ background: 'white', borderRadius: '12px', padding: '20px', boxShadow: '0 1px 3px rgba(0,0,0,0.08)' }}>
                        <h3 style={{ fontSize: '1rem', marginBottom: '16px', color: '#334155' }}>交易執行記錄</h3>
                        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '14px' }}>
                            <thead>
                                <tr style={{ borderBottom: '2px solid #e2e8f0', color: '#64748b', textAlign: 'left' }}>
                                    <th style={{ padding: '12px' }}>時間</th>
                                    <th style={{ padding: '12px' }}>類型</th>
                                    <th style={{ padding: '12px' }}>價格</th>
                                    <th style={{ padding: '12px' }}>數量</th>
                                    <th style={{ padding: '12px' }}>金額</th>
                                </tr>
                            </thead>
                            <tbody>
                                {status.history && status.history.map((t, i) => (
                                    <tr key={i} style={{ borderBottom: '1px solid #f1f5f9' }}>
                                        <td style={{ padding: '12px', color: '#334155' }}>{t.time}</td>
                                        <td style={{ padding: '12px', fontWeight: 600, color: t.type === 'BUY' ? '#22c55e' : '#ef4444' }}>
                                            {t.type}
                                        </td>
                                        <td style={{ padding: '12px' }}>${t.price?.toFixed(2)}</td>
                                        <td style={{ padding: '12px' }}>{t.shares}</td>
                                        <td style={{ padding: '12px' }}>${t.value?.toLocaleString(undefined, { minimumFractionDigits: 2 })}</td>
                                    </tr>
                                ))}
                                {(!status.history || status.history.length === 0) && (
                                    <tr>
                                        <td colSpan="5" style={{ padding: '24px', textAlign: 'center', color: '#94a3b8' }}>
                                            暫無交易記錄
                                        </td>
                                    </tr>
                                )}
                            </tbody>
                        </table>
                    </div>
                </>
            ) : (
                <div style={{ textAlign: 'center', padding: '60px', color: '#64748b' }}>
                    <div style={{ marginBottom: '16px', fontSize: '48px' }}>📉</div>
                    <h3 style={{ marginBottom: '8px' }}>模擬交易未啟動</h3>
                    <p>請輸入股票代碼並點擊 "開始模擬" 以啟動實盤模擬引擎。</p>
                </div>
            )}
        </div>
    );
};

export default SimulationDashboard;
