import { buildFlowChartTemplate } from './flow-chart-template.mjs';

export function buildBusinessFlow(runtime) {
  buildFlowChartTemplate(runtime, 'business-flow', {
    page: '理财购买界面',
    input: ['用户输入购买金额', '并选择理财产品'],
    check: ['校验余额与产品状态', '是否通过'],
    reject: ['信息有误', '（弹窗提示）'],
    database: '业务库',
    success: '生成成功订单',
    result: '账户首页',
  });
}
