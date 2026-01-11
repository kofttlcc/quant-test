// app.js - Main Entry Point (Modular Architecture)
import { API } from './modules/api_client.js';
import { UI, t } from './modules/ui_manager.js';
import { ChartManager } from './modules/chart_manager.js';

document.addEventListener('DOMContentLoaded', () => {
    // 1. Initialize Chart Engine
    ChartManager.init();

    // 2. Auto-Init on Load (Default Ticker: AAPL)
    const input = document.getElementById('ticker-input');
    const defaultTicker = input.value || 'AAPL';

    console.log("System Upgrade: Auto-fetching data for:", defaultTicker);
    loadSidePanels(defaultTicker);

    // 3. Setup Event Listeners
    setupEventListeners();
});

function setupEventListeners() {
    const btn = document.getElementById('run-btn');
    const input = document.getElementById('ticker-input');

    btn.addEventListener('click', async () => {
        const ticker = input.value.toUpperCase();
        if (!ticker) return;

        UI.setLoading(true);

        try {
            const strategy = document.getElementById('strategy-select').value;

            if (strategy === 'arena') {
                // --- Arena Mode ---
                const data = await API.runArena(ticker);
                if (data.error) {
                    alert(data.error);
                } else {
                    // Use Chart Container for Table
                    UI.renderArenaTable(ticker, data.results, ChartManager.getContainer());
                }
            } else {
                // --- Standard Backtest ---
                // Ensure Chart is reset if coming from Arena (re-init if needed or just clear HTML)
                // Since Arena overwrites InnerHTML, we might need to Re-Create chart if user goes back.
                // For simplicity, we assume ChartManager can handle updates or we reload page for now.
                // Ideally: Check if chart container has chart canvas, if not, re-init.
                // Let's rely on ChartManager.init() being idempotent but we need to clear HTML if it was table.
                if (ChartManager.getContainer().innerHTML.includes('table')) {
                    ChartManager.getContainer().innerHTML = ''; // Clear table
                    // Lightweight charts might need full re-init 
                    // Trick: Refresh page might be safer for Phase 9, but let's try auto-fix
                    window.location.reload(); // Simplest fix for switching View Modes without Router
                    return;
                }

                const data = await API.runBacktest(ticker, strategy);

                if (data.error) {
                    alert('錯誤: ' + data.error);
                } else {
                    UI.updateMetrics(data.metrics);

                    if (data.dates && data.equity_curve) {
                        const equityData = data.dates.map((date, index) => ({
                            time: date,
                            value: data.equity_curve[index]
                        }));
                        ChartManager.update([], equityData);
                    }
                }
            }

            // Always Refresh Side Data
            loadSidePanels(ticker);

        } catch (e) {
            console.error(e);
            alert('系統錯誤');
        } finally {
            UI.setLoading(false);
        }
    });
}

async function loadSidePanels(ticker) {
    const analysis = await API.getAnalysis(ticker);
    UI.updateAnalysis(analysis);

    const valuation = await API.getValuation(ticker);
    UI.updateValuation(valuation);
}

// Make globally available for Debug if needed
window.runArena = API.runArena;

