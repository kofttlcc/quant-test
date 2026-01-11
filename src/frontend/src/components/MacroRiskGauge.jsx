
import React, { useState, useEffect } from 'react';
import { Gauge, AlertTriangle, CheckCircle, Activity } from 'lucide-react';

const MacroRiskGauge = () => {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchData = async () => {
            try {
                // In production, use environment variable for API URL
                // Here we assume proxy or same host
                const response = await fetch('http://127.0.0.1:8045/api/v1/macro/overview', {
                    headers: {
                        'X-API-Key': 'gemini-quant-v5-dev' // Dev key, or empty in dev
                    }
                });

                if (!response.ok) {
                    throw new Error('Failed to fetch macro data');
                }

                const result = await response.json();
                setData(result);
            } catch (err) {
                console.error("Macro Fetch Error:", err);
                setError(err.message);
            } finally {
                setLoading(false);
            }
        };

        fetchData();
        const interval = setInterval(fetchData, 60000); // Update every minute
        return () => clearInterval(interval);
    }, []);

    if (loading) return (
        <div style={{
            background: '#1e293b',
            borderRadius: '12px',
            padding: '20px',
            color: '#94a3b8',
            textAlign: 'center'
        }}>
            載入宏觀數據中...
        </div>
    );

    if (error) return (
        <div style={{
            background: '#1e293b',
            borderRadius: '12px',
            padding: '20px',
            color: '#ef4444',
            textAlign: 'center'
        }}>
            宏觀數據載入失敗
        </div>
    );

    const { risk_score, risk_mode, timestamp } = data;

    // Color logic
    let color = '#3b82f6'; // Blue Neutral
    if (risk_score >= 75) color = '#ef4444'; // Red Risk Off
    else if (risk_score <= 30) color = '#22c55e'; // Green Risk On

    const Icon = risk_score >= 75 ? AlertTriangle : risk_score <= 30 ? CheckCircle : Activity;

    return (
        <div style={{
            background: '#1e293b',
            borderRadius: '12px',
            padding: '20px',
            marginTop: '20px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            border: `1px solid ${color}40`,
            boxShadow: `0 0 20px ${color}10`
        }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
                <div style={{
                    width: '80px',
                    height: '80px',
                    borderRadius: '50%',
                    border: `4px solid ${color}`,
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    justifyContent: 'center',
                    background: `${color}10`
                }}>
                    <span style={{ fontSize: '1.5rem', fontWeight: 'bold', color: color }}>
                        {risk_score}
                    </span>
                    <span style={{ fontSize: '0.7rem', color: '#94a3b8' }}>RISK</span>
                </div>

                <div>
                    <h3 style={{ margin: 0, color: '#e2e8f0', display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <Icon size={20} color={color} />
                        宏觀風險 (Macro Risk)
                    </h3>
                    <div style={{
                        fontSize: '1.2rem',
                        fontWeight: 'bold',
                        color: color,
                        marginTop: '4px'
                    }}>
                        {risk_mode === 'Risk Off' ? '避險模式 (Risk Off)' :
                            risk_mode === 'Risk On' ? '積極模式 (Risk On)' : '中性觀望 (Neutral)'}
                    </div>
                </div>
            </div>

            <div style={{ display: 'flex', gap: '40px', color: '#cbd5e1' }}>
                <div style={{ textAlign: 'center' }}>
                    <div style={{ fontSize: '0.8rem', color: '#94a3b8' }}>VIX 指數</div>
                    <div style={{ fontWeight: 'bold' }}>{data.vix.value}</div>
                    <div style={{ fontSize: '0.7rem', color: data.vix.status === 'High' ? '#ef4444' : '#22c55e' }}>
                        {data.vix.status}
                    </div>
                </div>

                <div style={{ textAlign: 'center' }}>
                    <div style={{ fontSize: '0.8rem', color: '#94a3b8' }}>美債利差 (10Y-2Y)</div>
                    <div style={{ fontWeight: 'bold' }}>{data.rates.spread_bps} bps</div>
                    <div style={{ fontSize: '0.7rem', color: data.rates.spread_bps < 0 ? '#ef4444' : '#22c55e' }}>
                        {data.rates.spread_bps < 0 ? '倒掛 (Inverted)' : '正常 (Normal)'}
                    </div>
                </div>

                <div style={{ textAlign: 'center' }}>
                    <div style={{ fontSize: '0.8rem', color: '#94a3b8' }}>市場情緒</div>
                    <div style={{ fontWeight: 'bold' }}>{data.sentiment.label}</div>
                    <div style={{ fontSize: '0.7rem' }}>Score: {data.sentiment.score}</div>
                </div>
            </div>

            <div style={{ textAlign: 'right', fontSize: '0.7rem', color: '#64748b' }}>
                更新時間: {new Date(timestamp).toLocaleTimeString()}
            </div>
        </div>
    );
};

export default MacroRiskGauge;
