
const API_BASE = '/api/v1'; // Use Proxy

export const API = {
    async getAnalysis(ticker) {
        try {
            const res = await fetch(`${API_BASE}/market/analysis?ticker=${ticker}`);
            return await res.json();
        } catch (e) {
            console.error("API Error:", e);
            return { error: e.message };
        }
    },

    async getValuation(ticker) {
        try {
            const res = await fetch(`${API_BASE}/stock/valuation?ticker=${ticker}`);
            return await res.json();
        } catch (e) {
            console.error("API Error:", e);
            return { error: e.message };
        }
    },

    async runBacktest(ticker, strategy, version = null) {
        try {
            let url = `${API_BASE}/backtest/run?ticker=${ticker}&strategy=${strategy}`;
            if (version) url += `&version=${version}`;
            const res = await fetch(url);
            return await res.json();
        } catch (e) {
            console.error("API Error:", e);
            return { error: e.message };
        }
    },

    async runArena(ticker) {
        try {
            const res = await fetch(`${API_BASE}/arena/battle?ticker=${ticker}`);
            return await res.json();
        } catch (e) {
            console.error("API Error:", e);
            return { error: e.message };
        }
    },

    // Sprint 4: 數據更新 API
    async auditData(tickers = 'AAPL,MSFT,GOOGL,NVDA') {
        try {
            const res = await fetch(`${API_BASE}/data/audit?tickers=${tickers}`);
            return await res.json();
        } catch (e) {
            console.error("API Error:", e);
            return { error: e.message };
        }
    },

    async updateData(tickers = ['AAPL', 'MSFT', 'GOOGL']) {
        try {
            const res = await fetch(`${API_BASE}/data/update`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ tickers })
            });
            return await res.json();
        } catch (e) {
            console.error("API Error:", e);
            return { error: e.message };
        }
    },

    async getUpdateProgress() {
        try {
            const res = await fetch(`${API_BASE}/data/progress`);
            return await res.json();
        } catch (e) {
            console.error("API Error:", e);
            return { error: e.message };
        }
    },

    // Demo Integration: 宏觀態勢感知
    async getMacroOverview() {
        try {
            const res = await fetch(`${API_BASE}/macro/overview`);
            return await res.json();
        } catch (e) {
            console.error("API Error:", e);
            return { error: e.message };
        }
    },

    // AI Integration: Gemini 3 Pro
    async generateAI(type, data = {}) {
        try {
            const res = await fetch(`${API_BASE}/ai/generate`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    type: type,
                    macro_data: data.macroData || {},
                    valuation_data: data.valuationData || {},
                    arena_data: data.arenaData || [],
                    prompt: data.prompt || ''
                })
            });
            return await res.json();
        } catch (e) {
            console.error("AI API Error:", e);
            return { success: false, error: e.message };
        }
    },

    async configureAI(apiUrl, apiKey, model) {
        try {
            const res = await fetch(`${API_BASE}/ai/config`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ api_url: apiUrl, api_key: apiKey, model: model })
            });
            return await res.json();
        } catch (e) {
            console.error("AI Config Error:", e);
            return { success: false, error: e.message };
        }
    },

    // AI Lab APIs (V2)
    async trainModel(modelType, ticker, params) {
        try {
            const res = await fetch(`${API_BASE}/model/train`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ model_type: modelType, ticker, params })
            });
            return await res.json();
        } catch (e) {
            console.error("Train Error:", e);
            return { error: e.message };
        }
    },

    async getTrainStatus(jobId) {
        try {
            const res = await fetch(`${API_BASE}/model/train/status/${jobId}`);
            return await res.json();
        } catch (e) {
            console.error("Train Status Error:", e);
            return { error: e.message };
        }
    },

    async listModels(type = null) {
        try {
            const url = type ? `${API_BASE}/models?type=${type}` : `${API_BASE}/models`;
            const res = await fetch(url);
            return await res.json();
        } catch (e) {
            console.error("List Models Error:", e);
            return { error: e.message };
        }
    },

    async deleteModel(type, version) {
        try {
            const res = await fetch(`${API_BASE}/models?type=${type}&version=${version}`, {
                method: 'DELETE'
            });
            return await res.json();
        } catch (e) {
            console.error("Delete Model Error:", e);
            return { error: e.message };
        }
    },

    async getInference(ticker, modelType = 'lightgbm') {
        try {
            const res = await fetch(`${API_BASE}/model/predict`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ ticker, model_type: modelType })
            });
            return await res.json();
        } catch (e) {
            console.error("Inference Error:", e);
            return { error: e.message };
        }
    }
};
