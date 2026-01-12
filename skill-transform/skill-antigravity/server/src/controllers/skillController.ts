
import { Request, Response } from 'express';
import * as skillService from '../services/skillService';

export const getSkills = async (req: Request, res: Response) => {
    try {
        const skills = await skillService.listSkills();
        res.json(skills);
    } catch (error) {
        res.status(500).json({ error: 'Failed to list skills' });
    }
};

export const importSkill = async (req: Request, res: Response) => {
    // Placeholder for import logic
    const { id } = req.body;
    try {
        const skill = await skillService.getSkill(id);
        if (!skill) {
            return res.status(404).json({ error: 'Skill not found' });
        }

        // TODO: Implement actual copying logic here
        // For now, just return success
        res.json({ message: `Simulated import of skill ${id}`, skill });
    } catch (error) {
        res.status(500).json({ error: 'Failed to import skill' });
    }
}
