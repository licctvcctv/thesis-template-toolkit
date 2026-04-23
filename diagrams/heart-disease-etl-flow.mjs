export function buildHeartDiseaseEtlFlow(runtime) {
  const { rect, vLine, hLine, pathLine, text, writeDiagram, BOLD, STROKE } = runtime;
  const body = [];
  const centerY = 200;
  const boxH = 70;
  const boxW = 180;

  body.push(text(800, 44, '数据处理ETL流程', { size: 32, family: BOLD, weight: '700' }));

  // 从左到右的流程
  let x = 40;

  // CSV原始文件
  body.push(rect(x, centerY - boxH / 2, boxW, boxH, 'CSV原始文件\n(Kaggle/UCI)', { size: 16, preserveLines: true, maxLines: 2, rounded: true, strokeWidth: 2.4 }));
  x += boxW;
  body.push(hLine(x, x + 40, centerY, { arrow: true }));
  x += 40;

  // 上传HDFS
  body.push(rect(x, centerY - boxH / 2, 140, boxH, '上传至\nHDFS', { size: 16, preserveLines: true, maxLines: 2 }));
  x += 140;
  body.push(hLine(x, x + 40, centerY, { arrow: true }));
  x += 40;

  // ODS建表
  body.push(rect(x, centerY - boxH / 2, boxW, boxH, 'Hive ODS\n建外部表(4张)', { size: 16, preserveLines: true, maxLines: 2 }));
  body.push(text(x + boxW / 2, centerY + 55, 'OpenCSVSerde', { size: 13, fill: '#666' }));
  body.push(text(x + boxW / 2, centerY + 73, 'STRING类型原样载入', { size: 13, fill: '#666' }));
  x += boxW;
  body.push(hLine(x, x + 40, centerY, { arrow: true }));
  x += 40;

  // DWD清洗
  body.push(rect(x, centerY - boxH / 2, boxW, boxH, 'Hive DWD\n清洗转换(5张)', { size: 16, preserveLines: true, maxLines: 2 }));
  body.push(text(x + boxW / 2, centerY + 55, 'INSERT OVERWRITE', { size: 13, fill: '#666' }));
  body.push(text(x + boxW / 2, centerY + 73, '类型转换/Yes→1/缺失→NULL', { size: 12, fill: '#666' }));
  x += boxW;
  body.push(hLine(x, x + 40, centerY, { arrow: true }));
  x += 40;

  // ADS聚合
  body.push(rect(x, centerY - boxH / 2, boxW, boxH, 'Hive ADS\nGROUP BY聚合(9张)', { size: 15, preserveLines: true, maxLines: 2 }));
  body.push(text(x + boxW / 2, centerY + 55, '多维统计', { size: 13, fill: '#666' }));
  body.push(text(x + boxW / 2, centerY + 73, '年龄/性别/BMI/共病/临床', { size: 12, fill: '#666' }));
  x += boxW;
  body.push(hLine(x, x + 40, centerY, { arrow: true }));
  x += 40;

  // Python同步
  body.push(rect(x, centerY - boxH / 2, 150, boxH, 'Python\n同步脚本', { size: 16, preserveLines: true, maxLines: 2 }));
  x += 150;
  body.push(hLine(x, x + 40, centerY, { arrow: true }));
  x += 40;

  // MySQL
  body.push(rect(x, centerY - boxH / 2, 140, boxH, 'MySQL\nADS表', { size: 16, preserveLines: true, maxLines: 2 }));
  x += 140;
  body.push(hLine(x, x + 40, centerY, { arrow: true }));
  x += 40;

  // Django API
  body.push(rect(x, centerY - boxH / 2, 140, boxH, 'Django\nREST API', { size: 16, preserveLines: true, maxLines: 2, rounded: true, strokeWidth: 2.4 }));

  writeDiagram('heart-disease-etl-flow', 1600, 340, body);
}
