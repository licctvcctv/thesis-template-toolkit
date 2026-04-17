import { buildRadialUseCase } from './radial-use-case-template.mjs';

export function buildAdminUseCase(runtime) {
  buildRadialUseCase(runtime, 'ocr-admin-usecase', '管理员', [
    ['用户管理', 290, 220],
    ['角色权限管理', 290, 380],
    ['系统日志查看', 290, 540],
    ['公告管理', 290, 700],
  ], [
    ['部门管理', 890, 220],
    ['数据备份', 890, 380],
    ['收费管理', 890, 540],
    ['支出管理', 890, 700],
  ]);
}

export function buildFinanceUseCase(runtime) {
  buildRadialUseCase(runtime, 'ocr-finance-usecase', '财务人员', [
    ['报销审批', 290, 260],
    ['薪资管理', 290, 460],
    ['收费信息管理', 290, 660],
  ], [
    ['支出信息管理', 890, 260],
    ['报销记录查询', 890, 460],
    ['财务统计', 890, 660],
  ]);
}

export function buildEmployeeUseCase(runtime) {
  buildRadialUseCase(runtime, 'ocr-employee-usecase', '员工', [
    ['提交报销申请', 290, 260],
    ['OCR发票识别', 290, 460],
    ['查看报销进度', 290, 660],
  ], [
    ['个人信息管理', 890, 260],
    ['薪资查询', 890, 460],
    ['留言反馈', 890, 660],
  ]);
}
