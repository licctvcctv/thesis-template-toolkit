export function buildOcrSystemFlow(runtime) {
  const { rect, diamond, vLine, hLine, pathLine, text, writeDiagram, BOLD } = runtime;
  const body = [];
  const centerX = 700;
  const boxW = 340;

  // 开始
  body.push(rect(centerX - 130, 60, 260, 70, '开始', { rounded: true, size: 28 }));
  body.push(vLine(centerX, 130, 190, { arrow: true }));

  // 登录
  body.push(rect(centerX - boxW / 2, 190, boxW, 70, '用户输入账号密码登录', { size: 24 }));
  body.push(vLine(centerX, 260, 320, { arrow: true }));

  // 判断身份
  body.push(diamond(centerX, 390, 340, 120, '验证用户身份', { size: 20 }));

  // 失败
  body.push(hLine(870, 1020, 390, { arrow: true }));
  body.push(text(940, 360, '失败', { size: 22 }));
  body.push(rect(1020, 355, 220, 70, '提示错误信息\n返回登录页', { size: 20, preserveLines: true, maxLines: 2 }));

  // 成功
  body.push(vLine(centerX, 450, 520, { arrow: true }));
  body.push(text(centerX + 30, 485, '成功', { size: 22 }));

  // 角色判断
  body.push(diamond(centerX, 590, 340, 120, '判断用户角色', { size: 20 }));

  // 三个角色分支
  const leftX = 300;
  const rightX = 1100;

  body.push(pathLine([[530, 590], [leftX, 590], [leftX, 700]], { width: 3, arrow: true }));
  body.push(text(380, 560, '员工', { size: 20 }));

  body.push(vLine(centerX, 650, 700, { arrow: true }));
  body.push(text(centerX + 50, 680, '财务', { size: 20 }));

  body.push(pathLine([[870, 590], [rightX, 590], [rightX, 700]], { width: 3, arrow: true }));
  body.push(text(1000, 560, '管理员', { size: 20 }));

  body.push(rect(leftX - 130, 700, 260, 70, '报销申请/OCR识别', { size: 22 }));
  body.push(rect(centerX - 130, 700, 260, 70, '报销审批/薪资管理', { size: 22 }));
  body.push(rect(rightX - 130, 700, 260, 70, '用户管理/系统配置', { size: 22 }));

  // 汇合
  body.push(vLine(leftX, 770, 830));
  body.push(vLine(centerX, 770, 830));
  body.push(vLine(rightX, 770, 830));
  body.push(hLine(leftX, rightX, 830));
  body.push(vLine(centerX, 830, 880, { arrow: true }));

  // 结束
  body.push(rect(centerX - 130, 880, 260, 70, '结束', { rounded: true, size: 28 }));

  writeDiagram('ocr-system-flow', 1400, 1010, body);
}

export function buildOcrAddFlow(runtime) {
  const { rect, diamond, vLine, hLine, text, writeDiagram } = runtime;
  const body = [];
  const cx = 500;
  const boxW = 280;

  body.push(rect(cx - 110, 40, 220, 60, '开始', { rounded: true, size: 26 }));
  body.push(vLine(cx, 100, 150, { arrow: true }));

  body.push(rect(cx - boxW / 2, 150, boxW, 60, '进入添加信息页面', { size: 22 }));
  body.push(vLine(cx, 210, 260, { arrow: true }));

  body.push(rect(cx - boxW / 2, 260, boxW, 60, '填写信息并提交', { size: 22 }));
  body.push(vLine(cx, 320, 380, { arrow: true }));

  body.push(diamond(cx, 440, 280, 110, '数据校验是否通过', { size: 18 }));

  // 否 → 返回
  body.push(hLine(640, 800, 440, { arrow: true }));
  body.push(text(720, 410, '否', { size: 20 }));
  body.push(rect(800, 410, 180, 60, '提示错误\n重新填写', { size: 18, preserveLines: true, maxLines: 2 }));

  // 是
  body.push(vLine(cx, 495, 550, { arrow: true }));
  body.push(text(cx + 25, 525, '是', { size: 20 }));

  body.push(rect(cx - boxW / 2, 550, boxW, 60, '写入数据库', { size: 22 }));
  body.push(vLine(cx, 610, 660, { arrow: true }));

  body.push(rect(cx - boxW / 2, 660, boxW, 60, '提示添加成功', { size: 22 }));
  body.push(vLine(cx, 720, 770, { arrow: true }));

  body.push(rect(cx - 110, 770, 220, 60, '结束', { rounded: true, size: 26 }));

  writeDiagram('ocr-add-flow', 1040, 880, body);
}

export function buildOcrEditFlow(runtime) {
  const { rect, diamond, vLine, hLine, text, writeDiagram } = runtime;
  const body = [];
  const cx = 500;
  const boxW = 280;

  body.push(rect(cx - 110, 40, 220, 60, '开始', { rounded: true, size: 26 }));
  body.push(vLine(cx, 100, 150, { arrow: true }));

  body.push(rect(cx - boxW / 2, 150, boxW, 60, '选择要修改的记录', { size: 22 }));
  body.push(vLine(cx, 210, 260, { arrow: true }));

  body.push(rect(cx - boxW / 2, 260, boxW, 60, '加载原有数据到表单', { size: 22 }));
  body.push(vLine(cx, 320, 380, { arrow: true }));

  body.push(rect(cx - boxW / 2, 380, boxW, 60, '修改信息并提交', { size: 22 }));
  body.push(vLine(cx, 440, 500, { arrow: true }));

  body.push(diamond(cx, 560, 280, 110, '数据校验是否通过', { size: 18 }));

  body.push(hLine(640, 800, 560, { arrow: true }));
  body.push(text(720, 530, '否', { size: 20 }));
  body.push(rect(800, 530, 180, 60, '提示错误\n重新修改', { size: 18, preserveLines: true, maxLines: 2 }));

  body.push(vLine(cx, 615, 670, { arrow: true }));
  body.push(text(cx + 25, 645, '是', { size: 20 }));

  body.push(rect(cx - boxW / 2, 670, boxW, 60, '更新数据库记录', { size: 22 }));
  body.push(vLine(cx, 730, 780, { arrow: true }));

  body.push(rect(cx - boxW / 2, 780, boxW, 60, '提示修改成功', { size: 22 }));
  body.push(vLine(cx, 840, 890, { arrow: true }));

  body.push(rect(cx - 110, 890, 220, 60, '结束', { rounded: true, size: 26 }));

  writeDiagram('ocr-edit-flow', 1040, 1000, body);
}

export function buildOcrDeleteFlow(runtime) {
  const { rect, diamond, vLine, hLine, text, writeDiagram } = runtime;
  const body = [];
  const cx = 500;
  const boxW = 280;

  body.push(rect(cx - 110, 40, 220, 60, '开始', { rounded: true, size: 26 }));
  body.push(vLine(cx, 100, 150, { arrow: true }));

  body.push(rect(cx - boxW / 2, 150, boxW, 60, '选择要删除的记录', { size: 22 }));
  body.push(vLine(cx, 210, 270, { arrow: true }));

  body.push(diamond(cx, 330, 280, 110, '确认是否删除', { size: 20 }));

  body.push(hLine(640, 800, 330, { arrow: true }));
  body.push(text(720, 300, '否', { size: 20 }));
  body.push(rect(800, 300, 180, 60, '取消操作\n返回列表', { size: 18, preserveLines: true, maxLines: 2 }));

  body.push(vLine(cx, 385, 440, { arrow: true }));
  body.push(text(cx + 25, 415, '是', { size: 20 }));

  body.push(rect(cx - boxW / 2, 440, boxW, 60, '从数据库删除记录', { size: 22 }));
  body.push(vLine(cx, 500, 550, { arrow: true }));

  body.push(rect(cx - boxW / 2, 550, boxW, 60, '提示删除成功', { size: 22 }));
  body.push(vLine(cx, 610, 660, { arrow: true }));

  body.push(rect(cx - 110, 660, 220, 60, '结束', { rounded: true, size: 26 }));

  writeDiagram('ocr-delete-flow', 1040, 770, body);
}
