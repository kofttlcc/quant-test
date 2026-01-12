
import React, { useMemo, useState } from 'react';
import { useSkills } from './hooks/useSkills';
import { SkillCard } from './components/SkillCard';
import { Bot, Search, Loader2, RefreshCw } from 'lucide-react';

function App() {
  const { skills, loading, error, refetch, importSkill } = useSkills();
  const [searchTerm, setSearchTerm] = useState('');

  const filteredSkills = useMemo(() => {
    return skills.filter(skill =>
      skill.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      skill.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
      skill.category.toLowerCase().includes(searchTerm.toLowerCase())
    );
  }, [skills, searchTerm]);

  return (
    <div className="min-h-screen bg-gray-50 text-gray-900 font-sans">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-10">
        <div className="container mx-auto px-4 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="bg-blue-600 p-2 rounded-lg">
              <Bot className="w-6 h-6 text-white" />
            </div>
            <h1 className="text-xl font-bold tracking-tight text-gray-900">
              Antigravity 技能庫
            </h1>
          </div>

          <div className="flex items-center gap-4">
            <div className="relative">
              <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
              <input
                type="text"
                placeholder="搜尋技能..."
                className="pl-9 pr-4 py-2 bg-gray-100 border-none rounded-md text-sm focus:ring-2 focus:ring-blue-500 w-64 outline-none"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>
            <button
              onClick={() => refetch()}
              className="p-2 text-gray-500 hover:text-blue-600 hover:bg-blue-50 rounded-md transition-colors"
            >
              <RefreshCw className="w-5 h-5" />
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        {loading ? (
          <div className="flex flex-col items-center justify-center h-64">
            <Loader2 className="w-8 h-8 text-blue-500 animate-spin mb-4" />
            <p className="text-gray-500">正在加載技能空間...</p>
          </div>
        ) : error ? (
          <div className="bg-red-50 text-red-600 p-4 rounded-lg flex items-center justify-center">
            錯誤: {error}
          </div>
        ) : (
          <>
            <div className="mb-6">
              <h2 className="text-lg font-semibold text-gray-800">
                可用技能 ({filteredSkills.length})
              </h2>
              <p className="text-sm text-gray-500">
                探索並導入技能到您的 Antigravity 代理中。
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
              {filteredSkills.map(skill => (
                <SkillCard key={skill.id} skill={skill} onImport={importSkill} />
              ))}
            </div>

            {filteredSkills.length === 0 && (
              <div className="text-center py-20 text-gray-400">
                沒有找到符合搜尋條件的技能。
              </div>
            )}
          </>
        )}
      </main>
    </div>
  );
}

export default App;
