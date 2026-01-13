#!/usr/bin/env node
/**
 * skill-antigravity CLI
 * 一鍵完成 skill 轉換，適配 Antigravity 系統
 *
 * 用法:
 *   npx skill-antigravity transform <name>   # 轉換單個 skill
 *   npx skill-antigravity transform --all    # 轉換所有 skills
 *   npx skill-antigravity sync               # 同步 skills 到 AGENTS.md
 *   npx skill-antigravity install <url>      # 從 Git URL 安裝 skill
 *   npx skill-antigravity list               # 列出已安裝的 skills
 */
import fs from 'fs-extra';
import path from 'path';
import { globSync } from 'glob';
import matter from 'gray-matter';
import { simpleGit } from 'simple-git';
import { transformSkill } from './transformer.js';
// 配置
const ROOT_DIR = process.cwd();
const SKILLS_DIR = path.join(ROOT_DIR, 'skills');
const AGENTS_MD_PATH = path.join(ROOT_DIR, 'AGENTS.md');
const TEMP_DIR = path.join(ROOT_DIR, '.skill-antigravity-temp');
// 顏色輸出
const colors = {
    green: (s) => `\x1b[32m${s}\x1b[0m`,
    red: (s) => `\x1b[31m${s}\x1b[0m`,
    yellow: (s) => `\x1b[33m${s}\x1b[0m`,
    cyan: (s) => `\x1b[36m${s}\x1b[0m`,
    dim: (s) => `\x1b[2m${s}\x1b[0m`,
};
// ============================================
// 核心功能
// ============================================
function findAllSkills() {
    if (!fs.existsSync(SKILLS_DIR)) {
        return [];
    }
    const skills = [];
    const skillFiles = globSync('**/SKILL.md', { cwd: SKILLS_DIR });
    for (const file of skillFiles) {
        const fullPath = path.join(SKILLS_DIR, file);
        try {
            const content = fs.readFileSync(fullPath, 'utf8');
            const { data } = matter(content);
            if (data.name) {
                const skillDir = path.dirname(fullPath);
                skills.push({
                    name: data.name,
                    description: data.description || '',
                    location: 'project',
                    path: skillDir
                });
            }
        }
        catch (error) {
            console.warn(colors.yellow(`⚠️  無法解析: ${file}`));
        }
    }
    return skills;
}
function generateSkillsXml(skills) {
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
When users ask you to perform tasks, check if any of the available skills below can help complete the task more effectively.

How to use skills:
- Invoke: Bash("openskills read <skill-name>")
- The skill content will load with detailed instructions
</usage>

<available_skills>
${skillTags}
</available_skills>
<!-- SKILLS_TABLE_END -->

</skills_system>`;
}
function updateAgentsMd(newXml) {
    let content = '';
    if (fs.existsSync(AGENTS_MD_PATH)) {
        content = fs.readFileSync(AGENTS_MD_PATH, 'utf8');
    }
    else {
        content = '# Skill Antigravity Agent Configuration\n\n';
    }
    const regex = /<skills_system[\s\S]*?<\/skills_system>/;
    if (regex.test(content)) {
        content = content.replace(regex, newXml);
    }
    else {
        content += '\n\n' + newXml;
    }
    fs.writeFileSync(AGENTS_MD_PATH, content, 'utf8');
}
// ============================================
// 命令實現
// ============================================
async function cmdTransform(args) {
    const hasAll = args.includes('--all');
    const hasPreview = args.includes('--preview');
    const hasOverwrite = args.includes('--overwrite');
    const skillName = args.find(a => !a.startsWith('--'));
    const options = {
        preview: hasPreview,
        overwrite: hasOverwrite,
    };
    if (hasAll) {
        console.log(colors.cyan('🔄 正在轉換所有 skills 為 Antigravity 格式...'));
        console.log();
        const skills = findAllSkills();
        if (skills.length === 0) {
            console.log(colors.yellow('⚠️  未找到任何 skills。'));
            return;
        }
        let successCount = 0;
        for (const skill of skills) {
            const result = await transformSkill(skill.path, options);
            if (result.success) {
                console.log(colors.green(`✅ ${result.skillName}`));
                successCount++;
            }
            else {
                console.log(colors.red(`❌ ${result.skillName}: ${result.message}`));
            }
        }
        console.log();
        console.log(colors.green(`🎉 完成！成功轉換 ${successCount}/${skills.length} 個 skills`));
    }
    else if (skillName) {
        console.log(colors.cyan(`🔄 正在轉換 ${skillName} 為 Antigravity 格式...`));
        console.log();
        const skillPath = path.join(SKILLS_DIR, skillName);
        if (!await fs.pathExists(skillPath)) {
            console.error(colors.red(`❌ 找不到 skill: ${skillName}`));
            return;
        }
        const result = await transformSkill(skillPath, options);
        if (result.success) {
            console.log(colors.green(`✅ 轉換成功！`));
            console.log(colors.dim(`   輸出: ${result.outputPath}`));
            if (result.preview) {
                console.log();
                console.log(colors.yellow('--- 預覽 ---'));
                console.log(result.preview);
            }
        }
        else {
            console.error(colors.red(`❌ ${result.message}`));
        }
    }
    else {
        console.error(colors.red('❌ 請指定 skill 名稱或使用 --all'));
        console.log('用法: skill-antigravity transform <skill-name>');
    }
}
async function cmdSync() {
    console.log(colors.cyan('🔄 正在同步 skills 到 AGENTS.md...'));
    const skills = findAllSkills();
    if (skills.length === 0) {
        console.log(colors.yellow('⚠️  未找到任何 skills。'));
        return;
    }
    const xml = generateSkillsXml(skills);
    updateAgentsMd(xml);
    console.log(colors.green(`✅ 已同步 ${skills.length} 個 skill(s) 到 AGENTS.md`));
}
async function cmdInstall(url) {
    if (!url) {
        console.error(colors.red('❌ 請提供 Git URL'));
        return;
    }
    console.log(colors.cyan(`📦 正在從 ${url} 安裝...`));
    const repoName = url.split('/').pop()?.replace('.git', '') || 'unknown';
    const tempPath = path.join(TEMP_DIR, `${repoName}-${Date.now()}`);
    try {
        await fs.ensureDir(TEMP_DIR);
        await simpleGit().clone(url, tempPath, ['--depth', '1']);
        const skillsFound = [];
        const findSkills = async (dir) => {
            const entries = await fs.readdir(dir, { withFileTypes: true });
            for (const entry of entries) {
                if (entry.isDirectory() && entry.name !== '.git') {
                    const fullPath = path.join(dir, entry.name);
                    if (await fs.pathExists(path.join(fullPath, 'SKILL.md'))) {
                        skillsFound.push(fullPath);
                    }
                    else {
                        await findSkills(fullPath);
                    }
                }
            }
        };
        if (await fs.pathExists(path.join(tempPath, 'SKILL.md'))) {
            skillsFound.push(tempPath);
        }
        else {
            await findSkills(tempPath);
        }
        if (skillsFound.length === 0) {
            console.error(colors.red('❌ 未找到 SKILL.md'));
            return;
        }
        await fs.ensureDir(SKILLS_DIR);
        for (const src of skillsFound) {
            const name = path.basename(src);
            await fs.copy(src, path.join(SKILLS_DIR, name));
        }
        await cmdSync();
        console.log(colors.green(`✅ 成功安裝 ${skillsFound.length} 個 skill(s)`));
    }
    catch (error) {
        console.error(colors.red(`❌ 安裝失敗: ${error.message}`));
    }
    finally {
        await fs.remove(tempPath);
    }
}
function cmdList() {
    console.log(colors.cyan('📋 已安裝的 Skills:'));
    console.log();
    const skills = findAllSkills();
    if (skills.length === 0) {
        console.log(colors.yellow('   (無)'));
        return;
    }
    skills.forEach((s, i) => {
        console.log(`   ${i + 1}. ${colors.green(s.name)}`);
        if (s.description) {
            console.log(colors.dim(`      ${s.description.slice(0, 60)}...`));
        }
    });
    console.log();
    console.log(colors.dim(`共 ${skills.length} 個 skill(s)`));
}
function cmdHelp() {
    console.log(`
${colors.cyan('skill-antigravity')} - 一鍵完成 skill 轉換，適配 Antigravity 系統

${colors.yellow('核心命令:')}
  transform <name>   🔄 轉換單個 skill 為 Antigravity 格式
  transform --all    🔄 轉換所有已安裝 skills

${colors.yellow('其他命令:')}
  sync               同步 skills 到 AGENTS.md
  install <url>      從 Git URL 安裝 skill
  list               列出已安裝的 skills

${colors.yellow('轉換選項:')}
  --preview          僅預覽，不寫入文件
  --overwrite        覆蓋原始 SKILL.md

${colors.yellow('範例:')}
  skill-antigravity transform pdf
  skill-antigravity transform --all
  skill-antigravity transform pdf --preview
`);
}
// ============================================
// 主入口
// ============================================
async function main() {
    const args = process.argv.slice(2);
    const command = args[0];
    switch (command) {
        case 'transform':
            await cmdTransform(args.slice(1));
            break;
        case 'sync':
            await cmdSync();
            break;
        case 'install':
            await cmdInstall(args[1]);
            break;
        case 'list':
            cmdList();
            break;
        case 'help':
        case '--help':
        case '-h':
            cmdHelp();
            break;
        default:
            if (command) {
                console.error(colors.red(`未知命令: ${command}`));
            }
            cmdHelp();
    }
}
main().catch(console.error);
