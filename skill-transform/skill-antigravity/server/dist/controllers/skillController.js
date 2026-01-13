"use strict";
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.uninstallAll = exports.uninstallSkill = exports.transformAll = exports.checkAdapted = exports.transformSkill = exports.getMarketplaceFeatures = exports.importSkill = exports.getSkills = void 0;
const skillService_1 = require("../services/skillService");
const marketplaceService_1 = require("../services/marketplaceService");
const skillInstaller_1 = require("../services/skillInstaller");
const getSkills = (req, res) => __awaiter(void 0, void 0, void 0, function* () {
    try {
        const skills = yield (0, skillService_1.listSkills)();
        res.json(skills);
    }
    catch (error) {
        res.status(500).json({ error: 'Failed to fetch skills: ' + error.message });
    }
});
exports.getSkills = getSkills;
const importSkill = (req, res) => __awaiter(void 0, void 0, void 0, function* () {
    const { id, url } = req.body;
    try {
        if (url) {
            // Import from Git URL (Standard Import)
            const result = yield (0, skillInstaller_1.installSkillFromUrl)(url);
            if (result.success) {
                res.json({ message: result.message });
            }
            else {
                res.status(400).json({ error: result.message });
            }
        }
        else {
            // Deprecated/Simulated ID-based import
            console.log(`Simulating import for skill ID: ${id}`);
            yield new Promise(resolve => setTimeout(resolve, 1000));
            res.json({ message: `Skill ${id} imported successfully (Simulated)` });
        }
    }
    catch (error) {
        res.status(500).json({ error: 'Failed to import skill: ' + error.message });
    }
});
exports.importSkill = importSkill;
const getMarketplaceFeatures = (req, res) => __awaiter(void 0, void 0, void 0, function* () {
    try {
        const data = yield (0, marketplaceService_1.getMarketplaceData)();
        res.json(data);
    }
    catch (error) {
        res.status(500).json({ error: 'Failed to load marketplace data: ' + error.message });
    }
});
exports.getMarketplaceFeatures = getMarketplaceFeatures;
const transformSkill = (req, res) => __awaiter(void 0, void 0, void 0, function* () {
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
    }
    catch (error) {
        console.error('Transform error:', error);
        res.status(500).json({
            error: `轉換失敗: ${error.message}`,
            details: error.stderr || error.stdout
        });
    }
});
exports.transformSkill = transformSkill;
const checkAdapted = (req, res) => __awaiter(void 0, void 0, void 0, function* () {
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
    }
    catch (error) {
        res.json({ adapted: false, skillName });
    }
});
exports.checkAdapted = checkAdapted;
const transformAll = (req, res) => __awaiter(void 0, void 0, void 0, function* () {
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
            timeout: 120000 // 2 分鐘超時
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
    }
    catch (error) {
        console.error('TransformAll error:', error);
        res.status(500).json({
            error: `批量轉換失敗: ${error.message}`,
            details: error.stderr || error.stdout
        });
    }
});
exports.transformAll = transformAll;
const uninstallSkill = (req, res) => __awaiter(void 0, void 0, void 0, function* () {
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
    }
    catch (error) {
        console.error('Uninstall error:', error);
        res.status(500).json({
            error: `卸載失敗: ${error.message}`
        });
    }
});
exports.uninstallSkill = uninstallSkill;
const uninstallAll = (req, res) => __awaiter(void 0, void 0, void 0, function* () {
    try {
        const fs = require('fs');
        const path = require('path');
        const serverDir = process.cwd();
        const skillsParentDir = path.resolve(serverDir, '../../..');
        const skillsDir = path.join(skillsParentDir, 'skills');
        // 獲取所有技能目錄
        const entries = fs.readdirSync(skillsDir, { withFileTypes: true });
        const skillDirs = entries.filter((e) => e.isDirectory() && !e.name.startsWith('_') && !e.name.startsWith('.'));
        let removedCount = 0;
        for (const dir of skillDirs) {
            const skillPath = path.join(skillsDir, dir.name);
            try {
                fs.rmSync(skillPath, { recursive: true, force: true });
                removedCount++;
                console.log(`[UninstallAll] Removed: ${dir.name}`);
            }
            catch (err) {
                console.error(`[UninstallAll] Failed to remove ${dir.name}:`, err);
            }
        }
        res.json({
            success: true,
            message: `成功卸載 ${removedCount} 個技能`
        });
    }
    catch (error) {
        console.error('UninstallAll error:', error);
        res.status(500).json({
            error: `批量卸載失敗: ${error.message}`
        });
    }
});
exports.uninstallAll = uninstallAll;
