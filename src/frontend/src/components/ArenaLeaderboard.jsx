
import React, { useState, useEffect } from 'react';
import { Trophy, Swords, BrainCircuit, Activity, TrendingUp, BarChart2 } from 'lucide-react';

const ArenaLeaderboard = () => {
    const [result, setResult] = useState(null);
    const [loading, setLoading] = useState(false);
    const [lastBattle, setLastBattle] = useState(null);
    // Sprint 1 Task 3: CAPM 分析狀態
    const [capmData, setCapmData] = useState(null);
    const [capmLoading, setCapmLoading] = useState(false);

    // Sprint 1: 獲取 CAPM 數據
    const fetchCAPM = async (ticker = 'BTC-USD') => {
        setCapmLoading(true);
        try {
            const API_BASE = import.meta.env.VITE_API_URL || '/api/v1';
            const response = await fetch(`${API_BASE}/capm/analyze?ticker=${ticker}&benchmark=SPY`, {
                headers: { 'X-API-Key': 'gemini-quant-v5-dev' }
            });
            if (response.ok) {
                const data = await response.json();
                setCapmData(data);
            }
        } catch (err) {
            console.error('CAPM fetch error:', err);
        } finally {
            setCapmLoading(false);
        }
    };

    // 頁面加載時獲取 CAPM
    useEffect(() => {
        fetchCAPM();
    }, []);

    const runBattle = async () => {
        setLoading(true);
        try {
            const API_BASE = import.meta.env.VITE_API_URL || '/api/v1';
            const response = await fetch(`${API_BASE}/arena/adversarial`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-API-Key': 'gemini-quant-v5-dev'
                },
                body: JSON.stringify({ ticker: 'BTC-USD' })
            });

            if (!response.ok) throw new Error('Battle failed');

            const data = await response.json();
            setResult(data);
            setLastBattle(new Date());
            // 同時刷新 CAPM 數據
            fetchCAPM('BTC-USD');
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div style={{
            background: '#1e293b',
            borderRadius: '12px',
            padding: '24px',
            marginTop: '20px',
            color: '#e2e8f0'
        }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
                <h3 style={{ margin: 0, display: 'flex', alignItems: 'center', gap: '10px', color: '#f59e0b' }}>
                    <Swords size={24} />
                    AI 對抗競技場 (Adversarial Arena)
                </h3>

                <button
                    onClick={runBattle}
                    disabled={loading}
                    style={{
                        background: loading ? '#475569' : '#f59e0b',
                        color: loading ? '#94a3b8' : '#fff',
                        border: 'none',
                        padding: '8px 16px',
                        borderRadius: '6px',
                        cursor: loading ? 'not-allowed' : 'pointer',
                        fontWeight: 'bold',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '8px'
                    }}
                >
                    {loading ? <Activity className="animate-spin" /> : <Swords size={16} />}
                    {loading ? '戰鬥中...' : '開始對戰 (Trigger Battle)'}
                </button>
            </div>

            {/* Sprint 1: CAPM 分析面板 */}
            <div style={{
                background: '#0f172a',
                borderRadius: '8px',
                padding: '16px',
                marginBottom: '20px',
                border: '1px solid #334155'
            }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
                    <BarChart2 size={18} color="#3b82f6" />
                    <span style={{ fontWeight: 'bold', color: '#3b82f6' }}>CAPM 分析 (Alpha/Beta)</span>
                    {capmLoading && <Activity size={14} className="animate-spin" style={{ color: '#64748b' }} />}
                </div>

                {capmData ? (
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '16px' }}>
                        <div style={{ textAlign: 'center' }}>
                            <div style={{ fontSize: '0.75rem', color: '#64748b' }}>Alpha (年化)</div>
                            <div style={{
                                fontSize: '1.25rem',
                                fontWeight: 'bold',
                                color: capmData.alpha > 0 ? '#10b981' : '#ef4444'
                            }}>
                                {capmData.alpha > 0 ? '+' : ''}{(capmData.alpha * 100).toFixed(2)}%
                            </div>
                            <div style={{ fontSize: '0.7rem', color: '#64748b' }}>
                                p={capmData.alpha_pvalue?.toFixed(3)}
                            </div>
                        </div>
                        <div style={{ textAlign: 'center' }}>
                            <div style={{ fontSize: '0.75rem', color: '#64748b' }}>Beta</div>
                            <div style={{
                                fontSize: '1.25rem',
                                fontWeight: 'bold',
                                color: capmData.beta > 1 ? '#f59e0b' : '#3b82f6'
                            }}>
                                {capmData.beta?.toFixed(3)}
                            </div>
                            <div style={{ fontSize: '0.7rem', color: '#64748b' }}>
                                {capmData.beta > 1 ? '高風險' : capmData.beta < 1 ? '低風險' : '中性'}
                            </div>
                        </div>
                        <div style={{ textAlign: 'center' }}>
                            <div style={{ fontSize: '0.75rem', color: '#64748b' }}>R² (解釋力)</div>
                            <div style={{ fontSize: '1.25rem', fontWeight: 'bold', color: '#e2e8f0' }}>
                                {(capmData.r_squared * 100).toFixed(1)}%
                            </div>
                            <div style={{ fontSize: '0.7rem', color: '#64748b' }}>
                                模型擬合度
                            </div>
                        </div>
                        <div style={{ textAlign: 'center' }}>
                            <div style={{ fontSize: '0.75rem', color: '#64748b' }}>樣本數</div>
                            <div style={{ fontSize: '1.25rem', fontWeight: 'bold', color: '#e2e8f0' }}>
                                {capmData.n_obs}
                            </div>
                            <div style={{ fontSize: '0.7rem', color: '#64748b' }}>
                                vs {capmData.benchmark}
                            </div>
                        </div>
                    </div>
                ) : (
                    <div style={{ textAlign: 'center', color: '#64748b', fontSize: '0.8rem' }}>
                        {capmLoading ? '正在計算 CAPM...' : '無數據'}
                    </div>
                )}
            </div>

            {!result ? (
                <div style={{ textAlign: 'center', color: '#64748b', padding: '40px' }}>
                    點擊「開始對戰」以觸發 Tree 模型與 Deep 模型的實時對抗
                </div>
            ) : (
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
                    {/* Winner Card */}
                    <div style={{
                        gridColumn: '1 / -1',
                        background: 'linear-gradient(90deg, #f59e0b20 0%, #1e293b 100%)',
                        border: '1px solid #f59e0b',
                        borderRadius: '8px',
                        padding: '20px',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '20px'
                    }}>
                        <div style={{
                            background: '#f59e0b',
                            borderRadius: '50%',
                            width: '60px',
                            height: '60px',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            color: '#fff'
                        }}>
                            <Trophy size={32} />
                        </div>
                        <div>
                            <div style={{ color: '#f59e0b', fontWeight: 'bold' }}>WINNER (本輪獲勝)</div>
                            <div style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>{result.winner}</div>
                            <div style={{ fontSize: '0.8rem', color: '#94a3b8' }}>
                                更新於: {new Date(result.timestamp).toLocaleTimeString()}
                            </div>
                        </div>
                    </div>

                    {/* Model Stats */}
                    {Object.entries(result.weights).map(([model, weight]) => (
                        <div key={model} style={{
                            background: '#0f172a',
                            borderRadius: '8px',
                            padding: '16px',
                            border: `1px solid ${model === result.winner ? '#f59e0b' : '#334155'}`
                        }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '10px' }}>
                                <BrainCircuit size={20} color={model.includes('Tree') ? '#10b981' : '#8b5cf6'} />
                                <span style={{ fontWeight: 'bold' }}>{model}</span>
                            </div>

                            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                                <span style={{ color: '#94a3b8' }}>動態權重 (Dynamic Weight)</span>
                                <span style={{ fontWeight: 'bold', color: '#fff' }}>{(weight * 100).toFixed(1)}%</span>
                            </div>

                            <div style={{
                                height: '6px',
                                background: '#334155',
                                borderRadius: '3px',
                                overflow: 'hidden'
                            }}>
                                <div style={{
                                    width: `${weight * 100}%`,
                                    height: '100%',
                                    background: model.includes('Tree') ? '#10b981' : '#8b5cf6'
                                }} />
                            </div>

                            <div style={{ marginTop: '12px', fontSize: '0.8rem', display: 'flex', gap: '10px' }}>
                                <span style={{ background: '#1e293b', padding: '2px 6px', borderRadius: '4px' }}>
                                    ROI: {result.metrics[model]?.roi.toFixed(2)}
                                </span>
                                <span style={{ background: '#1e293b', padding: '2px 6px', borderRadius: '4px' }}>
                                    Sharpe: {result.metrics[model]?.sharpe.toFixed(2)}
                                </span>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

export default ArenaLeaderboard;
