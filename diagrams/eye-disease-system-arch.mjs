export function buildEyeDiseaseSystemArch(runtime) {
  const { rect, cylinder, brace, text, writeDiagram, BOLD, STROKE, snap } = runtime;
  const body = [];
  const frameX = 40;
  const frameY = 40;
  const frameWidth = 1600;
  const frameHeight = 1100;
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

  // 外框
  body.push(
    `<rect x="${frameX}" y="${frameY}" width="${frameWidth}" height="${frameHeight}" fill="#fff" stroke="${STROKE}" stroke-width="3"/>`,
  );
  // 标题栏
  body.push(
    `<rect x="${frameX}" y="105" width="${frameWidth}" height="96" fill="#fff" stroke="${STROKE}" stroke-width="2.6"/>`,
  );
  body.push(text(840, 152, '眼底疾病智能识别系统架构图', { size: 36, family: BOLD, weight: '700' }));

  // 五个横带
  body.push(band(240, 100));   // 客户端
  body.push(band(380, 100));   // 用户角色
  body.push(band(520, 260));   // 服务应用层
  body.push(band(820, 92));    // 数据层
  body.push(band(950, 104));   // 运行环境

  braceBand('客户端', 240, 100);
  braceBand('用户角色', 380, 100);
  braceBand('服务应用层', 520, 260, 10);
  braceBand('数据层', 820, 92, 10);
  braceBand('运行环境', 950, 104, 14);

  // 客户端
  body.push(
    rect(340, 262, 1080, 56, '浏览器 / Web 客户端', { size: 26, family: BOLD, strokeWidth: 2.4 }),
  );
  // 用户角色
  placeCenteredRow(['医生', '患者', '系统管理员'], 405, 54, {
    width: 170,
    size: 23,
    padding: 140,
    minGap: 110,
  });
  // 服务应用层 - 功能模块
  placeCenteredRow(
    ['用户认证', '智能诊断', '数据预处理', '模型对比', '历史记录'],
    560,
    50,
    { width: 168, size: 20, padding: 34, minGap: 32 },
  );
  // 服务应用层 - 核心引擎
  placeCenteredRow(
    [
      { label: ['图像裁剪', '尺寸归一化'], width: 170, preserveLines: true, maxLines: 2 },
      { label: ['ResNet50', '模型推理'], width: 170, preserveLines: true, maxLines: 2 },
      { label: ['MobileNetV3', '模型推理'], width: 170, preserveLines: true, maxLines: 2 },
      { label: ['多标签概率', '结果解析'], width: 170, preserveLines: true, maxLines: 2 },
      { label: ['灰度/去噪', '均衡/归一化'], width: 170, preserveLines: true, maxLines: 2 },
    ],
    680,
    72,
    { size: 17, padding: 24, minGap: 28, preserveLines: true, maxLines: 2 },
  );
  // 数据层
  placeCenteredRow(
    [
      { label: '用户表', width: 150 },
      { label: '模型权重', width: 150 },
      { label: '眼底图像', width: 150 },
      { label: '预处理结果', width: 150 },
      { label: '训练报告', width: 150 },
    ],
    840,
    52,
    { size: 18, padding: 18, minGap: 22 },
  );
  // 运行环境
  placeCenteredRow(
    ['Python 3.9+', 'Django 4.2', 'PyTorch 2.0', 'Bootstrap 5', 'SQLite'],
    978,
    48,
    {
      width: 178,
      size: 16,
      minSize: 11,
      padding: 48,
      minGap: 34,
    },
  );

  writeDiagram('eye-disease-system-arch', 1700, 1180, body);
}
