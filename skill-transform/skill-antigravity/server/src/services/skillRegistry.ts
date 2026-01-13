
import fs from 'fs-extra';
import path from 'path';
import { globSync } from 'glob';
import matter from 'gray-matter';

// Paths relative to server/src/services
const ROOT_DIR = path.resolve(__dirname, '../../../../..');
const SKILLS_DIR = path.resolve(ROOT_DIR, 'skills');
const AGENTS_MD_PATH = path.resolve(ROOT_DIR, 'AGENTS.md');

interface SkillMetadata {
    name: string;
    description: string;
    location: 'project' | 'global';
}

export const syncSkills = async (): Promise<void> => {
    console.log('Syncing skills to AGENTS.md...');

    // 1. Find all skills
    if (!await fs.pathExists(SKILLS_DIR)) {
        await fs.ensureDir(SKILLS_DIR);
    }

    const skillFiles = globSync('**/SKILL.md', { cwd: SKILLS_DIR });
    const skills: SkillMetadata[] = [];

    for (const file of skillFiles) {
        const fullPath = path.join(SKILLS_DIR, file);
        try {
            const content = await fs.readFile(fullPath, 'utf8');
            const { data } = matter(content);

            if (data.name) {
                // Use the directory name as the skill name if data.name is missing (fallback)
                // But openskills uses data.name primarily.
                skills.push({
                    name: data.name,
                    description: data.description || '',
                    location: 'project'
                });
            }
        } catch (error) {
            console.warn(`Failed to parse skill at ${fullPath}:`, error);
        }
    }

    // 2. Generate XML
    const xml = generateSkillsXml(skills);

    // 3. Update AGENTS.md
    await updateAgentsMd(xml);
    console.log(`Synced ${skills.length} skills to AGENTS.md`);
};

const generateSkillsXml = (skills: SkillMetadata[]): string => {
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

const updateAgentsMd = async (newXml: string): Promise<void> => {
    let content = '';
    if (await fs.pathExists(AGENTS_MD_PATH)) {
        content = await fs.readFile(AGENTS_MD_PATH, 'utf8');
    } else {
        content = '# Skill Antigravity Agent Configuration\n\n';
    }

    const startMarker = '<skills_system';

    // Regex to match existing block including potential attributes on start tag
    const regex = /<skills_system[\s\S]*?<\/skills_system>/;

    if (regex.test(content)) {
        content = content.replace(regex, newXml);
    } else {
        // Append if not found
        content += '\n\n' + newXml;
    }

    await fs.writeFile(AGENTS_MD_PATH, content, 'utf8');
};
