export function buildHeartDiseasePredictionFlow(runtime) {
  const { rect, diamond, vLine, hLine, text, writeDiagram, BOLD } = runtime;
  const body = [];
  const centerX = 700;
  const boxW = 380;

  // 开始
  body.push(rect(centerX - 130, 60, 260, 70, '开始', { rounded: true, size: 28 }));
  body.push(vLine(centerX, 130, 190, { arrow: true }));

  // 填写表单
  body.push(rect(centerX - boxW / 2, 190, boxW, 70, '用户填写健康指标表单（16字段）', { size: 22 }));
  body.push(vLine(centerX, 260, 320, { arrow: true }));

  // POST请求
  body.push(rect(centerX - boxW / 2, 320, boxW, 70, '前端POST请求至 /api/predict', { size: 22 }));
  body.push(vLine(centerX, 390, 450, { arrow: true }));

  // 判断模型
  body.push(diamond(centerX, 510, 360, 120, '模型是否已加载', { size: 20 }));
  // 否
  body.push(hLine(880, 1020, 510, { arrow: true }));
  body.push(text(950, 480, '否', { size: 22 }));
  body.push(rect(1020, 475, 280, 70, '加载 model.joblib\n和 Pipeline', { size: 18, preserveLines: true, maxLines: 2 }));
  // 是
  body.push(vLine(centerX, 570, 630, { arrow: true }));
  body.push(text(centerX + 30, 600, '是', { size: 22 }));

  // 缺失值填充
  body.push(rect(centerX - boxW / 2, 630, boxW, 70, '缺失字段补充默认值（中位数/众数）', { size: 20 }));
  body.push(vLine(centerX, 700, 760, { arrow: true }));

  // 特征预处理
  body.push(rect(centerX - boxW / 2, 760, boxW, 80, 'OneHotEncoder + StandardScaler\n特征预处理', { size: 20, preserveLines: true, maxLines: 2 }));
  body.push(vLine(centerX, 840, 900, { arrow: true }));

  // 模型推理
  body.push(rect(centerX - boxW / 2, 900, boxW, 70, '逻辑回归模型推理，输出概率值P', { size: 22 }));
  body.push(vLine(centerX, 970, 1030, { arrow: true }));

  // 风险等级判断
  body.push(diamond(centerX, 1090, 400, 120, '风险等级划分', { size: 20 }));

  // 三条分支
  const leftX = 300;
  const rightX = 1100;
  body.push(hLine(leftX, centerX - 200, 1090));
  body.push(text(leftX + 40, 1060, 'P < 0.33', { size: 18 }));
  body.push(rect(leftX - 120, 1055, 150, 70, '低风险', { size: 22, family: BOLD }));

  body.push(vLine(centerX, 1150, 1200, { arrow: true }));
  body.push(text(centerX + 110, 1170, '0.33 ≤ P < 0.67', { size: 16 }));

  body.push(hLine(centerX + 200, rightX, 1090));
  body.push(text(rightX - 60, 1060, 'P ≥ 0.67', { size: 18 }));
  body.push(rect(rightX - 30, 1055, 150, 70, '高风险', { size: 22, family: BOLD }));

  // 中风险继续
  body.push(rect(centerX - 100, 1200, 200, 60, '中风险', { size: 22, family: BOLD }));
  body.push(vLine(centerX, 1260, 1320, { arrow: true }));

  // 保存记录
  body.push(rect(centerX - boxW / 2, 1320, boxW, 70, '保存预测记录到数据库', { size: 22 }));
  body.push(vLine(centerX, 1390, 1450, { arrow: true }));

  // 返回结果
  body.push(rect(centerX - boxW / 2, 1450, boxW, 80, '返回结果：概率 + 风险等级\n+ 影响因素Top3', { size: 20, preserveLines: true, maxLines: 2 }));
  body.push(vLine(centerX, 1530, 1590, { arrow: true }));

  // 前端渲染
  body.push(rect(centerX - boxW / 2, 1590, boxW, 70, '前端渲染结果卡片', { size: 22 }));
  body.push(vLine(centerX, 1660, 1720, { arrow: true }));

  // 结束
  body.push(rect(centerX - 130, 1720, 260, 70, '结束', { rounded: true, size: 28 }));

  writeDiagram('heart-disease-prediction-flow', 1400, 1850, body);
}
