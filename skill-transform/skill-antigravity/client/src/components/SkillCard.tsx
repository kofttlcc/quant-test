
import type { Skill } from '../types/skill';
import { useToast } from './Toast';
import { RefreshCw, FileText, Loader2, Check, Trash2 } from 'lucide-react';
import { useState, useEffect } from 'react';

interface SkillCardProps {
    skill: Skill;
    onUninstall?: (skillName: string) => void;
}

export const SkillCard: React.FC<SkillCardProps> = ({ skill, onUninstall }) => {
    const [transforming, setTransforming] = useState(false);
    const [uninstalling, setUninstalling] = useState(false);
    const [adapted, setAdapted] = useState(false);
    const { showToast } = useToast();

    // 檢查是否已經適配過
    useEffect(() => {
        checkAdaptedStatus();
    }, [skill.name]);

    const checkAdaptedStatus = async () => {
        try {
            const response = await fetch(`http://localhost:3001/api/skills/check-adapted/${encodeURIComponent(skill.name)}`);
            if (response.ok) {
                const result = await response.json();
                setAdapted(result.adapted);
            }
        } catch {
            // 忽略錯誤
        }
    };

    const handleTransform = async () => {
        if (adapted) return;

        setTransforming(true);
        try {
            const response = await fetch('http://localhost:3001/api/skills/transform', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ skillName: skill.name })
            });

            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.error || result.message || '轉換失敗');
            }

            setAdapted(true);
            showToast(`✅ ${skill.name} 轉換成功！`, 'success', 5000);
        } catch (err: any) {
            showToast(`❌ 轉換失敗: ${err.message}`, 'error', 10000);
        } finally {
            setTransforming(false);
        }
    };

    const handleUninstall = async () => {
        if (!confirm(`確定要卸載技能「${skill.name}」嗎？此操作不可逆。`)) {
            return;
        }

        setUninstalling(true);
        try {
            const response = await fetch(`http://localhost:3001/api/skills/uninstall/${encodeURIComponent(skill.name)}`, {
                method: 'DELETE'
            });

            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.error || '卸載失敗');
            }

            showToast(`🗑️ ${skill.name} 已卸載`, 'success', 5000);

            // 通知父組件刷新列表
            if (onUninstall) {
                onUninstall(skill.name);
            }
        } catch (err: any) {
            showToast(`❌ 卸載失敗: ${err.message}`, 'error', 10000);
        } finally {
            setUninstalling(false);
        }
    };

    return (
        <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow border border-gray-100 flex flex-col justify-between h-full">
            <div>
                <div className="flex items-center justify-between mb-2">
                    <h3 className="text-xl font-bold text-gray-800 flex items-center gap-2">
                        <FileText className="w-5 h-5 text-blue-500" />
                        {skill.name}
                    </h3>
                    <div className="flex items-center gap-2">
                        {adapted && (
                            <span className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded-full font-medium flex items-center gap-1">
                                <Check className="w-3 h-3" />
                                已適配
                            </span>
                        )}
                        <span className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded-full uppercase tracking-wide font-medium">
                            {skill.category || 'general'}
                        </span>
                    </div>
                </div>

                <p className="text-gray-600 text-sm mb-4 line-clamp-3">
                    {skill.description || 'No description provided.'}
                </p>
            </div>

            <div className="mt-4 pt-4 border-t border-gray-100 flex justify-end gap-2">
                {/* 適配按鈕 */}
                <button
                    onClick={handleTransform}
                    disabled={transforming || adapted}
                    className={`flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-colors ${adapted
                            ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                            : transforming
                                ? 'bg-gray-100 text-gray-400 cursor-wait'
                                : 'bg-purple-100 text-purple-700 hover:bg-purple-200 cursor-pointer'
                        }`}
                    title={adapted ? '已完成適配' : '將此技能轉換為 Antigravity 專屬格式'}
                >
                    {transforming ? (
                        <Loader2 className="w-4 h-4 animate-spin" />
                    ) : adapted ? (
                        <Check className="w-4 h-4" />
                    ) : (
                        <RefreshCw className="w-4 h-4" />
                    )}
                    {adapted ? '已適配' : transforming ? '適配中...' : '🔄 適配'}
                </button>

                {/* 卸載按鈕 */}
                <button
                    onClick={handleUninstall}
                    disabled={uninstalling}
                    className={`flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-colors ${uninstalling
                            ? 'bg-gray-100 text-gray-400 cursor-wait'
                            : 'bg-red-100 text-red-700 hover:bg-red-200 cursor-pointer'
                        }`}
                    title="卸載此技能"
                >
                    {uninstalling ? (
                        <Loader2 className="w-4 h-4 animate-spin" />
                    ) : (
                        <Trash2 className="w-4 h-4" />
                    )}
                    {uninstalling ? '卸載中...' : '卸載'}
                </button>
            </div>
        </div>
    );
};
