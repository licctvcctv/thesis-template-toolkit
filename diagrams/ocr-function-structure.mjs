export function buildOcrFunctionStructure(runtime) {
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
    rect(rootCenterX - 220, rootY, 440, rootHeight, '基于OCR的智能财务报销系统', {
      size: 28,
      family: BOLD,
    }),
  );
  body.push(vLine(rootCenterX, rootY + rootHeight, mainRailY));

  const groups = [
    {
      center: 220,
      width: 180,
      label: '员工报销端',
      children: ['报销申请', 'OCR识别', '进度查询', '薪资查询', '留言反馈'],
    },
    {
      center: 600,
      width: 200,
      label: '审批财务端',
      children: ['报销审批', '薪资管理', '收费管理', '支出管理', '财务统计'],
    },
    {
      center: 1000,
      width: 200,
      label: '系统管理端',
      children: ['用户管理', '角色管理', '部门管理', '公告管理', '日志管理'],
    },
    {
      center: 1380,
      width: 200,
      label: '智能辅助端',
      children: ['发票OCR', '双通道识别', '数据校验', '字段提取'],
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

  writeDiagram('ocr-function-structure', 1600, 980, body);
}
