export function buildRadialUseCase(runtime, fileName, actorLabel, leftItems, rightItems) {
  const { text, writeDiagram } = runtime;
  const lightStroke = '#b5b5b5';
  const lightText = '#5c5c5c';
  const line = (x1, y1, x2, y2, width = 2.4) =>
    `<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="${lightStroke}" stroke-width="${width}" stroke-linecap="round"/>`;
  const label = (x, y, value, size = 30) => text(x, y, value, { size, fill: lightText });
  const oval = (cx, cy, rx, ry, value) =>
    `<ellipse cx="${cx}" cy="${cy}" rx="${rx}" ry="${ry}" fill="#ffffff" stroke="${lightStroke}" stroke-width="2.6"/>${label(cx, cy, value)}`;
  const actor = `
    <circle cx="590" cy="416" r="16" fill="#ffffff" stroke="${lightStroke}" stroke-width="2.6"/>
    <rect x="568" y="448" width="44" height="76" rx="6" ry="6" fill="#ffffff" stroke="${lightStroke}" stroke-width="2.6"/>
    ${line(568, 468, 532, 496)}
    ${line(612, 468, 648, 496)}
    ${line(582, 488, 582, 558)}
    ${line(598, 488, 598, 558)}
    ${label(590, 590, actorLabel, 28)}`;

  const body = [actor];
  leftItems.forEach(([value, x, y]) => {
    body.push(line(560, 465, 290, y));
    body.push(oval(x, y, 110, 42, value));
  });
  rightItems.forEach(([value, x, y]) => {
    body.push(line(620, 465, 890, y));
    body.push(oval(x, y, 110, 42, value));
  });

  writeDiagram(fileName, 1180, 980, body);
}
