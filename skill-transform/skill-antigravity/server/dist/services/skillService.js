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
exports.getSkill = exports.listSkills = void 0;
const fs_extra_1 = __importDefault(require("fs-extra"));
const path_1 = __importDefault(require("path"));
const glob_1 = require("glob");
const gray_matter_1 = __importDefault(require("gray-matter"));
const SKILLS_DIR = path_1.default.resolve(__dirname, '../../../../../skills'); // Adjust based on build structure
const listSkills = () => __awaiter(void 0, void 0, void 0, function* () {
    try {
        console.log('__dirname:', __dirname);
        console.log('Searching skills in:', SKILLS_DIR);
        const exists = yield fs_extra_1.default.pathExists(SKILLS_DIR);
        console.log('SKILLS_DIR exists:', exists);
        const files = yield (0, glob_1.glob)('**/*.md', { cwd: SKILLS_DIR, ignore: ['**/node_modules/**'] });
        console.log(`Found ${files.length} files`);
        const skills = [];
        for (const file of files) {
            const filePath = path_1.default.join(SKILLS_DIR, file);
            const fileContent = yield fs_extra_1.default.readFile(filePath, 'utf-8');
            const { data, content } = (0, gray_matter_1.default)(fileContent);
            const relativePath = file;
            const id = relativePath.replace(/\.md$/, '').replace(/\//g, '.');
            const parts = relativePath.split('/');
            const category = parts.length > 1 ? parts[0] : 'general';
            skills.push({
                id,
                name: data.name || path_1.default.basename(file, '.md'),
                description: data.description || '',
                path: filePath,
                category,
                content,
                metadata: data
            });
        }
        return skills;
    }
    catch (error) {
        console.error('Error listing skills:', error);
        return [];
    }
});
exports.listSkills = listSkills;
const getSkill = (id) => __awaiter(void 0, void 0, void 0, function* () {
    const skills = yield (0, exports.listSkills)();
    return skills.find(s => s.id === id) || null;
});
exports.getSkill = getSkill;
