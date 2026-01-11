import React, { useState, useEffect, useRef } from 'react';
import {
    FlaskConical, Play, Save, History,
    Trash2, RefreshCw, Terminal, Cpu, Activity
} from 'lucide-react';
import { API } from '../services/api';
import './AILab.css';

const AILab = () => {
    // Training Form State
    const [modelType, setModelType] = useState('lightgbm');
    const [ticker, setTicker] = useState('BTC-USD');
    const [params, setParams] = useState({
        learning_rate: 0.05,
        n_estimators: 100,
        max_depth: 5
    });

    // Training Status State
    const [isTraining, setIsTraining] = useState(false);
    const [jobId, setJobId] = useState(null);
    const [progress, setProgress] = useState(0);
    const [logs, setLogs] = useState([]);
    const [statusMessage, setStatusMessage] = useState('');

    // Models List State
    const [models, setModels] = useState([]);
    const [isLoadingModels, setIsLoadingModels] = useState(false);

    // Refs
    const logsEndRef = useRef(null);

    // Polling for Status
    useEffect(() => {
        let interval;
        if (jobId && isTraining) {
            interval = setInterval(async () => {
                const status = await API.getTrainStatus(jobId);
                if (status && !status.error) {
                    setProgress(status.progress);
                    setLogs(status.logs || []);
                    setStatusMessage(status.status);

                    if (status.status === 'completed' || status.status === 'failed') {
                        setIsTraining(false);
                        setJobId(null);
                        fetchModels(); // Refresh list on complete
                    }
                }
            }, 1000);
        }
        return () => clearInterval(interval);
    }, [jobId, isTraining]);

    // Auto scroll logs
    useEffect(() => {
        logsEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [logs]);

    // Initial Load
    useEffect(() => {
        fetchModels();
    }, []);

    const fetchModels = async () => {
        setIsLoadingModels(true);
        const res = await API.listModels();
        if (res && res.models) {
            setModels(res.models);
        }
        setIsLoadingModels(false);
    };

    const handleTrainStart = async () => {
        setIsTraining(true);
        setLogs(['Starting training request...']);
        setProgress(0);

        const res = await API.trainModel(modelType, ticker, params);

        if (res && res.success && res.job_id) {
            setJobId(res.job_id);
            setLogs(prev => [...prev, `Job ID: ${res.job_id}`, 'Waiting for worker...']);
        } else {
            setIsTraining(false);
            setLogs(prev => [...prev, `Error: ${res.error || 'Request failed'}`]);
        }
    };

    const handleDelete = async (type, version) => {
        if (window.confirm(`Are you sure you want to delete ${type} ${version}?`)) {
            await API.deleteModel(type, version);
            fetchModels();
        }
    };

    return (
        <div className="ai-lab-container">
            <div className="lab-header">
                <FlaskConical size={28} color="#38bdf8" />
                <div>
                    <h2>AI 煉丹爐 (AI Lab)</h2>
                    <div style={{ color: '#94a3b8', fontSize: '0.9rem' }}>Train, Visualize and Manage your Alpha Models</div>
                </div>
            </div>

            <div className="lab-grid">
                {/* Left Panel: Configuration */}
                <div className="left-panel">
                    <div className="lab-card">
                        <h3><Cpu size={18} /> 訓練配置</h3>

                        <div className="form-group">
                            <label>Target Asset</label>
                            <input
                                className="form-input"
                                value={ticker}
                                onChange={e => setTicker(e.target.value)}
                            />
                        </div>

                        <div className="form-group">
                            <label>Model Architecture</label>
                            <select
                                className="form-select"
                                value={modelType}
                                onChange={e => setModelType(e.target.value)}
                            >
                                <option value="lightgbm">Gradient Boosting (LightGBM)</option>
                                <option value="mlp">Neural Network (MLP)</option>
                            </select>
                        </div>

                        <div className="form-group">
                            <label>Hyperparameters</label>
                            <div style={{ fontSize: '0.8rem', color: '#64748b', marginBottom: '8px' }}>Format: JSON</div>
                            <textarea
                                className="form-input"
                                rows={5}
                                style={{ fontFamily: 'monospace' }}
                                value={JSON.stringify(params, null, 2)}
                                onChange={e => {
                                    try {
                                        setParams(JSON.parse(e.target.value));
                                    } catch (err) {
                                        // allow editing
                                    }
                                }}
                            />
                        </div>

                        <button
                            className="btn-primary"
                            onClick={handleTrainStart}
                            disabled={isTraining}
                        >
                            {isTraining ? <RefreshCw className="spin" size={18} /> : <Play size={18} />}
                            {isTraining ? 'Training in Progress...' : 'Start Training'}
                        </button>
                    </div>
                </div>

                {/* Right Panel: Monitor & Repository */}
                <div className="right-panel">
                    {/* Training Monitor */}
                    <div className="lab-card">
                        <h3><Terminal size={18} /> 實時監控 (Training Monitor)</h3>

                        {isTraining || logs.length > 0 ? (
                            <div className="monitor-content">
                                {isTraining && (
                                    <div className="progress-container">
                                        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                                            <span>Progress</span>
                                            <span>{progress}%</span>
                                        </div>
                                        <div className="progress-bar">
                                            <div className="progress-fill" style={{ width: `${progress}%` }}></div>
                                        </div>
                                        <div className="status-text">{statusMessage}</div>
                                    </div>
                                )}

                                <div className="console-output">
                                    {logs.map((log, i) => (
                                        <div key={i}>{log}</div>
                                    ))}
                                    <div ref={logsEndRef} />
                                </div>
                            </div>
                        ) : (
                            <div className="empty-state">
                                <Activity size={48} style={{ opacity: 0.2 }} />
                                <p>Ready to train. Configure parameters on the left.</p>
                            </div>
                        )}
                    </div>

                    {/* Model Repository */}
                    <div className="lab-card">
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                            <h3><History size={18} /> 模型倉庫 (Model Registry)</h3>
                            <button onClick={fetchModels} style={{ background: 'none', border: 'none', color: '#94a3b8', cursor: 'pointer' }}>
                                <RefreshCw size={16} />
                            </button>
                        </div>

                        {isLoadingModels ? (
                            <div style={{ padding: '20px', textAlign: 'center' }}>Loading...</div>
                        ) : models.length > 0 ? (
                            <table className="model-table">
                                <thead>
                                    <tr>
                                        <th>Type</th>
                                        <th>Version</th>
                                        <th>Date</th>
                                        <th>Params</th>
                                        <th>Actions</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {models.map((m, i) => (
                                        <tr key={i}>
                                            <td style={{ textTransform: 'capitalize' }}>{m.type}</td>
                                            <td><span className="badge-version">{m.version}</span></td>
                                            <td style={{ fontSize: '0.85rem' }}>{m.timestamp}</td>
                                            <td style={{ fontFamily: 'monospace', fontSize: '0.8rem', maxWidth: '200px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                                                {JSON.stringify(m.params)}
                                            </td>
                                            <td>
                                                <button className="action-btn" onClick={() => handleDelete(m.type, m.version)}>
                                                    <Trash2 size={16} />
                                                </button>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        ) : (
                            <div className="empty-state">No models found.</div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default AILab;
