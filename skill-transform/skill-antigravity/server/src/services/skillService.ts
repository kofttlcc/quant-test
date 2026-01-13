
import fs from 'fs-extra';
import path from 'path';
import { glob } from 'glob';
import matter from 'gray-matter';

export interface Skill {
    id: string;
    name: string;
    description: string;
    path: string;
    category: string;
    content: string;
    metadata: any;
}

const SKILLS_DIR = path.resolve(__dirname, '../../../../../skills'); // Adjust based on build structure

export const listSkills = async (): Promise<Skill[]> => {
    try {
        console.log('__dirname:', __dirname);
        console.log('Searching skills in:', SKILLS_DIR);
        const exists = await fs.pathExists(SKILLS_DIR);
        console.log('SKILLS_DIR exists:', exists);

        const files = await glob('**/*.md', { cwd: SKILLS_DIR, ignore: ['**/node_modules/**'] });
        console.log(`Found ${files.length} files`);

        const skills: Skill[] = [];

        for (const file of files) {
            const filePath = path.join(SKILLS_DIR, file);
            const fileContent = await fs.readFile(filePath, 'utf-8');
            const { data, content } = matter(fileContent);

            const relativePath = file;
            const id = relativePath.replace(/\.md$/, '').replace(/\//g, '.');

            const parts = relativePath.split('/');
            const category = parts.length > 1 ? parts[0] : 'general';

            skills.push({
                id,
                name: data.name || path.basename(file, '.md'),
                description: data.description || '',
                path: filePath,
                category,
                content,
                metadata: data
            });
        }

        return skills;
    } catch (error) {
        console.error('Error listing skills:', error);
        return [];
    }
};

export const getSkill = async (id: string): Promise<Skill | null> => {
    const skills = await listSkills();
    return skills.find(s => s.id === id) || null;
}
