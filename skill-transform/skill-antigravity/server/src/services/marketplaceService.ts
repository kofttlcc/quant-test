
import fs from 'fs-extra';
import path from 'path';
import yaml from 'js-yaml';

export interface MarketplaceSkill {
    url: string;
    name: string;
    description: {
        en: string;
        zh: string;
    };
    tags: string[];
    featured: boolean;
}

export interface MarketplaceCategory {
    id: string;
    name: {
        en: string;
        zh: string;
    };
    description: {
        en: string;
        zh: string;
    };
    repositories: MarketplaceSkill[];
}

export interface MarketplaceData {
    version: string;
    last_updated: string;
    categories: MarketplaceCategory[];
}

export const getMarketplaceData = async (): Promise<MarketplaceData> => {
    // Path to the featured-repositories.yaml in agent-skills-guard
    // Relative to server/src/services
    // server/src/services -> server/src -> server -> skill-antigravity -> skill-transform -> agent-skills-guard
    const yamlPath = path.resolve(__dirname, '../../../../agent-skills-guard/featured-repositories.yaml');

    if (!fs.existsSync(yamlPath)) {
        throw new Error(`Marketplace configuration not found at: ${yamlPath}`);
    }

    const fileContent = await fs.readFile(yamlPath, 'utf8');
    const data = yaml.load(fileContent) as MarketplaceData;

    return data;
};
