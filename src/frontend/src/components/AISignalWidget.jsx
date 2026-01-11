import React, { useState, useEffect } from 'react';
import { Activity, ArrowUp, ArrowDown, Minus } from 'lucide-react';
import { API } from '../services/api';

const AISignalWidget = ({ ticker }) => {
    const [signal, setSignal] = useState(null);
    const [isLoading, setIsLoading] = useState(false);

    useEffect(() => {
        let interval;
        const fetchSignal = async () => {
            setIsLoading(true);
            const res = await API.getInference(ticker);
            if (res && !res.error) {
                setSignal(res);
            }
            setIsLoading(false);
        };

        fetchSignal();
        // Poll every 10 seconds
        interval = setInterval(fetchSignal, 10000);

        return () => clearInterval(interval);
    }, [ticker]);

    if (!signal) return (
        <div className="metric-card">
            <div className="metric-header">
                <span className="metric-title">AI 信號 ({ticker})</span>
                <Activity size={16} className="spin" />
            </div>
            <div className="metric-value" style={{ fontSize: '1.2rem', color: '#64748b' }}>初始化中...</div>
        </div>
    );

    const getSignalColor = (s) => {
        if (s === 'BUY') return '#22c55e';
        if (s === 'SELL') return '#ef4444';
        return '#94a3b8';
    };

    const getSignalIcon = (s) => {
        if (s === 'BUY') return <ArrowUp size={20} />;
        if (s === 'SELL') return <ArrowDown size={20} />;
        return <Minus size={20} />;
    };

    // Handle NO_MODEL case explicitly
    const isNoModel = signal.signal === 'NO_MODEL';
    const displaySignal = isNoModel ? '暫無模型' : signal.signal === 'BUY' ? '強烈買入' : signal.signal === 'SELL' ? '強烈賣出' : '觀望持有';
    const displayColor = isNoModel ? '#64748b' : getSignalColor(signal.signal);

    return (
        <div className="metric-card" style={{ borderLeft: `4px solid ${displayColor}` }}>
            <div className="metric-header">
                <span className="metric-title">AI 趨勢信號流 (AI SIGNAL FLOW)</span>
                <Activity size={16} color={displayColor} />
            </div>
            <div className="metric-body" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <div>
                    <div className="metric-value" style={{ color: displayColor, display: 'flex', alignItems: 'center', gap: '8px' }}>
                        {!isNoModel && getSignalIcon(signal.signal)}
                        {displaySignal}
                    </div>
                    <div className="metric-sub" style={{ marginTop: '4px' }}>
                        置信度: {(signal.confidence * 100).toFixed(0)}%
                    </div>
                </div>
                <div style={{ textAlign: 'right' }}>
                    <div style={{ fontSize: '0.8rem', color: '#64748b' }}>概率 (Prob.)</div>
                    <div style={{ fontSize: '1.1rem', fontWeight: 'bold', color: '#f1f5f9' }}>
                        {(signal.probability * 100).toFixed(1)}%
                    </div>
                </div>
            </div>
            <div style={{ fontSize: '0.7rem', color: '#475569', marginTop: '8px', textAlign: 'right' }}>
                更新於: {signal.timestamp}
            </div>
        </div>
    );
};

export default AISignalWidget;
