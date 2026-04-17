export function buildWangkongBusinessFlow(runtime) {
  const { rect, diamond, vLine, hLine, pathLine, text, writeDiagram } = runtime;
  const body = [];
  const cx = 700;
  const boxW = 340;

  // 开始
  body.push(rect(cx - 130, 60, 260, 70, '开始', { rounded: true, size: 28 }));
  body.push(vLine(cx, 130, 190, { arrow: true }));

  // 注册
  body.push(rect(cx - boxW / 2, 190, boxW, 70, '用户注册并填写身份证信息', { size: 22 }));
  body.push(vLine(cx, 260, 320, { arrow: true }));

  // 身份证校验
  body.push(diamond(cx, 390, 340, 120, '身份证校验通过', { size: 20 }));
  body.push(hLine(870, 1050, 390, { arrow: true }));
  body.push(text(960, 360, '否', { size: 22 }));
  body.push(rect(1050, 355, 220, 70, '提示格式错误\n注册失败', { size: 18, preserveLines: true, maxLines: 2 }));
  body.push(vLine(cx, 450, 510, { arrow: true }));
  body.push(text(cx + 30, 480, '是', { size: 22 }));

  // 登录
  body.push(rect(cx - boxW / 2, 510, boxW, 70, '登录系统', { size: 24 }));
  body.push(vLine(cx, 580, 640, { arrow: true }));

  // 浏览机器
  body.push(rect(cx - boxW / 2, 640, boxW, 70, '浏览机器列表，选择机器', { size: 22 }));
  body.push(vLine(cx, 710, 770, { arrow: true }));

  // 预约
  body.push(rect(cx - boxW / 2, 770, boxW, 70, '选择时段，提交预约', { size: 22 }));
  body.push(vLine(cx, 840, 900, { arrow: true }));

  // 冲突检测
  body.push(diamond(cx, 970, 340, 120, '时段冲突检测', { size: 20 }));
  body.push(hLine(870, 1050, 970, { arrow: true }));
  body.push(text(960, 940, '冲突', { size: 20 }));
  body.push(rect(1050, 935, 220, 70, '提示已被预约\n重新选择', { size: 18, preserveLines: true, maxLines: 2 }));
  body.push(vLine(cx, 1030, 1090, { arrow: true }));
  body.push(text(cx + 30, 1060, '无冲突', { size: 20 }));

  // 预约成功
  body.push(rect(cx - boxW / 2, 1090, boxW, 70, '预约成功，到店确认上机', { size: 22 }));
  body.push(vLine(cx, 1160, 1220, { arrow: true }));

  // 上机计时
  body.push(rect(cx - boxW / 2, 1220, boxW, 70, '系统创建会话，开始计时', { size: 22 }));
  body.push(vLine(cx, 1290, 1350, { arrow: true }));

  // 时长到期判断
  body.push(diamond(cx, 1420, 340, 120, '使用时长到期', { size: 20 }));
  body.push(vLine(cx, 1480, 1540, { arrow: true }));
  body.push(text(cx + 30, 1510, '是', { size: 22 }));

  // 续费选择
  body.push(diamond(cx, 1610, 300, 110, '选择续费', { size: 20 }));
  body.push(hLine(850, 1050, 1610, { arrow: true }));
  body.push(text(950, 1580, '否', { size: 22 }));

  // 结束上机
  body.push(rect(1050, 1575, 220, 70, '结束上机', { size: 22 }));

  // 续费 → 回到"系统创建会话，开始计时"（y=1220）
  body.push(pathLine([[cx - 150, 1610], [250, 1610], [250, 1255], [cx - boxW / 2, 1255]], { width: 3, arrow: true }));
  body.push(text(280, 1580, '是', { size: 22 }));

  // 计费结算
  body.push(vLine(1160, 1645, 1720, { arrow: true }));
  body.push(rect(1050 - 50, 1720, 320, 70, '按时段费率分段计费结算', { size: 20 }));
  body.push(vLine(1160, 1790, 1850, { arrow: true }));

  // 结束
  body.push(rect(1160 - 130, 1850, 260, 70, '结束', { rounded: true, size: 28 }));

  writeDiagram('wangkong-business-flow', 1400, 1980, body);
}

export function buildWangkongReserveFlow(runtime) {
  const { rect, diamond, vLine, hLine, text, writeDiagram } = runtime;
  const body = [];
  const cx = 500;
  const boxW = 280;

  body.push(rect(cx - 110, 40, 220, 60, '开始', { rounded: true, size: 26 }));
  body.push(vLine(cx, 100, 150, { arrow: true }));

  body.push(rect(cx - boxW / 2, 150, boxW, 60, '选择目标机器', { size: 22 }));
  body.push(vLine(cx, 210, 260, { arrow: true }));

  body.push(rect(cx - boxW / 2, 260, boxW, 60, '选择使用时段', { size: 22 }));
  body.push(vLine(cx, 320, 380, { arrow: true }));

  body.push(diamond(cx, 440, 280, 110, '机器状态是否空闲', { size: 18 }));
  body.push(hLine(640, 800, 440, { arrow: true }));
  body.push(text(720, 410, '否', { size: 20 }));
  body.push(rect(800, 410, 180, 60, '提示不可预约', { size: 18 }));

  body.push(vLine(cx, 495, 560, { arrow: true }));
  body.push(text(cx + 25, 530, '是', { size: 20 }));

  body.push(diamond(cx, 620, 280, 110, '时段是否冲突', { size: 18 }));
  body.push(hLine(640, 800, 620, { arrow: true }));
  body.push(text(720, 590, '是', { size: 20 }));
  body.push(rect(800, 590, 180, 60, '提示已被预约', { size: 18 }));

  body.push(vLine(cx, 675, 740, { arrow: true }));
  body.push(text(cx + 25, 710, '否', { size: 20 }));

  body.push(rect(cx - boxW / 2, 740, boxW, 60, '创建预约记录', { size: 22 }));
  body.push(vLine(cx, 800, 850, { arrow: true }));

  body.push(rect(cx - boxW / 2, 850, boxW, 60, '更新机器状态为已预约', { size: 20 }));
  body.push(vLine(cx, 910, 960, { arrow: true }));

  body.push(rect(cx - 110, 960, 220, 60, '结束', { rounded: true, size: 26 }));

  writeDiagram('wangkong-reserve-flow', 1040, 1070, body);
}
