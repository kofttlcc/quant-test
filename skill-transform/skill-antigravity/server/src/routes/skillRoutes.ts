import { Router } from 'express';
import { getSkills, importSkill, getMarketplaceFeatures } from '../controllers/skillController';

const router = Router();

router.get('/skills/local', getSkills);
router.post('/skills/import', importSkill);
router.get('/market/features', getMarketplaceFeatures);

export default router;
