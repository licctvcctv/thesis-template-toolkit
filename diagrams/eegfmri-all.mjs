import { createRuntime, parseArgs } from './runtime.mjs';

const args = parseArgs();
const R = createRuntime(args);
const { rect, diamond, cylinder, vLine, hLine, pathLine, text, brace, tallRect, pill, writeDiagram, BOLD, STROKE, snap } = R;

// ===== 1. 数据处理流程图（标准流程图风格） =====
function buildPipelineFlow() {
  const body = [];
  const W = 1600, H = 1400;
  const cx = 500;         // EEG column center
  const rx = 1100;        // fMRI column center
  const mx = 800;         // merge center
  const stepW = 300, stepH = 70;
  const topW = 240;

  // ── 开始 ──
  body.push(rect(mx - topW / 2, 60, topW, 70, '同步采集开始', { rounded: true, size: 26 }));
  body.push(pathLine([[mx - 60, 130], [cx, 190]], { arrow: true }));
  body.push(pathLine([[mx + 60, 130], [rx, 190]], { arrow: true }));

  // ── EEG通道（左列） ──
  body.push(text(cx, 170, 'EEG通道', { size: 22, family: BOLD }));
  const eegSteps = [
    '读取原始EEG\n(64通道, 5000Hz)',
    '梯度伪迹去除\n(AAS算法)',
    '降采样\n(5000→200Hz)',
    'FIR低通滤波\n(截止50Hz)',
    'BCG心搏伪迹校正',
    '运动区9通道选择\n(FC1/FC2/C1-C4/CP1/CP2/Cz)',
  ];
  let ey = 200;
  eegSteps.forEach((label, i) => {
    body.push(rect(cx - stepW / 2, ey, stepW, stepH, label, { size: 20 }));
    if (i < eegSteps.length - 1) {
      body.push(vLine(cx, ey + stepH, ey + stepH + 30, { arrow: true }));
      ey += stepH + 30;
    }
  });
  const eegEnd = ey + stepH;

  // ── fMRI通道（右列） ──
  body.push(text(rx, 170, 'fMRI通道', { size: 22, family: BOLD }));
  const fmriSteps = [
    '读取原始fMRI\n(TR=2s, 3T Siemens)',
    '运动校正\n空间标准化',
    '平滑滤波\n时间域滤波',
    'ROI提取\n(左/右运动皮层)',
    'BOLD信号\n时间序列导出',
  ];
  let fy = 200;
  fmriSteps.forEach((label, i) => {
    body.push(rect(rx - stepW / 2, fy, stepW, stepH, label, { size: 20 }));
    if (i < fmriSteps.length - 1) {
      body.push(vLine(rx, fy + stepH, fy + stepH + 30, { arrow: true }));
      fy += stepH + 30;
    }
  });
  const fmriEnd = fy + stepH;

  // ── 特征提取（各自下方） ──
  const featY = Math.max(eegEnd, fmriEnd) + 40;
  body.push(rect(cx - stepW / 2, featY, stepW, stepH, 'EEG特征提取\n(时域/频域/NF得分)', { size: 20 }));
  body.push(rect(rx - stepW / 2, featY, stepW, stepH, 'BOLD特征提取\n(ROI衍生指标)', { size: 20 }));
  body.push(vLine(cx, eegEnd, featY, { arrow: true }));
  body.push(vLine(rx, fmriEnd, featY, { arrow: true }));

  // ── 菱形判断：是否融合 ──
  const diaY = featY + stepH + 60;
  body.push(diamond(mx, diaY, 380, 140, '是否进行\n多模态融合?', { size: 22 }));
  body.push(pathLine([[cx, featY + stepH], [cx, diaY - 70], [mx - 190, diaY]], { arrow: true }));
  body.push(pathLine([[rx, featY + stepH], [rx, diaY - 70], [mx + 190, diaY]], { arrow: true }));

  // 是 → 融合
  const fusionY = diaY + 100;
  body.push(text(mx + 20, diaY + 85, '是', { size: 22 }));
  body.push(rect(mx - 160, fusionY, 320, stepH, '特征级融合\n(15维融合特征集)', { size: 22 }));
  body.push(vLine(mx, diaY + 70, fusionY, { arrow: true }));

  // 否 → 单模态
  body.push(text(mx + 210, diaY - 20, '否', { size: 22 }));
  body.push(rect(1250, diaY - 35, 260, stepH, '单模态特征集\n(EEG或BOLD)', { size: 20 }));
  body.push(hLine(mx + 190, 1250, diaY, { arrow: true }));
  // 单模态也汇入分类
  body.push(pathLine([[1380, diaY + 35], [1380, fusionY + stepH + 65], [mx + 160, fusionY + stepH + 65]], { arrow: true }));

  // ── 分类 ──
  const clsY = fusionY + stepH + 30;
  body.push(rect(mx - 160, clsY, 320, stepH, '机器学习分类\n(SVM / kNN / RF)', { size: 22 }));
  body.push(vLine(mx, fusionY + stepH, clsY, { arrow: true }));

  // ── 脑功能网络（侧分支） ──
  body.push(rect(100, diaY - 35, 240, stepH, '脑功能网络构建\n(图论指标分析)', { size: 19 }));
  body.push(hLine(mx - 190, 340, diaY, { arrow: false, dashed: true }));
  body.push(hLine(240, 340, diaY, { arrow: false, dashed: true }));
  body.push(pathLine([[cx - stepW / 2, featY + stepH / 2], [340, featY + stepH / 2], [340, diaY], [340, diaY]], {}));
  body.push(hLine(340, 340, diaY, {}));
  // Simpler: arrow from EEG features to network box
  body.push(pathLine([[cx - stepW / 2, featY + stepH / 2], [220, featY + stepH / 2], [220, diaY - 35]], { arrow: true, dashed: true }));

  // ── 评估 ──
  const evalY = clsY + stepH + 30;
  body.push(rect(mx - 160, evalY, 320, stepH, '性能评估\n(准确率/精确率/召回率/F1)', { size: 20 }));
  body.push(vLine(mx, clsY + stepH, evalY, { arrow: true }));

  // ── 结束 ──
  const endY = evalY + stepH + 30;
  body.push(rect(mx - topW / 2, endY, topW, 70, '输出结果', { rounded: true, size: 26 }));
  body.push(vLine(mx, evalY + stepH, endY, { arrow: true }));

  writeDiagram('eegfmri-pipeline', W, H, body);
}

// ===== 2. 功能结构图 =====
function buildFunctionStructure() {
  const body = [];
  const rootCenterX = 800;

  body.push(rect(rootCenterX - 250, 40, 500, 76, '多模态脑信号分析与分类系统', { size: 28, family: BOLD }));
  body.push(vLine(rootCenterX, 116, 170));

  const groups = [
    {
      center: 220, width: 200, label: '数据预处理',
      children: ['梯度伪迹去除', '降采样滤波', 'BCG校正', '通道选择']
    },
    {
      center: 590, width: 200, label: '特征提取',
      children: ['时域特征', '频域特征', 'NF衍生特征', 'BOLD特征']
    },
    {
      center: 960, width: 240, label: '网络分析',
      children: ['连接矩阵', '聚类系数', '全局效率', '动态分析']
    },
    {
      center: 1380, width: 240, label: '分类与评估',
      children: ['SVM', 'kNN', '随机森林', '交叉验证']
    },
  ];

  const mainRailY = 170;
  const groupY = 220;
  const childRailY = 370;
  const childY = 410;
  const childWidth = 62;
  const childHeight = 200;
  const childGap = 14;

  body.push(hLine(groups[0].center, groups[groups.length - 1].center, mainRailY));

  groups.forEach((group) => {
    body.push(rect(group.center - group.width / 2, groupY, group.width, 72, group.label, { size: 24, family: BOLD }));
    body.push(vLine(group.center, mainRailY, groupY));
    body.push(vLine(group.center, groupY + 72, childRailY));

    const boxes = group.children.map((label, idx) => {
      const rawX = group.center - (group.children.length * childWidth + (group.children.length - 1) * childGap) / 2 + idx * (childWidth + childGap);
      const x = snap(rawX);
      return { label, x, centerX: x + childWidth / 2 };
    });

    body.push(hLine(boxes[0].centerX, boxes[boxes.length - 1].centerX, childRailY));
    boxes.forEach(({ label, x, centerX }) => {
      body.push(vLine(centerX, childRailY, childY));
      body.push(tallRect(x, childY, childWidth, childHeight, label, { size: 17, family: BOLD }));
    });
  });

  writeDiagram('eegfmri-function-structure', 1600, 680, body);
}

// ===== 3. 分类实验流程图 =====
function buildClassificationFlow() {
  const body = [];
  const W = 1200, H = 1100;
  const cx = 600;

  body.push(rect(cx - 120, 60, 240, 70, '开始', { rounded: true, size: 28 }));
  body.push(vLine(cx, 130, 180, { arrow: true }));

  body.push(rect(cx - 180, 180, 360, 70, '加载多模态特征数据\n(10被试 × 3条件 × 20块)', { size: 20 }));
  body.push(vLine(cx, 250, 300, { arrow: true }));

  body.push(rect(cx - 180, 300, 360, 70, '构建四种特征集\n(Handcrafted/EEG/BOLD/Fusion)', { size: 20 }));
  body.push(vLine(cx, 370, 420, { arrow: true }));

  body.push(rect(cx - 200, 420, 400, 80, '嵌套GroupKFold交叉验证\n外层5折(按被试分组)\n内层网格搜索调参', { size: 19 }));
  body.push(vLine(cx, 500, 550, { arrow: true }));

  // Three models in parallel
  const modelY = 550;
  const modelW = 200, modelH = 70;
  body.push(rect(cx - 350, modelY, modelW, modelH, 'SVM\n(RBF核, C/γ调优)', { size: 18 }));
  body.push(rect(cx - modelW / 2, modelY, modelW, modelH, 'kNN\n(k=3,5,7,9)', { size: 18 }));
  body.push(rect(cx + 150, modelY, modelW, modelH, 'Random Forest\n(树数/深度调优)', { size: 18 }));

  body.push(pathLine([[cx, 500], [cx - 250, 550]], { arrow: true }));
  body.push(pathLine([[cx, 500], [cx, 550]], { arrow: true }));
  body.push(pathLine([[cx, 500], [cx + 250, 550]], { arrow: true }));

  // Converge
  body.push(pathLine([[cx - 250, modelY + modelH], [cx - 250, 680], [cx, 700]], { arrow: false }));
  body.push(pathLine([[cx, modelY + modelH], [cx, 700]], { arrow: false }));
  body.push(pathLine([[cx + 250, modelY + modelH], [cx + 250, 680], [cx, 700]], { arrow: false }));
  body.push(vLine(cx, 700, 730, { arrow: true }));

  body.push(rect(cx - 180, 730, 360, 70, '计算性能指标\n(准确率/精确率/召回率/F1)', { size: 20 }));
  body.push(vLine(cx, 800, 850, { arrow: true }));

  body.push(diamond(cx, 910, 360, 120, '融合优于\n单模态?', { size: 22 }));

  // Yes
  body.push(hLine(cx + 180, cx + 350, 910, { arrow: true }));
  body.push(text(cx + 260, 882, '是', { size: 22 }));
  body.push(rect(cx + 350, 875, 200, 70, '输出最优模型\n(Fusion+SVM)', { size: 18 }));

  // No
  body.push(vLine(cx, 970, 1020, { arrow: true }));
  body.push(text(cx + 30, 998, '否', { size: 22 }));
  body.push(rect(cx - 120, 1020, 240, 60, '分析原因', { size: 22 }));

  writeDiagram('eegfmri-classification-flow', W, H, body);
}

buildPipelineFlow();
buildFunctionStructure();
buildClassificationFlow();
