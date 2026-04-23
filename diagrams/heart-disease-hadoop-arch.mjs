export function buildHeartDiseaseHadoopArch(runtime) {
  const { rect, brace, text, writeDiagram, BOLD, STROKE, snap } = runtime;
  const body = [];
  const frameX = 80;
  const frameY = 40;
  const frameWidth = 1200;
  const frameHeight = 700;
  const bandX = 280;
  const bandWidth = 900;
  const labelX = 200;
  const archText = { family: BOLD, weight: '400' };

  const roundedBox = (x, y, width, height, label, opts = {}) =>
    rect(x, y, width, height, label, {
      rounded: true, size: opts.size || 20, minSize: opts.minSize || 12,
      family: opts.family || BOLD, weight: '400', strokeWidth: 2.6,
      preserveLines: opts.preserveLines || false, maxLines: opts.maxLines || Infinity,
    });
  const band = (y, height) =>
    `<rect x="${bandX}" y="${snap(y)}" width="${bandWidth}" height="${snap(height)}" fill="#fff" stroke="${STROKE}" stroke-width="2.6"/>`;
  const braceBand = (label, y, height, inset = 12) => {
    body.push(brace(labelX, y + inset, y + height - inset, label, { ...archText, size: 20, lineHeight: 23 }));
  };
  const placeCenteredRow = (items, y, height, opts = {}) => {
    const padding = opts.padding || 32;
    const available = bandWidth - padding * 2;
    const widths = items.map(i => typeof i === 'string' ? opts.width || 150 : i.width || opts.width || 150);
    const totalWidth = widths.reduce((s, w) => s + w, 0);
    const gap = opts.gap ?? Math.max(opts.minGap || 18, items.length > 1 ? (available - totalWidth) / (items.length - 1) : 0);
    const usedWidth = totalWidth + gap * Math.max(0, items.length - 1);
    let cursor = bandX + padding + Math.max(0, (available - usedWidth) / 2);
    items.forEach((item, idx) => {
      const spec = typeof item === 'string' ? { label: item } : item;
      body.push(roundedBox(cursor, y, spec.width || opts.width || 150, height, spec.label, {
        size: spec.size || opts.size || 18,
        preserveLines: spec.preserveLines ?? false,
        maxLines: spec.maxLines || Infinity,
      }));
      cursor += (spec.width || opts.width || 150) + gap;
    });
  };

  body.push(`<rect x="${frameX}" y="${frameY}" width="${frameWidth}" height="${frameHeight}" fill="#fff" stroke="${STROKE}" stroke-width="3"/>`);
  body.push(`<rect x="${frameX}" y="100" width="${frameWidth}" height="80" fill="#fff" stroke="${STROKE}" stroke-width="2.6"/>`);
  body.push(text(680, 140, 'Hadoop分布式计算框架架构', { size: 30, family: BOLD, weight: '700' }));

  body.push(band(220, 100));  // 应用层
  body.push(band(360, 100));  // 资源调度
  body.push(band(500, 100));  // 存储层
  body.push(band(640, 80));   // 基础设施

  braceBand('应用层', 220, 100);
  braceBand('资源调度', 360, 100);
  braceBand('存储层', 500, 100);
  braceBand('基础设施', 640, 80, 8);

  // 应用层
  placeCenteredRow([
    { label: 'Hive 数据仓库', width: 220 },
    { label: 'MapReduce 批处理', width: 220 },
    { label: 'Spark（可选）', width: 220 },
  ], 245, 52, { size: 18, padding: 60, minGap: 50 });

  // 资源调度
  placeCenteredRow([
    { label: 'ResourceManager\n（全局资源管理）', width: 300, preserveLines: true, maxLines: 2 },
    { label: 'NodeManager\n（节点容器管理）', width: 300, preserveLines: true, maxLines: 2 },
  ], 380, 60, { size: 16, padding: 60, minGap: 80 });

  // 存储层
  placeCenteredRow([
    { label: 'NameNode\n（元数据管理）', width: 220, preserveLines: true, maxLines: 2 },
    { label: 'DataNode × N\n（数据块存储）', width: 220, preserveLines: true, maxLines: 2 },
    { label: '128MB数据块\n3副本容错', width: 220, preserveLines: true, maxLines: 2 },
  ], 520, 60, { size: 16, padding: 50, minGap: 40 });

  // 基础设施
  placeCenteredRow([
    { label: '服务器集群（多节点）', width: 500 },
  ], 660, 44, { size: 18, padding: 180 });

  writeDiagram('heart-disease-hadoop-arch', 1400, 780, body);
}
