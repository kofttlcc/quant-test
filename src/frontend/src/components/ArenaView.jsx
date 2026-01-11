
import React from 'react';

const t = (text) => {
    const map = {
        "Momentum": "動能模型",
        "Deep Learning": "深度學習 (LSTM)",
        "Mean Reversion": "均值回歸",
        "AI": "🤖 AI 策略",
        "Traditional": "📊 傳統策略",
        "Winning": "獲勝",
        "Eliminated": "淘汰"
    };
    return map[text] || text;
};

export const ArenaView = ({ results }) => {
    // Mock Next Battle Time
    const nextBattle = new Date(Date.now() + 3600000).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    // 分離 AI 和傳統策略
    const aiStrategies = results.filter(r => r.Type === 'AI');
    const traditionalStrategies = results.filter(r => r.Type === 'Traditional');

    // 計算平均 Sharpe
    const avgAiSharpe = aiStrategies.length > 0
        ? (aiStrategies.reduce((sum, r) => sum + r.Sharpe, 0) / aiStrategies.length).toFixed(2)
        : 'N/A';
    const avgTradSharpe = traditionalStrategies.length > 0
        ? (traditionalStrategies.reduce((sum, r) => sum + r.Sharpe, 0) / traditionalStrategies.length).toFixed(2)
        : 'N/A';

    // 冠軍
    const champion = results[0];
    const isAiWinner = champion?.Type === 'AI';

    return (
        <div style={{ padding: '20px', height: '100%', boxSizing: 'border-box', overflowY: 'auto' }}>
            {/* Header */}
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '20px', alignItems: 'center' }}>
                <div>
                    <h2 style={{ margin: 0 }}>⚔️ Alpha 競技場 (Season 1)</h2>
                    <div style={{ color: '#888', fontSize: '0.9em' }}>AI vs 傳統策略對抗平台</div>
                </div>
                <div style={{ textAlign: 'right' }}>
                    <div style={{ fontSize: '1.5em', fontWeight: 'bold', color: 'var(--accent-blue)' }}>{nextBattle}</div>
                    <div style={{ fontSize: '0.8em', color: '#666' }}>下一次對決時間</div>
                </div>
            </div>

            {/* 冠軍展示 */}
            {champion && (
                <div className="card" style={{
                    marginBottom: '20px',
                    background: isAiWinner ? 'linear-gradient(135deg, #1a237e20, #311b9220)' : 'linear-gradient(135deg, #1b5e2020, #33691e20)',
                    borderColor: isAiWinner ? '#7c4dff' : '#00c853',
                    borderWidth: '2px',
                    borderStyle: 'solid'
                }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '15px' }}>
                        <div style={{ fontSize: '3em' }}>🏆</div>
                        <div>
                            <div style={{ fontSize: '0.8em', color: '#888' }}>本輪冠軍</div>
                            <div style={{ fontSize: '1.5em', fontWeight: 'bold' }}>{champion.Strategy}</div>
                            <div style={{
                                display: 'inline-block',
                                padding: '2px 8px',
                                borderRadius: '4px',
                                fontSize: '0.8em',
                                background: isAiWinner ? '#7c4dff' : '#00c853',
                                color: 'white'
                            }}>
                                {t(champion.Type)}
                            </div>
                        </div>
                        <div style={{ marginLeft: 'auto', textAlign: 'right' }}>
                            <div style={{ fontSize: '2em', fontWeight: 'bold', color: 'var(--success)' }}>
                                {champion.Sharpe?.toFixed(2)}
                            </div>
                            <div style={{ fontSize: '0.8em', color: '#888' }}>Sharpe Ratio</div>
                        </div>
                    </div>
                </div>
            )}

            {/* AI vs 傳統 對比摘要 */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px', marginBottom: '20px' }}>
                <div className="card" style={{ borderColor: '#7c4dff', borderWidth: '1px', borderStyle: 'solid' }}>
                    <div style={{ fontSize: '1.2em', fontWeight: 'bold', marginBottom: '10px' }}>🤖 AI 陣營</div>
                    <div className="metric-row">
                        <span>參賽數量</span>
                        <span className="metric-val">{aiStrategies.length}</span>
                    </div>
                    <div className="metric-row">
                        <span>平均 Sharpe</span>
                        <span className="metric-val" style={{ color: 'var(--accent-blue)' }}>{avgAiSharpe}</span>
                    </div>
                </div>
                <div className="card" style={{ borderColor: '#00c853', borderWidth: '1px', borderStyle: 'solid' }}>
                    <div style={{ fontSize: '1.2em', fontWeight: 'bold', marginBottom: '10px' }}>📊 傳統陣營</div>
                    <div className="metric-row">
                        <span>參賽數量</span>
                        <span className="metric-val">{traditionalStrategies.length}</span>
                    </div>
                    <div className="metric-row">
                        <span>平均 Sharpe</span>
                        <span className="metric-val" style={{ color: 'var(--success)' }}>{avgTradSharpe}</span>
                    </div>
                </div>
            </div>

            {/* Leaderboard */}
            <div className="card" style={{ marginBottom: '20px' }}>
                <h3>🏆 完整排行榜 (Leaderboard)</h3>
                <table className="arena-table">
                    <thead>
                        <tr>
                            <th>排名</th>
                            <th>類型</th>
                            <th>策略模型</th>
                            <th>夏普比率</th>
                            <th>總回報</th>
                            <th>最大回撤</th>
                        </tr>
                    </thead>
                    <tbody>
                        {results.map((row, i) => (
                            <tr key={i} style={{ background: i === 0 ? 'rgba(0, 200, 83, 0.1)' : 'transparent' }}>
                                <td>
                                    {i === 0 ? '🥇' : (i === 1 ? '🥈' : (i === 2 ? '🥉' : i + 1))}
                                </td>
                                <td style={{
                                    color: row.Type === 'AI' ? '#7c4dff' : '#00c853',
                                    fontWeight: 'bold'
                                }}>
                                    {row.Type === 'AI' ? '🤖' : '📊'}
                                </td>
                                <td style={{ fontWeight: i === 0 ? 'bold' : 'normal' }}>{row.Strategy}</td>
                                <td style={{ color: row.Sharpe > 1 ? 'var(--success)' : '#ddd' }}>{row.Sharpe?.toFixed(2)}</td>
                                <td>{((row['Total Return'] || 0) * 100).toFixed(2)}%</td>
                                <td style={{ color: 'var(--danger)' }}>{((row['Max DD'] || 0) * 100).toFixed(2)}%</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>

            {/* Contestants - MAJOR-008 FIX: 動態渲染，不再硬編碼 */}
            <h3>🤖 參賽選手 (Models)</h3>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '15px' }}>
                {results.map((row, i) => (
                    <div
                        key={i}
                        className="card"
                        style={{
                            borderColor: row.Type === 'AI' ? '#7c4dff' :
                                (row.Rank === 1 ? 'var(--success)' : '#ffab00'),
                            borderWidth: '1px',
                            borderStyle: 'solid',
                            background: row.Rank === 1 ? 'rgba(0, 200, 83, 0.05)' : 'transparent'
                        }}
                    >
                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                            <span style={{ fontSize: '1.2em' }}>
                                {row.Type === 'AI' ? '🤖' : '📊'}
                            </span>
                            <span style={{ fontWeight: 'bold' }}>{row.Strategy}</span>
                            {row.Rank === 1 && <span title="冠軍">🏆</span>}
                        </div>
                        <div style={{ fontSize: '0.85em', color: '#aaa', marginBottom: '8px' }}>
                            {row.Description || '無描述'}
                        </div>
                        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8em' }}>
                            <span>Sharpe: <span style={{ color: row.Sharpe > 1 ? 'var(--success)' : '#ddd' }}>
                                {row.Sharpe?.toFixed(2)}
                            </span></span>
                            <span>排名: #{row.Rank}</span>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

