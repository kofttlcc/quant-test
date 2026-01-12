/**
 * Skill Transformer - 將 openskills 格式轉換成 Antigravity 專屬版本
 *
 * 轉換內容:
 * 1. 語言: English → 繁體中文
 * 2. 結構: 自由格式 → 標準化 (概述→使用情境→快速開始)
 * 3. Frontmatter: 擴展 (trigger, language, adapted_from)
 * 4. 專案整合: 添加與 _base/ 的關聯
 */
export interface TransformOptions {
    overwrite?: boolean;
    useAI?: boolean;
    preview?: boolean;
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
export declare function transformSkill(skillPath: string, options?: TransformOptions): Promise<TransformResult>;
export declare const colors: {
    green: (s: string) => string;
    red: (s: string) => string;
    yellow: (s: string) => string;
    cyan: (s: string) => string;
    dim: (s: string) => string;
};
