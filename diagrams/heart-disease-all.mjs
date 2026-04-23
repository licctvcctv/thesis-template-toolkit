import { parseArgs, createRuntime } from './runtime.mjs';
import { buildHeartDiseaseSystemArch } from './heart-disease-system-arch.mjs';
import { buildHeartDiseaseFunctionStructure } from './heart-disease-function-structure.mjs';
import { buildHeartDiseasePredictionFlow } from './heart-disease-prediction-flow.mjs';
import { buildHeartDiseaseWarehouse } from './heart-disease-warehouse.mjs';
import { buildHeartDiseaseModelPipeline } from './heart-disease-model-pipeline.mjs';
import { buildHeartDiseaseEtlFlow } from './heart-disease-etl-flow.mjs';
import { buildHeartDiseaseHadoopArch } from './heart-disease-hadoop-arch.mjs';
import { buildHeartDiseaseHiveArch } from './heart-disease-hive-arch.mjs';

const args = parseArgs();
const runtime = createRuntime(args);

buildHeartDiseaseSystemArch(runtime);
buildHeartDiseaseFunctionStructure(runtime);
buildHeartDiseasePredictionFlow(runtime);
buildHeartDiseaseWarehouse(runtime);
buildHeartDiseaseModelPipeline(runtime);
buildHeartDiseaseEtlFlow(runtime);
buildHeartDiseaseHadoopArch(runtime);
buildHeartDiseaseHiveArch(runtime);
