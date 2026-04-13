export function buildErDiagram(runtime) {
  const { rect, diamond, ellipse, pathLine, card, BOLD, writeDiagram } = runtime;
  const body = [];

  const entity = (x, y, label, width = 200, height = 62) => {
    const node = { x, y, w: width, h: height, cx: x + width / 2, cy: y + height / 2 };
    body.push(rect(x, y, width, height, label, { size: 24, family: BOLD, strokeWidth: 2.8 }));
    return node;
  };
  const relation = (cx, cy, label, width = 96, height = 62) => {
    const node = { cx, cy, w: width, h: height };
    body.push(diamond(cx, cy, width, height, label, { size: 20, maxLines: 1 }));
    return node;
  };
  const rectAnchor = (node, tx, ty) => {
    const dx = tx - node.cx;
    const dy = ty - node.cy;
    if (Math.abs(dx) * (node.h / 2) > Math.abs(dy) * (node.w / 2)) {
      return [dx >= 0 ? node.x + node.w : node.x, node.cy];
    }
    return [node.cx, dy >= 0 ? node.y + node.h : node.y];
  };
  const diamondAnchor = (node, tx, ty) => {
    const dx = tx - node.cx;
    const dy = ty - node.cy;
    if (Math.abs(dx) / (node.w / 2) > Math.abs(dy) / (node.h / 2)) {
      return [node.cx + (Math.sign(dx || 1) * node.w) / 2, node.cy];
    }
    return [node.cx, node.cy + (Math.sign(dy || 1) * node.h) / 2];
  };
  const ovalAnchor = (cx, cy, rx, ry, tx, ty) => {
    const dx = tx - cx;
    const dy = ty - cy;
    const scale = Math.sqrt((dx * dx) / (rx * rx) + (dy * dy) / (ry * ry)) || 1;
    return [cx + dx / scale, cy + dy / scale];
  };
  const connectEntityRelation = (entityNode, relationNode) => {
    const [x1, y1] = rectAnchor(entityNode, relationNode.cx, relationNode.cy);
    const [x2, y2] = diamondAnchor(relationNode, entityNode.cx, entityNode.cy);
    body.push(
      pathLine(
        [
          [x1, y1],
          [x2, y2],
        ],
        { width: 2.5 },
      ),
    );
  };
  const connectRelationEntity = (relationNode, entityNode) => {
    const [x1, y1] = diamondAnchor(relationNode, entityNode.cx, entityNode.cy);
    const [x2, y2] = rectAnchor(entityNode, relationNode.cx, relationNode.cy);
    body.push(
      pathLine(
        [
          [x1, y1],
          [x2, y2],
        ],
        { width: 2.5 },
      ),
    );
  };
  const attribute = (entityNode, cx, cy, label, opts = {}) => {
    const rx = opts.rx || 84;
    const ry = opts.ry || 30;
    const [x1, y1] = rectAnchor(entityNode, cx, cy);
    const [x2, y2] = ovalAnchor(cx, cy, rx, ry, entityNode.cx, entityNode.cy);
    body.push(
      pathLine(
        [
          [x1, y1],
          [x2, y2],
        ],
        { width: 2.3 },
      ),
    );
    body.push(
      ellipse(cx, cy, rx, ry, label, {
        size: opts.size || 18,
        minSize: 12,
        maxLines: opts.maxLines || 2,
      }),
    );
  };

  const product = entity(140, 150, '理财产品');
  const user = entity(760, 140, '用户');
  const admin = entity(1410, 150, '管理员');
  const order = entity(220, 500, '订单');
  const holding = entity(220, 920, '持仓');
  const loan = entity(1100, 500, '贷款申请', 220);
  const risk = entity(1100, 920, '风险事件', 220);

  [
    [60, 100, '产品编号'],
    [240, 60, '产品名称'],
    [430, 100, '年化收益率'],
    [80, 265, '起购金额'],
    [280, 280, '风险等级'],
  ].forEach(([cx, cy, label]) => attribute(product, cx, cy, label));

  [
    [680, 90, '用户编号'],
    [860, 50, '用户名'],
    [1060, 90, '手机号'],
    [1080, 225, '账户余额'],
    [650, 230, '用户状态'],
  ].forEach(([cx, cy, label]) => attribute(user, cx, cy, label));

  [
    [1340, 100, '管理员编号'],
    [1520, 55, '姓名'],
    [1700, 95, '角色'],
    [1700, 225, '联系电话'],
  ].forEach(([cx, cy, label]) => attribute(admin, cx, cy, label));

  [
    [80, 630, '订单编号'],
    [430, 640, '订单类型'],
    [100, 810, '订单金额'],
    [470, 810, '创建时间'],
  ].forEach(([cx, cy, label]) => attribute(order, cx, cy, label));

  [
    [110, 1040, '持仓编号'],
    [290, 1095, '持仓份额'],
    [480, 1030, '持仓金额'],
    [500, 930, '累计收益'],
  ].forEach(([cx, cy, label]) => attribute(holding, cx, cy, label));

  [
    [980, 620, '贷款编号'],
    [1420, 620, '贷款期限'],
    [980, 820, '评分快照'],
    [1470, 820, '审批状态'],
  ].forEach(([cx, cy, label]) => attribute(loan, cx, cy, label));

  [
    [980, 1040, '事件编号'],
    [1210, 1105, '风险类型'],
    [1430, 1040, '风险分值'],
    [1470, 930, '处置状态'],
  ].forEach(([cx, cy, label]) => attribute(risk, cx, cy, label));

  const correspond = relation(260, 340, '对应');
  const place = relation(560, 330, '下单');
  const hold = relation(560, 720, '持有');
  const generate = relation(320, 740, '形成');
  const apply = relation(1040, 330, '申请');
  const approve = relation(1380, 330, '审批');
  const trigger = relation(1210, 740, '触发');
  const dispose = relation(1460, 720, '处置');

  connectEntityRelation(product, correspond);
  connectRelationEntity(correspond, order);
  connectEntityRelation(user, place);
  connectRelationEntity(place, order);
  connectEntityRelation(user, hold);
  connectRelationEntity(hold, holding);
  connectEntityRelation(order, generate);
  connectRelationEntity(generate, holding);
  connectEntityRelation(user, apply);
  connectRelationEntity(apply, loan);
  connectEntityRelation(admin, approve);
  connectRelationEntity(approve, loan);
  connectEntityRelation(loan, trigger);
  connectRelationEntity(trigger, risk);
  connectEntityRelation(admin, dispose);
  connectRelationEntity(dispose, risk);

  [
    [205, 250, '1'],
    [240, 430, 'n'],
    [650, 250, '1'],
    [420, 430, 'n'],
    [650, 620, '1'],
    [420, 850, 'n'],
    [280, 690, '1'],
    [280, 850, '1'],
    [1110, 250, '1'],
    [1110, 430, 'n'],
    [1410, 250, '1'],
    [1285, 430, 'n'],
    [1210, 640, '1'],
    [1210, 850, 'n'],
    [1490, 620, '1'],
    [1420, 850, 'n'],
  ].forEach(([x, y, value]) => body.push(card(x, y, value)));

  writeDiagram('er-diagram', 1800, 1240, body);
}
