import { createRuntime, parseArgs } from './runtime.mjs';
import { buildRadialUseCase } from './radial-use-case-template.mjs';

/* ====== 用户端用例图 ====== */
function buildUseCaseUser(R) {
  buildRadialUseCase(R, 'canteen-usecase-user', '用户',
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
  buildRadialUseCase(R, 'canteen-usecase-admin', '管理员/员工',
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
    rect(x, y, w, h, label, { rounded: true, size: opts.size || 22, minSize: opts.minSize || 12, family: opts.family || BOLD, weight: '400', strokeWidth: 2.6, preserveLines: opts.preserveLines || false, maxLines: opts.maxLines || Infinity });
  const band = (y, h) =>
    `<rect x="${bandX}" y="${snap(y)}" width="${bandW}" height="${snap(h)}" fill="#fff" stroke="${STROKE}" stroke-width="2.6"/>`;
  const braceBand = (label, y, h, inset = 12) =>
    body.push(brace(labelX, y + inset, y + h - inset, label, { size: 22, lineHeight: 25, family: BOLD }));
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
      body.push(roundedBox(cx, y, spec.width || opts.width || 150, h, spec.label, { size: spec.size || opts.size || 22, minSize: spec.minSize || opts.minSize || 12, preserveLines: spec.preserveLines ?? false, maxLines: spec.maxLines || Infinity }));
      cx += (spec.width || opts.width || 150) + gap;
    });
  };

  body.push(`<rect x="${frameX}" y="${frameY}" width="${frameW}" height="${frameH}" fill="#fff" stroke="${STROKE}" stroke-width="3"/>`);
  body.push(`<rect x="${frameX}" y="105" width="${frameW}" height="96" fill="#fff" stroke="${STROKE}" stroke-width="2.6"/>`);
  body.push(text(840, 152, '社区老年食堂订餐系统架构图', { size: 36, family: BOLD, weight: '700' }));

  body.push(band(240, 100)); body.push(band(380, 100)); body.push(band(520, 260));
  body.push(band(820, 92)); body.push(band(950, 104));

  braceBand('表现层', 240, 100); braceBand('用户角色', 380, 100);
  braceBand('业务逻辑层', 520, 260, 10); braceBand('数据层', 820, 92, 10);
  braceBand('运行环境', 950, 104, 14);

  placeCenteredRow(
    [{ label: '用户端（HTML/CSS/JS）', width: 380 }, { label: '管理端（Vue 2 + Element UI）', width: 400 }],
    262, 56, { size: 22, padding: 60, minGap: 100 });
  placeCenteredRow(['用户', '员工', '管理员'], 405, 54, { width: 180, size: 24, padding: 150, minGap: 120 });
  placeCenteredRow(
    ['菜品管理', '订单管理', '用户管理', '供应商管理', '论坛管理', '公告管理', '评价管理'],
    560, 50, { width: 140, size: 18, padding: 24, minGap: 18 });
  placeCenteredRow([
    { label: ['Token认证', '身份校验'], width: 180, preserveLines: true, maxLines: 2 },
    { label: ['拦截器', '权限过滤'], width: 180, preserveLines: true, maxLines: 2 },
    { label: ['MyBatis-Plus', '数据持久'], width: 190, preserveLines: true, maxLines: 2 },
    { label: ['字典服务', '枚举转换'], width: 160, preserveLines: true, maxLines: 2 },
    { label: ['文件上传', '静态资源'], width: 160, preserveLines: true, maxLines: 2 },
  ], 680, 72, { size: 17, padding: 34, minGap: 20, preserveLines: true, maxLines: 2 });
  placeCenteredRow([
    { label: 'yonghu', width: 110 }, { label: 'caipin', width: 110 },
    { label: 'caipin_order', width: 130 }, { label: 'gongyingshang', width: 140 },
    { label: 'forum', width: 100 }, { label: 'news', width: 90 },
    { label: 'commentback', width: 130 }, { label: 'dictionary', width: 120 },
  ], 840, 50, { size: 14, minSize: 11, padding: 18, minGap: 8 });
  placeCenteredRow(
    ['JDK 1.8', 'Spring Boot 2.2', 'MySQL 5.7', 'Maven 3.0', 'Node.js'],
    978, 48, { width: 180, size: 17, minSize: 12, padding: 48, minGap: 28 });

  writeDiagram('canteen-system-arch', 1700, 1180, body);
}

/* ====== 功能结构图 ====== */
function buildFunctionStructure(R) {
  const { rect, vLine, hLine, tallRect, BOLD, snap, writeDiagram } = R;
  const body = [];
  const rootCX = 900, rootY = 40, rootH = 76;
  const mainRailY = 180, groupY = 240;
  const childRailY = 390, childY = 440;
  const childW = 62, childH = 218, childGap = 14;

  body.push(rect(rootCX - 240, rootY, 480, rootH, '社区老年食堂订餐系统', { size: 28, family: BOLD }));
  body.push(vLine(rootCX, rootY + rootH, mainRailY));

  const groups = [
    { center: 300, width: 180, label: '用户端模块', children: ['菜品浏览', '在线订餐', '订单管理', '菜品收藏', '菜品评价', '论坛交流'] },
    { center: 900, width: 180, label: '员工端模块', children: ['菜品上下架', '订单发货', '公告管理'] },
    { center: 1500, width: 180, label: '管理员模块', children: ['用户管理', '员工管理', '供应商管理', '字典管理', '轮播图管理', '系统设置'] },
  ];

  body.push(hLine(groups[0].center, groups[groups.length - 1].center, mainRailY));
  groups.forEach(g => {
    body.push(rect(g.center - g.width / 2, groupY, g.width, 72, g.label, { size: 24, family: BOLD }));
    body.push(vLine(g.center, mainRailY, groupY));
    body.push(vLine(g.center, groupY + 72, childRailY));
    const boxes = g.children.map((label, i) => {
      const rawX = g.center - (g.children.length * childW + (g.children.length - 1) * childGap) / 2 + i * (childW + childGap);
      const x = snap(rawX);
      return { label, x, w: snap(childW), cx: x + snap(childW) / 2 };
    });
    body.push(hLine(boxes[0].cx, boxes[boxes.length - 1].cx, childRailY));
    boxes.forEach(b => {
      body.push(vLine(b.cx, childRailY, childY));
      body.push(tallRect(b.x, childY, b.w, childH, b.label, { size: 18, family: BOLD }));
    });
  });

  writeDiagram('canteen-func-structure', 1800, 980, body);
}

/* ====== 业务流程图 ====== */
function buildBusinessFlow(R) {
  const { rect, diamond, vLine, hLine, pathLine, text, writeDiagram } = R;
  const body = [];
  const cx = 500, boxW = 300;

  body.push(rect(cx - 100, 40, 200, 56, '开始', { rounded: true, size: 26 }));
  body.push(vLine(cx, 96, 140, { arrow: true }));

  body.push(rect(cx - boxW / 2, 140, boxW, 56, '用户登录系统', { size: 22 }));
  body.push(vLine(cx, 196, 250, { arrow: true }));

  body.push(rect(cx - boxW / 2, 250, boxW, 56, '浏览菜品列表', { size: 22 }));
  body.push(vLine(cx, 306, 360, { arrow: true }));

  body.push(rect(cx - boxW / 2, 360, boxW, 56, '选择菜品，填写数量', { size: 22 }));
  body.push(vLine(cx, 416, 480, { arrow: true }));

  // 库存是否充足
  body.push(diamond(cx, 540, 280, 110, '库存是否充足', { size: 20 }));
  body.push(hLine(cx + 140, cx + 340, 540, { arrow: true }));
  body.push(text(cx + 230, 510, '否', { size: 20 }));
  body.push(rect(cx + 340, 510, 200, 56, '提示库存不足', { size: 18 }));

  body.push(vLine(cx, 595, 660, { arrow: true }));
  body.push(text(cx + 20, 630, '是', { size: 20 }));

  // 余额是否充足
  body.push(diamond(cx, 720, 280, 110, '余额是否充足', { size: 20 }));
  body.push(hLine(cx + 140, cx + 340, 720, { arrow: true }));
  body.push(text(cx + 230, 690, '否', { size: 20 }));
  body.push(rect(cx + 340, 690, 200, 56, '提示余额不足', { size: 18 }));

  body.push(vLine(cx, 775, 840, { arrow: true }));
  body.push(text(cx + 20, 810, '是', { size: 20 }));

  body.push(rect(cx - boxW / 2, 840, boxW, 56, '创建订单，扣库存/余额', { size: 20 }));
  body.push(vLine(cx, 896, 950, { arrow: true }));

  body.push(rect(cx - boxW / 2, 950, boxW, 56, '累加积分，评定会员等级', { size: 20 }));
  body.push(vLine(cx, 1006, 1060, { arrow: true }));

  body.push(rect(cx - boxW / 2, 1060, boxW, 56, '管理员/员工发货', { size: 22 }));
  body.push(vLine(cx, 1116, 1170, { arrow: true }));

  body.push(rect(cx - boxW / 2, 1170, boxW, 56, '用户确认收货', { size: 22 }));
  body.push(vLine(cx, 1226, 1280, { arrow: true }));

  body.push(rect(cx - boxW / 2, 1280, boxW, 56, '用户提交评价', { size: 22 }));
  body.push(vLine(cx, 1336, 1390, { arrow: true }));

  body.push(rect(cx - 100, 1390, 200, 56, '结束', { rounded: true, size: 26 }));

  writeDiagram('canteen-business-flow', 1100, 1500, body);
}

/* ====== E-R 图 ====== */
function buildErDiagram(R) {
  const { rect, diamond, pathLine, text, BOLD, writeDiagram } = R;
  const body = [];
  const W = 2.4;

  const entity = (x, y, label, width = 160, height = 56) => {
    const node = { x, y, w: width, h: height, cx: x + width / 2, cy: y + height / 2 };
    body.push(rect(x, y, width, height, label, { size: 22, family: BOLD, strokeWidth: 2.8 }));
    return node;
  };
  const rel = (cx, cy, label, width = 90, height = 56) => {
    const node = { cx, cy, w: width, h: height };
    body.push(diamond(cx, cy, width, height, label, { size: 18, maxLines: 1 }));
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
  const yonghu = entity(570, 200, '用户');

  // Row 0: 员工 and 供应商 flanking above
  const yuangong = entity(120, 60, '员工');
  const gys      = entity(1020, 60, '供应商', 180);

  // 用户 left/right peers
  const forum    = entity(120, 200, '论坛');
  const order    = entity(1020, 200, '订单');

  // 菜品 hub - center bottom
  const caipin   = entity(570, 450, '菜品');

  // 菜品 left/right peers
  const collect  = entity(120, 450, '收藏');
  const comment  = entity(1020, 450, '评价');

  // 公告 - bottom left (managed by admin, separate)
  const news     = entity(120, 650, '公告');

  // === Row 0: 员工-登录-用户, 用户-管理-供应商 ===
  // 员工 → 用户: diagonal, use fold (员工 bottom-right → 用户 top-left)
  const r_login = rel(370, 150, '登录');
  line([yuangong.x + yuangong.w, yuangong.cy], [r_login.cx - r_login.w / 2, r_login.cy]);
  line([r_login.cx + r_login.w / 2, r_login.cy], [yonghu.x, yonghu.cy]);

  // 用户 → 供应商: diagonal fold
  const r_manage = rel(930, 150, '管理');
  line([yonghu.x + yonghu.w, yonghu.cy], [r_manage.cx - r_manage.w / 2, r_manage.cy]);
  line([r_manage.cx + r_manage.w / 2, r_manage.cy], [gys.x, gys.cy]);

  // === 用户 horizontal: 论坛-发帖-用户, 用户-下单-订单 ===
  connect(forum, rel(370, 228, '发帖', 80), yonghu);
  connect(yonghu, rel(830, 228, '下单', 80), order);

  // === 用户→菜品: vertical center ===
  connect(yonghu, rel(650, 340, '浏览'), caipin);

  // === 菜品 horizontal: 收藏-关联-菜品, 菜品-针对-评价 ===
  // 收藏 is left of 菜品 (关联=菜品与收藏的关系)
  connect(collect, rel(370, 478, '关联'), caipin);
  // 评价 is right of 菜品
  connect(caipin, rel(830, 478, '针对'), comment);

  // === 菜品→订单: vertical right column ===
  connect(caipin, rel(830, 340, '包含'), order);

  // === 用户→收藏: fold down-left (用户左下角 → 收藏上方) ===
  const r_fav = rel(350, 340, '收藏', 80);
  // 用户 bottom-left → fold left → down to diamond
  line([yonghu.x, yonghu.cy + 15], [r_fav.cx, yonghu.cy + 15], [r_fav.cx, r_fav.cy - r_fav.h / 2]);
  line([r_fav.cx, r_fav.cy + r_fav.h / 2], [collect.cx, collect.y]);

  // === 用户→评价: fold down-right (用户右下角 → 评价上方) ===
  const r_review = rel(950, 340, '评价', 80);
  line([yonghu.x + yonghu.w, yonghu.cy + 15], [r_review.cx, yonghu.cy + 15], [r_review.cx, r_review.cy - r_review.h / 2]);
  line([r_review.cx, r_review.cy + r_review.h / 2], [comment.cx, comment.y]);

  // === 管理员→公告: fold from 用户 bottom-left to 公告 ===
  const r_pub = rel(200, 550, '发布', 80);
  line([yonghu.cx - 20, yonghu.y + yonghu.h], [yonghu.cx - 20, r_pub.cy - 60], [r_pub.cx, r_pub.cy - 60], [r_pub.cx, r_pub.cy - r_pub.h / 2]);
  line([r_pub.cx, r_pub.cy + r_pub.h / 2], [news.cx, news.y]);

  writeDiagram('canteen-er-diagram', 1300, 750, body);
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
  buildErDiagram(R);

  console.log('canteen diagrams done.');
}

main();
