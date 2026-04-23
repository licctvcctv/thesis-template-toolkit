export function buildHeartDiseaseFunctionStructure(runtime) {
  const { rect, vLine, hLine, tallRect, BOLD, snap, writeDiagram } = runtime;
  const body = [];
  const rootY = 40;
  const rootHeight = 76;
  const rootCenterX = 900;
  const mainRailY = 180;
  const groupY = 240;
  const childRailY = 390;
  const childY = 440;
  const childWidth = 60;
  const childHeight = 218;
  const childGap = 16;

  body.push(
    rect(rootCenterX - 280, rootY, 560, rootHeight, '心脏病健康数据分析系统', {
      size: 28,
      family: BOLD,
    }),
  );
  body.push(vLine(rootCenterX, rootY + rootHeight, mainRailY));

  const groups = [
    {
      center: 220,
      width: 180,
      label: '数据分析',
      children: ['年龄分析', '生活习惯', '临床指标', '相关性', '数据对比'],
    },
    {
      center: 620,
      width: 200,
      label: '机器学习',
      children: ['模型训练', '模型对比', '特征重要性', '风险预测'],
    },
    {
      center: 1020,
      width: 200,
      label: '数据管理',
      children: ['数据总览', '数据清洗', '仓库分层'],
    },
    {
      center: 1400,
      width: 200,
      label: '系统管理',
      children: ['系统监控', '日志管理', '用户管理'],
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

  writeDiagram('heart-disease-function-structure', 1700, 980, body);
}
