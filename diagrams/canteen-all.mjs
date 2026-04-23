import { createRuntime, parseArgs } from './runtime.mjs';
import { buildRadialUseCase } from './radial-use-case-template.mjs';

/* ====== 用户端用例图 ====== */
function buildUseCaseUser(R) {
  buildRadialUseCase(R, 'usecase-user', '用户',
    [
      ['注册登录', 180, 200], ['菜品浏览', 180, 320], ['菜品搜索', 180, 440],
      ['在线订餐', 180, 560], ['订单查看', 180, 680], ['订单退款', 180, 800],
    ],
    [
      ['菜品收藏', 1000, 200], ['菜品评价', 1000, 320], ['余额充值', 1000, 440],
      ['论坛交流', 1000, 560], ['公告浏览', 1000, 680], ['个人中心', 1000, 800],
    ]
  );
}

/* ====== 管理端用例图 ====== */
function buildUseCaseAdmin(R) {
  buildRadialUseCase(R, 'usecase-admin', '管理员/员工',
    [
      ['菜品管理', 180, 200], ['订单管理', 180, 320], ['用户管理', 180, 440],
      ['员工管理', 180, 560], ['供应商管理', 180, 680], ['评价管理', 180, 800],
    ],
    [
      ['收藏管理', 1000, 200], ['论坛管理', 1000, 320], ['公告管理', 1000, 440],
      ['字典管理', 1000, 560], ['轮播图管理', 1000, 680], ['系统设置', 1000, 800],
    ]
  );
}

/* ====== 系统架构图 ====== */
function buildSystemArch(R) {
  const { rect, brace, text, writeDiagram, BOLD, STROKE, snap } = R;
  const body = [];
  const frameX = 40, frameY = 40, frameW = 1600, frameH = 1100;
  const bandX = 260, bandW = 1240, labelX = 170;

  const roundedBox = (x, y, w, h, label, opts = {}) =>
    rect(x, y, w, h, label, { rounded: true, size: opts.size || 26, minSize: opts.minSize || 16, family: opts.family || BOLD, weight: '400', strokeWidth: 2.8, preserveLines: opts.preserveLines || false, maxLines: opts.maxLines || Infinity });
  const band = (y, h) =>
    `<rect x="${bandX}" y="${snap(y)}" width="${bandW}" height="${snap(h)}" fill="#fff" stroke="${STROKE}" stroke-width="2.6"/>`;
  const braceBand = (label, y, h, inset = 12) =>
    body.push(brace(labelX, y + inset, y + h - inset, label, { size: 26, lineHeight: 30, family: BOLD }));
  const placeCenteredRow = (items, y, h, opts = {}) => {
    const pad = opts.padding ?? 32;
    const available = bandW - pad * 2;
    const widths = items.map(it => (typeof it === 'string' ? opts.width || 150 : it.width || opts.width || 150));
    const totalW = widths.reduce((s, w) => s + w, 0);
    const gap = opts.gap ?? Math.max(opts.minGap ?? 18, items.length > 1 ? (available - totalW) / (items.length - 1) : 0);
    const usedW = totalW + gap * Math.max(0, items.length - 1);
    let cx = bandX + pad + Math.max(0, (available - usedW) / 2);
    items.forEach((it) => {
      const spec = typeof it === 'string' ? { label: it, width: opts.width || 150 } : it;
      body.push(roundedBox(cx, y, spec.width || opts.width || 150, h, spec.label, { size: spec.size || opts.size || 26, minSize: spec.minSize || opts.minSize || 16, preserveLines: spec.preserveLines ?? false, maxLines: spec.maxLines || Infinity }));
      cx += (spec.width || opts.width || 150) + gap;
    });
  };

  body.push(`<rect x="${frameX}" y="${frameY}" width="${frameW}" height="${frameH}" fill="#fff" stroke="${STROKE}" stroke-width="3"/>`);
  body.push(`<rect x="${frameX}" y="${frameY}" width="${frameW}" height="140" fill="#fff" stroke="${STROKE}" stroke-width="2.6"/>`);
  body.push(text(840, 110, '社区老年食堂订餐系统架构图', { size: 42, family: BOLD, weight: '700' }));

  body.push(band(240, 100)); body.push(band(380, 100)); body.push(band(520, 260));
  body.push(band(820, 92)); body.push(band(950, 104));

  braceBand('表现层', 240, 100); braceBand('用户角色', 380, 100);
  braceBand('业务逻辑层', 520, 260, 10); braceBand('数据层', 820, 92, 10);
  braceBand('运行环境', 950, 104, 14);

  placeCenteredRow(
    [{ label: '用户端（HTML/CSS/JS）', width: 380 }, { label: '管理端（Vue 2 + Element UI）', width: 400 }],
    262, 56, { size: 26, padding: 60, minGap: 100 });
  placeCenteredRow(['用户', '员工', '管理员'], 405, 54, { width: 180, size: 28, padding: 150, minGap: 120 });
  placeCenteredRow(
    ['菜品管理', '订单管理', '用户管理', '供应商管理', '论坛管理', '公告管理', '评价管理'],
    560, 52, { width: 150, size: 25, minSize: 21, padding: 18, minGap: 12 });
  placeCenteredRow([
    { label: ['Token认证', '身份校验'], width: 200, preserveLines: true, maxLines: 2 },
    { label: ['拦截器', '权限过滤'], width: 200, preserveLines: true, maxLines: 2 },
    { label: ['MyBatis-Plus', '数据持久'], width: 230, preserveLines: true, maxLines: 2 },
    { label: ['字典服务', '枚举转换'], width: 190, preserveLines: true, maxLines: 2 },
    { label: ['文件上传', '静态资源'], width: 190, preserveLines: true, maxLines: 2 },
  ], 680, 76, { size: 24, minSize: 20, padding: 24, minGap: 14, preserveLines: true, maxLines: 2 });
  placeCenteredRow([
    { label: 'yonghu', width: 120 }, { label: 'caipin', width: 120 },
    { label: 'caipin_order', width: 160 }, { label: 'gongyingshang', width: 170 },
    { label: 'forum', width: 110 }, { label: 'news', width: 100 },
    { label: 'commentback', width: 160 }, { label: 'dictionary', width: 140 },
  ], 840, 54, { size: 22, minSize: 17, padding: 14, minGap: 6 });
  placeCenteredRow(
    ['JDK 1.8', 'Spring Boot 2.2', 'MySQL 5.7', 'Maven 3.0', 'Node.js'],
    978, 52, { width: 190, size: 24, minSize: 19, padding: 36, minGap: 20 });

  writeDiagram('system-arch', 1700, 1180, body);
}

/* ====== 功能结构图 ====== */
function buildFunctionStructure(R) {
  const { rect, vLine, hLine, tallRect, BOLD, snap, writeDiagram } = R;
  const body = [];
  const rootCX = 900, rootY = 40, rootH = 86;
  const mainRailY = 180, groupY = 240;
  const childRailY = 390, childY = 440;
  const childW = 76, childH = 218, childGap = 12;

  body.push(rect(rootCX - 285, rootY, 570, rootH, '社区老年食堂订餐系统', { size: 42, minSize: 34, family: BOLD }));
  body.push(vLine(rootCX, rootY + rootH, mainRailY));

  const groups = [
    { center: 300, width: 180, label: '用户端模块', children: ['菜品浏览', '在线订餐', '订单管理', '菜品收藏', '菜品评价', '论坛交流'] },
    { center: 900, width: 180, label: '员工端模块', children: ['菜品上下架', '订单发货', '公告管理'] },
    { center: 1500, width: 180, label: '管理员模块', children: ['用户管理', '员工管理', '供应商管理', '字典管理', '轮播图管理', '系统设置'] },
  ];

  body.push(hLine(groups[0].center, groups[groups.length - 1].center, mainRailY));
  groups.forEach(g => {
    body.push(rect(g.center - g.width / 2, groupY, g.width, 78, g.label, { size: 36, minSize: 28, family: BOLD }));
    body.push(vLine(g.center, mainRailY, groupY));
    body.push(vLine(g.center, groupY + 78, childRailY));
    const boxes = g.children.map((label, i) => {
      const rawX = g.center - (g.children.length * childW + (g.children.length - 1) * childGap) / 2 + i * (childW + childGap);
      const x = snap(rawX);
      return { label, x, w: snap(childW), cx: x + snap(childW) / 2 };
    });
    body.push(hLine(boxes[0].cx, boxes[boxes.length - 1].cx, childRailY));
    boxes.forEach(b => {
      body.push(vLine(b.cx, childRailY, childY));
      body.push(tallRect(b.x, childY, b.w, childH, b.label, { size: 30, family: BOLD }));
    });
  });

  writeDiagram('func-structure', 1800, 760, body);
}

/* ====== 业务流程图 ====== */
function buildBusinessFlow(R) {
  const { rect, diamond, vLine, hLine, pathLine, text, writeDiagram } = R;
  const body = [];
  const cx = 500, boxW = 360;

  body.push(rect(cx - 120, 40, 240, 62, '开始', { rounded: true, size: 32 }));
  body.push(vLine(cx, 96, 140, { arrow: true }));

  body.push(rect(cx - boxW / 2, 140, boxW, 62, '用户登录系统', { size: 28 }));
  body.push(vLine(cx, 196, 250, { arrow: true }));

  body.push(rect(cx - boxW / 2, 250, boxW, 62, '浏览菜品列表', { size: 28 }));
  body.push(vLine(cx, 306, 360, { arrow: true }));

  body.push(rect(cx - boxW / 2, 360, boxW, 62, '选择菜品，填写数量', { size: 27 }));
  body.push(vLine(cx, 416, 480, { arrow: true }));

  // 库存是否充足
  body.push(diamond(cx, 540, 350, 130, '库存是否充足', { size: 27, minSize: 22 }));
  body.push(hLine(cx + 175, cx + 340, 540, { arrow: true }));
  body.push(text(cx + 255, 508, '否', { size: 26 }));
  body.push(rect(cx + 340, 506, 250, 66, '提示库存不足', { size: 25 }));

  body.push(vLine(cx, 595, 660, { arrow: true }));
  body.push(text(cx + 26, 630, '是', { size: 26 }));

  // 余额是否充足
  body.push(diamond(cx, 720, 350, 130, '余额是否充足', { size: 27, minSize: 22 }));
  body.push(hLine(cx + 175, cx + 340, 720, { arrow: true }));
  body.push(text(cx + 255, 688, '否', { size: 26 }));
  body.push(rect(cx + 340, 686, 250, 66, '提示余额不足', { size: 25 }));

  body.push(vLine(cx, 775, 840, { arrow: true }));
  body.push(text(cx + 26, 810, '是', { size: 26 }));

  body.push(rect(cx - boxW / 2, 840, boxW, 62, '创建订单，扣库存/余额', { size: 25 }));
  body.push(vLine(cx, 896, 950, { arrow: true }));

  body.push(rect(cx - boxW / 2, 950, boxW, 62, '累加积分，评定会员等级', { size: 25 }));
  body.push(vLine(cx, 1006, 1060, { arrow: true }));

  body.push(rect(cx - boxW / 2, 1060, boxW, 62, '管理员/员工发货', { size: 27 }));
  body.push(vLine(cx, 1116, 1170, { arrow: true }));

  body.push(rect(cx - boxW / 2, 1170, boxW, 62, '用户确认收货', { size: 28 }));
  body.push(vLine(cx, 1226, 1280, { arrow: true }));

  body.push(rect(cx - boxW / 2, 1280, boxW, 62, '用户提交评价', { size: 28 }));
  body.push(vLine(cx, 1336, 1390, { arrow: true }));

  body.push(rect(cx - 120, 1390, 240, 62, '结束', { rounded: true, size: 32 }));

  writeDiagram('business-flow', 1100, 1500, body);
}

/* ====== 订餐活动图 ====== */
function buildOrderActivity(R) {
  const { rect, diamond, vLine, hLine, pathLine, text, writeDiagram, STROKE, BOLD } = R;
  const body = [];
  const lanes = [
    { x: 40, w: 300, label: '用户' },
    { x: 340, w: 460, label: '系统' },
    { x: 800, w: 300, label: '员工/管理员' },
  ];
  body.push(`<rect x="40" y="40" width="1060" height="1420" fill="#fff" stroke="${STROKE}" stroke-width="3"/>`);
  lanes.forEach((lane) => {
    body.push(`<rect x="${lane.x}" y="40" width="${lane.w}" height="70" fill="#f5f5f5" stroke="${STROKE}" stroke-width="2.5"/>`);
    body.push(text(lane.x + lane.w / 2, 75, lane.label, { size: 36, family: BOLD, weight: '700' }));
    body.push(`<line x1="${lane.x}" y1="110" x2="${lane.x}" y2="1460" stroke="${STROKE}" stroke-width="2"/>`);
  });
  body.push(`<line x1="1100" y1="110" x2="1100" y2="1460" stroke="${STROKE}" stroke-width="2"/>`);

  const userX = 190;
  const sysX = 570;
  const adminX = 950;
  const box = (cx, y, label, w = 280) => body.push(rect(cx - w / 2, y, w, 72, label, { rounded: true, size: 29, minSize: 22, family: BOLD }));
  const decision = (cx, y, label) => body.push(diamond(cx, y + 42, 300, 122, label, { size: 27, minSize: 21 }));
  const arrow = (x1, y1, x2, y2) => body.push(pathLine([[x1, y1], [x2, y2]], { arrow: true, width: 2.8 }));

  box(userX, 150, '登录系统');
  arrow(userX, 216, userX, 270);
  box(userX, 270, '浏览菜品');
  arrow(userX, 336, userX, 390);
  box(userX, 390, '选择菜品数量');
  arrow(userX, 456, sysX, 520);

  decision(sysX, 480, '库存是否充足');
  arrow(sysX, 575, sysX, 660);
  body.push(text(sysX + 34, 625, '是', { size: 26 }));
  hLine(sysX + 125, 900, 522, { arrow: true });
  body.push(text(735, 492, '否', { size: 26 }));
  box(adminX, 490, '提示库存不足', 240);

  decision(sysX, 660, '余额是否充足');
  arrow(sysX, 755, sysX, 840);
  body.push(text(sysX + 34, 805, '是', { size: 26 }));
  hLine(sysX + 125, 900, 702, { arrow: true });
  body.push(text(735, 672, '否', { size: 26 }));
  box(adminX, 670, '提示余额不足', 240);

  box(sysX, 840, '生成订单并扣减库存', 320);
  arrow(sysX, 906, sysX, 970);
  box(sysX, 970, '扣减余额并累计积分', 320);
  arrow(sysX, 1036, adminX, 1090);
  box(adminX, 1060, '处理订单发货', 240);
  arrow(adminX, 1126, userX, 1190);
  box(userX, 1160, '确认收货');
  arrow(userX, 1226, userX, 1290);
  box(userX, 1290, '提交评价');
  arrow(userX, 1356, sysX, 1390);
  box(sysX, 1360, '更新订单状态', 260);

  writeDiagram('order-activity', 1140, 1500, body);
}

/* ====== E-R 图 ====== */
function buildErDiagram(R) {
  const { rect, diamond, pathLine, text, BOLD, writeDiagram } = R;
  const body = [];
  const W = 2.4;

  const entity = (x, y, label, width = 160, height = 56) => {
    const node = { x, y, w: width, h: height, cx: x + width / 2, cy: y + height / 2 };
    body.push(rect(x, y, width, height, label, { size: 29, minSize: 24, family: BOLD, strokeWidth: 2.8 }));
    return node;
  };
  const rel = (cx, cy, label, width = 90, height = 56) => {
    const node = { cx, cy, w: width, h: height };
    body.push(diamond(cx, cy, width, height, label, { size: 24, minSize: 19, maxLines: 1 }));
    return node;
  };
  const line = (...pts) => body.push(pathLine(pts, { width: W }));
  const connect = (eA, r, eB) => {
    // Simple horizontal or vertical connection through a diamond
    const dxA = r.cx - eA.cx, dyA = r.cy - eA.cy;
    const dxB = r.cx - eB.cx, dyB = r.cy - eB.cy;
    // A → rel
    if (Math.abs(dxA) > Math.abs(dyA)) {
      const ax = dxA > 0 ? eA.x + eA.w : eA.x;
      const rx = dxA > 0 ? r.cx - r.w / 2 : r.cx + r.w / 2;
      line([ax, eA.cy], [rx, r.cy]);
    } else {
      const ay = dyA > 0 ? eA.y + eA.h : eA.y;
      const ry = dyA > 0 ? r.cy - r.h / 2 : r.cy + r.h / 2;
      line([eA.cx, ay], [r.cx, ry]);
    }
    // rel → B
    if (Math.abs(dxB) > Math.abs(dyB)) {
      const bx = dxB > 0 ? eB.x + eB.w : eB.x;
      const rx = dxB > 0 ? r.cx - r.w / 2 : r.cx + r.w / 2;
      line([rx, r.cy], [bx, eB.cy]);
    } else {
      const by = dyB > 0 ? eB.y + eB.h : eB.y;
      const ry = dyB > 0 ? r.cy - r.h / 2 : r.cy + r.h / 2;
      line([r.cx, ry], [eB.cx, by]);
    }
  };

  // =========================================================
  // 布局：用户居中上方，菜品居中下方，两个hub辐射连接
  //
  //         员工                        供应商
  //           \  登录            管理  /
  //            \                    /
  //    论坛 —发帖— 用户 —下单— 订单
  //                  |
  //                浏览
  //                  |
  //    收藏 —关联— 菜品 —包含— (订单)
  //                  |
  //                针对
  //                  |
  //    公告        评价
  //
  // =========================================================

  // 用户 hub - center top
  const yonghu = entity(560, 200, '用户', 180, 62);

  // Row 0: 员工 and 供应商 flanking above
  const yuangong = entity(110, 60, '员工', 180, 62);
  const gys      = entity(1010, 60, '供应商', 200, 62);

  // 用户 left/right peers
  const forum    = entity(110, 200, '论坛', 180, 62);
  const order    = entity(1010, 200, '订单', 180, 62);

  // 菜品 hub - center bottom
  const caipin   = entity(560, 450, '菜品', 180, 62);

  // 菜品 left/right peers
  const collect  = entity(110, 450, '收藏', 180, 62);
  const comment  = entity(1010, 450, '评价', 180, 62);

  // 公告 - bottom left (managed by admin, separate)
  const news     = entity(110, 650, '公告', 180, 62);

  // === Row 0: 员工-登录-用户, 用户-管理-供应商 ===
  // 员工 → 用户: diagonal, use fold (员工 bottom-right → 用户 top-left)
  const r_login = rel(370, 150, '登录', 100, 64);
  line([yuangong.x + yuangong.w, yuangong.cy], [r_login.cx - r_login.w / 2, r_login.cy]);
  line([r_login.cx + r_login.w / 2, r_login.cy], [yonghu.x, yonghu.cy]);

  // 用户 → 供应商: diagonal fold
  const r_manage = rel(930, 150, '管理', 100, 64);
  line([yonghu.x + yonghu.w, yonghu.cy], [r_manage.cx - r_manage.w / 2, r_manage.cy]);
  line([r_manage.cx + r_manage.w / 2, r_manage.cy], [gys.x, gys.cy]);

  // === 用户 horizontal: 论坛-发帖-用户, 用户-下单-订单 ===
  connect(forum, rel(370, 228, '发帖', 100, 64), yonghu);
  connect(yonghu, rel(830, 228, '下单', 100, 64), order);

  // === 用户→菜品: vertical center ===
  connect(yonghu, rel(650, 340, '浏览', 100, 64), caipin);

  // === 菜品 horizontal: 收藏-关联-菜品, 菜品-针对-评价 ===
  // 收藏 is left of 菜品 (关联=菜品与收藏的关系)
  connect(collect, rel(370, 478, '关联', 100, 64), caipin);
  // 评价 is right of 菜品
  connect(caipin, rel(830, 478, '针对', 100, 64), comment);

  // === 菜品→订单: vertical right column ===
  connect(caipin, rel(830, 340, '包含', 100, 64), order);

  // === 用户→收藏: fold down-left (用户左下角 → 收藏上方) ===
  const r_fav = rel(350, 340, '收藏', 100, 64);
  // 用户 bottom-left → fold left → down to diamond
  line([yonghu.x, yonghu.cy + 15], [r_fav.cx, yonghu.cy + 15], [r_fav.cx, r_fav.cy - r_fav.h / 2]);
  line([r_fav.cx, r_fav.cy + r_fav.h / 2], [collect.cx, collect.y]);

  // === 用户→评价: fold down-right (用户右下角 → 评价上方) ===
  const r_review = rel(950, 340, '评价', 100, 64);
  line([yonghu.x + yonghu.w, yonghu.cy + 15], [r_review.cx, yonghu.cy + 15], [r_review.cx, r_review.cy - r_review.h / 2]);
  line([r_review.cx, r_review.cy + r_review.h / 2], [comment.cx, comment.y]);

  // === 管理员→公告: fold from 用户 bottom-left to 公告 ===
  const r_pub = rel(210, 550, '发布', 100, 64);
  line([yonghu.cx - 20, yonghu.y + yonghu.h], [yonghu.cx - 20, r_pub.cy - 60], [r_pub.cx, r_pub.cy - 60], [r_pub.cx, r_pub.cy - r_pub.h / 2]);
  line([r_pub.cx, r_pub.cy + r_pub.h / 2], [news.cx, news.y]);

  writeDiagram('er-diagram', 1300, 750, body);
}

/* ====== 实体属性图 ====== */
function buildEntityAttributeDiagrams(R) {
  const { rect, ellipse, pathLine, writeDiagram, BOLD } = R;
  const entities = [
    ['er-user', '用户', ['用户编号', '账号', '密码', '姓名', '手机号', '身份证号', '头像', '性别', '邮箱', '账户余额', '累计积分', '当前积分', '会员等级', '创建时间']],
    ['er-dish', '菜品', ['菜品编号', '菜品名称', '菜品图片', '菜品类型', '积分单价', '库存数量', '原价', '现价', '浏览次数', '菜品描述', '上架状态', '删除标记', '创建时间']],
    ['er-order', '订单', ['订单编号', '菜品编号', '用户编号', '购买数量', '预定时间', '实付金额', '订单状态', '支付方式', '下单时间', '创建时间']],
    ['er-supplier', '供应商', ['供应商编号', '供应商名称', '联系电话', '供应物品', '物品类型', '供应价格', '供应商描述', '创建时间']],
    ['er-comment', '评价', ['评价编号', '菜品编号', '用户编号', '评价内容', '评价时间', '回复内容', '回复时间', '创建时间']],
    ['er-forum', '论坛', ['帖子编号', '帖子标题', '用户编号', '员工编号', '管理员编号', '帖子内容', '父帖编号', '帖子状态', '发帖时间', '创建时间']],
    ['er-news', '公告', ['公告编号', '公告标题', '公告类型', '封面图片', '发布时间', '公告内容', '创建时间']],
  ];
  entities.forEach(([name, label, attrs]) => {
    const body = [];
    const W = 1500;
    const H = 920;
    const entity = { x: 610, y: 410, w: 280, h: 82, cx: 750, cy: 451 };
    body.push(rect(entity.x, entity.y, entity.w, entity.h, label, { size: 38, minSize: 30, family: BOLD, strokeWidth: 3.2 }));
    const left = attrs.slice(0, Math.ceil(attrs.length / 2));
    const right = attrs.slice(Math.ceil(attrs.length / 2));
    const renderCol = (items, x, side) => {
      const gap = 98;
      const startY = Math.round(entity.cy - ((items.length - 1) * gap) / 2);
      items.forEach((attr, i) => {
        const cy = startY + i * gap;
        const rx = 116;
        const ry = 36;
        body.push(ellipse(x, cy, rx, ry, attr, { size: 27, minSize: 21, maxLines: 1 }));
        const fromX = side === 'left' ? entity.x : entity.x + entity.w;
        const toX = side === 'left' ? x + rx : x - rx;
        body.push(pathLine([[fromX, entity.cy], [toX, cy]], { width: 2.6 }));
      });
    };
    renderCol(left, 300, 'left');
    renderCol(right, 1200, 'right');
    writeDiagram(name, W, H, body);
  });
}

/* ====== 构件图 ====== */
function buildComponentDiagram(R, name, title, components) {
  const { rect, pathLine, text, writeDiagram, BOLD, STROKE } = R;
  const body = [];
  const W = 1240;
  const H = 500;
  body.push(text(W / 2, 58, title, { size: 48, family: BOLD, weight: '700' }));
  body.push(`<rect x="10" y="100" width="${W - 20}" height="260" fill="#fff" stroke="${STROKE}" stroke-width="3"/>`);

  const x = [130, 375, 620, 865, 1110];
  const y = 230;
  const comp = (cx, cy, label, w = 220, h = 126) => {
    const left = cx - w / 2;
    const top = cy - h / 2;
    body.push(`<rect x="${left}" y="${top}" width="${w}" height="${h}" fill="#fff" stroke="${STROKE}" stroke-width="3"/>`);
    body.push(`<rect x="${left + 16}" y="${top + 30}" width="34" height="20" fill="#fff" stroke="${STROKE}" stroke-width="2.4"/>`);
    body.push(`<rect x="${left + 16}" y="${top + 78}" width="34" height="20" fill="#fff" stroke="${STROKE}" stroke-width="2.4"/>`);
    body.push(rect(left + 54, top + 18, w - 70, h - 36, label, { size: 32, minSize: 26, family: BOLD, strokeWidth: 0, preserveLines: Array.isArray(label), maxLines: Array.isArray(label) ? label.length : Infinity }));
  };
  components.forEach((label, i) => comp(x[i], y, label, i === components.length - 1 ? 230 : 220));
  const arrowLabels = ['HTTP请求', '参数校验', '业务调用', '数据访问'];
  for (let i = 0; i < components.length - 1; i += 1) {
    body.push(pathLine([[x[i] + 112, y], [x[i + 1] - 112, y]], { arrow: true, width: 3 }));
    body.push(text((x[i] + x[i + 1]) / 2, y - 84, arrowLabels[i] || '调用', { size: 30, family: BOLD }));
  }
  body.push(text(W / 2, 430, '页面构件、控制构件、业务构件、数据访问构件和数据表依次协作完成该功能。', { size: 32, family: BOLD }));
  writeDiagram(name, W, H, body);
}

function buildCanteenComponentDiagrams(R) {
  buildComponentDiagram(R, 'cmp-login', '用户登录与注册构件图', ['Login页面', ['Yonghu', 'Controller'], ['Yonghu', 'Service'], 'YonghuDao', ['yonghu', 'token表']]);
  buildComponentDiagram(R, 'cmp-dish-browse', '菜品浏览与搜索构件图', ['首页/列表页面', ['Caipin', 'Controller'], ['Caipin', 'Service'], 'CaipinDao', 'caipin表']);
  buildComponentDiagram(R, 'cmp-order', '在线订餐构件图', ['菜品详情页面', ['CaipinOrder', 'Controller'], '订单Service', '订单Mapper', ['订单/用户', '菜品表']]);
  buildComponentDiagram(R, 'cmp-forum', '论坛交流构件图', ['论坛页面', ['Forum', 'Controller'], ['Forum', 'Service'], 'ForumDao', 'forum表']);
  buildComponentDiagram(R, 'cmp-admin-dish', '菜品管理构件图', ['后台菜品页面', ['Caipin', 'Controller'], ['Caipin', 'Service'], 'CaipinDao', 'caipin表']);
  buildComponentDiagram(R, 'cmp-admin-order', '订单管理构件图', ['后台订单页面', ['CaipinOrder', 'Controller'], '订单Service', '订单Mapper', ['订单/用户', '菜品表']]);
  buildComponentDiagram(R, 'cmp-notice', '公告管理构件图', ['公告管理页面', ['News', 'Controller'], ['News', 'Service'], 'NewsDao', 'news表']);
}

/* ====== 时序图 ====== */
function buildSequence(R, name, title, actorLabel, lifelines, messages) {
  const { actor, rect, activation, pathLine, text, writeDiagram, STROKE, BOLD } = R;
  const body = [];
  body.push(text(650, 48, title, { size: 44, family: BOLD, weight: '700' }));
  body.push(actor(85, 130, actorLabel));
  const startX = 245;
  const gap = 210;
  const xs = lifelines.map((_, i) => startX + i * gap);
  lifelines.forEach((label, i) => {
    const x = xs[i];
    body.push(rect(x - 86, 90, 172, 66, label, { size: 29, minSize: 22 }));
    body.push(`<line x1="${x}" y1="156" x2="${x}" y2="820" stroke="#888" stroke-width="2.4" stroke-dasharray="8 6"/>`);
    body.push(activation(x, 210 + i * 35, 360 - i * 20));
  });
  const point = (idx) => (idx === -1 ? 125 : xs[idx]);
  messages.forEach((m, i) => {
    const y = 220 + i * 70;
    const dashed = m[3] === 'return';
    const from = point(m[0]);
    const to = point(m[1]);
    body.push(pathLine([[from, y], [to, y]], { arrow: true, dashed, width: 2.5, color: dashed ? '#555' : STROKE }));
    body.push(text((from + to) / 2, y - 22, `${i + 1}. ${m[2]}`, { size: 25, family: BOLD }));
  });
  writeDiagram(name, 1300, 880, body);
}

function buildCanteenSequenceDiagrams(R) {
  const common = ['前端页面', 'Controller', 'Service', 'Mapper', 'MySQL'];
  buildSequence(R, 'seq-login', '用户登录时序图', '用户', common, [
    [-1, 0, '输入账号密码'], [0, 1, '提交登录请求'], [1, 2, '校验用户信息'], [2, 3, '查询用户记录'], [3, 4, '读取yonghu/token表'], [4, 3, '返回查询结果', 'return'], [2, 1, '生成Token', 'return'], [1, 0, '返回登录结果', 'return'], [0, -1, '进入系统首页', 'return'],
  ]);
  buildSequence(R, 'seq-dish-browse', '菜品浏览与搜索时序图', '用户', common, [
    [-1, 0, '打开首页'], [0, 1, '请求菜品列表'], [1, 2, '组装查询条件'], [2, 3, '执行分页查询'], [3, 4, '读取菜品数据'], [4, 3, '返回数据集', 'return'], [2, 1, '转换字典字段', 'return'], [1, 0, '返回菜品列表', 'return'], [0, -1, '展示菜品卡片', 'return'],
  ]);
  buildSequence(R, 'seq-order', '在线订餐时序图', '用户', common, [
    [-1, 0, '选择菜品并提交订单'], [0, 1, '发送下单请求'], [1, 2, '校验库存和余额'], [2, 3, '查询菜品和用户'], [3, 4, '读取业务数据'], [2, 3, '写入订单并更新库存余额'], [3, 4, '提交事务'], [2, 1, '返回下单结果', 'return'], [1, 0, '提示下单成功', 'return'],
  ]);
  buildSequence(R, 'seq-forum', '论坛发帖时序图', '用户', common, [
    [-1, 0, '填写帖子内容'], [0, 1, '提交发帖请求'], [1, 2, '校验登录状态'], [2, 3, '保存帖子记录'], [3, 4, '写入forum表'], [4, 3, '返回写入结果', 'return'], [2, 1, '返回帖子对象', 'return'], [1, 0, '刷新帖子列表', 'return'],
  ]);
  buildSequence(R, 'seq-admin-dish', '菜品管理时序图', '管理员', common, [
    [-1, 0, '填写菜品信息'], [0, 1, '提交新增/编辑请求'], [1, 2, '校验权限和重复名称'], [2, 3, '保存菜品数据'], [3, 4, '写入caipin表'], [4, 3, '返回执行结果', 'return'], [2, 1, '返回保存结果', 'return'], [1, 0, '刷新菜品列表', 'return'],
  ]);
  buildSequence(R, 'seq-admin-order', '订单管理时序图', '管理员', common, [
    [-1, 0, '选择订单执行发货'], [0, 1, '提交状态变更'], [1, 2, '校验订单状态'], [2, 3, '更新订单记录'], [3, 4, '写入caipin_order表'], [4, 3, '返回更新结果', 'return'], [2, 1, '返回处理结果', 'return'], [1, 0, '刷新订单列表', 'return'],
  ]);
  buildSequence(R, 'seq-notice', '公告发布时序图', '管理员', common, [
    [-1, 0, '填写公告内容'], [0, 1, '提交发布请求'], [1, 2, '校验公告字段'], [2, 3, '保存公告信息'], [3, 4, '写入news表'], [4, 3, '返回写入结果', 'return'], [2, 1, '返回发布结果', 'return'], [1, 0, '刷新公告列表', 'return'],
  ]);
}


/* ====== 主入口 ====== */
async function main() {
  const args = parseArgs();
  const R = createRuntime(args);

  buildUseCaseUser(R);
  buildUseCaseAdmin(R);
  buildSystemArch(R);
  buildFunctionStructure(R);
  buildBusinessFlow(R);
  buildOrderActivity(R);
  buildErDiagram(R);
  buildEntityAttributeDiagrams(R);
  buildCanteenComponentDiagrams(R);
  buildCanteenSequenceDiagrams(R);

  console.log('canteen diagrams done.');
}

main();
