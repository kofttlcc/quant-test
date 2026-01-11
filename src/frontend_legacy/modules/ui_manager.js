
// UI Manager - Handles DOM updates and Localization

const CN_MAP = {
    "Bull": "牛市",
    "Bear": "熊市",
    "Volatile": "震盪",
    "Unknown": "未知",
    "Undervalued (Strong)": "嚴重低估",
    "Undervalued": "低估",
    "Overvalued": "高估",
    "Fair Value": "合理",
    "Elevated": "風險升高",
    "Critical": "極度危險",
    "Low Risk": "低風險",
    "System Watch": "監控中",
    "Market Volatility Detected": "檢測到市場波動",
    "Favorable Market Conditions": "市場環境有利",
    "High Risk / Crash Warning": "高風險 / 崩盤預警",
    "Waiting for Macro Data...": "等待宏觀數據...",
    "Momentum (Baseline)": "動能策略 (基準)",
    "Momentum (Fast)": "動能策略 (快線)",
    "Momentum (Slow)": "動能策略 (慢線)",
    "Strategy": "策略名稱",
    "Sharpe": "夏普比率",
    "Total Return": "總回報率",
    "Max DD": "最大回撤"
};

/**
 * Translate Text
 * @param {string} text 
 */
export function t(text) {
    return CN_MAP[text] || text;
}

export const UI = {
    setLoading(isLoading) {
        const btn = document.getElementById('run-btn');
        const overlay = document.getElementById('loading-overlay');

        if (isLoading) {
            if (btn) {
                btn.disabled = true;
                btn.innerText = '計算中...';
            }
            if (overlay) overlay.style.display = 'flex';
        } else {
            if (btn) {
                btn.disabled = false;
                btn.innerText = '執行回測';
            }
            if (overlay) overlay.style.display = 'none';
        }
    },

    updateAnalysis(data) {
        if (data.error) return;

        // Regime
        const regimeEl = document.getElementById('val-regime');
        const defconCircle = document.getElementById('defcon-circle');
        const defconLabel = document.getElementById('defcon-label');
        const defconDesc = document.getElementById('defcon-desc');

        if (regimeEl) {
            regimeEl.innerText = t(data.regime);

            let color = '#FFab00'; // Default Volatile
            let defcon = 3;
            let defText = t("Elevated"); // Use key for map
            let defDesc = t("Market Volatility Detected");

            if (data.regime === 'Bull') {
                color = '#00C853';
                defcon = 5;
                defText = t("Low Risk");
                defDesc = t("Favorable Market Conditions");
            } else if (data.regime === 'Bear') {
                color = '#FF3D00';
                defcon = 1;
                defText = t("Critical");
                defDesc = t("High Risk / Crash Warning");
            }

            regimeEl.style.color = color;

            if (defconCircle) {
                defconCircle.innerText = defcon;
                defconCircle.style.borderColor = color;
                defconCircle.style.color = color;
                defconCircle.style.boxShadow = `0 0 15px ${color}40`;
            }
            if (defconLabel) {
                defconLabel.innerText = defText;
                defconLabel.style.color = color;
            }
            if (defconDesc) {
                defconDesc.innerText = defDesc;
            }
        }

        // Sentiment
        const sentEl = document.getElementById('val-sentiment');
        if (sentEl) sentEl.innerText = data.sentiment.score;

        const descEl = document.getElementById('val-sent-desc');
        if (descEl) descEl.innerText = data.sentiment.description;
    },

    updateValuation(data) {
        if (data.error) return;

        // Fair Value
        const fairEl = document.getElementById('val-fair');
        if (fairEl) fairEl.innerText = "$" + data.fair_value.toFixed(2);

        // Upside
        const upsideEl = document.getElementById('val-upside');
        if (upsideEl) {
            const upside = ((data.fair_value - data.current_price) / data.current_price * 100);
            upsideEl.innerText = (upside > 0 ? "+" : "") + upside.toFixed(1) + "% 空間";
            upsideEl.style.color = upside > 0 ? '#00C853' : '#FF3D00';
        }

        // Status
        const statusEl = document.getElementById('val-status');
        if (statusEl) {
            statusEl.innerText = t(data.status);
            if (data.status.includes('Undervalued')) statusEl.style.color = '#00C853';
            else if (data.status.includes('Overvalued')) statusEl.style.color = '#FF3D00';
            else statusEl.style.color = '#ffffff';
        }

        // Models
        const modelsEl = document.getElementById('val-models');
        if (modelsEl && data.models) {
            let text = "";
            if (data.models.DCF) text += `DCF: $${data.models.DCF} `;
            if (data.models.Graham) text += `| Graham: $${data.models.Graham}`;
            modelsEl.innerText = text;
        }
    },

    updateMetrics(metrics) {
        document.getElementById('val-return').innerText = (metrics.Total_Return * 100).toFixed(2) + '%';
        document.getElementById('val-sharpe').innerText = metrics.Sharpe_Ratio.toFixed(2);
        document.getElementById('val-dd').innerText = (metrics.Max_Drawdown * 100).toFixed(2) + '%';
    },

    renderArenaTable(ticker, results, container) {
        container.innerHTML = `
            <div style="padding: 20px; color: white;">
                <h2>⚔️ 策略競技場結果: ${ticker}</h2>
                <table style="width: 100%; border-collapse: collapse; margin-top: 20px;">
                    <thead>
                        <tr style="text-align: left; border-bottom: 2px solid #333;">
                            <th style="padding: 10px;">${t('Strategy')}</th>
                            <th style="padding: 10px;">${t('Sharpe')}</th>
                            <th style="padding: 10px;">${t('Total Return')}</th>
                            <th style="padding: 10px;">${t('Max DD')}</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${results.map((row, index) => `
                            <tr style="border-bottom: 1px solid #333; background: ${index === 0 ? '#1b5e20' : 'transparent'}">
                                <td style="padding: 15px; font-weight: bold;">
                                    ${index === 0 ? '🏆 ' : ''}${t(row.Strategy)}
                                </td>
                                <td style="padding: 15px; color: ${row.Sharpe > 1 ? '#00C853' : '#E0E0E0'}">${row.Sharpe.toFixed(2)}</td>
                                <td style="padding: 15px;">${(row['Total Return'] * 100).toFixed(2)}%</td>
                                <td style="padding: 15px; color: #FF3D00">${(row['Max DD'] * 100).toFixed(2)}%</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
                <div style="margin-top: 20px; font-size: 0.9em; color: #888;">
                    * 獲勝者由夏普比率（風險調整後回報）決定。
                </div>
            </div>
        `;
    }
};
