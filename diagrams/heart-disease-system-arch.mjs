export function buildHeartDiseaseSystemArch(runtime) {
  const { rect, brace, text, writeDiagram, BOLD, STROKE, snap } = runtime;
  const body = [];
  const frameX = 40;
  const frameY = 40;
  const frameWidth = 1600;
  const frameHeight = 1260;
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
  body.push(text(840, 152, '心脏病健康数据分析系统架构图', { size: 36, family: BOLD, weight: '700' }));

  // 六个横带
  body.push(band(240, 100));   // 客户端
  body.push(band(380, 100));   // 展示层
  body.push(band(520, 140));   // 服务层
  body.push(band(700, 140));   // 数据层
  body.push(band(880, 140));   // 大数据层
  body.push(band(1060, 104));  // 运行环境

  braceBand('客户端', 240, 100);
  braceBand('展示层', 380, 100);
  braceBand('服务层', 520, 140, 10);
  braceBand('数据层', 700, 140, 10);
  braceBand('大数据层', 880, 140, 10);
  braceBand('运行环境', 1060, 104, 14);

  // 客户端
  body.push(
    rect(340, 262, 1080, 56, '浏览器 / Web 客户端', { size: 26, family: BOLD, strokeWidth: 2.4 }),
  );
  // 展示层
  placeCenteredRow(
    [
      { label: ['可视化大屏', 'ECharts'], width: 220, preserveLines: true, maxLines: 2 },
      { label: ['分页分析界面', 'Naive UI'], width: 220, preserveLines: true, maxLines: 2 },
      { label: ['风险预测页面', '表单 + 结果卡片'], width: 220, preserveLines: true, maxLines: 2 },
      { label: ['系统管理', '用户/日志/监控'], width: 220, preserveLines: true, maxLines: 2 },
    ],
    400,
    60,
    { size: 17, padding: 34, minGap: 28, preserveLines: true, maxLines: 2 },
  );
  // 服务层
  placeCenteredRow(
    ['用户认证', '数据查询API', '在线预测API', '模型加载'],
    545,
    50,
    { width: 200, size: 20, padding: 34, minGap: 48 },
  );
  placeCenteredRow(
    [
      { label: ['JWT令牌', '会话管理'], width: 170, preserveLines: true, maxLines: 2 },
      { label: ['ADS表查询', 'Repository模式'], width: 200, preserveLines: true, maxLines: 2 },
      { label: ['Pipeline预处理', '逻辑回归推理'], width: 200, preserveLines: true, maxLines: 2 },
      { label: ['joblib反序列化', '特征默认值填充'], width: 200, preserveLines: true, maxLines: 2 },
    ],
    615,
    52,
    { size: 15, padding: 34, minGap: 28, preserveLines: true, maxLines: 2 },
  );
  // 数据层
  placeCenteredRow(
    [
      { label: 'MySQL ADS聚合表', width: 200 },
      { label: '用户账户表', width: 160 },
      { label: '预测记录表', width: 160 },
      { label: '模型文件(joblib)', width: 200 },
      { label: '特征重要性JSON', width: 200 },
    ],
    730,
    50,
    { size: 16, padding: 18, minGap: 18 },
  );
  placeCenteredRow(
    [
      { label: ['Kaggle 2020', '319795条×18字段'], width: 220, preserveLines: true, maxLines: 2 },
      { label: ['Kaggle 2022', '246022条×40字段'], width: 220, preserveLines: true, maxLines: 2 },
      { label: ['UCI Cleveland', '303条×14字段'], width: 220, preserveLines: true, maxLines: 2 },
    ],
    795,
    46,
    { size: 14, padding: 80, minGap: 40, preserveLines: true, maxLines: 2 },
  );
  // 大数据层
  placeCenteredRow(
    [
      { label: ['HDFS', '分布式文件存储'], width: 200, preserveLines: true, maxLines: 2 },
      { label: ['Hive ODS', '原始数据层(4表)'], width: 200, preserveLines: true, maxLines: 2 },
      { label: ['Hive DWD', '清洗明细层(5表)'], width: 200, preserveLines: true, maxLines: 2 },
      { label: ['Hive ADS', '聚合应用层(9表)'], width: 200, preserveLines: true, maxLines: 2 },
    ],
    905,
    60,
    { size: 16, padding: 34, minGap: 28, preserveLines: true, maxLines: 2 },
  );
  placeCenteredRow(
    [
      { label: ['MapReduce', 'ETL数据清洗'], width: 240, preserveLines: true, maxLines: 2 },
      { label: ['Python同步脚本', 'Hive ADS → MySQL'], width: 260, preserveLines: true, maxLines: 2 },
    ],
    980,
    46,
    { size: 15, padding: 180, minGap: 120, preserveLines: true, maxLines: 2 },
  );
  // 运行环境
  placeCenteredRow(
    ['Python 3.10', 'Django 4.2', 'Vue3 + Vite', 'MySQL 8.0', 'Hadoop 3.x', 'Docker'],
    1090,
    46,
    { width: 160, size: 15, minSize: 11, padding: 28, minGap: 18 },
  );

  writeDiagram('heart-disease-system-arch', 1700, 1340, body);
}
