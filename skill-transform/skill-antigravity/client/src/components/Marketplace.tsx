
import { useState, useEffect, useCallback } from 'react';
import { useMarketplace } from '../hooks/useMarketplace';
import { useToast } from './Toast';
import { Download, Loader2, Tag, Globe, ExternalLink, Check, Plus, X, Trash2, RefreshCw } from 'lucide-react';

export const Marketplace = () => {
    const { data, loading, error, importFromMarket, importing } = useMarketplace();
    const { showToast } = useToast();
    // 使用 Map 存儲: repoUrl/repoName -> 本地安裝的技能名稱
    const [installedMap, setInstalledMap] = useState<Map<string, string>>(new Map());
    const [showAddSource, setShowAddSource] = useState(false);
    const [customUrl, setCustomUrl] = useState('');
    const [customInstalling, setCustomInstalling] = useState(false);
    const [uninstalling, setUninstalling] = useState<string | null>(null);

    // 獲取已安裝的技能列表
    const fetchInstalledSkills = useCallback(async () => {
        try {
            const response = await fetch('http://localhost:3001/api/skills/local');
            if (response.ok) {
                const skills = await response.json();
                const newMap = new Map<string, string>();

                // 建立技能名稱到本地名稱的映射
                for (const skill of skills) {
                    const lowerName = skill.name.toLowerCase();
                    newMap.set(lowerName, skill.name);
                }

                setInstalledMap(newMap);
            }
        } catch {
            // 忽略錯誤
        }
    }, []);

    useEffect(() => {
        fetchInstalledSkills();
    }, [fetchInstalledSkills]);

    // 檢查技能是否已安裝
    const isSkillInstalled = (repoName: string, repoUrl: string): boolean => {
        const urlName = repoUrl.split('/').pop()?.replace('.git', '')?.toLowerCase() || '';
        const repoNameLower = repoName.toLowerCase();
        return installedMap.has(repoNameLower) || installedMap.has(urlName);
    };

    // 獲取已安裝技能的本地名稱
    const getInstalledName = (repoName: string, repoUrl: string): string => {
        const urlName = repoUrl.split('/').pop()?.replace('.git', '')?.toLowerCase() || '';
        const repoNameLower = repoName.toLowerCase();
        return installedMap.get(repoNameLower) || installedMap.get(urlName) || repoName;
    };

    const handleImport = async (url: string, name: string) => {
        const result = await importFromMarket(url, name);
        showToast(
            result.message,
            result.success ? 'success' : 'error',
            result.success ? 5000 : 10000
        );

        if (result.success) {
            // 立即更新狀態 - 使用多種可能的名稱
            const urlName = url.split('/').pop()?.replace('.git', '')?.toLowerCase() || '';
            setInstalledMap(prev => {
                const newMap = new Map(prev);
                newMap.set(name.toLowerCase(), name);
                newMap.set(urlName, name);
                return newMap;
            });
            // 不再自動重新獲取，避免狀態被覆蓋
        }
    };

    const handleUninstall = async (url: string, skillName: string) => {
        if (!confirm(`確定要卸載技能「${skillName}」嗎？`)) {
            return;
        }

        setUninstalling(url);

        try {
            const response = await fetch(`http://localhost:3001/api/skills/uninstall/${encodeURIComponent(skillName)}`, {
                method: 'DELETE'
            });

            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.error || '卸載失敗');
            }

            showToast(`🗑️ ${skillName} 已卸載`, 'success', 5000);

            // 更新已安裝狀態
            const urlName = url.split('/').pop()?.replace('.git', '')?.toLowerCase() || '';
            setInstalledMap(prev => {
                const newMap = new Map(prev);
                newMap.delete(skillName.toLowerCase());
                newMap.delete(urlName);
                return newMap;
            });
        } catch (err: any) {
            showToast(`❌ 卸載失敗: ${err.message}`, 'error', 10000);
        } finally {
            setUninstalling(null);
        }
    };

    const handleCustomInstall = async () => {
        if (!customUrl.trim()) {
            showToast('❌ 請輸入有效的 Git URL', 'error', 5000);
            return;
        }

        setCustomInstalling(true);

        try {
            const response = await fetch('http://localhost:3001/api/skills/import', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url: customUrl.trim() })
            });

            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.error || '安裝失敗');
            }

            showToast(`✅ ${result.message}`, 'success', 8000);
            setCustomUrl('');
            setShowAddSource(false);
            // 刷新已安裝列表
            fetchInstalledSkills();
        } catch (err: any) {
            showToast(`❌ 安裝失敗: ${err.message}`, 'error', 10000);
        } finally {
            setCustomInstalling(false);
        }
    };

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
                <div className="flex justify-between items-start">
                    <div>
                        <h2 className="text-3xl font-bold mb-2">技能市集</h2>
                        <p className="opacity-90">探索由社區和官方提供的精選技能，一鍵擴展您的代理能力。</p>
                        <div className="mt-4 text-sm opacity-75">
                            版本: {data.version} | 最後更新: {data.last_updated}
                        </div>
                    </div>

                    {/* 添加技能源按鈕 */}
                    <button
                        onClick={() => setShowAddSource(true)}
                        className="flex items-center gap-2 bg-white/20 hover:bg-white/30 px-4 py-2 rounded-lg text-sm font-medium transition-colors cursor-pointer"
                    >
                        <Plus className="w-4 h-4" />
                        添加技能源
                    </button>
                </div>
            </div>

            {/* 添加技能源模態框 */}
            {showAddSource && (
                <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
                    <div className="bg-white rounded-xl p-6 w-full max-w-lg shadow-2xl">
                        <div className="flex justify-between items-center mb-4">
                            <h3 className="text-xl font-bold text-gray-800">添加自定義技能源</h3>
                            <button
                                onClick={() => setShowAddSource(false)}
                                className="text-gray-400 hover:text-gray-600"
                            >
                                <X className="w-5 h-5" />
                            </button>
                        </div>

                        <p className="text-gray-600 text-sm mb-4">
                            輸入包含 SKILL.md 文件的 Git 倉庫 URL，系統將自動下載並安裝其中的技能。
                        </p>

                        <input
                            type="text"
                            placeholder="https://github.com/username/skill-repo"
                            value={customUrl}
                            onChange={(e) => setCustomUrl(e.target.value)}
                            className="w-full px-4 py-3 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none mb-4"
                        />

                        <div className="flex gap-3">
                            <button
                                onClick={() => setShowAddSource(false)}
                                className="flex-1 py-2 border border-gray-300 rounded-lg text-gray-600 hover:bg-gray-50 transition-colors"
                            >
                                取消
                            </button>
                            <button
                                onClick={handleCustomInstall}
                                disabled={customInstalling}
                                className={`flex-1 py-2 rounded-lg flex items-center justify-center gap-2 transition-colors ${customInstalling
                                        ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                                        : 'bg-blue-600 text-white hover:bg-blue-700 cursor-pointer'
                                    }`}
                            >
                                {customInstalling ? (
                                    <>
                                        <Loader2 className="w-4 h-4 animate-spin" />
                                        安裝中...
                                    </>
                                ) : (
                                    <>
                                        <Download className="w-4 h-4" />
                                        安裝
                                    </>
                                )}
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {data.categories.map((category) => (
                <div key={category.id} className="space-y-4">
                    <div className="flex items-center gap-2 border-b border-gray-200 pb-2">
                        <Globe className="w-5 h-5 text-gray-500" />
                        <h3 className="text-xl font-bold text-gray-800">{category.name.zh}</h3>
                        <span className="text-sm text-gray-500 ml-2">- {category.description.zh}</span>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-2 xl:grid-cols-3 gap-6">
                        {category.repositories.map((repo) => {
                            const isInstalled = isSkillInstalled(repo.name, repo.url);
                            const installedName = getInstalledName(repo.name, repo.url);
                            const isUninstalling = uninstalling === repo.url;

                            return (
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
                                        <div className="flex items-center gap-2">
                                            {isInstalled && (
                                                <span className="bg-green-100 text-green-700 text-xs px-2 py-1 rounded-full font-medium flex items-center gap-1">
                                                    <Check className="w-3 h-3" />
                                                    已安裝
                                                </span>
                                            )}
                                            {repo.featured && (
                                                <span className="bg-amber-100 text-amber-800 text-xs px-2 py-1 rounded-full font-medium">
                                                    精選
                                                </span>
                                            )}
                                        </div>
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

                                    {/* 操作按鈕 */}
                                    {isInstalled ? (
                                        <div className="flex gap-2">
                                            {/* 卸載按鈕 */}
                                            <button
                                                onClick={() => handleUninstall(repo.url, installedName)}
                                                disabled={isUninstalling}
                                                className={`flex-1 py-2 rounded-lg flex items-center justify-center gap-2 transition-colors ${isUninstalling
                                                        ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                                                        : 'bg-red-100 text-red-700 hover:bg-red-200 cursor-pointer'
                                                    }`}
                                            >
                                                {isUninstalling ? (
                                                    <>
                                                        <Loader2 className="w-4 h-4 animate-spin" />
                                                        卸載中...
                                                    </>
                                                ) : (
                                                    <>
                                                        <Trash2 className="w-4 h-4" />
                                                        卸載
                                                    </>
                                                )}
                                            </button>

                                            {/* 更新按鈕 */}
                                            <button
                                                onClick={() => handleImport(repo.url, repo.name)}
                                                disabled={!!importing}
                                                className={`py-2 px-4 rounded-lg flex items-center justify-center gap-2 transition-colors ${importing === repo.name
                                                        ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                                                        : 'bg-blue-100 text-blue-700 hover:bg-blue-200 cursor-pointer'
                                                    }`}
                                                title="檢查更新並重新安裝"
                                            >
                                                {importing === repo.name ? (
                                                    <Loader2 className="w-4 h-4 animate-spin" />
                                                ) : (
                                                    <RefreshCw className="w-4 h-4" />
                                                )}
                                                更新
                                            </button>
                                        </div>
                                    ) : (
                                        /* 下載安裝按鈕 */
                                        <button
                                            onClick={() => handleImport(repo.url, repo.name)}
                                            disabled={!!importing}
                                            className={`w-full py-2 rounded-lg flex items-center justify-center gap-2 transition-colors ${importing === repo.name
                                                    ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                                                    : 'bg-blue-600 hover:bg-blue-700 text-white cursor-pointer'
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
                                    )}
                                </div>
                            );
                        })}
                    </div>
                </div>
            ))}
        </div>
    );
};
