export function buildHeartDiseaseWarehouse(runtime) {
  const { rect, cylinder, vLine, hLine, pathLine, text, writeDiagram, BOLD, STROKE, snap } = runtime;
  const body = [];

  // 标题
  body.push(text(900, 50, '数据仓库ODS-DWD-ADS分层架构', { size: 32, family: BOLD, weight: '700' }));

  // === 数据源列 ===
  const srcX = 60;
  body.push(text(srcX + 90, 120, '数据源', { size: 22, family: BOLD }));
  body.push(rect(srcX, 150, 200, 56, 'Kaggle 2020 CSV', { size: 16, rounded: true, strokeWidth: 2.4 }));
  body.push(rect(srcX, 226, 200, 56, 'Kaggle 2022 CSV', { size: 16, rounded: true, strokeWidth: 2.4 }));
  body.push(rect(srcX, 302, 200, 56, 'UCI Cleveland', { size: 16, rounded: true, strokeWidth: 2.4 }));
  body.push(rect(srcX, 378, 200, 56, 'UCI Cost Data', { size: 16, rounded: true, strokeWidth: 2.4 }));

  // 箭头 数据源 → ODS
  const arrowSrcX = srcX + 200;
  const odsX = 360;
  [178, 254, 330, 406].forEach(y => {
    body.push(hLine(arrowSrcX, odsX, y, { arrow: true }));
  });

  // === ODS 列 ===
  body.push(text(odsX + 110, 100, 'ODS层', { size: 22, family: BOLD }));
  body.push(text(odsX + 110, 125, '（原始数据层）', { size: 16 }));
  body.push(cylinder(odsX, 150, 220, 60, 'ods_heart_2020_raw', { size: 14 }));
  body.push(cylinder(odsX, 226, 220, 60, 'ods_heart_2022_raw', { size: 14 }));
  body.push(cylinder(odsX, 302, 220, 60, 'ods_uci_cleveland_raw', { size: 14 }));
  body.push(cylinder(odsX, 378, 220, 60, 'ods_uci_cost_raw', { size: 14 }));

  // 箭头 ODS → DWD
  const arrowOdsX = odsX + 220;
  const dwdX = 680;
  body.push(pathLine([[arrowOdsX, 180], [dwdX, 180]], { arrow: true }));
  body.push(pathLine([[arrowOdsX, 256], [dwdX, 222]], { arrow: true }));
  body.push(pathLine([[arrowOdsX, 332], [dwdX, 310]], { arrow: true }));
  body.push(pathLine([[arrowOdsX, 406], [dwdX, 376]], { arrow: true }));

  // 中间注释
  body.push(text(640, 440, 'INSERT OVERWRITE', { size: 14, fill: '#666' }));
  body.push(text(640, 460, '类型转换 / 缺失值处理', { size: 14, fill: '#666' }));

  // === DWD 列 ===
  body.push(text(dwdX + 110, 100, 'DWD层', { size: 22, family: BOLD }));
  body.push(text(dwdX + 110, 125, '（清洗明细层）', { size: 16 }));
  body.push(cylinder(dwdX, 150, 220, 52, 'dwd_heart_2020_clean', { size: 13 }));
  body.push(cylinder(dwdX, 216, 220, 52, 'dwd_heart_2022_clean', { size: 13 }));
  body.push(cylinder(dwdX, 282, 220, 52, 'dwd_uci_cleveland_clean', { size: 12 }));
  body.push(cylinder(dwdX, 348, 220, 52, 'dwd_uci_cost_clean', { size: 13 }));
  body.push(cylinder(dwdX, 414, 220, 52, 'dwd_heart_feature_sample', { size: 12 }));

  // 箭头 DWD → ADS
  const arrowDwdX = dwdX + 220;
  const adsX = 1010;
  body.push(pathLine([[arrowDwdX, 200], [adsX, 180]], { arrow: true }));
  body.push(pathLine([[arrowDwdX, 320], [adsX, 280]], { arrow: true }));
  body.push(pathLine([[arrowDwdX, 440], [adsX, 380]], { arrow: true }));

  body.push(text(960, 460, 'GROUP BY 聚合', { size: 14, fill: '#666' }));

  // === ADS 列 ===
  body.push(text(adsX + 110, 100, 'ADS层', { size: 22, family: BOLD }));
  body.push(text(adsX + 110, 125, '（应用聚合层）', { size: 16 }));
  const adsNames = [
    'ads_heart_overview',
    'ads_heart_by_age',
    'ads_heart_by_sex',
    'ads_heart_by_bmi',
    'ads_heart_lifestyle',
    'ads_heart_comorbidity',
    'ads_uci_clinical_risk',
    'ads_uci_cost_analysis',
    'ads_model_metrics',
  ];
  adsNames.forEach((name, i) => {
    body.push(cylinder(adsX, 150 + i * 46, 220, 40, name, { size: 11 }));
  });

  // 箭头 ADS → MySQL
  const arrowAdsX = adsX + 220;
  const mysqlX = 1340;
  body.push(pathLine([[arrowAdsX, 300], [mysqlX, 260]], { arrow: true }));
  body.push(text(1290, 220, 'Python同步', { size: 14, fill: '#666' }));

  // === MySQL ===
  body.push(text(mysqlX + 80, 100, '应用端', { size: 22, family: BOLD }));
  body.push(cylinder(mysqlX, 240, 180, 80, 'MySQL ADS表', { size: 16 }));
  body.push(vLine(mysqlX + 90, 320, 370, { arrow: true }));
  body.push(rect(mysqlX, 370, 180, 60, 'Django API', { size: 18, family: BOLD, rounded: true, strokeWidth: 2.4 }));
  body.push(vLine(mysqlX + 90, 430, 470, { arrow: true }));
  body.push(rect(mysqlX, 470, 180, 60, 'Vue3 前端', { size: 18, family: BOLD, rounded: true, strokeWidth: 2.4 }));

  writeDiagram('heart-disease-warehouse', 1600, 560, body);
}
