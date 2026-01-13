import { Router } from 'express';
import { getSkills, importSkill, getMarketplaceFeatures, transformSkill, checkAdapted, transformAll, uninstallSkill, uninstallAll } from '../controllers/skillController';

const router = Router();

router.get('/skills/local', getSkills);
router.post('/skills/import', importSkill);
router.post('/skills/transform', transformSkill);
router.post('/skills/transform-all', transformAll);
router.delete('/skills/uninstall/:skillName', uninstallSkill);
router.delete('/skills/uninstall-all', uninstallAll);
router.get('/skills/check-adapted/:skillName', checkAdapted);
router.get('/market/features', getMarketplaceFeatures);

export default router;
