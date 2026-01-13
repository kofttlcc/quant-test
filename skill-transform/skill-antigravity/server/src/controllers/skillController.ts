
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

export const transformSkill = async (req: Request, res: Response) => {
    const { skillName } = req.body;

    if (!skillName) {
        res.status(400).json({ error: 'Missing skillName parameter' });
        return;
    }

    try {
        const { execSync } = require('child_process');
        const path = require('path');

        // 服務器 CWD 是 skill-antigravity/server
        // CLI 需要在 coding/ (skills 的父目錄) 運行
        const serverDir = process.cwd();
        const cliPath = path.join(serverDir, '..', 'cli', 'dist', 'index.js');

        // skills 目錄在 /Users/jerrylee/coding/skills
        // 服務器在 /Users/jerrylee/coding/skill-transform/skill-antigravity/server
        // 所以 CWD 應該是 ../../.. = /Users/jerrylee/coding
        const skillsParentDir = path.resolve(serverDir, '../../..');

        console.log(`[Transform] CLI Path: ${cliPath}`);
        console.log(`[Transform] Skills Parent Dir (CWD): ${skillsParentDir}`);

        // 調用 CLI transform 命令
        const result = execSync(`node "${cliPath}" transform "${skillName}"`, {
            encoding: 'utf8',
            cwd: skillsParentDir
        });

        console.log(`[Transform] CLI Output: ${result}`);

        // 解析輸出路徑
        const outputMatch = result.match(/輸出: (.+)/);
        const outputPath = outputMatch ? outputMatch[1].trim() : `skills/${skillName}/SKILL.antigravity.md`;

        res.json({
            success: true,
            message: `成功轉換 ${skillName} 為 Antigravity 格式`,
            outputPath
        });
    } catch (error: any) {
        console.error('Transform error:', error);
        res.status(500).json({
            error: `轉換失敗: ${error.message}`,
            details: error.stderr || error.stdout
        });
    }
};

export const checkAdapted = async (req: Request, res: Response) => {
    const { skillName } = req.params;

    try {
        const fs = require('fs');
        const path = require('path');

        // 檢查 skills 目錄中是否存在 .antigravity.md 文件
        const serverDir = process.cwd();
        const skillsParentDir = path.resolve(serverDir, '../../..');
        const antigravityPath = path.join(skillsParentDir, 'skills', skillName, 'SKILL.antigravity.md');

        const adapted = fs.existsSync(antigravityPath);

        res.json({ adapted, skillName });
    } catch (error: any) {
        res.json({ adapted: false, skillName });
    }
};

export const transformAll = async (req: Request, res: Response) => {
    try {
        const { execSync } = require('child_process');
        const path = require('path');

        const serverDir = process.cwd();
        const cliPath = path.join(serverDir, '..', 'cli', 'dist', 'index.js');
        const skillsParentDir = path.resolve(serverDir, '../../..');

        console.log(`[TransformAll] Starting batch transform...`);

        const result = execSync(`node "${cliPath}" transform --all`, {
            encoding: 'utf8',
            cwd: skillsParentDir,
            timeout: 120000  // 2 分鐘超時
        });

        console.log(`[TransformAll] Result: ${result}`);

        // 解析成功數量
        const match = result.match(/成功轉換 (\d+)\/(\d+)/);
        const successCount = match ? match[1] : '?';
        const totalCount = match ? match[2] : '?';

        res.json({
            success: true,
            message: `批量轉換完成！成功 ${successCount}/${totalCount} 個技能`,
            details: result
        });
    } catch (error: any) {
        console.error('TransformAll error:', error);
        res.status(500).json({
            error: `批量轉換失敗: ${error.message}`,
            details: error.stderr || error.stdout
        });
    }
};

export const uninstallSkill = async (req: Request, res: Response) => {
    const { skillName } = req.params;

    try {
        const fs = require('fs');
        const path = require('path');

        const serverDir = process.cwd();
        const skillsParentDir = path.resolve(serverDir, '../../..');
        const skillPath = path.join(skillsParentDir, 'skills', skillName);

        // 檢查技能是否存在
        if (!fs.existsSync(skillPath)) {
            res.status(404).json({ error: `技能 ${skillName} 不存在` });
            return;
        }

        // 遞歸刪除技能目錄
        fs.rmSync(skillPath, { recursive: true, force: true });

        console.log(`[Uninstall] Removed skill: ${skillName}`);

        res.json({
            success: true,
            message: `成功卸載技能: ${skillName}`
        });
    } catch (error: any) {
        console.error('Uninstall error:', error);
        res.status(500).json({
            error: `卸載失敗: ${error.message}`
        });
    }
};

export const uninstallAll = async (req: Request, res: Response) => {
    try {
        const fs = require('fs');
        const path = require('path');

        const serverDir = process.cwd();
        const skillsParentDir = path.resolve(serverDir, '../../..');
        const skillsDir = path.join(skillsParentDir, 'skills');

        // 獲取所有技能目錄
        const entries = fs.readdirSync(skillsDir, { withFileTypes: true });
        const skillDirs = entries.filter((e: any) => e.isDirectory() && !e.name.startsWith('_') && !e.name.startsWith('.'));

        let removedCount = 0;
        for (const dir of skillDirs) {
            const skillPath = path.join(skillsDir, dir.name);
            try {
                fs.rmSync(skillPath, { recursive: true, force: true });
                removedCount++;
                console.log(`[UninstallAll] Removed: ${dir.name}`);
            } catch (err) {
                console.error(`[UninstallAll] Failed to remove ${dir.name}:`, err);
            }
        }

        res.json({
            success: true,
            message: `成功卸載 ${removedCount} 個技能`
        });
    } catch (error: any) {
        console.error('UninstallAll error:', error);
        res.status(500).json({
            error: `批量卸載失敗: ${error.message}`
        });
    }
};
