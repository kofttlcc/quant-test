
import React from 'react';
import { ValuationDetail } from '../services/api';

interface Props {
    data: ValuationDetail;
}

export function ValuationAnalysis({ data }: Props) {
    const mos = data.margin_of_safety;
    const mosColor = mos > 0.1 ? '#00ff9d' : (mos < -0.1 ? '#ff0055' : '#ff9900');

    return (
        <div style={{
            background: 'rgba(20, 20, 30, 0.6)',
            padding: '1.2rem',
            borderRadius: '12px',
            border: '1px solid #333'
        }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1rem' }}>
                <h4 style={{ margin: 0, color: '#aaa' }}>Intrinsic Value Analysis</h4>
                <div style={{ color: mosColor, fontWeight: 'bold' }}>{data.status}</div>
            </div>

            <div style={{ display: 'flex', alignItems: 'flex-end', gap: '1rem', marginBottom: '1.5rem' }}>
                <div>
                    <div style={{ fontSize: '0.8rem', color: '#888' }}>Current Price</div>
                    <div style={{ fontSize: '1.8rem', fontFamily: 'monospace' }}>${data.current_price.toFixed(2)}</div>
                </div>
                <div style={{ fontSize: '1.5rem', color: '#555' }}>vs</div>
                <div>
                    <div style={{ fontSize: '0.8rem', color: '#888' }}>Intrinsic Value</div>
                    <div style={{ fontSize: '1.8rem', fontFamily: 'monospace', color: '#00d2ff' }}>${data.composite_value.toFixed(2)}</div>
                </div>
                <div style={{ marginLeft: 'auto', textAlign: 'right' }}>
                    <div style={{ fontSize: '0.8rem', color: '#888' }}>Margin of Safety</div>
                    <div style={{ fontSize: '1.5rem', color: mosColor }}>{(mos * 100).toFixed(1)}%</div>
                </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.8rem' }}>
                <Row label="DCF Model" value={data.method_values.dcf} />
                <Row label="Graham Number" value={data.method_values.graham} />
                <Row label="Relative PE" value={data.method_values.relative_pe} />
                <Row label="Relative PB" value={data.method_values.relative_pb} />
            </div>

            {data.sentiment_impact && (
                <div style={{ marginTop: '1rem', fontSize: '0.8rem', color: '#666', fontStyle: 'italic' }}>
                    Sentiment Score: {data.sentiment_impact.score.toFixed(2)} (WACC: {(data.sentiment_impact.wacc_used * 100).toFixed(1)}%)
                </div>
            )}
        </div>
    );
}

function Row({ label, value }: { label: string, value: number }) {
    return (
        <div style={{ display: 'flex', justifyContent: 'space-between', padding: '0.5rem', background: 'rgba(255,255,255,0.03)', borderRadius: '4px' }}>
            <span style={{ color: '#888' }}>{label}</span>
            <span style={{ fontFamily: 'monospace' }}>${value.toFixed(2)}</span>
        </div>
    )
}
