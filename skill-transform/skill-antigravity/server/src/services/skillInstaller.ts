
import simpleGit from 'simple-git';
import fs from 'fs-extra';
import path from 'path';
import matter from 'gray-matter';
import { syncSkills } from './skillRegistry';

// Get the resolved path to the skills directory (same as in skillService)
const SKILLS_DIR = path.resolve(__dirname, '../../../../../skills');
const TEMP_DIR = path.resolve(__dirname, '../../temp_installs');

interface InstallResult {
    success: boolean;
    message: string;
    skillPath?: string;
}

export const installSkillFromUrl = async (repoUrl: string): Promise<InstallResult> => {
    // Determine skill name from URL
    // e.g., https://github.com/owner/repo -> repo
    const repoName = repoUrl.split('/').pop()?.replace('.git', '') || 'unknown-skill';
    const tempPath = path.join(TEMP_DIR, `${repoName}-${Date.now()}`);

    try {
        // Ensure temp dir exists
        await fs.ensureDir(TEMP_DIR);

        // 1. Clone repository
        console.log(`Cloning ${repoUrl} to ${tempPath}...`);
        await simpleGit().clone(repoUrl, tempPath, ['--depth', '1']);

        // 2. Find skills in the repo
        // Recursively search for SKILL.md files
        const skillsFound: string[] = [];
        // Simple recursive search function
        const findSkills = async (dir: string) => {
            const entries = await fs.readdir(dir, { withFileTypes: true });
            for (const entry of entries) {
                const fullPath = path.join(dir, entry.name);
                if (entry.isDirectory()) {
                    if (entry.name === '.git') continue; // Skip .git
                    const skillMdPath = path.join(fullPath, 'SKILL.md');
                    if (await fs.pathExists(skillMdPath)) {
                        skillsFound.push(fullPath);
                    } else {
                        await findSkills(fullPath);
                    }
                }
            }
        };

        // Check if root has SKILL.md
        if (await fs.pathExists(path.join(tempPath, 'SKILL.md'))) {
            skillsFound.push(tempPath);
        } else {
            await findSkills(tempPath);
        }

        if (skillsFound.length === 0) {
            return { success: false, message: 'No SKILL.md found in repository.' };
        }

        // 3. Install skills
        // For now, we just install the first one found or all of them.
        // Let's implement installing all found skills.
        const results: string[] = [];

        for (const skillSrc of skillsFound) {
            const skillName = path.basename(skillSrc);
            const destPath = path.join(SKILLS_DIR, skillName);

            // Read SKILL.md to validate
            const skillContent = await fs.readFile(path.join(skillSrc, 'SKILL.md'), 'utf8');
            const { data } = matter(skillContent);
            if (!data.name) {
                console.warn(`Skipping ${skillName}: Invalid SKILL.md`);
                continue;
            }

            // Check if exists
            if (await fs.pathExists(destPath)) {
                // Determine if we should overwrite. For now, let's append a timestamp if exists or just skip.
                // Or better: Backup existing?
                // Simple implementation: Overwrite
                console.log(`Skill ${skillName} exists. Overwriting...`);
            }

            // Copy
            await fs.copy(skillSrc, destPath);
            results.push(skillName);
        }

        // [NEW] Sync installed skills to AGENTS.md
        await syncSkills();

        return {
            success: true,
            message: `Successfully installed ${results.length} skills: ${results.join(', ')}`,
            skillPath: SKILLS_DIR
        };

    } catch (error: any) {
        console.error('Install error:', error);
        return { success: false, message: error.message };
    } finally {
        // Cleanup temp
        await fs.remove(tempPath);
    }
};

export const installSkillFromLocalPath = async (localPath: string): Promise<InstallResult> => {
    // This is for importing from a local folder on the user's machine
    // Similar logic to Git install, but source is local
    // TODO: Implement if needed. For now the UI uses Git URL mostly for marketplace.
    return { success: false, message: 'Local path import not yet implemented.' };
};
