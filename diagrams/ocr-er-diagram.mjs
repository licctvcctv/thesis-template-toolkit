export function buildOcrErDiagram(runtime) {
  runtime.buildERDiagram('ocr-er-diagram', {
    entities: [
      { label: '报销信息', attrs: ['报销编号', '报销标题', '报销金额', '发票图片', 'OCR结果', '审批状态'] },
      { label: '员工', attrs: ['员工编号', '姓名', '部门', '手机号', '账号'] },
      { label: '财务人员', attrs: ['人员编号', '姓名', '职称', '联系电话'] },
      { label: '薪资', attrs: ['薪资编号', '基本工资', '绩效工资', '发放月份'] },
      { label: '用户', attrs: ['用户编号', '用户名', '密码', '角色', '状态'] },
    ],
    relations: [
      { from: 1, to: 0, label: '提交' },
      { from: 2, to: 0, label: '审批' },
      { from: 1, to: 3, label: '领取' },
      { from: 4, to: 1, label: '关联' },
      { from: 4, to: 2, label: '关联' },
    ],
    width: 1800,
    height: 1400,
  });
}
