
import { useState, useEffect } from 'react';

export interface MarketplaceSkill {
    url: string;
    name: string;
    description: {
        en: string;
        zh: string;
    };
    tags: string[];
    featured: boolean;
}

export interface MarketplaceCategory {
    id: string;
    name: {
        en: string;
        zh: string;
    };
    description: {
        en: string;
        zh: string;
    };
    repositories: MarketplaceSkill[];
}

export interface MarketplaceData {
    version: string;
    last_updated: string;
    categories: MarketplaceCategory[];
}

export interface ImportResult {
    success: boolean;
    message: string;
}

export const useMarketplace = () => {
    const [data, setData] = useState<MarketplaceData | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [importing, setImporting] = useState<string | null>(null);
    const [lastResult, setLastResult] = useState<ImportResult | null>(null);

    useEffect(() => {
        fetchMarketplace();
    }, []);

    const fetchMarketplace = async () => {
        try {
            setLoading(true);
            const response = await fetch('http://localhost:3001/api/market/features');
            if (!response.ok) {
                throw new Error('無法加載市集數據');
            }
            const result = await response.json();
            setData(result);
        } catch (err: any) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const importFromMarket = async (url: string, name: string): Promise<ImportResult> => {
        try {
            setImporting(name);
            setLastResult(null);

            const response = await fetch('http://localhost:3001/api/skills/import', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ url })
            });

            const resultData = await response.json();

            if (!response.ok) {
                const errorMessage = resultData.error || '導入失敗';
                const result = { success: false, message: `❌ 導入失敗: ${errorMessage}` };
                setLastResult(result);
                return result;
            }

            const result = { success: true, message: `✅ ${resultData.message}` };
            setLastResult(result);
            return result;
        } catch (err: any) {
            const result = { success: false, message: `❌ 網絡錯誤: ${err.message}` };
            setLastResult(result);
            return result;
        } finally {
            setImporting(null);
        }
    };

    const clearResult = () => setLastResult(null);

    return { data, loading, error, importFromMarket, importing, lastResult, clearResult };
};
