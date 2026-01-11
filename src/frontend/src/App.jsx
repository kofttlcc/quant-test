import React, { useState } from 'react'
import QuantDashboard from './components/QuantDashboard'
import SimulationDashboard from './components/SimulationDashboard'
import AILab from './components/AILab'
import MacroRiskGauge from './components/MacroRiskGauge'
import ArenaLeaderboard from './components/ArenaLeaderboard'
import './index.css'
import { Layout, LineChart, FlaskConical } from 'lucide-react'

function App() {
    const [view, setView] = useState('dashboard');

    return (
        <div className="app-container">
            <nav style={{
                background: '#0f172a',
                padding: '10px 20px',
                borderBottom: '1px solid #1e293b',
                display: 'flex',
                gap: '20px',
                alignItems: 'center'
            }}>
                <div style={{ color: '#38bdf8', fontWeight: 'bold', fontSize: '1.2rem', marginRight: '20px' }}>
                    Gemini Quant
                </div>
                <button
                    onClick={() => setView('dashboard')}
                    style={{
                        background: view === 'dashboard' ? '#1e293b' : 'transparent',
                        color: view === 'dashboard' ? '#38bdf8' : '#94a3b8',
                        border: 'none',
                        padding: '8px 16px',
                        cursor: 'pointer',
                        borderRadius: '6px',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '8px'
                    }}
                >
                    <Layout size={16} /> 儀表板
                </button>
                <button
                    onClick={() => setView('simulation')}
                    style={{
                        background: view === 'simulation' ? '#1e293b' : 'transparent',
                        color: view === 'simulation' ? '#38bdf8' : '#94a3b8',
                        border: 'none',
                        padding: '8px 16px',
                        cursor: 'pointer',
                        borderRadius: '6px',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '8px'
                    }}
                >
                    <LineChart size={16} /> 模擬交易
                </button>
                <button
                    onClick={() => setView('ailab')}
                    style={{
                        background: view === 'ailab' ? '#1e293b' : 'transparent',
                        color: view === 'ailab' ? '#38bdf8' : '#94a3b8',
                        border: 'none',
                        padding: '8px 16px',
                        cursor: 'pointer',
                        borderRadius: '6px',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '8px'
                    }}
                >
                    <FlaskConical size={16} /> AI 實驗室
                </button>
            </nav>

            <main style={{ minHeight: 'calc(100vh - 60px)', padding: '20px' }}>
                {view === 'dashboard' ? (
                    <>
                        <MacroRiskGauge />
                        <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '20px' }}>
                            <div>
                                <QuantDashboard onNavigate={setView} />
                            </div>
                            <div>
                                <ArenaLeaderboard />
                            </div>
                        </div>
                    </>
                ) : view === 'simulation' ? <SimulationDashboard /> :
                    <AILab />}
            </main>
        </div>
    )
}

export default App
