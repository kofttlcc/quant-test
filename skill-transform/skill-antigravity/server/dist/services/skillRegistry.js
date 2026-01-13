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
exports.syncSkills = void 0;
const fs_extra_1 = __importDefault(require("fs-extra"));
const path_1 = __importDefault(require("path"));
const glob_1 = require("glob");
const gray_matter_1 = __importDefault(require("gray-matter"));
// Paths relative to server/src/services
const ROOT_DIR = path_1.default.resolve(__dirname, '../../../../..');
const SKILLS_DIR = path_1.default.resolve(ROOT_DIR, 'skills');
const AGENTS_MD_PATH = path_1.default.resolve(ROOT_DIR, 'AGENTS.md');
const syncSkills = () => __awaiter(void 0, void 0, void 0, function* () {
    console.log('Syncing skills to AGENTS.md...');
    // 1. Find all skills
    if (!(yield fs_extra_1.default.pathExists(SKILLS_DIR))) {
        yield fs_extra_1.default.ensureDir(SKILLS_DIR);
    }
    const skillFiles = (0, glob_1.globSync)('**/SKILL.md', { cwd: SKILLS_DIR });
    const skills = [];
    for (const file of skillFiles) {
        const fullPath = path_1.default.join(SKILLS_DIR, file);
        try {
            const content = yield fs_extra_1.default.readFile(fullPath, 'utf8');
            const { data } = (0, gray_matter_1.default)(content);
            if (data.name) {
                // Use the directory name as the skill name if data.name is missing (fallback)
                // But openskills uses data.name primarily.
                skills.push({
                    name: data.name,
                    description: data.description || '',
                    location: 'project'
                });
            }
        }
        catch (error) {
            console.warn(`Failed to parse skill at ${fullPath}:`, error);
        }
    }
    // 2. Generate XML
    const xml = generateSkillsXml(skills);
    // 3. Update AGENTS.md
    yield updateAgentsMd(xml);
    console.log(`Synced ${skills.length} skills to AGENTS.md`);
});
exports.syncSkills = syncSkills;
const generateSkillsXml = (skills) => {
    const skillTags = skills.map(s => `
<skill>
<name>${s.name}</name>
<description>${s.description}</description>
<location>${s.location}</location>
</skill>`).join('\n');
    return `<skills_system priority="1">

## Available Skills

<!-- SKILLS_TABLE_START -->
<usage>
When users ask you to perform tasks, check if any of the available skills below can help complete the task more effectively. Skills provide specialized capabilities and domain knowledge.

How to use skills:
- Invoke: Bash("openskills read <skill-name>")
- The skill content will load with detailed instructions on how to complete the task
- Base directory provided in output for resolving bundled resources (references/, scripts/, assets/)

Usage notes:
- Only use skills listed in <available_skills> below
- Do not invoke a skill that is already loaded in your context
- Each skill invocation is stateless
</usage>

<available_skills>
${skillTags}
</available_skills>
<!-- SKILLS_TABLE_END -->

</skills_system>`;
};
const updateAgentsMd = (newXml) => __awaiter(void 0, void 0, void 0, function* () {
    let content = '';
    if (yield fs_extra_1.default.pathExists(AGENTS_MD_PATH)) {
        content = yield fs_extra_1.default.readFile(AGENTS_MD_PATH, 'utf8');
    }
    else {
        content = '# Skill Antigravity Agent Configuration\n\n';
    }
    const startMarker = '<skills_system';
    // Regex to match existing block including potential attributes on start tag
    const regex = /<skills_system[\s\S]*?<\/skills_system>/;
    if (regex.test(content)) {
        content = content.replace(regex, newXml);
    }
    else {
        // Append if not found
        content += '\n\n' + newXml;
    }
    yield fs_extra_1.default.writeFile(AGENTS_MD_PATH, content, 'utf8');
});
