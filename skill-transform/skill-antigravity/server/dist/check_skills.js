"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const path_1 = __importDefault(require("path"));
const glob_1 = require("glob");
const fs_extra_1 = __importDefault(require("fs-extra"));
const SKILLS_DIR = path_1.default.resolve(__dirname, '../../../../skills');
console.log('__dirname:', __dirname);
console.log('SKILLS_DIR:', SKILLS_DIR);
console.log('Exists:', fs_extra_1.default.existsSync(SKILLS_DIR));
(0, glob_1.glob)('**/*.md', { cwd: SKILLS_DIR }).then(files => {
    console.log(`Found ${files.length} files`);
    if (files.length > 0) {
        console.log('First 5 files:', files.slice(0, 5));
    }
}).catch(err => console.error(err));
