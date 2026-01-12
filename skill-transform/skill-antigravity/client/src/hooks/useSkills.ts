
import { useState, useEffect } from 'react';
import type { Skill } from '../types/skill';

export const useSkills = () => {
    const [skills, setSkills] = useState<Skill[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        fetchSkills();
    }, []);

    const fetchSkills = async () => {
        try {
            setLoading(true);
            const response = await fetch('http://localhost:3001/api/skills/local');
            if (!response.ok) {
                throw new Error('Failed to fetch skills');
            }
            const data = await response.json();
            setSkills(data);
        } catch (err: any) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const importSkill = async (id: string) => {
        try {
            const response = await fetch('http://localhost:3001/api/skills/import', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ id })
            });
            if (!response.ok) {
                throw new Error('導入技能失敗');
            }
            alert('技能導入成功（模擬）');
        } catch (err: any) {
            alert('導入技能失敗: ' + err.message);
        }
    }

    return { skills, loading, error, refetch: fetchSkills, importSkill };
};
