/**
 * Skill Transformer - 將 openskills 格式轉換成 Antigravity 專屬版本
 * 
 * 轉換內容:
 * 1. 語言: English → 繁體中文
 * 2. 結構: 自由格式 → 標準化 (概述→使用情境→快速開始)
 * 3. Frontmatter: 擴展 (trigger, language, adapted_from)
 * 4. 專案整合: 添加與 _base/ 的關聯
 */

import fs from 'fs-extra';
import path from 'path';
import matter from 'gray-matter';

// 標準術語對照表 (基礎翻譯)
const TERM_TRANSLATIONS: Record<string, string> = {
    // 標題
    'Overview': '概述',
    'Quick Start': '快速開始',
    'Quick Reference': '快速參考',
    'Installation': '安裝',
    'Usage': '使用方式',
    'Examples': '範例',
    'Common Tasks': '常見任務',
    'Next Steps': '後續步驟',
    'Requirements': '需求',
    'Configuration': '配置',
    'API Reference': 'API 參考',
    'Troubleshooting': '故障排除',
    'Best Practices': '最佳實踐',
    'Security': '安全',
    'License': '授權',

    // 常見片語
    'This guide': '本指南',
    'For more information': '更多資訊請參考',
    'See also': '另請參閱',
    'Note:': '注意：',
    'Warning:': '警告：',
    'Important:': '重要：',
    'Tip:': '提示：',
};

// 標題翻譯映射
const HEADING_TRANSLATIONS: Record<string, string> = {
    'PDF Processing Guide': 'PDF 處理指南',
    'Python Libraries': 'Python 函式庫',
    'Command-Line Tools': '命令行工具',
    'Basic Operations': '基本操作',
    'Merge PDFs': '合併 PDF',
    'Split PDF': '分割 PDF',
    'Extract Text': '提取文字',
    'Extract Tables': '提取表格',
    'Create PDFs': '創建 PDF',
    'Add Watermark': '添加水印',
    'Password Protection': '密碼保護',
    'Extract Images': '提取圖片',
    // xlsx
    'Spreadsheet Guide': '電子表格指南',
    'Reading Data': '讀取數據',
    'Writing Data': '寫入數據',
    'Formulas': '公式',
    'Formatting': '格式設定',
    // docx
    'Document Processing': '文檔處理',
    'Create Documents': '創建文檔',
    'Edit Documents': '編輯文檔',
    'Track Changes': '追蹤變更',
    // 通用
    'Getting Started': '入門指南',
    'Advanced Usage': '進階用法',
    'Reference': '參考資料',
};

export interface TransformOptions {
    overwrite?: boolean;    // 是否覆蓋原始文件
    useAI?: boolean;        // 是否使用 AI 翻譯
    preview?: boolean;      // 僅預覽不寫入
}

export interface TransformResult {
    success: boolean;
    skillName: string;
    outputPath: string;
    message: string;
    preview?: string;
}

/**
 * 轉換單個 Skill
 */
export async function transformSkill(
    skillPath: string,
    options: TransformOptions = {}
): Promise<TransformResult> {
    const skillName = path.basename(skillPath);
    const skillMdPath = path.join(skillPath, 'SKILL.md');

    if (!await fs.pathExists(skillMdPath)) {
        return {
            success: false,
            skillName,
            outputPath: '',
            message: `找不到 SKILL.md: ${skillMdPath}`
        };
    }

    try {
        // 1. 讀取原始內容
        const rawContent = await fs.readFile(skillMdPath, 'utf8');
        const { data: frontmatter, content } = matter(rawContent);

        // 2. 轉換 Frontmatter
        const newFrontmatter = transformFrontmatter(frontmatter, skillName);

        // 3. 轉換內容
        const transformedContent = await transformContent(content, options);

        // 4. 組裝最終輸出
        const header = generateAntigravityHeader(skillName, frontmatter);
        const finalContent = matter.stringify(
            header + '\n\n' + transformedContent,
            newFrontmatter
        );

        // 5. 輸出
        const outputPath = options.overwrite
            ? skillMdPath
            : path.join(skillPath, 'SKILL.antigravity.md');

        if (options.preview) {
            return {
                success: true,
                skillName,
                outputPath,
                message: '預覽模式',
                preview: finalContent.slice(0, 2000) + '\n...'
            };
        }

        await fs.writeFile(outputPath, finalContent, 'utf8');

        return {
            success: true,
            skillName,
            outputPath,
            message: `成功轉換: ${outputPath}`
        };

    } catch (error: any) {
        return {
            success: false,
            skillName,
            outputPath: '',
            message: `轉換失敗: ${error.message}`
        };
    }
}

/**
 * 轉換 Frontmatter
 */
function transformFrontmatter(
    original: Record<string, any>,
    skillName: string
): Record<string, any> {
    return {
        name: original.name || skillName,
        description: translateText(original.description || '', 'description'),
        trigger: 'when_needed',
        language: 'zh-TW',
        adapted_from: `openskills/${skillName}`,
        version: '1.0.0-antigravity',
        original_license: original.license || 'Unknown',
    };
}

/**
 * 轉換內容
 */
async function transformContent(
    content: string,
    options: TransformOptions
): Promise<string> {
    let result = content;

    // 翻譯標題 (## Heading)
    result = translateHeadings(result);

    // 翻譯常見術語
    result = translateTerms(result);

    // 添加使用情境區塊
    result = insertUsageSection(result);

    // 添加專案整合說明
    result = appendProjectIntegration(result);

    return result;
}

/**
 * 翻譯標題
 */
function translateHeadings(content: string): string {
    let result = content;

    for (const [en, zh] of Object.entries(HEADING_TRANSLATIONS)) {
        // 匹配 # Heading, ## Heading, ### Heading
        const regex = new RegExp(`^(#{1,3})\\s*${escapeRegex(en)}\\s*$`, 'gm');
        result = result.replace(regex, `$1 ${zh}`);
    }

    return result;
}

/**
 * 翻譯常見術語
 */
function translateTerms(content: string): string {
    let result = content;

    for (const [en, zh] of Object.entries(TERM_TRANSLATIONS)) {
        result = result.split(en).join(zh);
    }

    return result;
}

/**
 * 翻譯描述文字 (簡單翻譯)
 */
function translateText(text: string, context: string): string {
    // 基礎翻譯邏輯
    let result = text;

    // 翻譯常見描述片語
    const descTranslations: Record<string, string> = {
        'Comprehensive': '全面的',
        'manipulation': '操作',
        'toolkit': '工具包',
        'extracting text': '提取文字',
        'tables': '表格',
        'creating new': '創建新的',
        'merging': '合併',
        'splitting': '分割',
        'documents': '文檔',
        'handling forms': '處理表單',
        'When Claude needs': '當需要',
        'programmatically': '以程式方式',
        'process': '處理',
        'generate': '生成',
        'analyze': '分析',
        'at scale': '大規模',
        'PDF': 'PDF',
        'spreadsheet': '電子表格',
        'presentation': '簡報',
        'document': '文檔',
    };

    for (const [en, zh] of Object.entries(descTranslations)) {
        result = result.split(en).join(zh);
    }

    return result;
}

/**
 * 生成 Antigravity 標準頭部
 */
function generateAntigravityHeader(
    skillName: string,
    originalFrontmatter: Record<string, any>
): string {
    const desc = originalFrontmatter.description || '';
    const translatedDesc = translateText(desc, 'description');

    return `# ${skillName.toUpperCase()} 處理指南

> **技能版本**: v1.0 (Antigravity 適配版)  
> **原始來源**: openskills/${skillName}  
> **語言**: 繁體中文

## 概述

${translatedDesc}

---`;
}

/**
 * 插入使用情境區塊
 */
function insertUsageSection(content: string): string {
    const usageSection = `
## 使用情境

此技能適用於以下情況：
- 用戶明確要求相關功能時
- 任務需要專業領域知識時
- 需要遵循特定工作流程時

---
`;

    // 插入到第一個主要內容區塊之前
    const firstH2 = content.indexOf('\n## ');
    if (firstH2 > 0) {
        return content.slice(0, firstH2) + usageSection + content.slice(firstH2);
    }

    return usageSection + content;
}

/**
 * 添加專案整合說明
 */
function appendProjectIntegration(content: string): string {
    const integration = `

---

## 專案整合

此技能已適配 Antigravity 系統：

- 遵循 \`skills/_base/coding_style.md\` 編碼規範
- 與 \`skills/_base/architecture.md\` 架構模式一致
- 符合 Constitution v3.1 語言規範 (繁體中文)

### 相關技能

可搭配以下技能使用：
- \`systematic-debugging\` - 系統化除錯
- \`verification-before-completion\` - 完成前驗證
`;

    return content + integration;
}

/**
 * 輔助函數：轉義正則特殊字符
 */
function escapeRegex(str: string): string {
    return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

// 導出顏色輸出
export const colors = {
    green: (s: string) => `\x1b[32m${s}\x1b[0m`,
    red: (s: string) => `\x1b[31m${s}\x1b[0m`,
    yellow: (s: string) => `\x1b[33m${s}\x1b[0m`,
    cyan: (s: string) => `\x1b[36m${s}\x1b[0m`,
    dim: (s: string) => `\x1b[2m${s}\x1b[0m`,
};
