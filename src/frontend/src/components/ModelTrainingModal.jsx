/**
 * ModelTrainingModal.jsx - AI 模型調參界面
 * 功能:
 * 1. 預設組合選擇（穩健/激進/均衡）
 * 2. 滑動條調參區域
 * 3. 訓練預覽
 */

import React, { useState } from 'react';
import { X, Sliders, Zap, Shield, Target, Play, Bot, Settings2 } from 'lucide-react';

// 預設參數組合
const PRESET_CONFIGS = {
    balanced: {
        name: '均衡模式',
        icon: Target,
        description: '平衡風險與收益，適合大多數用戶',
        params: {
            n_estimators: 200,
            learning_rate: 0.1,
            max_depth: 8,
            rsi_period: 14,
            momentum_window: 20
        }
    },
    conservative: {
        name: '穩健模式',
        icon: Shield,
        description: '降低風險，減少虧損可能',
        params: {
            n_estimators: 100,
            learning_rate: 0.05,
            max_depth: 5,
            rsi_period: 21,
            momentum_window: 50
        }
    },
    aggressive: {
        name: '激進模式',
        icon: Zap,
        description: '追求高收益，承受較高風險',
        params: {
            n_estimators: 500,
            learning_rate: 0.2,
            max_depth: 15,
            rsi_period: 7,
            momentum_window: 10
        }
    }
};

// 參數範圍定義
const PARAM_RANGES = {
    n_estimators: { min: 50, max: 500, step: 50, label: '樹數量 (n_estimators)', unit: '' },
    learning_rate: { min: 0.01, max: 0.3, step: 0.01, label: '學習率 (learning_rate)', unit: '' },
    max_depth: { min: 3, max: 15, step: 1, label: '最大深度 (max_depth)', unit: '' },
    rsi_period: { min: 7, max: 21, step: 1, label: 'RSI 週期', unit: '天' },
    momentum_window: { min: 5, max: 50, step: 5, label: '動能窗口', unit: '天' }
};

export default function ModelTrainingModal({ onClose, onTrain }) {
    const [selectedPreset, setSelectedPreset] = useState('balanced');
    const [customParams, setCustomParams] = useState(PRESET_CONFIGS.balanced.params);
    const [isTraining, setIsTraining] = useState(false);
    const [modelType, setModelType] = useState('lightgbm');

    // 選擇預設時更新參數
    const handlePresetChange = (preset) => {
        setSelectedPreset(preset);
        setCustomParams(PRESET_CONFIGS[preset].params);
    };

    // 滑動條變更
    const handleParamChange = (key, value) => {
        setCustomParams(prev => ({ ...prev, [key]: parseFloat(value) }));
        setSelectedPreset('custom'); // 切換為自定義
    };

    // 開始訓練
    const handleTrain = async () => {
        setIsTraining(true);
        try {
            if (onTrain) {
                const response = await onTrain({
                    model_type: modelType,
                    preset: selectedPreset,
                    params: customParams
                });

                // 檢查是否有 job_id，表示異步任務啟動成功
                if (response && response.job_id) {
                    alert(`訓練任務已啟動 (Job ID: ${response.job_id})\n\n請前往「AI Lab」頁面查看實時訓練進度與日誌。`);
                    onClose(); // 關閉模態框
                }
            }
        } catch (e) {
            console.error('Training error:', e);
            alert('訓練請求發送失敗，請稍後重試。');
        }
        setIsTraining(false);
    };

    return (
        <div className="modal-overlay" style={styles.overlay}>
            <div className="modal-content" style={styles.modal}>
                {/* 標題 */}
                <div style={styles.header}>
                    <div style={styles.titleRow}>
                        <Bot size={24} style={{ color: '#6366f1' }} />
                        <h2 style={styles.title}>AI 模型訓練場</h2>
                    </div>
                    <button onClick={onClose} style={styles.closeBtn}>
                        <X size={20} />
                    </button>
                </div>

                {/* 模型類型選擇 */}
                <div style={styles.section}>
                    <label style={styles.sectionLabel}>
                        <Settings2 size={14} /> 選擇模型類型
                    </label>
                    <div style={styles.modelTypeRow}>
                        {[
                            { id: 'lightgbm', label: '梯度提升樹 (LightGBM)' },
                            { id: 'mlp', label: '神經網絡 (MLP)' },
                            { id: 'rsi', label: 'RSI 回歸' },
                            { id: 'momentum', label: '動能趨勢' }
                        ].map(type => (
                            <button
                                key={type.id}
                                onClick={() => setModelType(type.id)}
                                style={{
                                    ...styles.modelTypeBtn,
                                    ...(modelType === type.id ? styles.modelTypeBtnActive : {})
                                }}
                            >
                                {type.label}
                            </button>
                        ))}
                    </div>
                </div>

                {/* 預設組合選擇 */}
                <div style={styles.section}>
                    <label style={styles.sectionLabel}>
                        <Target size={14} /> 預設組合
                    </label>
                    <div style={styles.presetRow}>
                        {Object.entries(PRESET_CONFIGS).map(([key, config]) => {
                            const IconComp = config.icon;
                            return (
                                <button
                                    key={key}
                                    onClick={() => handlePresetChange(key)}
                                    style={{
                                        ...styles.presetBtn,
                                        ...(selectedPreset === key ? styles.presetBtnActive : {})
                                    }}
                                >
                                    <IconComp size={20} />
                                    <span style={styles.presetName}>{config.name}</span>
                                    <span style={styles.presetDesc}>{config.description}</span>
                                </button>
                            );
                        })}
                    </div>
                </div>

                {/* 滑動條調參區域 */}
                <div style={styles.section}>
                    <label style={styles.sectionLabel}>
                        <Sliders size={14} /> 參數微調
                        {selectedPreset === 'custom' && <span style={styles.customBadge}>自定義</span>}
                    </label>
                    <div style={styles.slidersArea}>
                        {Object.entries(PARAM_RANGES).map(([key, range]) => (
                            <div key={key} style={styles.sliderRow}>
                                <div style={styles.sliderLabel}>
                                    <span>{range.label}</span>
                                    <span style={styles.sliderValue}>
                                        {customParams[key]}{range.unit}
                                    </span>
                                </div>
                                <input
                                    type="range"
                                    min={range.min}
                                    max={range.max}
                                    step={range.step}
                                    value={customParams[key]}
                                    onChange={(e) => handleParamChange(key, e.target.value)}
                                    style={styles.slider}
                                />
                                <div style={styles.sliderRange}>
                                    <span>{range.min}</span>
                                    <span>{range.max}</span>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                {/* 操作按鈕 */}
                <div style={styles.actions}>
                    <button onClick={onClose} style={styles.cancelBtn}>
                        取消
                    </button>
                    <button
                        onClick={handleTrain}
                        disabled={isTraining}
                        style={styles.trainBtn}
                    >
                        <Play size={16} />
                        {isTraining ? '訓練中...' : '開始訓練'}
                    </button>
                </div>
            </div>
        </div>
    );
}

// 內聯樣式（可後續遷移到 CSS）
const styles = {
    overlay: {
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        backgroundColor: 'rgba(0,0,0,0.6)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 1000
    },
    modal: {
        backgroundColor: '#1e1e2e',
        borderRadius: '16px',
        padding: '24px',
        width: '600px',
        maxHeight: '85vh',
        overflowY: 'auto',
        boxShadow: '0 20px 60px rgba(0,0,0,0.5)'
    },
    header: {
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '20px',
        borderBottom: '1px solid #333',
        paddingBottom: '16px'
    },
    titleRow: {
        display: 'flex',
        alignItems: 'center',
        gap: '12px'
    },
    title: {
        margin: 0,
        color: '#fff',
        fontSize: '1.4rem'
    },
    closeBtn: {
        background: 'none',
        border: 'none',
        color: '#888',
        cursor: 'pointer',
        padding: '4px'
    },
    section: {
        marginBottom: '20px'
    },
    sectionLabel: {
        display: 'flex',
        alignItems: 'center',
        gap: '8px',
        color: '#aaa',
        fontSize: '0.9rem',
        marginBottom: '12px'
    },
    modelTypeRow: {
        display: 'flex',
        gap: '8px'
    },
    modelTypeBtn: {
        flex: 1,
        padding: '10px',
        background: '#2a2a3e',
        border: '1px solid #444',
        borderRadius: '8px',
        color: '#888',
        cursor: 'pointer',
        fontSize: '0.85rem',
        fontWeight: 600
    },
    modelTypeBtnActive: {
        background: '#6366f1',
        borderColor: '#6366f1',
        color: '#fff'
    },
    presetRow: {
        display: 'flex',
        gap: '12px'
    },
    presetBtn: {
        flex: 1,
        padding: '16px 12px',
        background: '#2a2a3e',
        border: '1px solid #444',
        borderRadius: '12px',
        cursor: 'pointer',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        gap: '8px',
        color: '#aaa',
        transition: 'all 0.2s'
    },
    presetBtnActive: {
        background: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
        borderColor: '#6366f1',
        color: '#fff'
    },
    presetName: {
        fontWeight: 600,
        fontSize: '0.95rem'
    },
    presetDesc: {
        fontSize: '0.75rem',
        opacity: 0.7,
        textAlign: 'center'
    },
    customBadge: {
        background: '#f59e0b',
        color: '#000',
        padding: '2px 8px',
        borderRadius: '4px',
        fontSize: '0.7rem',
        marginLeft: '8px'
    },
    slidersArea: {
        background: '#252535',
        borderRadius: '12px',
        padding: '16px'
    },
    sliderRow: {
        marginBottom: '16px'
    },
    sliderLabel: {
        display: 'flex',
        justifyContent: 'space-between',
        color: '#ccc',
        fontSize: '0.85rem',
        marginBottom: '6px'
    },
    sliderValue: {
        color: '#6366f1',
        fontWeight: 600
    },
    slider: {
        width: '100%',
        height: '6px',
        borderRadius: '3px',
        appearance: 'none',
        background: '#444',
        cursor: 'pointer'
    },
    sliderRange: {
        display: 'flex',
        justifyContent: 'space-between',
        color: '#666',
        fontSize: '0.7rem',
        marginTop: '4px'
    },
    actions: {
        display: 'flex',
        gap: '12px',
        marginTop: '24px',
        paddingTop: '16px',
        borderTop: '1px solid #333'
    },
    cancelBtn: {
        flex: 1,
        padding: '12px',
        background: '#2a2a3e',
        border: '1px solid #444',
        borderRadius: '8px',
        color: '#aaa',
        cursor: 'pointer',
        fontSize: '0.95rem'
    },
    trainBtn: {
        flex: 2,
        padding: '12px',
        background: 'linear-gradient(135deg, #22c55e 0%, #16a34a 100%)',
        border: 'none',
        borderRadius: '8px',
        color: '#fff',
        cursor: 'pointer',
        fontSize: '0.95rem',
        fontWeight: 600,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        gap: '8px'
    }
};
