export function buildEyeDiseaseFunction(runtime) {
  const { rect, vLine, hLine, tallRect, BOLD, snap, writeDiagram } = runtime;
  const body = [];
  const rootY = 40;
  const rootHeight = 76;
  const rootCenterX = 800;
  const mainRailY = 180;
  const groupY = 240;
  const childRailY = 390;
  const childY = 440;
  const childWidth = 60;
  const childHeight = 218;
  const childGap = 16;

  body.push(
    rect(rootCenterX - 250, rootY, 500, rootHeight, '眼底疾病智能识别系统', {
      size: 28,
      family: BOLD,
    }),
  );
  body.push(vLine(rootCenterX, rootY + rootHeight, mainRailY));

  const groups = [
    {
      center: 220,
      width: 180,
      label: '用户管理',
      children: ['用户注册', '用户登录', '密码修改', '密码找回'],
    },
    {
      center: 560,
      width: 180,
      label: '智能诊断',
      children: ['图像上传', '模型推理', '结果展示', '双模型对比'],
    },
    {
      center: 900,
      width: 200,
      label: '数据预处理',
      children: ['灰度转换', '高斯去噪', '直方图均衡', '归一化'],
    },
    {
      center: 1220,
      width: 180,
      label: '模型对比',
      children: ['训练曲线', '混淆矩阵', 'ROC曲线', '指标对比'],
    },
    {
      center: 1500,
      width: 180,
      label: '历史记录',
      children: ['上传记录', '图像浏览'],
    },
  ];

  body.push(hLine(groups[0].center, groups[groups.length - 1].center, mainRailY));

  groups.forEach((group) => {
    body.push(
      rect(group.center - group.width / 2, groupY, group.width, 72, group.label, {
        size: 26,
        family: BOLD,
      }),
    );
    body.push(vLine(group.center, mainRailY, groupY));
    body.push(vLine(group.center, groupY + 72, childRailY));
    const renderedBoxes = group.children.map((label, idx) => {
      const rawX =
        group.center -
        (group.children.length * childWidth + (group.children.length - 1) * childGap) / 2 +
        idx * (childWidth + childGap);
      const x = snap(rawX);
      const width = snap(childWidth);
      return { label, x, width, centerX: x + width / 2 };
    });
    body.push(
      hLine(
        renderedBoxes[0].centerX,
        renderedBoxes[renderedBoxes.length - 1].centerX,
        childRailY,
      ),
    );
    renderedBoxes.forEach(({ label, x, width, centerX }) => {
      body.push(vLine(centerX, childRailY, childY));
      body.push(tallRect(x, childY, width, childHeight, label, { size: 18, family: BOLD }));
    });
  });

  writeDiagram('eye-disease-function-structure', 1700, 980, body);
}
