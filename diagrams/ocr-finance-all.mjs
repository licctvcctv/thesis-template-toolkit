import { parseArgs, createRuntime } from './runtime.mjs';
import { buildAdminUseCase, buildFinanceUseCase, buildEmployeeUseCase } from './ocr-use-cases.mjs';
import { buildOcrFunctionStructure } from './ocr-function-structure.mjs';
import { buildOcrSystemArch } from './ocr-system-arch.mjs';
import { buildOcrErDiagram } from './ocr-er-diagram.mjs';
import { buildOcrSystemFlow, buildOcrAddFlow, buildOcrEditFlow, buildOcrDeleteFlow } from './ocr-flows.mjs';

const args = parseArgs();
const runtime = createRuntime(args);

buildAdminUseCase(runtime);
buildFinanceUseCase(runtime);
buildEmployeeUseCase(runtime);
buildOcrFunctionStructure(runtime);
buildOcrSystemArch(runtime);
buildOcrErDiagram(runtime);
buildOcrSystemFlow(runtime);
buildOcrAddFlow(runtime);
buildOcrEditFlow(runtime);
buildOcrDeleteFlow(runtime);
