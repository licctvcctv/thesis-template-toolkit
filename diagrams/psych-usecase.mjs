import { createRuntime, parseArgs } from './runtime.mjs';

const args = parseArgs();
const R = createRuntime(args);
const { ellipse, pathLine, text, actor, writeDiagram, STROKE } = R;

function buildAdminUseCase() {
  const body = [];
  const W = 780, H = 620;

  // System boundary (dashed rectangle)
  body.push(`<rect x="210" y="20" width="520" height="560" fill="none" stroke="${STROKE}" stroke-width="2" stroke-dasharray="10 6" rx="6" ry="6"/>`);
  body.push(text(470, 50, '综合心理服务平台', { size: 20, weight: '700' }));

  // Actor: 管理员
  body.push(actor(85, 160, '管理员'));

  // Use cases inside boundary
  const cx = 400, rx = 108, ry = 34;
  const useCases = ['用户账号管理', '咨询师审核管理', '社区内容审核', '数据统计与报表', '系统设置'];
  const ys = [100, 200, 310, 410, 510];

  // Actor body center at (85, ~250), spread connection points along the body
  const actorConnY = [220, 240, 260, 280, 300];

  for (let i = 0; i < useCases.length; i++) {
    body.push(ellipse(cx, ys[i], rx, ry, useCases[i], { size: 19 }));
    // Connect actor right side to use case left edge
    body.push(pathLine([[121, actorConnY[i]], [cx - rx, ys[i]]], { width: 2 }));
  }

  // <<include>> 社区内容审核 → 违规内容下架 (inside boundary, right side)
  const extX = 620, extY = 240;
  body.push(ellipse(extX, extY, 88, 30, '违规内容下架', { size: 16 }));
  // Dashed arrow from 社区内容审核 to 违规内容下架
  body.push(pathLine([[cx + rx - 30, ys[2] - ry + 5], [extX - 50, extY + 28]], { width: 1.5, dashed: true, arrow: true }));
  body.push(text(570, 295, '«include»', { size: 12 }));

  writeDiagram('psych-admin-usecase', W, H, body);
}

buildAdminUseCase();
