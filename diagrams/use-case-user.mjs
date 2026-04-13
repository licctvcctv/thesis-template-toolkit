import { buildRadialUseCase } from './radial-use-case-template.mjs';

export function buildUseCaseUser(runtime) {
  buildRadialUseCase(
    runtime,
    'use-case-diagram-user',
    '普通用户',
    [
      ['注册登录', 180, 160],
      ['个人中心', 180, 320],
      ['充值提现', 180, 480],
      ['持仓查询', 180, 640],
      ['订单查询', 180, 800],
    ],
    [
      ['理财购买', 1000, 160],
      ['贷款申请', 1000, 320],
      ['产品浏览', 1000, 480],
      ['资产查看', 1000, 640],
      ['消息通知', 1000, 800],
    ],
  );
}
