import { useState, useEffect } from 'react';
import styles from '../app/Dashboard.module.css';
import { I18N } from './i18n';
import { LogViewer } from './LogViewer';

export const DataManager = () => {
    const [status, setStatus] = useState<any>(null);
    const [loading, setLoading] = useState(false);
    const [logs, setLogs] = useState<string[]>([]);
    const [provider, setProvider] = useState<'yfinance' | 'finnhub'>('yfinance');
    const [apiKey, setApiKey] = useState('');

    // Status Polling
    const fetchStatus = async () => {
        try {
            const res = await fetch('http://127.0.0.1:8000/api/data/status');
            const data = await res.json();
            setStatus(data);
        } catch (e) {
            console.error(e);
        }
    };

    // Log Polling
    const fetchLogs = async () => {
        try {
            const res = await fetch('http://127.0.0.1:8000/api/data/logs');
            const data = await res.json();
            if (data.logs) {
                setLogs(data.logs);
            }
        } catch (e) {
            console.error(e);
        }
    };

    useEffect(() => {
        fetchStatus();
        const statusDetails = setInterval(fetchStatus, 30000); // 30s for status
        const logDetails = setInterval(fetchLogs, 2000); // 2s for logs

        return () => {
            clearInterval(statusDetails);
            clearInterval(logDetails);
        };
    }, []);

    const handleUpdate = async (type: 'price' | 'financial' | 'btc') => {
        setLoading(true);
        try {
            const endpoint = type === 'btc' ? 'update_btc' : `update_${type}`;
            const res = await fetch(`http://127.0.0.1:8000/api/data/${endpoint}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    tickers: [],
                    provider: provider,
                    api_key: apiKey
                })
            });
            await res.json();
            // Immediate log fetch to show start
            fetchLogs();
        } catch (e) {
            console.error("Update failed", e);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className={styles.card} style={{ marginTop: '1.5rem' }}>
            <h3 className={styles.cardTitle}>{I18N.dataManager.title}</h3>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.8rem' }}>
                {/* Status Info */}
                <div style={{ fontSize: '0.8rem', color: '#888' }}>
                    <div>最後更新: {status?.last_updated || '從未'}</div>
                    <div>文件: {status?.price_count || 0} (Price), {status?.financial_count || 0} (Fin)</div>
                </div>

                {/* Config Section */}
                <div style={{ borderTop: '1px solid #333', paddingTop: '0.5rem' }}>
                    <label className={styles.label}>{I18N.dataManager.sourceLabel}</label>
                    <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '0.5rem' }}>
                        <select
                            className={styles.select}
                            value={provider}
                            onChange={(e) => setProvider(e.target.value as any)}
                        >
                            <option value="yfinance">YFinance (Free)</option>
                            <option value="finnhub">Finnhub (API Key)</option>
                        </select>
                    </div>

                    {provider === 'finnhub' && (
                        <input
                            className={styles.input}
                            placeholder={I18N.dataManager.apiKeyPlaceholder}
                            value={apiKey}
                            onChange={(e) => setApiKey(e.target.value)}
                            style={{ marginBottom: '0.5rem' }}
                        />
                    )}
                </div>

                {/* Buttons */}
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem' }}>
                    <button
                        className={styles.button}
                        onClick={() => handleUpdate('price')}
                        disabled={loading}
                    >
                        {I18N.dataManager.btnUpdatePrice}
                    </button>
                    <button
                        className={styles.button}
                        onClick={() => handleUpdate('btc')}
                        disabled={loading}
                        style={{ backgroundColor: '#f7931a', color: '#000' }}
                    >
                        {I18N.dataManager.btnUpdateBTC}
                    </button>
                </div>

                <button
                    className={styles.button}
                    onClick={() => handleUpdate('financial')}
                    disabled={loading}
                    style={{ backgroundColor: '#333', fontSize: '0.8rem' }}
                >
                    {I18N.dataManager.btnUpdateFinancial}
                </button>

                {/* Log Viewer */}
                <LogViewer logs={logs} />

            </div>
        </div>
    );
};
