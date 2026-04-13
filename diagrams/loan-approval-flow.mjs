import { buildFlowChartTemplate } from './flow-chart-template.mjs';

export function buildLoanApprovalFlow(runtime) {
  buildFlowChartTemplate(runtime, 'loan-approval-flow', {
    page: '贷款申请界面',
    input: ['用户输入金额与期限', '并提交贷款申请'],
    check: ['管理员审批贷款申请', '是否通过'],
    reject: ['驳回申请', '（返回结果）'],
    database: '业务库',
    success: '写入放款与审批结果',
    result: '审批结果页面',
  });
}
