export function buildSequenceDiagram(runtime) {
  const { actor, rect, activation, pathLine, text, snap, STROKE, writeDiagram } = runtime;
  const body = [];
  body.push(actor(90, 140, '用户'));
  const lifelines = [
    { x: 320, label: ':WealthMarket.tsx' },
    { x: 560, label: ':wealthApi.ts' },
    { x: 820, label: ':order.py' },
    { x: 1080, label: ':dao.py' },
    { x: 1340, label: ':MySQL' },
  ];
  lifelines.forEach(({ x, label }) => {
    body.push(rect(x - 110, 100, 220, 60, label, { size: 22, minSize: 11 }));
    body.push(
      `<line x1="${snap(x)}" y1="160" x2="${snap(x)}" y2="870" stroke="#888" stroke-width="2" stroke-dasharray="8 6"/>`,
    );
  });
  body.push(activation(320, 230, 110));
  body.push(activation(560, 320, 110));
  body.push(activation(820, 400, 250));
  body.push(activation(1080, 490, 170));
  body.push(activation(1340, 520, 120));

  const message = (from, to, y, label, dashed = false, labelOffset = -18) => {
    body.push(
      pathLine(
        [
          [from, y],
          [to, y],
        ],
        { arrow: true, dashed, width: 2.5, color: dashed ? '#555' : STROKE },
      ),
    );
    body.push(text((from + to) / 2, y + labelOffset, label, { size: 20 }));
  };

  message(132, 308, 230, '1：提交理财购买请求');
  message(332, 548, 320, '2：调用 submitPurchase()');
  message(572, 808, 400, '3：发送购买请求');
  message(832, 1068, 490, '4：写入订单与持仓');
  message(1092, 1328, 520, '5：访问业务库');
  message(1328, 1092, 640, '6：返回写入结果', true, -16);
  message(1068, 832, 710, '7：返回订单对象', true, -16);
  message(808, 572, 790, '8：刷新余额与持仓', true, -16);
  message(548, 332, 860, '9：更新页面显示', true, -16);

  writeDiagram('sequence-diagram', 1500, 960, body);
}
