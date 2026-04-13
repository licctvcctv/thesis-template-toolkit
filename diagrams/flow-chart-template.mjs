export function buildFlowChartTemplate(runtime, name, config) {
  const { rect, diamond, cylinder, vLine, hLine, pathLine, text, writeDiagram } = runtime;
  const body = [];
  const centerX = 800;
  const topW = 220;
  const stepW = 320;
  const wideStepW = 420;
  const successBox = {
    x: centerX - 150,
    y: 790,
    width: 300,
    height: 70,
  };
  const startLabel = config.startLabel || '开始';
  const endLabel = config.endLabel || '流程结束';
  const yesLabel = config.yesLabel || '是';
  const noLabel = config.noLabel || '否';

  body.push(rect(centerX - topW / 2, 110, topW, 74, startLabel, { rounded: true, size: 28 }));
  body.push(rect(centerX - stepW / 2, 250, stepW, 70, config.page, { size: 26 }));
  body.push(
    rect(centerX - wideStepW / 2, 420, wideStepW, 90, config.input, {
      size: 26,
      preserveLines: true,
      maxLines: 2,
    }),
  );
  body.push(diamond(centerX, 640, 380, 140, config.check, { size: 21, maxLines: 2 }));
  body.push(
    rect(1080, 590, 250, 88, config.reject, { size: 24, preserveLines: true, maxLines: 2 }),
  );
  body.push(cylinder(120, 590, 130, 110, config.database, { size: 22 }));
  body.push(
    rect(successBox.x, successBox.y, successBox.width, successBox.height, config.success, {
      size: 25,
    }),
  );
  body.push(rect(centerX - 160, 950, 320, 70, config.result, { size: 25 }));
  body.push(rect(centerX - 140, 1090, 280, 74, endLabel, { rounded: true, size: 28 }));

  body.push(vLine(centerX, 184, 250, { arrow: true }));
  body.push(vLine(centerX, 320, 420, { arrow: true }));
  body.push(vLine(centerX, 510, 570, { arrow: true }));
  body.push(vLine(centerX, 710, 790, { arrow: true }));
  body.push(vLine(centerX, 860, 950, { arrow: true }));
  body.push(vLine(centerX, 1020, 1090, { arrow: true }));

  body.push(hLine(990, 1080, 640, { arrow: true }));
  body.push(text(1035, 606, noLabel, { size: 24 }));
  body.push(
    pathLine(
      [
        [1205, 590],
        [1205, 270],
        [960, 270],
      ],
      { arrow: true },
    ),
  );

  body.push(
    pathLine(
      [
        [610, 640],
        [250, 640],
      ],
      { arrow: true },
    ),
  );
  body.push(
    pathLine(
      [
        [185, 700],
        [185, successBox.y + successBox.height / 2],
        [successBox.x, successBox.y + successBox.height / 2],
      ],
      { arrow: true },
    ),
  );
  body.push(text(835, 748, yesLabel, { size: 24, anchor: 'start' }));

  writeDiagram(name, 1400, 1220, body);
}
