import { parseArgs, createRuntime } from './runtime.mjs';
import { buildEyeDiseaseSystemArch } from './eye-disease-system-arch.mjs';
import { buildEyeDiseaseFunction } from './eye-disease-function-structure.mjs';
import { buildEyeDiseaseFlow } from './eye-disease-flow.mjs';
import { buildResNet50Arch, buildMobileNetArch } from './eye-disease-models.mjs';

const args = parseArgs();
const runtime = createRuntime(args);

buildEyeDiseaseSystemArch(runtime);
buildEyeDiseaseFunction(runtime);
buildEyeDiseaseFlow(runtime);
buildResNet50Arch(runtime);
buildMobileNetArch(runtime);
