export function buildHeartDiseaseHiveArch(runtime) {
  const { rect, cylinder, vLine, hLine, pathLine, text, writeDiagram, BOLD, STROKE } = runtime;
  const body = [];

  body.push(text(700, 44, 'Hive数据仓库工作原理', { size: 30, family: BOLD, weight: '700' }));

  // === 用户接口（左上）===
  body.push(rect(60, 100, 160, 50, 'CLI 命令行', { size: 16, rounded: true, strokeWidth: 2.4 }));
  body.push(rect(60, 170, 160, 50, 'JDBC / ODBC', { size: 16, rounded: true, strokeWidth: 2.4 }));
  body.push(rect(60, 240, 160, 50, 'Web UI', { size: 16, rounded: true, strokeWidth: 2.4 }));
  body.push(text(140, 80, '用户接口', { size: 18, family: BOLD }));

  // 箭头 接口 → Driver
  body.push(pathLine([[220, 125], [340, 180]], { arrow: true }));
  body.push(pathLine([[220, 195], [340, 210]], { arrow: true }));
  body.push(pathLine([[220, 265], [340, 240]], { arrow: true }));
  body.push(text(280, 155, 'HiveQL', { size: 14, fill: '#666' }));

  // === Driver 驱动器（中间大框）===
  body.push(rect(340, 100, 620, 200, '', { strokeWidth: 2.8 }));
  body.push(text(650, 120, 'Driver 驱动器', { size: 20, family: BOLD }));

  // 4个子模块横排
  const driverModules = [
    { label: '解析器\n(Parser)', x: 370 },
    { label: '编译器\n(Compiler)', x: 510 },
    { label: '优化器\n(Optimizer)', x: 650 },
    { label: '执行器\n(Executor)', x: 790 },
  ];
  driverModules.forEach((m, i) => {
    body.push(rect(m.x, 155, 120, 60, m.label, { size: 14, preserveLines: true, maxLines: 2, strokeWidth: 2 }));
    if (i < driverModules.length - 1) {
      body.push(hLine(m.x + 120, driverModules[i + 1].x, 185, { arrow: true }));
    }
  });
  body.push(text(560, 250, 'SQL → AST → 逻辑计划 → 优化 → 物理计划', { size: 13, fill: '#666' }));

  // === MetaStore（下方）===
  body.push(cylinder(460, 360, 280, 80, 'MetaStore（MySQL）', { size: 16 }));
  body.push(text(600, 460, '表结构 / 分区信息 / HDFS路径映射', { size: 13, fill: '#666' }));
  // 双向箭头 Driver ↔ MetaStore
  body.push(vLine(600, 300, 360, { arrow: true }));
  body.push(vLine(640, 360, 300, { arrow: true }));

  // === 执行引擎（右侧）===
  body.push(hLine(960, 1060, 185, { arrow: true }));
  body.push(text(1010, 165, '提交任务', { size: 14, fill: '#666' }));
  body.push(rect(1060, 100, 200, 70, 'MapReduce / Tez\n计算引擎', { size: 16, preserveLines: true, maxLines: 2 }));
  body.push(vLine(1160, 170, 240, { arrow: true }));

  // YARN
  body.push(rect(1060, 240, 200, 60, 'YARN\n资源调度', { size: 16, preserveLines: true, maxLines: 2 }));
  body.push(vLine(1160, 300, 360, { arrow: true }));

  // === HDFS（底部）===
  body.push(cylinder(1000, 360, 320, 80, 'HDFS 分布式文件系统', { size: 18 }));
  body.push(text(1160, 460, '数据读写', { size: 14, fill: '#666' }));

  // 结果返回
  body.push(pathLine([[1060, 135], [960, 135]], { arrow: true, dashed: true }));
  body.push(text(1010, 118, '返回结果', { size: 13, fill: '#666' }));

  writeDiagram('heart-disease-hive-arch', 1400, 500, body);
}
