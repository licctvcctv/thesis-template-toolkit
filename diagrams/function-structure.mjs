export function buildFunctionStructure(runtime) {
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
    rect(rootCenterX - 190, rootY, 380, rootHeight, '互联网金融数据仓库系统', {
      size: 28,
      family: BOLD,
    }),
  );
  body.push(vLine(rootCenterX, rootY + rootHeight, mainRailY));

  const groups = [
    {
      center: 290,
      width: 180,
      label: '用户功能',
      children: ['注册登录', '充值提现', '理财购买', '持仓查询', '贷款申请', '订单查询'],
    },
    {
      center: 800,
      width: 240,
      label: '后台管理功能',
      children: ['贷款审批', '经营看板', '风险监控', '用户画像', '营销分析'],
    },
    {
      center: 1310,
      width: 210,
      label: '数仓治理功能',
      children: ['数据抽取', '指标分析', '血缘管理', '作业日志', '质量校验', '接口服务'],
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

  writeDiagram('function-structure', 1600, 980, body);
}
