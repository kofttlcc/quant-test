
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

export const useMarketplace = () => {
    const [data, setData] = useState<MarketplaceData | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [importing, setImporting] = useState<string | null>(null);

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

    const importFromMarket = async (url: string, name: string) => {
        try {
            setImporting(name);
            const response = await fetch('http://localhost:3001/api/skills/import', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ url })
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || '導入失敗');
            }

            const result = await response.json();
            alert(`成功導入技能: ${result.message}`);
        } catch (err: any) {
            alert(`導入失敗: ${err.message}`);
        } finally {
            setImporting(null);
        }
    };

    return { data, loading, error, importFromMarket, importing };
};
