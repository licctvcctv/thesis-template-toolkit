/**
 * 陈才论文（房屋租赁与销售平台）图表生成器 v3
 */
import { createRuntime } from '../../../diagrams/runtime.mjs';

const runtime = createRuntime(new Map([
  ['--out-dir', '/Users/a136/vs/45425/thesis_project/papers/chencai/images'],
  ['--src-dir', '/Users/a136/vs/45425/thesis_project/papers/chencai/diagrams/svg-src'],
]));

const { rect, diamond, ellipse, cylinder, brace, pathLine, vLine, hLine, text,
        card, snap, createLayout, writeDiagram, STROKE, BOLD, actor } = runtime;

// ========== 1. 系统架构图 ==========
function buildArchitecture() {
  const body = [];
  const W = 1600, H = 820, frameX = 40, frameY = 40;
  const bandX = 280, bandW = 1240, labelX = 185;
  const bandH = 94;

  const band = (y, h) =>
    `<rect x="${bandX}" y="${snap(y)}" width="${bandW}" height="${snap(h)}" fill="#fff" stroke="${STROKE}" stroke-width="2.6"/>`;
  const braceBand = (label, y, h) => {
    body.push(brace(labelX, y + 12, y + h - 12, label, { size: 24, lineHeight: 27, family: BOLD }));
  };
  const roundedBox = (x, y, w, h, label, opts = {}) =>
    rect(x, y, w, h, label, { rounded: true, size: opts.size || 22, minSize: 14, family: BOLD, strokeWidth: 2.4 });
  const placeCenteredRow = (items, y, h, opts = {}) => {
    const pad = opts.padding || 32;
    const w = opts.width || 150;
    const avail = bandW - pad * 2;
    const gap = items.length > 1 ? (avail - w * items.length) / (items.length - 1) : 0;
    let cursor = bandX + pad + Math.max(0, (avail - (w * items.length + gap * (items.length - 1))) / 2);
    items.forEach((label, idx) => {
      body.push(roundedBox(cursor, y, w, h, label, opts));
      cursor += w + gap;
    });
  };

  // 外框
  body.push(`<rect x="${frameX}" y="${frameY}" width="${W - 80}" height="${H - 80}" fill="#fff" stroke="${STROKE}" stroke-width="3"/>`);

  // 五层
  body.push(band(90, bandH));
  body.push(band(220, bandH));
  body.push(band(350, bandH));
  body.push(band(480, bandH));
  body.push(band(610, bandH));

  braceBand('表现层', 90, bandH);
  braceBand('控制层', 220, bandH);
  braceBand('业务层', 350, bandH);
  braceBand('持久层', 480, bandH);
  braceBand('数据层', 610, bandH);

  placeCenteredRow(['JSP页面', 'HTML/CSS', 'JavaScript', '浏览器'], 112, 58, { width: 180, padding: 60, size: 20 });
  placeCenteredRow(['DispatcherServlet', 'Controller', '请求分发', '视图解析'], 242, 58, { width: 190, padding: 50, size: 18 });
  placeCenteredRow(['用户服务', '房屋服务', '订单服务', '公告服务'], 372, 58, { width: 180, padding: 60, size: 20 });
  placeCenteredRow(['AdminMapper', 'MemberMapper', 'FwMapper', 'DdMapper'], 502, 58, { width: 190, padding: 50, size: 18 });
  body.push(cylinder(bandX + bandW / 2 - 100, 630, 200, 74, 'MySQL 5.7', { size: 24, family: BOLD }));

  writeDiagram('chencai-architecture', W, H, body);
}

// ========== 1b. 用例图 ==========
function buildUseCaseDiagram(name, actorLabel, useCases) {
  const body = [];
  const W = 1600, H = 980;
  const actorX = 210, actorY = 290;
  const system = { x: 430, y: 70, w: 1080, h: 780 };
  const cols = [790, 1180];
  const rows = [240, 430, 620];

  body.push(`<rect x="${system.x}" y="${system.y}" width="${system.w}" height="${system.h}" fill="#fff" stroke="${STROKE}" stroke-width="3"/>`);
  body.push(text(system.x + system.w / 2, system.y + 34, '房屋租赁与销售平台', { size: 28, family: BOLD, weight: '700' }));
  body.push(actor(actorX, actorY, actorLabel));

  useCases.forEach((label, idx) => {
    const cx = idx < 3 ? cols[0] : cols[1];
    const cy = rows[idx % 3];
    const linkY = 250 + idx * 32;
    body.push(ellipse(cx, cy, 175, 56, label, { size: 24, minSize: 18, maxLines: 2 }));
    body.push(
      pathLine(
        [
          [actorX + 40, linkY],
          [360, linkY],
          [360, cy],
          [cx - 175, cy],
        ],
        { width: 2.6 },
      ),
    );
  });

  writeDiagram(name, W, H, body);
}

// ========== 2. ER图 — 手动布局（避免交叉线） ==========
function buildOverallERDiagram() {
  const body = [];
  const W = 1600, H = 1100;
  const layout = createLayout(W, H);
  const EW = 180, EH = 56;

  const entity = (cx, cy, label, w = EW) => {
    const node = { x: cx - w / 2, y: cy - EH / 2, w, h: EH, cx, cy };
    body.push(rect(node.x, node.y, node.w, node.h, label, { size: 22, family: BOLD, strokeWidth: 2.8 }));
    layout.registerBox(node);
    return node;
  };

  const rectAnchor = (node, tx, ty) => {
    const dx = tx - node.cx, dy = ty - node.cy;
    if (Math.abs(dx) * (node.h / 2) > Math.abs(dy) * (node.w / 2))
      return [dx >= 0 ? node.x + node.w : node.x, node.cy];
    return [node.cx, dy >= 0 ? node.y + node.h : node.y];
  };
  const diamondAnchor = (node, tx, ty) => {
    const dx = tx - node.cx, dy = ty - node.cy;
    if (Math.abs(dx) / (node.w / 2) > Math.abs(dy) / (node.h / 2))
      return [node.cx + (Math.sign(dx || 1) * node.w) / 2, node.cy];
    return [node.cx, node.cy + (Math.sign(dy || 1) * node.h) / 2];
  };
  const link = (e1, r, e2) => {
    const [x1, y1] = rectAnchor(e1, r.cx, r.cy);
    const [x2, y2] = diamondAnchor(r, e1.cx, e1.cy);
    body.push(pathLine([[x1, y1], [x2, y2]], { width: 2.5 }));
    const [x3, y3] = diamondAnchor(r, e2.cx, e2.cy);
    const [x4, y4] = rectAnchor(e2, r.cx, r.cy);
    body.push(pathLine([[x3, y3], [x4, y4]], { width: 2.5 }));
  };
  const rel = (cx, cy, label) => {
    const r = { cx, cy, w: 100, h: 56 };
    body.push(diamond(cx, cy, 100, 56, label, { size: 18, maxLines: 1 }));
    layout.registerBox({ x: cx - 50, y: cy - 28, w: 100, h: 56 }, 4);
    return r;
  };

  // 布局：上排3个，中排（房屋信息居中），下排（分类）
  //       管理员    用户     订单
  //  留言      房屋信息      公告
  //              分类
  const admin    = entity(250,  200, '管理员');
  const user     = entity(800,  200, '用户');
  const order    = entity(1350, 200, '订单');
  const msg      = entity(150,  600, '留言');
  const house    = entity(800,  600, '房屋信息', 200);
  const notice   = entity(1450, 600, '公告');
  const category = entity(800,  950, '分类');

  // 关系菱形
  const r1 = rel(525, 400, '管理');   // admin→house
  const r2 = rel(800, 420, '浏览');   // user→house
  const r3 = rel(1075, 200, '下单');  // user→order
  const r4 = rel(400, 600, '留言');   // user→msg (斜线)
  const r5 = rel(1200, 400, '发布');  // admin→notice
  const r6 = rel(800, 780, '属于');   // house→category

  // 连线
  link(admin, r1, house);
  link(user, r2, house);
  link(user, r3, order);
  // user→留言：从user底部到留言菱形
  const [ux1, uy1] = rectAnchor(user, r4.cx, r4.cy);
  const [dx1, dy1] = diamondAnchor(r4, user.cx, user.cy);
  body.push(pathLine([[ux1, uy1], [dx1, dy1]], { width: 2.5 }));
  const [dx2, dy2] = diamondAnchor(r4, msg.cx, msg.cy);
  const [mx1, my1] = rectAnchor(msg, r4.cx, r4.cy);
  body.push(pathLine([[dx2, dy2], [mx1, my1]], { width: 2.5 }));
  // admin→公告
  link(admin, r5, notice);
  link(house, r6, category);

  // 基数标注
  const cardLabel = (e1, e2, r) => {
    const dx = e2.cx - e1.cx, dy = e2.cy - e1.cy;
    const dist = Math.sqrt(dx * dx + dy * dy) || 1;
    const nx = dx / dist, ny = dy / dist;
    body.push(card(Math.round(e1.cx + nx * 80 + ny * 16), Math.round(e1.cy + ny * 80 - nx * 16), '1'));
    body.push(card(Math.round(e2.cx - nx * 80 + ny * 16), Math.round(e2.cy - ny * 80 - nx * 16), 'n'));
  };
  cardLabel(admin, house, r1);
  cardLabel(user, house, r2);
  cardLabel(user, order, r3);
  cardLabel(user, msg, r4);
  cardLabel(admin, notice, r5);
  cardLabel(house, category, r6);

  // 属性
  layout.autoAttrs(body, admin, ['编号', '账号', '密码', '姓名', '电话'],
    { startAngle: -Math.PI * 0.85, span: Math.PI * 0.7, radius: 140 });
  layout.autoAttrs(body, user, ['编号', '账号', '密码', '姓名', '手机号'],
    { startAngle: -Math.PI * 0.85, span: Math.PI * 0.7, radius: 140 });
  layout.autoAttrs(body, order, ['编号', '房屋名称', '用户姓名', '总价', '时间'],
    { startAngle: -Math.PI * 0.3, span: Math.PI * 0.6, radius: 140 });
  layout.autoAttrs(body, house, ['编号', '名称', '户型', '面积', '价格', '状态'],
    { startAngle: Math.PI * 0.15, span: Math.PI * 0.7, radius: 155 });
  layout.autoAttrs(body, msg, ['编号', '内容', '用户', '时间'],
    { startAngle: Math.PI * 0.2, span: Math.PI * 0.8, radius: 130 });
  layout.autoAttrs(body, notice, ['编号', '名称', '内容', '时间'],
    { startAngle: -Math.PI * 0.1, span: Math.PI * 0.8, radius: 130 });
  layout.autoAttrs(body, category, ['编号', '名称'],
    { startAngle: Math.PI * 0.55, span: Math.PI * 0.4, radius: 120 });

  writeDiagram('chencai-er-diagram', W, H, body);
}

// ========== 2b. 单实体 ER 图 ==========
function buildSingleEntityER(name, entityLabel, attrs) {
  const body = [];
  const count = attrs.length;
  const EW = 200, EH = 56;
  const AW = count <= 4 ? 110 : count <= 8 ? 95 : 82;
  const AH = count <= 4 ? 38 : 32;
  // span: 属性少时窄扇，多时宽扇
  const spanRatio = count <= 2 ? 0.55 : count <= 5 ? 0.7 : 0.85;
  // radius 确保相邻椭圆不重叠：r > AW * (count-1) / (span * π)
  const minR = count > 1 ? (AW * 1.35) * (count - 1) / (spanRatio * Math.PI) : 100;
  const radius = Math.max(150, Math.round(minR));
  const W = Math.max(500, radius * 2 + AW + 80);
  const H = radius + EH + 110;
  const cx = W / 2, cy = H - 55 - EH / 2;

  // 实体矩形（底部居中）
  body.push(rect(cx - EW / 2, cy - EH / 2, EW, EH, entityLabel, { size: 22, family: BOLD, strokeWidth: 2.8 }));

  // 属性向上扇出
  const startAngle = -Math.PI * (0.5 + spanRatio / 2);
  const span = Math.PI * spanRatio;
  attrs.forEach((label, i) => {
    const angle = count === 1 ? -Math.PI / 2 : startAngle + (span * i) / (count - 1);
    const ax = cx + Math.cos(angle) * radius;
    const ay = cy + Math.sin(angle) * radius;
    body.push(ellipse(ax, ay, AW, AH, label, { size: 16, strokeWidth: 1.6 }));
    body.push(pathLine([[cx, cy - EH / 2], [ax, ay + AH / 2]], { width: 1.8 }));
  });

  writeDiagram(name, W, H, body);
}

// ========== 3. 管理员核心类图 — 标准 UML 类图 ==========
function buildAdminClassDiagram() {
  const body = [];

  function classBox(x, y, w, name, stereotypes, attrs, methods) {
    const lineH = 20;
    const stereoH = stereotypes ? 18 : 0;
    const nameH = 32 + stereoH;
    const attrH = Math.max(attrs.length * lineH, lineH) + 8;
    const methH = Math.max(methods.length * lineH, lineH) + 8;
    const h = nameH + attrH + methH;

    body.push(`<rect x="${snap(x)}" y="${snap(y)}" width="${snap(w)}" height="${snap(h)}" fill="#fff" stroke="${STROKE}" stroke-width="2.4"/>`);

    if (stereotypes) {
      body.push(text(x + w / 2, y + 14, stereotypes, { size: 13, fill: '#555' }));
    }
    body.push(text(x + w / 2, y + (stereoH ? 32 : nameH / 2), name, { size: 17, weight: '700', family: BOLD }));

    const y1 = y + nameH;
    body.push(`<line x1="${snap(x)}" y1="${snap(y1)}" x2="${snap(x + w)}" y2="${snap(y1)}" stroke="${STROKE}" stroke-width="1.2"/>`);
    attrs.forEach((a, i) => {
      body.push(text(x + 10, y1 + 12 + i * lineH, a, { size: 13, anchor: 'start' }));
    });

    const y2 = y1 + attrH;
    body.push(`<line x1="${snap(x)}" y1="${snap(y2)}" x2="${snap(x + w)}" y2="${snap(y2)}" stroke="${STROKE}" stroke-width="1.2"/>`);
    methods.forEach((m, i) => {
      body.push(text(x + 10, y2 + 12 + i * lineH, m, { size: 13, anchor: 'start' }));
    });

    return { cx: x + w / 2, cy: y + h / 2, top: y, bottom: y + h, left: x, right: x + w, w, h };
  }

  // Controller
  const ctrl = classBox(20, 30, 240, 'AdminController', null,
    ['+login(): ModelAndView', '+editInfo(): String', '+updatePwd(): String'],
    ['-adminService: AdminService']);

  // Service 接口
  const svcI = classBox(340, 30, 240, 'AdminService', '<<interface>>',
    ['+checkLogin(): Admin', '+getById(): Admin', '+updateInfo(): void', '+updatePwd(): boolean'],
    []);

  // Service 实现
  const svcImpl = classBox(340, 280, 240, 'AdminServiceImpl', null,
    ['-adminMapper: AdminMapper'],
    ['+checkLogin(): Admin', '+getById(): Admin', '+updateInfo(): void']);

  // Mapper 接口
  const mapper = classBox(680, 30, 230, 'AdminMapper', '<<interface>>',
    ['+selectByNamePwd(): Admin', '+selectById(): Admin', '+updateById(): int'],
    []);

  // Entity
  const entity = classBox(680, 280, 230, 'Admin', null,
    ['-id: int', '-name: String', '-password: String', '-realname: String', '-sex: String', '-tel: String'],
    ['+getter/setter()']);

  // 关系线
  // Controller --依赖--> Service接口
  body.push(pathLine([[ctrl.right, ctrl.cy], [svcI.left, svcI.cy]], { arrow: true, dashed: true, width: 2 }));
  body.push(text((ctrl.right + svcI.left) / 2, ctrl.cy - 14, '依赖', { size: 13 }));

  // ServiceImpl --|> Service接口（实现）
  body.push(pathLine([[svcImpl.cx, svcImpl.top], [svcI.cx, svcI.bottom]], { arrow: true, dashed: true, width: 2 }));
  body.push(text(svcImpl.cx + 30, (svcImpl.top + svcI.bottom) / 2, '实现', { size: 13 }));

  // ServiceImpl --依赖--> Mapper
  body.push(pathLine([[svcImpl.right, svcImpl.cy], [mapper.left, mapper.bottom - 30]], { arrow: true, dashed: true, width: 2 }));
  body.push(text((svcImpl.right + mapper.left) / 2, svcImpl.cy - 14, '依赖', { size: 13 }));

  // Controller/Service 使用 Entity
  body.push(pathLine([[svcI.right, svcI.bottom - 20], [entity.left, entity.top + 20]], { arrow: true, width: 2 }));
  body.push(text((svcI.right + entity.left) / 2 + 10, (svcI.bottom + entity.top) / 2 - 10, '使用', { size: 13 }));

  writeDiagram('chencai-admin-class', 940, 530, body);
}

// ========== 3b. 用户核心类图 ==========
function buildMemberClassDiagram() {
  const body = [];

  function classBox(x, y, w, name, stereotypes, attrs, methods) {
    const lineH = 20;
    const stereoH = stereotypes ? 18 : 0;
    const nameH = 32 + stereoH;
    const attrH = Math.max(attrs.length * lineH, lineH) + 8;
    const methH = Math.max(methods.length * lineH, lineH) + 8;
    const h = nameH + attrH + methH;

    body.push(`<rect x="${snap(x)}" y="${snap(y)}" width="${snap(w)}" height="${snap(h)}" fill="#fff" stroke="${STROKE}" stroke-width="2.4"/>`);
    if (stereotypes) {
      body.push(text(x + w / 2, y + 14, stereotypes, { size: 13, fill: '#555' }));
    }
    body.push(text(x + w / 2, y + (stereoH ? 32 : nameH / 2), name, { size: 17, weight: '700', family: BOLD }));

    const y1 = y + nameH;
    body.push(`<line x1="${snap(x)}" y1="${snap(y1)}" x2="${snap(x + w)}" y2="${snap(y1)}" stroke="${STROKE}" stroke-width="1.2"/>`);
    attrs.forEach((a, i) => {
      body.push(text(x + 10, y1 + 12 + i * lineH, a, { size: 13, anchor: 'start' }));
    });

    const y2 = y1 + attrH;
    body.push(`<line x1="${snap(x)}" y1="${snap(y2)}" x2="${snap(x + w)}" y2="${snap(y2)}" stroke="${STROKE}" stroke-width="1.2"/>`);
    methods.forEach((m, i) => {
      body.push(text(x + 10, y2 + 12 + i * lineH, m, { size: 13, anchor: 'start' }));
    });

    return { cx: x + w / 2, cy: y + h / 2, top: y, bottom: y + h, left: x, right: x + w };
  }

  const ctrl = classBox(20, 30, 250, 'MemberController', null,
    ['+login(): ModelAndView', '+register(): String', '+editInfo(): String'],
    ['-memberService: MemberService']);
  const svcI = classBox(350, 30, 250, 'MemberService', '<<interface>>',
    ['+checkLogin(): Member', '+register(): int', '+getById(): Member', '+updateInfo(): void'],
    []);
  const svcImpl = classBox(350, 280, 250, 'MemberServiceImpl', null,
    ['-memberMapper: MemberMapper'],
    ['+checkLogin(): Member', '+register(): int', '+getById(): Member']);
  const mapper = classBox(700, 30, 240, 'MemberMapper', '<<interface>>',
    ['+selectByNamePwd(): Member', '+insert(): int', '+selectById(): Member', '+updateById(): int'],
    []);
  const entity = classBox(700, 280, 240, 'Member', null,
    ['-id: int', '-username: String', '-password: String', '-realname: String', '-sjh: String', '-ifuse: String'],
    ['+getter/setter()']);

  body.push(pathLine([[ctrl.right, ctrl.cy], [svcI.left, svcI.cy]], { arrow: true, dashed: true, width: 2 }));
  body.push(text((ctrl.right + svcI.left) / 2, ctrl.cy - 14, '依赖', { size: 13 }));
  body.push(pathLine([[svcImpl.cx, svcImpl.top], [svcI.cx, svcI.bottom]], { arrow: true, dashed: true, width: 2 }));
  body.push(text(svcImpl.cx + 30, (svcImpl.top + svcI.bottom) / 2, '实现', { size: 13 }));
  body.push(pathLine([[svcImpl.right, svcImpl.cy], [mapper.left, mapper.bottom - 30]], { arrow: true, dashed: true, width: 2 }));
  body.push(text((svcImpl.right + mapper.left) / 2, svcImpl.cy - 14, '依赖', { size: 13 }));
  body.push(pathLine([[svcI.right, svcI.bottom - 20], [entity.left, entity.top + 20]], { arrow: true, width: 2 }));
  body.push(text((svcI.right + entity.left) / 2 + 10, (svcI.bottom + entity.top) / 2 - 10, '使用', { size: 13 }));

  writeDiagram('chencai-member-class', 980, 560, body);
}

// ========== 4. 流程图 ==========
function buildLargeFlowChart(name, config) {
  const body = [];
  const W = 1600, H = 1360;
  const centerX = 820;
  const topW = 280;
  const stepW = 440;
  const wideStepW = 560;
  const successBox = {
    x: centerX - 200,
    y: 880,
    width: 400,
    height: 92,
  };

  body.push(rect(centerX - topW / 2, 90, topW, 88, config.startLabel || '开始', { rounded: true, size: 34 }));
  body.push(rect(centerX - stepW / 2, 260, stepW, 92, config.page, { size: 32 }));
  body.push(
    rect(centerX - wideStepW / 2, 450, wideStepW, 120, config.input, {
      size: 30,
      preserveLines: true,
      maxLines: 2,
    }),
  );
  body.push(diamond(centerX, 720, 460, 190, config.check, { size: 26, maxLines: 2 }));
  body.push(rect(1150, 655, 320, 110, config.reject, { size: 28, preserveLines: true, maxLines: 2 }));
  body.push(cylinder(110, 650, 180, 140, config.database, { size: 26 }));
  body.push(rect(successBox.x, successBox.y, successBox.width, successBox.height, config.success, { size: 29, preserveLines: true, maxLines: 2 }));
  body.push(rect(centerX - 210, 1060, 420, 92, config.result, { size: 30, preserveLines: true, maxLines: 2 }));
  body.push(rect(centerX - 160, 1210, 320, 88, config.endLabel || '流程结束', { rounded: true, size: 34 }));

  body.push(vLine(centerX, 178, 260, { arrow: true }));
  body.push(vLine(centerX, 352, 450, { arrow: true }));
  body.push(vLine(centerX, 570, 625, { arrow: true }));
  body.push(vLine(centerX, 815, 880, { arrow: true }));
  body.push(vLine(centerX, 972, 1060, { arrow: true }));
  body.push(vLine(centerX, 1152, 1210, { arrow: true }));

  body.push(hLine(1050, 1150, 720, { arrow: true }));
  body.push(text(1100, 684, config.noLabel || '否', { size: 26 }));
  body.push(
    pathLine(
      [
        [1310, 655],
        [1310, 306],
        [1040, 306],
      ],
      { arrow: true },
    ),
  );
  body.push(
    pathLine(
      [
        [590, 720],
        [290, 720],
      ],
      { arrow: true },
    ),
  );
  body.push(
    pathLine(
      [
        [200, 790],
        [200, successBox.y + successBox.height / 2],
        [successBox.x, successBox.y + successBox.height / 2],
      ],
      { arrow: true },
    ),
  );
  body.push(text(860, 842, config.yesLabel || '是', { size: 26, anchor: 'start' }));

  writeDiagram(name, W, H, body);
}

function buildLoginFlow() {
  buildLargeFlowChart('chencai-login-flow', {
    page: '系统登录页面',
    input: '输入账号和密码\n点击登录按钮',
    check: '账号密码\n是否正确',
    reject: '提示错误信息\n返回登录页面',
    database: '用户信息表',
    success: '登录成功\n加载用户功能',
    result: '进入系统首页',
  });
}

function buildBrowseFlow() {
  buildLargeFlowChart('chencai-browse-flow', {
    page: '房屋信息列表页面',
    input: '选择出售或出租类型\n浏览房屋列表',
    check: '是否选择\n具体房屋',
    reject: '继续浏览列表\n或筛选条件',
    database: '房屋信息表',
    success: '查看房屋详情\n价格户型位置',
    result: '房屋详情页面',
  });
}

function buildRentalFlow() {
  buildLargeFlowChart('chencai-rental-flow', {
    page: '房屋详情页面',
    input: '确认房屋信息\n提交租赁或购买请求',
    check: '房屋状态\n是否可用',
    reject: '提示房屋已被\n租售，返回列表',
    database: '订单信息表',
    success: '生成订单记录\n更新房屋状态',
    result: '订单确认页面',
  });
}

function buildAdminFlow() {
  buildLargeFlowChart('chencai-admin-flow', {
    page: '管理员后台首页',
    input: '选择管理功能模块\n执行管理操作',
    check: '操作数据\n是否合法',
    reject: '提示操作失败\n返回管理页面',
    database: '系统数据库',
    success: '操作成功\n更新数据记录',
    result: '返回管理列表',
  });
}

// ========== 测试流程图 ==========
function buildTestFlow() {
  const body = [];
  const cx = 700;

  body.push(rect(cx - 100, 40, 200, 60, '开始测试', { rounded: true, size: 22 }));
  body.push(vLine(cx, 100, 140, { arrow: true }));
  body.push(rect(cx - 140, 140, 280, 60, '编写测试用例', { size: 22 }));
  body.push(vLine(cx, 200, 250, { arrow: true }));
  body.push(rect(cx - 140, 250, 280, 60, '搭建测试环境', { size: 22 }));
  body.push(vLine(cx, 310, 360, { arrow: true }));
  body.push(rect(cx - 140, 360, 280, 60, '执行功能测试', { size: 22 }));
  body.push(vLine(cx, 420, 480, { arrow: true }));
  body.push(diamond(cx, 540, 280, 110, '测试是否通过', { size: 20 }));

  body.push(hLine(cx + 140, 1080, 540, { arrow: true }));
  body.push(text(940, 524, '否', { size: 20 }));
  body.push(rect(1000, 510, 200, 60, '修复缺陷', { size: 22 }));
  body.push(pathLine([[1100, 510], [1100, 390], [cx + 140, 390]], { arrow: true }));

  body.push(vLine(cx, 595, 650, { arrow: true }));
  body.push(text(cx + 20, 630, '是', { size: 20, anchor: 'start' }));
  body.push(rect(cx - 140, 650, 280, 60, '记录测试结果', { size: 22 }));
  body.push(vLine(cx, 710, 760, { arrow: true }));
  body.push(rect(cx - 100, 760, 200, 60, '测试完成', { rounded: true, size: 22 }));

  writeDiagram('chencai-test-flow', 1400, 870, body);
}

// 执行
buildArchitecture();
buildUseCaseDiagram('chencai-admin-usecase', '管理员', [
  '用户管理',
  '房屋出售管理',
  '房屋出租管理',
  '订单管理',
  '公告管理',
  '轮播图管理',
]);
buildUseCaseDiagram('chencai-user-usecase', '普通用户', [
  '首页浏览',
  '个人中心',
  '房屋出售查询',
  '房屋出租查询',
  '订单提交',
  '公告查看',
]);
buildOverallERDiagram();
// 7 个单实体 ER 图
buildSingleEntityER('chencai-er-admin', '管理员信息',
  ['编号', '账号', '密码', '姓名', '性别', '年龄', '地址', '电话', '添加时间']);
buildSingleEntityER('chencai-er-user', '用户信息',
  ['编号', '账号', '密码', '姓名', '性别', '身份证号', '手机号', '照片', '注册时间', '状态']);
buildSingleEntityER('chencai-er-house', '房屋信息',
  ['编号', '名称', '发布房东', '手机号', '户型', '面积', '价格', '总价', '图片', '位置', '发布时间', '状态']);
buildSingleEntityER('chencai-er-category', '分类信息', ['编号', '标题']);
buildSingleEntityER('chencai-er-order', '订单信息',
  ['编号', '房屋名称', '用户姓名', '总价', '时间']);
buildSingleEntityER('chencai-er-message', '留言信息',
  ['编号', '内容', '用户', '时间', '回复']);
buildSingleEntityER('chencai-er-notice', '公告信息',
  ['编号', '名称', '内容', '时间']);
buildAdminClassDiagram();
buildMemberClassDiagram();
buildLoginFlow();
buildBrowseFlow();
buildRentalFlow();
buildAdminFlow();
buildTestFlow();
console.log('Done: diagrams generated');
