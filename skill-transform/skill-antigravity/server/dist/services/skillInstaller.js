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
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.installSkillFromLocalPath = exports.installSkillFromUrl = void 0;
const simple_git_1 = __importDefault(require("simple-git"));
const fs_extra_1 = __importDefault(require("fs-extra"));
const path_1 = __importDefault(require("path"));
const gray_matter_1 = __importDefault(require("gray-matter"));
const skillRegistry_1 = require("./skillRegistry");
// Get the resolved path to the skills directory (same as in skillService)
const SKILLS_DIR = path_1.default.resolve(__dirname, '../../../../../skills');
const TEMP_DIR = path_1.default.resolve(__dirname, '../../temp_installs');
const installSkillFromUrl = (repoUrl) => __awaiter(void 0, void 0, void 0, function* () {
    var _a;
    // Determine skill name from URL
    // e.g., https://github.com/owner/repo -> repo
    const repoName = ((_a = repoUrl.split('/').pop()) === null || _a === void 0 ? void 0 : _a.replace('.git', '')) || 'unknown-skill';
    const tempPath = path_1.default.join(TEMP_DIR, `${repoName}-${Date.now()}`);
    try {
        // Ensure temp dir exists
        yield fs_extra_1.default.ensureDir(TEMP_DIR);
        // 1. Clone repository
        console.log(`Cloning ${repoUrl} to ${tempPath}...`);
        yield (0, simple_git_1.default)().clone(repoUrl, tempPath, ['--depth', '1']);
        // 2. Find skills in the repo
        // Recursively search for SKILL.md files
        const skillsFound = [];
        // Simple recursive search function
        const findSkills = (dir) => __awaiter(void 0, void 0, void 0, function* () {
            const entries = yield fs_extra_1.default.readdir(dir, { withFileTypes: true });
            for (const entry of entries) {
                const fullPath = path_1.default.join(dir, entry.name);
                if (entry.isDirectory()) {
                    if (entry.name === '.git')
                        continue; // Skip .git
                    const skillMdPath = path_1.default.join(fullPath, 'SKILL.md');
                    if (yield fs_extra_1.default.pathExists(skillMdPath)) {
                        skillsFound.push(fullPath);
                    }
                    else {
                        yield findSkills(fullPath);
                    }
                }
            }
        });
        // Check if root has SKILL.md
        if (yield fs_extra_1.default.pathExists(path_1.default.join(tempPath, 'SKILL.md'))) {
            skillsFound.push(tempPath);
        }
        else {
            yield findSkills(tempPath);
        }
        if (skillsFound.length === 0) {
            return { success: false, message: 'No SKILL.md found in repository.' };
        }
        // 3. Install skills
        // For now, we just install the first one found or all of them.
        // Let's implement installing all found skills.
        const results = [];
        for (const skillSrc of skillsFound) {
            const skillName = path_1.default.basename(skillSrc);
            const destPath = path_1.default.join(SKILLS_DIR, skillName);
            // Read SKILL.md to validate
            const skillContent = yield fs_extra_1.default.readFile(path_1.default.join(skillSrc, 'SKILL.md'), 'utf8');
            const { data } = (0, gray_matter_1.default)(skillContent);
            if (!data.name) {
                console.warn(`Skipping ${skillName}: Invalid SKILL.md`);
                continue;
            }
            // Check if exists
            if (yield fs_extra_1.default.pathExists(destPath)) {
                // Determine if we should overwrite. For now, let's append a timestamp if exists or just skip.
                // Or better: Backup existing?
                // Simple implementation: Overwrite
                console.log(`Skill ${skillName} exists. Overwriting...`);
            }
            // Copy
            yield fs_extra_1.default.copy(skillSrc, destPath);
            results.push(skillName);
        }
        // [NEW] Sync installed skills to AGENTS.md
        yield (0, skillRegistry_1.syncSkills)();
        return {
            success: true,
            message: `Successfully installed ${results.length} skills: ${results.join(', ')}`,
            skillPath: SKILLS_DIR
        };
    }
    catch (error) {
        console.error('Install error:', error);
        return { success: false, message: error.message };
    }
    finally {
        // Cleanup temp
        yield fs_extra_1.default.remove(tempPath);
    }
});
exports.installSkillFromUrl = installSkillFromUrl;
const installSkillFromLocalPath = (localPath) => __awaiter(void 0, void 0, void 0, function* () {
    // This is for importing from a local folder on the user's machine
    // Similar logic to Git install, but source is local
    // TODO: Implement if needed. For now the UI uses Git URL mostly for marketplace.
    return { success: false, message: 'Local path import not yet implemented.' };
});
exports.installSkillFromLocalPath = installSkillFromLocalPath;
