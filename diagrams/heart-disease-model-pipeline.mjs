export function buildHeartDiseaseModelPipeline(runtime) {
  const { rect, diamond, vLine, hLine, pathLine, text, writeDiagram, BOLD, STROKE } = runtime;
  const body = [];
  const boxH = 60;

  // 标题
  body.push(text(800, 44, '心脏病预测模型训练流程', { size: 32, family: BOLD, weight: '700' }));

  // === 原始数据 ===
  body.push(rect(50, 100, 220, boxH, 'dwd_heart_feature_sample', { size: 15, rounded: true, strokeWidth: 2.4 }));
  body.push(hLine(270, 330, 130, { arrow: true }));

  // === 数据集划分 ===
  body.push(rect(330, 100, 180, boxH, '数据集划分\n80%训练 / 20%验证', { size: 14, preserveLines: true, maxLines: 2 }));
  body.push(hLine(510, 570, 130, { arrow: true }));

  // === 特征工程（两路） ===
  body.push(rect(570, 80, 260, 100, '', { strokeWidth: 2.4 }));
  body.push(text(700, 100, '特征工程', { size: 18, family: BOLD }));
  // 数值路径
  body.push(rect(585, 118, 110, 24, '数值(4个)', { size: 12, strokeWidth: 1.6 }));
  body.push(rect(710, 118, 110, 24, 'StandardScaler', { size: 11, strokeWidth: 1.6 }));
  body.push(hLine(695, 710, 130));
  // 分类路径
  body.push(rect(585, 148, 110, 24, '分类(13个)', { size: 12, strokeWidth: 1.6 }));
  body.push(rect(710, 148, 110, 24, 'OneHotEncoder', { size: 11, strokeWidth: 1.6 }));
  body.push(hLine(695, 710, 160));

  body.push(hLine(830, 900, 130, { arrow: true }));

  // === 并行训练 4 模型 ===
  const modelX = 900;
  const modelW = 200;
  const models = ['逻辑回归', 'SGD线性分类器', '随机森林(250棵)', 'Extra Trees(300棵)'];
  body.push(rect(modelX, 68, modelW, 130, '', { strokeWidth: 2.4 }));
  body.push(text(modelX + modelW / 2, 82, '并行训练', { size: 16, family: BOLD }));
  models.forEach((name, i) => {
    body.push(rect(modelX + 14, 96 + i * 24, modelW - 28, 22, name, { size: 12, strokeWidth: 1.4 }));
  });

  body.push(hLine(1100, 1170, 130, { arrow: true }));

  // === 模型评估 ===
  body.push(rect(1170, 90, 180, 80, 'Accuracy\nPrecision / Recall\nF1 / AUC', { size: 14, preserveLines: true, maxLines: 3 }));
  body.push(hLine(1350, 1410, 130, { arrow: true }));

  // === 选最优 ===
  body.push(diamond(1470, 130, 120, 80, 'AUC\n最高', { size: 14, maxLines: 2 }));

  // 向下箭头
  body.push(vLine(1470, 170, 230, { arrow: true }));

  // === 输出 ===
  body.push(rect(1370, 230, 200, boxH, 'model.joblib\nmetrics.json', { size: 14, preserveLines: true, maxLines: 2, rounded: true, strokeWidth: 2.4 }));

  writeDiagram('heart-disease-model-pipeline', 1600, 320, body);
}
