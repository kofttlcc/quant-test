
import React from 'react';
import { SentinelReport } from '../services/api';

interface Props {
    data: SentinelReport;
}

const colorMap: Record<string, string> = {
    'green': '#00ff9d',
    'yellow': '#ffdd00',
    'orange': '#ff9900',
    'red': '#ff0055',
    'gray': '#888888'
};

export function MacroSentinelCard({ data }: Props) {
    const verdictColor = colorMap[data.verdict_color] || '#fff';

    return (
        <div style={{
            background: 'rgba(20, 20, 30, 0.8)',
            padding: '1.5rem',
            borderRadius: '16px',
            border: `1px solid ${verdictColor}`,
            marginBottom: '1.5rem'
        }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                <h3 style={{ margin: 0, fontSize: '1.1rem', color: '#ccc' }}>MACRO SENTINEL</h3>
                <div style={{
                    background: verdictColor,
                    color: '#000',
                    fontWeight: 'bold',
                    padding: '0.25rem 0.8rem',
                    borderRadius: '4px'
                }}>
                    {data.verdict}
                </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '1rem' }}>
                <MetricBox label="Risk Score" value={`${data.risk_score.toFixed(0)}/100`} color={data.risk_score > 60 ? '#ff0055' : '#00ff9d'} />
                <MetricBox label="Valuation" value={data.valuation_status} color={data.valuation_status === '高估' ? '#ff9900' : '#fff'} />
                <MetricBox label="VIX" value={data.components?.vix?.toFixed(1) || 'N/A'} />
                <MetricBox label="Trend" value={data.metrics?.price > data.metrics?.ma200 ? 'Bull' : 'Bear'} />
            </div>

            {data.reasons.length > 0 && (
                <div style={{ marginTop: '1rem', paddingTop: '1rem', borderTop: '1px solid #333' }}>
                    <div style={{ fontSize: '0.8rem', color: '#888', marginBottom: '0.5rem' }}>KEY DRIVERS</div>
                    {data.reasons.map((r, i) => (
                        <div key={i} style={{ fontSize: '0.9rem', color: '#ddd', marginBottom: '0.25rem' }}>• {r}</div>
                    ))}
                </div>
            )}
        </div>
    );
}

function MetricBox({ label, value, color = '#fff' }: { label: string, value: string | number, color?: string }) {
    return (
        <div style={{ background: 'rgba(255,255,255,0.05)', padding: '0.8rem', borderRadius: '8px', textAlign: 'center' }}>
            <div style={{ fontSize: '0.75rem', color: '#888', marginBottom: '0.2rem' }}>{label}</div>
            <div style={{ fontSize: '1.2rem', fontWeight: 'bold', color }}>{value}</div>
        </div>
    );
}
