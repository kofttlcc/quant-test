
import React from 'react';
import type { Skill } from '../types/skill';
import { Download, FileText } from 'lucide-react';

interface SkillCardProps {
    skill: Skill;
    onImport: (id: string) => void;
}

export const SkillCard: React.FC<SkillCardProps> = ({ skill, onImport }) => {
    return (
        <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow border border-gray-100 flex flex-col justify-between h-full">
            <div>
                <div className="flex items-center justify-between mb-2">
                    <h3 className="text-xl font-bold text-gray-800 flex items-center gap-2">
                        <FileText className="w-5 h-5 text-blue-500" />
                        {skill.name}
                    </h3>
                    <span className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded-full uppercase tracking-wide font-medium">
                        {skill.category}
                    </span>
                </div>

                <p className="text-gray-600 text-sm mb-4 line-clamp-3">
                    {skill.description || 'No description provided.'}
                </p>
            </div>

            <div className="mt-4 pt-4 border-t border-gray-100 flex justify-end">
                <button
                    onClick={() => onImport(skill.id)}
                    className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors text-sm font-medium cursor-pointer"
                >
                    <Download className="w-4 h-4" />
                    導入
                </button>
            </div>
        </div>
    );
};
