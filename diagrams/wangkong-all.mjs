import { parseArgs, createRuntime } from './runtime.mjs';
import { buildRadialUseCase } from './radial-use-case-template.mjs';
import { buildWangkongSystemArch } from './wangkong-system-arch.mjs';
import { buildWangkongBusinessFlow, buildWangkongReserveFlow } from './wangkong-flows.mjs';
import { buildWangkongFunctionStructure } from './wangkong-function-structure.mjs';

const args = parseArgs();
const runtime = createRuntime(args);

buildRadialUseCase(runtime, 'wangkong-usecase-user', '用户', [
  ['注册/登录', 290, 220],
  ['身份证认证', 290, 380],
  ['浏览机器', 290, 540],
  ['预约机器', 290, 700],
], [
  ['自助上机', 890, 220],
  ['查看时长/续费', 890, 380],
  ['消费记录', 890, 540],
  ['在线充值', 890, 700],
]);

buildRadialUseCase(runtime, 'wangkong-usecase-admin', '管理员', [
  ['机器管理', 290, 220],
  ['用户管理', 290, 380],
  ['费率配置', 290, 540],
  ['公告管理', 290, 700],
], [
  ['预约记录', 890, 220],
  ['上机记录', 890, 380],
  ['数据统计', 890, 540],
  ['登录/权限', 890, 700],
]);

buildWangkongFunctionStructure(runtime);
buildWangkongSystemArch(runtime);
buildWangkongBusinessFlow(runtime);
buildWangkongReserveFlow(runtime);
