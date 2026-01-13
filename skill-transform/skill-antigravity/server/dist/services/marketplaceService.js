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
exports.getMarketplaceData = void 0;
const fs_extra_1 = __importDefault(require("fs-extra"));
const path_1 = __importDefault(require("path"));
const js_yaml_1 = __importDefault(require("js-yaml"));
const getMarketplaceData = () => __awaiter(void 0, void 0, void 0, function* () {
    // Path to the featured-repositories.yaml in agent-skills-guard
    // Relative to server/src/services
    // server/src/services -> server/src -> server -> skill-antigravity -> skill-transform -> agent-skills-guard
    const yamlPath = path_1.default.resolve(__dirname, '../../../../agent-skills-guard/featured-repositories.yaml');
    if (!fs_extra_1.default.existsSync(yamlPath)) {
        throw new Error(`Marketplace configuration not found at: ${yamlPath}`);
    }
    const fileContent = yield fs_extra_1.default.readFile(yamlPath, 'utf8');
    const data = js_yaml_1.default.load(fileContent);
    return data;
});
exports.getMarketplaceData = getMarketplaceData;
