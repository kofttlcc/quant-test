
import { useMemo, useState, useCallback } from 'react';
import { useSkills } from './hooks/useSkills';
import { SkillCard } from './components/SkillCard';
import { Marketplace } from './components/Marketplace';
import { useToast } from './components/Toast';
import { Bot, Search, Loader2, RefreshCw, LayoutGrid, ShoppingBag, Zap, Trash2 } from 'lucide-react';

function App() {
  const [view, setView] = useState<'local' | 'market'>('local');
  const { skills, loading, error, refetch } = useSkills();
  const [searchTerm, setSearchTerm] = useState('');
  const [transformingAll, setTransformingAll] = useState(false);
  const [uninstallingAll, setUninstallingAll] = useState(false);
  const { showToast } = useToast();

  const filteredSkills = useMemo(() => {
    return skills.filter(skill =>
      (skill.name?.toLowerCase() || '').includes(searchTerm.toLowerCase()) ||
      (skill.description?.toLowerCase() || '').includes(searchTerm.toLowerCase()) ||
      (skill.category?.toLowerCase() || '').includes(searchTerm.toLowerCase())
    );
  }, [skills, searchTerm]);

  const handleTransformAll = async () => {
    if (transformingAll) return;

    setTransformingAll(true);
    showToast('🚀 開始批量轉換所有技能...', 'info', 3000);

    try {
      const response = await fetch('http://localhost:3001/api/skills/transform-all', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });

      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.error || '批量轉換失敗');
      }

      showToast(`✅ ${result.message}`, 'success', 8000);
      setTimeout(() => refetch(), 1000);
    } catch (err: any) {
      showToast(`❌ 批量轉換失敗: ${err.message}`, 'error', 10000);
    } finally {
      setTransformingAll(false);
    }
  };

  const handleUninstallAll = async () => {
    if (!confirm('⚠️ 確定要卸載所有技能嗎？此操作不可逆！')) {
      return;
    }

    setUninstallingAll(true);
    showToast('🗑️ 開始批量卸載所有技能...', 'info', 3000);

    try {
      const response = await fetch('http://localhost:3001/api/skills/uninstall-all', {
        method: 'DELETE'
      });

      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.error || '批量卸載失敗');
      }

      showToast(`🗑️ ${result.message}`, 'success', 8000);
      refetch();
    } catch (err: any) {
      showToast(`❌ 批量卸載失敗: ${err.message}`, 'error', 10000);
    } finally {
      setUninstallingAll(false);
    }
  };

  const handleSkillUninstall = useCallback((skillName: string) => {
    // 刷新列表
    refetch();
  }, [refetch]);

  return (
    <div className="min-h-screen bg-gray-50 text-gray-900 font-sans">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-10">
        <div className="container mx-auto px-4 h-16 flex items-center justify-between">
          <div className="flex items-center gap-8">
            <div className="flex items-center gap-3">
              <div className="bg-blue-600 p-2 rounded-lg">
                <Bot className="w-6 h-6 text-white" />
              </div>
              <h1 className="text-xl font-bold tracking-tight text-gray-900 hidden md:block">
                Antigravity
              </h1>
            </div>

            {/* Navigation */}
            <nav className="flex items-center gap-1 bg-gray-100 p-1 rounded-lg">
              <button
                onClick={() => setView('local')}
                className={`flex items-center gap-2 px-4 py-1.5 rounded-md text-sm font-medium transition-all ${view === 'local'
                  ? 'bg-white text-blue-600 shadow-sm'
                  : 'text-gray-500 hover:text-gray-700'
                  }`}
              >
                <LayoutGrid className="w-4 h-4" />
                本地技能
              </button>
              <button
                onClick={() => setView('market')}
                className={`flex items-center gap-2 px-4 py-1.5 rounded-md text-sm font-medium transition-all ${view === 'market'
                  ? 'bg-white text-blue-600 shadow-sm'
                  : 'text-gray-500 hover:text-gray-700'
                  }`}
              >
                <ShoppingBag className="w-4 h-4" />
                技能市集
              </button>
            </nav>
          </div>

          {view === 'local' && (
            <div className="flex items-center gap-4">
              <div className="relative hidden md:block">
                <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                <input
                  type="text"
                  placeholder="搜尋已安裝技能..."
                  className="pl-9 pr-4 py-2 bg-gray-100 border-none rounded-md text-sm focus:ring-2 focus:ring-blue-500 w-64 outline-none"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </div>
              <button
                onClick={() => refetch()}
                className="p-2 text-gray-500 hover:text-blue-600 hover:bg-blue-50 rounded-md transition-colors"
                title="重新整理列表"
              >
                <RefreshCw className="w-5 h-5" />
              </button>
            </div>
          )}
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        {view === 'market' ? (
          <Marketplace />
        ) : (
          <>
            {loading ? (
              <div className="flex flex-col items-center justify-center h-64">
                <Loader2 className="w-8 h-8 text-blue-500 animate-spin mb-4" />
                <p className="text-gray-500">正在掃描本地技能...</p>
              </div>
            ) : error ? (
              <div className="bg-red-50 text-red-600 p-4 rounded-lg flex items-center justify-center">
                錯誤: {error}
              </div>
            ) : (
              <>
                <div className="mb-6 flex justify-between items-end">
                  <div>
                    <h2 className="text-lg font-semibold text-gray-800">
                      已安裝技能 ({filteredSkills.length})
                    </h2>
                    <p className="text-sm text-gray-500">
                      管理您的 Antigravity 代理當前擁有的能力。
                    </p>
                  </div>

                  {/* 批量操作按鈕 */}
                  <div className="flex gap-3">
                    {/* 一鍵全部卸載 */}
                    <button
                      onClick={handleUninstallAll}
                      disabled={uninstallingAll || filteredSkills.length === 0}
                      className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${uninstallingAll || filteredSkills.length === 0
                          ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                          : 'bg-red-100 text-red-700 hover:bg-red-200 cursor-pointer'
                        }`}
                    >
                      {uninstallingAll ? (
                        <Loader2 className="w-4 h-4 animate-spin" />
                      ) : (
                        <Trash2 className="w-4 h-4" />
                      )}
                      {uninstallingAll ? '卸載中...' : '🗑️ 全部卸載'}
                    </button>

                    {/* 一鍵全部適配 */}
                    <button
                      onClick={handleTransformAll}
                      disabled={transformingAll || filteredSkills.length === 0}
                      className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${transformingAll || filteredSkills.length === 0
                          ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                          : 'bg-gradient-to-r from-purple-600 to-indigo-600 text-white hover:from-purple-700 hover:to-indigo-700 cursor-pointer shadow-md'
                        }`}
                    >
                      {transformingAll ? (
                        <Loader2 className="w-4 h-4 animate-spin" />
                      ) : (
                        <Zap className="w-4 h-4" />
                      )}
                      {transformingAll ? '適配中...' : '⚡ 全部適配'}
                    </button>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                  {filteredSkills.map(skill => (
                    <SkillCard
                      key={skill.id}
                      skill={skill}
                      onUninstall={handleSkillUninstall}
                    />
                  ))}
                </div>

                {filteredSkills.length === 0 && (
                  <div className="text-center py-20 text-gray-400">
                    沒有找到符合搜尋條件的技能。
                  </div>
                )}
              </>
            )}
          </>
        )}
      </main>
    </div>
  );
}

export default App;
