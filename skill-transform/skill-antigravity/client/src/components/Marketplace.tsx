
import React from 'react';
import { useMarketplace } from '../hooks/useMarketplace';
import { Download, Loader2, Tag, Globe, ExternalLink } from 'lucide-react';

export const Marketplace = () => {
    const { data, loading, error, importFromMarket, importing } = useMarketplace();

    if (loading) {
        return (
            <div className="flex flex-col items-center justify-center h-64">
                <Loader2 className="w-8 h-8 text-blue-500 animate-spin mb-4" />
                <p className="text-gray-500">正在連接到 Antigravity 市集...</p>
            </div>
        );
    }

    if (error) {
        return (
            <div className="bg-red-50 text-red-600 p-4 rounded-lg text-center">
                錯誤: {error}
            </div>
        );
    }

    if (!data) return null;

    return (
        <div className="space-y-8">
            <div className="bg-gradient-to-r from-blue-600 to-indigo-700 rounded-2xl p-8 text-white">
                <h2 className="text-3xl font-bold mb-2">技能市集</h2>
                <p className="opacity-90">探索由社區和官方提供的精選技能，一鍵擴展您的代理能力。</p>
                <div className="mt-4 text-sm opacity-75">
                    版本: {data.version} | 最後更新: {data.last_updated}
                </div>
            </div>

            {data.categories.map((category) => (
                <div key={category.id} className="space-y-4">
                    <div className="flex items-center gap-2 border-b border-gray-200 pb-2">
                        <Globe className="w-5 h-5 text-gray-500" />
                        <h3 className="text-xl font-bold text-gray-800">{category.name.zh}</h3>
                        <span className="text-sm text-gray-500 ml-2">- {category.description.zh}</span>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-2 xl:grid-cols-3 gap-6">
                        {category.repositories.map((repo) => (
                            <div key={repo.url} className="bg-white rounded-xl border border-gray-200 p-6 hover:shadow-lg transition-shadow flex flex-col">
                                <div className="flex justify-between items-start mb-4">
                                    <div>
                                        <h4 className="text-lg font-bold text-gray-900">{repo.name}</h4>
                                        <a
                                            href={repo.url}
                                            target="_blank"
                                            rel="noreferrer"
                                            className="text-xs text-blue-500 flex items-center gap-1 hover:underline mt-1"
                                        >
                                            查看源碼 <ExternalLink className="w-3 h-3" />
                                        </a>
                                    </div>
                                    {repo.featured && (
                                        <span className="bg-amber-100 text-amber-800 text-xs px-2 py-1 rounded-full font-medium">
                                            精選
                                        </span>
                                    )}
                                </div>

                                <p className="text-gray-600 text-sm mb-4 flex-grow">
                                    {repo.description.zh}
                                </p>

                                <div className="flex flex-wrap gap-2 mb-6">
                                    {repo.tags.map(tag => (
                                        <span key={tag} className="flex items-center gap-1 bg-gray-100 text-gray-600 px-2 py-1 rounded text-xs">
                                            <Tag className="w-3 h-3" /> {tag}
                                        </span>
                                    ))}
                                </div>

                                <button
                                    onClick={() => importFromMarket(repo.url, repo.name)}
                                    disabled={!!importing}
                                    className={`w-full py-2 rounded-lg flex items-center justify-center gap-2 transition-colors ${importing === repo.name
                                            ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                                            : 'bg-blue-600 hover:bg-blue-700 text-white'
                                        }`}
                                >
                                    {importing === repo.name ? (
                                        <>
                                            <Loader2 className="w-4 h-4 animate-spin" />
                                            正在下載...
                                        </>
                                    ) : (
                                        <>
                                            <Download className="w-4 h-4" />
                                            下載並安裝
                                        </>
                                    )}
                                </button>
                            </div>
                        ))}
                    </div>
                </div>
            ))}
        </div>
    );
};
