
const API_BASE = 'http://127.0.0.1:5001/api/v1';

export const API = {
    /**
     * Fetch Market Analysis (Regime, Sentiment)
     * @param {string} ticker 
     */
    async getAnalysis(ticker) {
        try {
            const res = await fetch(`${API_BASE}/market/analysis?ticker=${ticker}`);
            return await res.json();
        } catch (e) {
            console.error("API Error (Analysis):", e);
            return { error: e.message };
        }
    },

    /**
     * Fetch Stock Valuation
     * @param {string} ticker 
     */
    async getValuation(ticker) {
        try {
            const res = await fetch(`${API_BASE}/stock/valuation?ticker=${ticker}`);
            return await res.json();
        } catch (e) {
            console.error("API Error (Valuation):", e);
            return { error: e.message };
        }
    },

    /**
     * Run Standard Backtest
     * @param {string} ticker 
     * @param {string} strategy 
     */
    async runBacktest(ticker, strategy) {
        try {
            const res = await fetch(`${API_BASE}/backtest/run?ticker=${ticker}&strategy=${strategy}`);
            return await res.json();
        } catch (e) {
            console.error("API Error (Backtest):", e);
            return { error: e.message };
        }
    },

    /**
     * Run Multi-Strategy Arena
     * @param {string} ticker 
     */
    async runArena(ticker) {
        try {
            const res = await fetch(`${API_BASE}/arena/battle?ticker=${ticker}`);
            return await res.json();
        } catch (e) {
            console.error("API Error (Arena):", e);
            return { error: e.message };
        }
    }
};
