
const API_BASE = 'http://127.0.0.1:8000';

export interface SentinelReport {
    verdict: string;
    verdict_color: string;
    risk_score: number;
    valuation_status: string;
    reasons: string[];
    metrics: {
        price: number;
        ma200: number;
        vix: number;
        z_score: number;
    };
    components: any;
}

export interface ValuationDetail {
    ticker: string;
    current_price: number;
    composite_value: number;
    margin_of_safety: number;
    status: string;
    confidence: string;
    method_values: {
        dcf: number;
        graham: number;
        relative_pe: number;
        relative_pb: number;
    };
    sentiment_impact?: {
        score: number;
        wacc_used: number;
    }
}

export interface MLSignalReport {
    regime: string;
    signal: number;
    confidence: number;
    position_size: number;
    risk_score: number;
    strategy_weights: Record<string, number>;
}

export const api = {
    getMacroReport: async (): Promise<SentinelReport> => {
        const res = await fetch(`${API_BASE}/api/macro/report`);
        if (!res.ok) throw new Error('Failed to fetch macro report');
        return res.json();
    },

    getValuation: async (ticker: string): Promise<ValuationDetail> => {
        const res = await fetch(`${API_BASE}/api/stock/${ticker}/valuation`);
        if (!res.ok) throw new Error('Failed to fetch valuation');
        return res.json();
    },

    getMLSignal: async (ticker: string): Promise<MLSignalReport> => {
        const res = await fetch(`${API_BASE}/api/stock/${ticker}/ml-signal`);
        if (!res.ok) throw new Error('Failed to fetch ML signal');
        return res.json();
    }
};
