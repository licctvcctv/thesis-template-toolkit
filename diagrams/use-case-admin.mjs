import { buildRadialUseCase } from './radial-use-case-template.mjs';

export function buildUseCaseAdmin(runtime) {
  buildRadialUseCase(
    runtime,
    'use-case-diagram',
    '管理员',
    [
      ['贷款审批', 180, 160],
      ['风险监控', 180, 320],
      ['数据治理', 180, 480],
      ['血缘查看', 180, 640],
      ['ETL任务', 180, 800],
    ],
    [
      ['经营大屏', 1000, 160],
      ['用户画像', 1000, 320],
      ['风险处置', 1000, 480],
      ['ADS指标', 1000, 640],
      ['指标接口', 1000, 800],
    ],
  );
}
