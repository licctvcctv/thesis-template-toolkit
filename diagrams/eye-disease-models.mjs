export function buildResNet50Arch(runtime) {
  const { rect, vLine, hLine, pathLine, text, writeDiagram, BOLD, STROKE, snap } = runtime;
  const body = [];

  // 两行布局，上面是主干网络，下面是分类头
  const row1Y = 120;
  const row2Y = 340;
  const boxH = 100;
  const gap = 40;

  // 第一行：输入 → Backbone → 冻结层 → 微调层
  const r1 = [
    { label: '输入图像\n224×224×3', w: 180 },
    { label: 'ResNet50 Backbone\n(ImageNet 预训练)', w: 280 },
    { label: '冻结层\nconv1 ~ layer3', w: 220 },
    { label: '微调层\nlayer4', w: 180 },
  ];

  // 第二行：GAP → Dropout → FC → Sigmoid → 输出
  const r2 = [
    { label: 'Global Average\nPooling', w: 200 },
    { label: 'Dropout\np = 0.3', w: 160 },
    { label: '全连接层\n2048 → 8', w: 180 },
    { label: 'Sigmoid\n激活函数', w: 160 },
    { label: '8 类疾病\n预测概率', w: 180 },
  ];

  // 计算第一行位置
  let cursor = 100;
  r1.forEach((b) => { b.x = cursor; cursor += b.w + gap; });
  const row1End = cursor - gap;

  // 计算第二行位置，右对齐
  let totalR2 = r2.reduce((s, b) => s + b.w, 0) + (r2.length - 1) * gap;
  cursor = row1End - totalR2;
  r2.forEach((b) => { b.x = cursor; cursor += b.w + gap; });

  const canvasW = row1End + 100;

  // 标题
  body.push(text(canvasW / 2, 50, 'ResNet50 模型结构', { size: 36, family: BOLD, weight: '700' }));

  // 画第一行
  r1.forEach((b) => {
    body.push(rect(b.x, row1Y, b.w, boxH, b.label, {
      size: 22, family: BOLD, preserveLines: true, maxLines: 2,
    }));
  });
  // 第一行箭头
  for (let i = 0; i < r1.length - 1; i++) {
    body.push(hLine(r1[i].x + r1[i].w, r1[i + 1].x, row1Y + boxH / 2, { arrow: true }));
  }

  // 第一行末尾转弯到第二行
  const turnX = r1[r1.length - 1].x + r1[r1.length - 1].w / 2;
  const turn2X = r2[0].x + r2[0].w / 2;
  body.push(vLine(turnX, row1Y + boxH, row2Y, { arrow: false }));
  body.push(hLine(turn2X, turnX, row2Y, { arrow: false }));
  body.push(vLine(turn2X, row2Y, row2Y + 20, { arrow: true }));

  // 画第二行
  r2.forEach((b) => {
    body.push(rect(b.x, row2Y + 20, b.w, boxH, b.label, {
      size: 22, family: BOLD, preserveLines: true, maxLines: 2,
    }));
  });
  // 第二行箭头
  for (let i = 0; i < r2.length - 1; i++) {
    body.push(hLine(r2[i].x + r2[i].w, r2[i + 1].x, row2Y + 20 + boxH / 2, { arrow: true }));
  }

  writeDiagram('eye-disease-resnet50-arch', canvasW, 520, body);
}

export function buildMobileNetArch(runtime) {
  const { rect, vLine, hLine, pathLine, text, writeDiagram, BOLD, STROKE, snap } = runtime;
  const body = [];

  const row1Y = 120;
  const row2Y = 340;
  const boxH = 100;
  const gap = 40;

  // 第一行：输入 → Backbone → 冻结层 → 微调层
  const r1 = [
    { label: '输入图像\n224×224×3', w: 180 },
    { label: 'MobileNetV3-Large\n(ImageNet 预训练)', w: 280 },
    { label: '冻结层\n前部特征提取层', w: 220 },
    { label: '微调层\n后 20 层', w: 180 },
  ];

  // 第二行：Linear → Hardswish → Dropout → Linear → Sigmoid → 输出
  const r2 = [
    { label: 'Linear\n960 → 1024', w: 160 },
    { label: 'Hardswish\n激活函数', w: 160 },
    { label: 'Dropout\np = 0.3', w: 140 },
    { label: 'Linear\n1024 → 8', w: 160 },
    { label: 'Sigmoid\n激活函数', w: 140 },
    { label: '8 类疾病\n预测概率', w: 160 },
  ];

  // 先算第二行总宽，确保画布够大
  let totalR2 = r2.reduce((s, b) => s + b.w, 0) + (r2.length - 1) * gap;
  let totalR1 = r1.reduce((s, b) => s + b.w, 0) + (r1.length - 1) * gap;
  const contentW = Math.max(totalR1, totalR2);
  const startX = 100;

  let cursor = startX;
  r1.forEach((b) => { b.x = cursor; cursor += b.w + gap; });
  const row1End = cursor - gap;

  // 第二行右对齐到第一行
  cursor = startX + contentW - totalR2;
  r2.forEach((b) => { b.x = cursor; cursor += b.w + gap; });

  const canvasW = startX + contentW + 100;

  body.push(text(canvasW / 2, 50, 'MobileNetV3 模型结构', { size: 36, family: BOLD, weight: '700' }));

  r1.forEach((b) => {
    body.push(rect(b.x, row1Y, b.w, boxH, b.label, {
      size: 22, family: BOLD, preserveLines: true, maxLines: 2,
    }));
  });
  for (let i = 0; i < r1.length - 1; i++) {
    body.push(hLine(r1[i].x + r1[i].w, r1[i + 1].x, row1Y + boxH / 2, { arrow: true }));
  }

  const turnX = r1[r1.length - 1].x + r1[r1.length - 1].w / 2;
  const turn2X = r2[0].x + r2[0].w / 2;
  body.push(vLine(turnX, row1Y + boxH, row2Y, { arrow: false }));
  body.push(hLine(turn2X, turnX, row2Y, { arrow: false }));
  body.push(vLine(turn2X, row2Y, row2Y + 20, { arrow: true }));

  r2.forEach((b) => {
    body.push(rect(b.x, row2Y + 20, b.w, boxH, b.label, {
      size: 22, family: BOLD, preserveLines: true, maxLines: 2,
    }));
  });
  for (let i = 0; i < r2.length - 1; i++) {
    body.push(hLine(r2[i].x + r2[i].w, r2[i + 1].x, row2Y + 20 + boxH / 2, { arrow: true }));
  }

  writeDiagram('eye-disease-mobilenet-arch', canvasW, 520, body);
}
