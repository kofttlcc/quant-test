
import { Request, Response } from 'express';
import { listSkills, getSkill } from '../services/skillService';
import { getMarketplaceData } from '../services/marketplaceService';
import { installSkillFromUrl } from '../services/skillInstaller';

export const getSkills = async (req: Request, res: Response) => {
    try {
        const skills = await listSkills();
        res.json(skills);
    } catch (error: any) {
        res.status(500).json({ error: 'Failed to fetch skills: ' + error.message });
    }
};

export const importSkill = async (req: Request, res: Response) => {
    const { id, url } = req.body;
    try {
        if (url) {
            // Import from Git URL (Standard Import)
            const result = await installSkillFromUrl(url);
            if (result.success) {
                res.json({ message: result.message });
            } else {
                res.status(400).json({ error: result.message });
            }
        } else {
            // Deprecated/Simulated ID-based import
            console.log(`Simulating import for skill ID: ${id}`);
            await new Promise(resolve => setTimeout(resolve, 1000));
            res.json({ message: `Skill ${id} imported successfully (Simulated)` });
        }
    } catch (error: any) {
        res.status(500).json({ error: 'Failed to import skill: ' + error.message });
    }
};

export const getMarketplaceFeatures = async (req: Request, res: Response) => {
    try {
        const data = await getMarketplaceData();
        res.json(data);
    } catch (error: any) {
        res.status(500).json({ error: 'Failed to load marketplace data: ' + error.message });
    }
};
