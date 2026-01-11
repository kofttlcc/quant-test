import { ResponsiveContainer, AreaChart, Area, CartesianGrid, XAxis, YAxis, Tooltip } from 'recharts';
import styles from '../app/Dashboard.module.css';

interface ChartCardProps {
    title: string;
    data: any[];
    dataKey: string;
    color: string;
    height?: string;
}

export const ChartCard = ({ title, data, dataKey, color, height = "250px" }: ChartCardProps) => {
    return (
        <div className={styles.card} style={{ flex: 1, minWidth: '400px' }}>
            <h3 className={styles.cardTitle}>{title}</h3>
            <div className={styles.chartContainer} style={{ height }}>
                <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={data}>
                        <defs>
                            <linearGradient id={`color-${dataKey}`} x1="0" y1="0" x2="0" y2="1">
                                <stop offset="5%" stopColor={color} stopOpacity={0.3} />
                                <stop offset="95%" stopColor={color} stopOpacity={0} />
                            </linearGradient>
                        </defs>
                        <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                        <XAxis dataKey="date" stroke="#666" />
                        <YAxis stroke="#666" domain={['auto', 'auto']} />
                        <Tooltip
                            contentStyle={{ backgroundColor: '#111', border: '1px solid #333' }}
                            itemStyle={{ color: '#fff' }}
                        />
                        <Area
                            type="monotone"
                            dataKey={dataKey}
                            stroke={color}
                            strokeWidth={2}
                            fillOpacity={1}
                            fill={`url(#color-${dataKey})`}
                        />
                    </AreaChart>
                </ResponsiveContainer>
            </div>
        </div>
    );
};
