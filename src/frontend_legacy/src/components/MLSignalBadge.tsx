
import React from 'react';
import { MLSignalReport } from '../services/api';

interface Props {
    data: MLSignalReport;
}

export function MLSignalBadge({ data }: Props) {
    const isBull = data.signal > 0;
    const strength = Math.abs(data.signal);
    const color = isBull ? '#00ff9d' : '#ff0055';

    // Opacity based on strength
    const bg = isBull ? `rgba(0, 255, 157, 0.1)` : `rgba(255, 0, 85, 0.1)`;

    return (
        <div style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '0.8rem',
            padding: '0.5rem 1rem',
            background: bg,
            border: `1px solid ${color}`,
            borderRadius: '30px'
        }}>
            <div style={{ fontSize: '0.8rem', color: '#aaa', textTransform: 'uppercase' }}>ML Signal</div>
            <div style={{ fontSize: '1.2rem', fontWeight: 'bold', color }}>
                {data.signal > 0 ? '+' : ''}{data.signal.toFixed(2)}
            </div>
            <div style={{ width: '1px', height: '20px', background: '#444' }} />
            <div style={{ fontSize: '0.9rem', color: '#fff' }}>
                Regime: <span style={{ color: '#00d2ff' }}>{data.regime}</span>
            </div>
            <div style={{ fontSize: '0.7rem', color: '#666' }}>
                (Conf: {(data.confidence * 100).toFixed(0)}%)
            </div>
        </div>
    );
}
