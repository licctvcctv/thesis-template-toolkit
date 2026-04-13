/**
 * 陈才论文（房屋租赁与销售平台）图表生成器 v2
 * 参照 thesis-studio 项目的标准画法
 */
import { createRuntime } from '/Users/a136/Downloads/undergrad-thesis-studio-codex-thesis-pack-manifest-content-model/scripts/thesis-diagrams/runtime.mjs';
import { buildFlowChartTemplate } from '/Users/a136/Downloads/undergrad-thesis-studio-codex-thesis-pack-manifest-content-model/scripts/thesis-diagrams/flow-chart-template.mjs';

const runtime = createRuntime(new Map([
  ['--out-dir', '/Users/a136/vs/45425/thesis_project/papers/chencai/images'],
  ['--src-dir', '/Users/a136/vs/45425/thesis_project/papers/chencai/diagrams/svg-src'],
]));

const { rect, diamond, ellipse, cylinder, pill, brace, pathLine, vLine, hLine, text,
        multiline, card, snap, writeDiagram, STROKE, FONT, BOLD } = runtime;

// ========== 1. 系统架构图 — 参照 system-architecture.mjs 风格 ==========
function buildArchitecture() {
  const body = [];
  const W = 1600, frameX = 40, frameY = 40;
  const bandX = 260, bandW = 1200, labelX = 170;

  const band = (y, h) =>
    `<rect x="${bandX}" y="${snap(y)}" width="${bandW}" height="${snap(h)}" fill="#fff" stroke="${STROKE}" stroke-width="2.6"/>`;
  const braceBand = (label, y, h) => {
    body.push(brace(labelX, y + 12, y + h - 12, label, { size: 22, lineHeight: 25, family: BOLD }));
  };
  const roundedBox = (x, y, w, h, label, opts = {}) =>
    rect(x, y, w, h, label, { rounded: true, size: opts.size || 20, minSize: 12, family: BOLD, strokeWidth: 2.4 });
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
  body.push(`<rect x="${frameX}" y="${frameY}" width="${W - 80}" height="820" fill="#fff" stroke="${STROKE}" stroke-width="3"/>`);
  // 标题栏
  body.push(`<rect x="${frameX}" y="90" width="${W - 80}" height="80" fill="#fff" stroke="${STROKE}" stroke-width="2.6"/>`);
  body.push(text(W / 2, 130, '房屋租赁与销售平台架构图', { size: 30, family: BOLD, weight: '700' }));

  // 五层
  body.push(band(210, 90));
  body.push(band(340, 90));
  body.push(band(470, 90));
  body.push(band(600, 90));
  body.push(band(730, 90));

  braceBand('表现层', 210, 90);
  braceBand('控制层', 340, 90);
  braceBand('业务层', 470, 90);
  braceBand('持久层', 600, 90);
  braceBand('数据层', 730, 90);

  placeCenteredRow(['JSP页面', 'HTML/CSS', 'JavaScript', '浏览器'], 230, 50, { width: 160, padding: 60, size: 18 });
  placeCenteredRow(['DispatcherServlet', 'Controller', '请求分发', '视图解析'], 360, 50, { width: 170, padding: 50, size: 16 });
  placeCenteredRow(['用户服务', '房屋服务', '订单服务', '公告服务'], 490, 50, { width: 160, padding: 60, size: 18 });
  placeCenteredRow(['AdminMapper', 'MemberMapper', 'FwMapper', 'DdMapper'], 620, 50, { width: 170, padding: 50, size: 16 });
  body.push(cylinder(bandX + bandW / 2 - 80, 745, 160, 60, 'MySQL 5.7', { size: 22, family: BOLD }));

  writeDiagram('chencai-architecture', W, 900, body);
}

// ========== 2. ER图 — 参照 er-diagram.mjs 标准画法 ==========
function buildERDiagram() {
  const body = [];

  const entity = (x, y, label, w = 180, h = 56) => {
    const node = { x, y, w, h, cx: x + w / 2, cy: y + h / 2 };
    body.push(rect(x, y, w, h, label, { size: 22, family: BOLD, strokeWidth: 2.8 }));
    return node;
  };
  const relation = (cx, cy, label, w = 100, h = 56) => {
    const node = { cx, cy, w, h };
    body.push(diamond(cx, cy, w, h, label, { size: 18, maxLines: 1 }));
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
  const ovalAnchor = (cx, cy, rx, ry, tx, ty) => {
    const dx = tx - cx, dy = ty - cy;
    const s = Math.sqrt((dx * dx) / (rx * rx) + (dy * dy) / (ry * ry)) || 1;
    return [cx + dx / s, cy + dy / s];
  };
  const connectER = (e, r) => {
    const [x1, y1] = rectAnchor(e, r.cx, r.cy);
    const [x2, y2] = diamondAnchor(r, e.cx, e.cy);
    body.push(pathLine([[x1, y1], [x2, y2]], { width: 2.5 }));
  };
  const connectRE = (r, e) => {
    const [x1, y1] = diamondAnchor(r, e.cx, e.cy);
    const [x2, y2] = rectAnchor(e, r.cx, r.cy);
    body.push(pathLine([[x1, y1], [x2, y2]], { width: 2.5 }));
  };
  const attribute = (e, cx, cy, label) => {
    const rx = 78, ry = 28;
    const [x1, y1] = rectAnchor(e, cx, cy);
    const [x2, y2] = ovalAnchor(cx, cy, rx, ry, e.cx, e.cy);
    body.push(pathLine([[x1, y1], [x2, y2]], { width: 2 }));
    body.push(ellipse(cx, cy, rx, ry, label, { size: 16, minSize: 11, maxLines: 1 }));
  };

  // 实体
  const admin = entity(80, 120, '管理员');
  const user = entity(680, 120, '用户');
  const house = entity(380, 430, '房屋信息', 200);
  const order = entity(1080, 120, '订单');
  const msg = entity(80, 720, '留言');
  const notice = entity(680, 720, '公告');
  const category = entity(1080, 720, '分类');

  // 属性
  [[30, 60, '编号'], [200, 40, '账号'], [350, 70, '密码'], [80, 240, '姓名'], [260, 230, '电话']].forEach(([x, y, l]) => attribute(admin, x, y, l));
  [[630, 55, '编号'], [810, 40, '账号'], [980, 60, '密码'], [650, 240, '姓名'], [860, 230, '手机号']].forEach(([x, y, l]) => attribute(user, x, y, l));
  [[250, 370, '编号'], [430, 350, '名称'], [620, 370, '户型'], [250, 560, '面积'], [430, 580, '价格'], [620, 560, '状态']].forEach(([x, y, l]) => attribute(house, x, y, l));
  [[1030, 55, '编号'], [1210, 40, '房屋名称'], [1380, 60, '用户姓名'], [1100, 240, '总价'], [1280, 230, '时间']].forEach(([x, y, l]) => attribute(order, x, y, l));
  [[30, 660, '编号'], [210, 650, '内容'], [30, 840, '用户'], [210, 840, '时间']].forEach(([x, y, l]) => attribute(msg, x, y, l));
  [[630, 660, '编号'], [810, 650, '名称'], [650, 840, '内容'], [840, 840, '时间']].forEach(([x, y, l]) => attribute(notice, x, y, l));
  [[1030, 660, '编号'], [1210, 650, '名称']].forEach(([x, y, l]) => attribute(category, x, y, l));

  // 关系
  const r1 = relation(270, 310, '管理');
  connectER(admin, r1); connectRE(r1, house);

  const r2 = relation(600, 300, '浏览');
  connectER(user, r2); connectRE(r2, house);

  const r3 = relation(900, 180, '下单');
  connectER(user, r3); connectRE(r3, order);

  const r4 = relation(170, 510, '留言');
  connectER(user, { cx: 170, cy: 510 }); // 近似连接
  body.push(pathLine([[msg.cx, msg.y], [170, 540]], { width: 2.5 }));

  const r5 = relation(900, 500, '属于');
  connectER(house, r5); connectRE(r5, category);

  // 基数标注
  [[180, 250, '1'], [270, 380, 'n'],
   [700, 220, '1'], [530, 370, 'n'],
   [800, 155, '1'], [1010, 155, 'n']].forEach(([x, y, v]) => body.push(card(x, y, v)));

  writeDiagram('chencai-er-diagram', 1500, 900, body);
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

// ========== 流程图（沿用 flow-chart-template） ==========
function buildLoginFlow() {
  buildFlowChartTemplate(runtime, 'chencai-login-flow', {
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
  buildFlowChartTemplate(runtime, 'chencai-browse-flow', {
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
  buildFlowChartTemplate(runtime, 'chencai-rental-flow', {
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
  buildFlowChartTemplate(runtime, 'chencai-admin-flow', {
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
buildERDiagram();
buildAdminClassDiagram();
buildLoginFlow();
buildBrowseFlow();
buildRentalFlow();
buildAdminFlow();
buildTestFlow();
console.log('Done: 8 diagrams generated');
