
import path from 'path';
import { glob } from 'glob';
import fs from 'fs-extra';

const SKILLS_DIR = path.resolve(__dirname, '../../../../skills');
console.log('__dirname:', __dirname);
console.log('SKILLS_DIR:', SKILLS_DIR);
console.log('Exists:', fs.existsSync(SKILLS_DIR));

glob('**/*.md', { cwd: SKILLS_DIR }).then(files => {
    console.log(`Found ${files.length} files`);
    if (files.length > 0) {
        console.log('First 5 files:', files.slice(0, 5));
    }
}).catch(err => console.error(err));
