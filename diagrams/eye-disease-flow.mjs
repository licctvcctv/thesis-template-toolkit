export function buildEyeDiseaseFlow(runtime) {
  const { rect, diamond, vLine, hLine, pathLine, text, writeDiagram, BOLD } = runtime;
  const body = [];
  const centerX = 700;
  const boxW = 340;
  const smallW = 260;

  // 开始
  body.push(rect(centerX - 130, 60, 260, 70, '开始', { rounded: true, size: 28 }));
  body.push(vLine(centerX, 130, 190, { arrow: true }));

  // 用户上传
  body.push(rect(centerX - boxW / 2, 190, boxW, 70, '用户上传眼底图像', { size: 26 }));
  body.push(vLine(centerX, 260, 320, { arrow: true }));

  // 图像预处理
  body.push(rect(centerX - boxW / 2, 320, boxW, 90, '图像预处理\n裁剪黑边 → 缩放224×224 → 归一化', { size: 20, preserveLines: true, maxLines: 2 }));
  body.push(vLine(centerX, 410, 470, { arrow: true }));

  // 判断：是否合法图像
  body.push(diamond(centerX, 530, 360, 120, '图像格式是否合法', { size: 20 }));

  // 否 → 提示错误
  body.push(hLine(880, 1000, 530, { arrow: true }));
  body.push(text(940, 500, '否', { size: 22 }));
  body.push(rect(1000, 495, 240, 70, '提示错误信息\n返回上传页面', { size: 20, preserveLines: true, maxLines: 2 }));

  // 是 → 继续
  body.push(vLine(centerX, 590, 650, { arrow: true }));
  body.push(text(centerX + 30, 620, '是', { size: 22 }));

  // 并行推理
  body.push(rect(centerX - boxW / 2, 650, boxW, 60, '加载预训练模型', { size: 24 }));
  body.push(vLine(centerX, 710, 760, { arrow: true }));

  // 分叉 - 两个模型
  const leftX = 430;
  const rightX = 970;
  body.push(hLine(leftX, rightX, 760));
  body.push(vLine(leftX, 760, 800, { arrow: true }));
  body.push(vLine(rightX, 760, 800, { arrow: true }));

  body.push(rect(leftX - smallW / 2, 800, smallW, 70, 'ResNet50 推理', { size: 24, family: BOLD }));
  body.push(rect(rightX - smallW / 2, 800, smallW, 70, 'MobileNetV3 推理', { size: 24, family: BOLD }));

  body.push(vLine(leftX, 870, 920));
  body.push(vLine(rightX, 870, 920));
  body.push(hLine(leftX, rightX, 920));
  body.push(vLine(centerX, 920, 960, { arrow: true }));

  // Sigmoid + 阈值
  body.push(rect(centerX - boxW / 2, 960, boxW, 70, 'Sigmoid激活 → 8类疾病概率', { size: 22 }));
  body.push(vLine(centerX, 1030, 1090, { arrow: true }));

  // 结果展示
  body.push(rect(centerX - boxW / 2, 1090, boxW, 90, '结果展示\n概率条图 + 检出标识 + 双模型对比', { size: 20, preserveLines: true, maxLines: 2 }));
  body.push(vLine(centerX, 1180, 1240, { arrow: true }));

  // 结束
  body.push(rect(centerX - 130, 1240, 260, 70, '结束', { rounded: true, size: 28 }));

  writeDiagram('eye-disease-flow', 1400, 1370, body);
}
