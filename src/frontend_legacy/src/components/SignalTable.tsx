import styles from '../app/Dashboard.module.css';
import { I18N } from './i18n';

interface Signal {
    date: string;
    ticker: string;
    action: string;
    price: number;
    size: number;
}

interface SignalTableProps {
    signals: Signal[];
}

export const SignalTable = ({ signals }: SignalTableProps) => {
    if (!signals || signals.length === 0) {
        return (
            <div className={styles.card} style={{ textAlign: 'center', color: '#666', padding: '2rem' }}>
                {I18N.signals.noSignals}
            </div>
        );
    }

    return (
        <div className={styles.card}>
            <h3 className={styles.cardTitle}>{I18N.signals.title}</h3>
            <div style={{ maxHeight: '300px', overflowY: 'auto' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.9rem' }}>
                    <thead>
                        <tr style={{ borderBottom: '1px solid #333', color: '#888' }}>
                            <th style={{ textAlign: 'left', padding: '8px' }}>{I18N.signals.colDate}</th>
                            <th style={{ textAlign: 'left', padding: '8px' }}>{I18N.signals.colAction}</th>
                            <th style={{ textAlign: 'right', padding: '8px' }}>{I18N.signals.colPrice}</th>
                            <th style={{ textAlign: 'right', padding: '8px' }}>{I18N.signals.colSize}</th>
                        </tr>
                    </thead>
                    <tbody>
                        {signals.map((s, idx) => (
                            <tr key={idx} style={{ borderBottom: '1px solid #222' }}>
                                <td style={{ padding: '8px', color: '#ccc' }}>{s.date}</td>
                                <td style={{ padding: '8px' }}>
                                    <span style={{
                                        color: s.action === 'BUY' ? '#00ff9d' : '#ff0055',
                                        fontWeight: 'bold'
                                    }}>
                                        {s.action}
                                    </span>
                                </td>
                                <td style={{ padding: '8px', textAlign: 'right' }}>${s.price.toFixed(2)}</td>
                                <td style={{ padding: '8px', textAlign: 'right' }}>{s.size.toFixed(4)}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
};
