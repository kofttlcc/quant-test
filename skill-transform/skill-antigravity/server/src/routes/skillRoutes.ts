
import { Router } from 'express';
import * as skillController from '../controllers/skillController';

const router = Router();

router.get('/local', skillController.getSkills);
router.post('/import', skillController.importSkill);

export default router;
