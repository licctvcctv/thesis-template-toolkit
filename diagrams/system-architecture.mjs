export function buildSystemArchitecture(runtime) {
  const { rect, cylinder, brace, text, writeDiagram, BOLD, STROKE, snap } = runtime;
  const body = [];
  const frameX = 40;
  const frameY = 40;
  const frameWidth = 1600;
  const frameHeight = 1280;
  const bandX = 260;
  const bandWidth = 1240;
  const labelX = 170;
  const archText = { family: BOLD, weight: '400' };
  const roundedBox = (x, y, width, height, label, opts = {}) =>
    rect(x, y, width, height, label, {
      rounded: true,
      size: opts.size || 22,
      minSize: opts.minSize || 12,
      family: opts.family || BOLD,
      weight: opts.weight || '400',
      strokeWidth: opts.strokeWidth || 2.6,
      preserveLines: opts.preserveLines || false,
      maxLines: opts.maxLines || Infinity,
    });
  const band = (y, height) =>
    `<rect x="${bandX}" y="${snap(y)}" width="${bandWidth}" height="${snap(height)}" fill="#fff" stroke="${STROKE}" stroke-width="2.6"/>`;
  const braceBand = (label, y, height, inset = 12) => {
    body.push(
      brace(labelX, y + inset, y + height - inset, label, {
        ...archText,
        size: 22,
        lineHeight: 25,
      }),
    );
  };
  const placeCenteredRow = (items, y, height, opts = {}) => {
    const paddingLeft = opts.paddingLeft ?? opts.padding ?? 32;
    const paddingRight = opts.paddingRight ?? opts.padding ?? 32;
    const widths = items.map((item) =>
      typeof item === 'string' ? opts.width || 150 : item.width || opts.width || 150,
    );
    const available = bandWidth - paddingLeft - paddingRight;
    const totalWidth = widths.reduce((sum, width) => sum + width, 0);
    const defaultGap = items.length > 1 ? (available - totalWidth) / (items.length - 1) : 0;
    const gap = opts.gap ?? Math.max(opts.minGap ?? 18, defaultGap);
    const usedWidth = totalWidth + gap * Math.max(0, items.length - 1);
    let cursor = bandX + paddingLeft + Math.max(0, (available - usedWidth) / 2);

    items.forEach((item, idx) => {
      const spec = typeof item === 'string' ? { label: item, width: opts.width || 150 } : item;
      body.push(
        roundedBox(cursor, y, spec.width || opts.width || 150, height, spec.label, {
          size: spec.size || opts.size || 22,
          minSize: spec.minSize || opts.minSize || 12,
          preserveLines: spec.preserveLines ?? opts.preserveLines ?? false,
          maxLines: spec.maxLines || opts.maxLines || Infinity,
        }),
      );
      cursor += (spec.width || opts.width || 150) + (idx === items.length - 1 ? 0 : gap);
    });
  };

  body.push(
    `<rect x="${frameX}" y="${frameY}" width="${frameWidth}" height="${frameHeight}" fill="#fff" stroke="${STROKE}" stroke-width="3"/>`,
  );
  body.push(
    `<rect x="${frameX}" y="105" width="${frameWidth}" height="96" fill="#fff" stroke="${STROKE}" stroke-width="2.6"/>`,
  );
  body.push(text(840, 152, '平台系统架构图', { size: 36, family: BOLD, weight: '700' }));

  body.push(band(240, 110));
  body.push(band(390, 110));
  body.push(band(540, 275));
  body.push(band(855, 92));
  body.push(band(987, 104));
  body.push(band(1131, 104));

  braceBand('客户端', 240, 110);
  braceBand('对象', 390, 110);
  braceBand('服务应用层', 540, 275, 10);
  braceBand('数据层', 855, 92, 10);
  braceBand('数据库', 987, 104, 14);
  braceBand('运行环境', 1131, 104, 14);

  body.push(
    rect(340, 265, 1080, 62, '浏览器 / Web 客户端', { size: 26, family: BOLD, strokeWidth: 2.4 }),
  );
  placeCenteredRow(['终端用户', '管理员', '风控人员'], 420, 54, {
    width: 170,
    size: 23,
    padding: 140,
    minGap: 110,
  });
  placeCenteredRow(
    ['用户认证', '理财交易', '贷款审批', '风险监控', '经营分析', '数仓治理'],
    585,
    50,
    { width: 148, size: 19, padding: 34, minGap: 32 },
  );
  placeCenteredRow(
    [
      { label: ['注册登录', '个人中心'], width: 158, preserveLines: true, maxLines: 2 },
      { label: ['产品申购', '资产订单'], width: 158, preserveLines: true, maxLines: 2 },
      { label: ['贷款申请', '用户画像'], width: 158, preserveLines: true, maxLines: 2 },
      { label: ['风险预警', '事件处置'], width: 158, preserveLines: true, maxLines: 2 },
      { label: ['指标推送', '经营大屏'], width: 158, preserveLines: true, maxLines: 2 },
      { label: ['数据血缘', '任务日志'], width: 158, preserveLines: true, maxLines: 2 },
    ],
    700,
    72,
    { size: 17, padding: 24, minGap: 28, preserveLines: true, maxLines: 2 },
  );
  placeCenteredRow(
    [
      { label: '用户表', width: 130 },
      { label: '产品表', width: 130 },
      { label: '订单表', width: 130 },
      { label: '持仓表', width: 130 },
      { label: '贷款表', width: 130 },
      { label: '风控事件表', width: 146 },
      { label: '指标结果表', width: 146 },
    ],
    876,
    48,
    { size: 18, padding: 18, minGap: 22 },
  );
  body.push(cylinder(760, 1008, 160, 62, 'MySQL 8.0', { size: 24, family: BOLD }));
  placeCenteredRow(
    ['Docker Compose', 'Python 3.11', 'FastAPI', 'React + Vite', 'Node.js 22'],
    1158,
    48,
    {
      width: 178,
      size: 16,
      minSize: 11,
      padding: 48,
      minGap: 34,
    },
  );

  writeDiagram('system-architecture', 1700, 1360, body);
}
