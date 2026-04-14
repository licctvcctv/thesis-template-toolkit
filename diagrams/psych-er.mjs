import { createRuntime, parseArgs } from './runtime.mjs';

const args = parseArgs();
const R = createRuntime(args);
const { rect, diamond, ellipse, pathLine, hLine, vLine, text, writeDiagram, BOLD, STROKE } = R;

function buildER() {
  const body = [];
  const W = 1800, H = 1400;

  // Helper: draw entity box
  const ent = (x, y, label) => {
    const w = 160, h = 56;
    body.push(rect(x - w/2, y - h/2, w, h, label, { size: 22, family: BOLD }));
    return { x, y, w, h };
  };

  // Helper: draw attribute ellipse
  const attr = (cx, cy, label) => {
    body.push(ellipse(cx, cy, 68, 22, label, { size: 16, minSize: 13 }));
  };

  // Helper: draw relationship diamond
  const rel = (cx, cy, label) => {
    body.push(diamond(cx, cy, 140, 70, label, { size: 18 }));
    return { x: cx, y: cy };
  };

  // Helper: connect two points with a line
  const connect = (x1, y1, x2, y2) => {
    body.push(pathLine([[x1, y1], [x2, y2]], { width: 2 }));
  };

  // Helper: label on a line
  const lineLabel = (x, y, label) => {
    body.push(text(x, y, label, { size: 16 }));
  };

  // ============ Layout (manually positioned) ============

  // Center: 用户
  const user = ent(900, 700, '用户');
  // Attributes for 用户 (fan out to the right)
  attr(1140, 610, '用户名');
  attr(1140, 660, '邮箱');
  attr(1140, 710, '角色');
  attr(1140, 760, '头像');
  attr(1140, 810, '状态');
  connect(980, 700, 1072, 610);
  connect(980, 700, 1072, 660);
  connect(980, 700, 1072, 710);
  connect(980, 700, 1072, 760);
  connect(980, 700, 1072, 810);

  // Top-left: 咨询师档案
  const counselor = ent(300, 200, '咨询师档案');
  attr(100, 110, '专长领域');
  attr(260, 110, '从业年限');
  attr(420, 110, '评分');
  attr(540, 110, '等级');
  connect(300, 172, 100, 132);
  connect(300, 172, 260, 132);
  connect(300, 172, 420, 132);
  connect(300, 172, 540, 132);

  // Top-center: 排班
  const schedule = ent(700, 200, '排班');
  attr(580, 110, '排班日期');
  attr(700, 110, '开始时间');
  attr(820, 110, '结束时间');
  attr(940, 110, '状态');
  connect(700, 172, 580, 132);
  connect(700, 172, 700, 132);
  connect(700, 172, 820, 132);
  connect(700, 172, 940, 132);

  // Top-right: 预约
  const appt = ent(1150, 200, '预约');
  attr(1030, 110, '预约时间');
  attr(1150, 110, '状态');
  attr(1270, 110, '评分');
  connect(1150, 172, 1030, 132);
  connect(1150, 172, 1150, 132);
  connect(1150, 172, 1270, 132);

  // Left: 聊天消息
  const chat = ent(200, 700, '聊天消息');
  attr(60, 600, '房间编号');
  attr(60, 650, '发送者');
  attr(60, 700, '内容');
  attr(60, 750, '消息类型');
  connect(120, 700, 128, 600);
  connect(120, 700, 128, 650);
  connect(120, 700, 128, 700);
  connect(120, 700, 128, 750);

  // Bottom-left: 社区帖子
  const post = ent(300, 1100, '社区帖子');
  attr(120, 1200, '内容');
  attr(240, 1200, '情绪标签');
  attr(360, 1200, '点赞数');
  attr(480, 1200, '状态');
  connect(300, 1128, 120, 1178);
  connect(300, 1128, 240, 1178);
  connect(300, 1128, 360, 1178);
  connect(300, 1128, 480, 1178);

  // Bottom-center: 评论
  const comment = ent(750, 1100, '评论');
  attr(650, 1200, '内容');
  attr(770, 1200, '状态');
  attr(890, 1200, '帖子编号');
  connect(750, 1128, 650, 1178);
  connect(750, 1128, 770, 1178);
  connect(750, 1128, 890, 1178);

  // Bottom-right: 测评记录
  const assess = ent(1200, 1100, '测评记录');
  attr(1060, 1200, '量表类型');
  attr(1200, 1200, '总分');
  attr(1340, 1200, '严重程度');
  connect(1200, 1128, 1060, 1178);
  connect(1200, 1128, 1200, 1178);
  connect(1200, 1128, 1340, 1178);

  // Right: 风险预警
  const risk = ent(1550, 700, '风险预警');
  attr(1690, 620, '风险等级');
  attr(1690, 700, '关键词');
  attr(1690, 780, '来源');
  connect(1630, 700, 1622, 620);
  connect(1630, 700, 1622, 700);
  connect(1630, 700, 1622, 780);

  // ============ Relationships ============

  // 用户 —— 拥有 —— 咨询师档案
  const r1 = rel(550, 450, '拥有');
  connect(900, 672, 550+70, 450);    // user → diamond
  connect(550-70, 450, 300, 228);    // diamond → counselor
  lineLabel(780, 510, '1');
  lineLabel(380, 350, '1');

  // 咨询师档案 —— 安排 —— 排班
  const r2 = rel(500, 200, '安排');
  connect(380, 200, 500-70, 200);    // counselor → diamond
  connect(500+70, 200, 620, 200);    // diamond → schedule
  lineLabel(420, 185, '1');
  lineLabel(600, 185, 'n');

  // 用户 —— 预约 —— 预约
  const r3 = rel(1050, 450, '预约');
  connect(900, 672, 1050, 450+35);   // user → diamond
  connect(1050, 450-35, 1150, 228);  // diamond → appointment
  lineLabel(950, 580, '1');
  lineLabel(1120, 310, 'n');

  // 用户 —— 发送 —— 聊天消息
  const r4 = rel(550, 700, '发送');
  connect(820, 700, 550+70, 700);    // user → diamond
  connect(550-70, 700, 280, 700);    // diamond → chat
  lineLabel(760, 685, '1');
  lineLabel(350, 685, 'n');

  // 用户 —— 发布 —— 社区帖子
  const r5 = rel(550, 920, '发布');
  connect(900, 728, 550+70, 920);    // user → diamond
  connect(550-70, 920, 300, 1072);   // diamond → post
  lineLabel(780, 820, '1');
  lineLabel(380, 1000, 'n');

  // 社区帖子 —— 包含 —— 评论
  const r6 = rel(530, 1100, '包含');
  connect(380, 1100, 530-70, 1100);  // post → diamond
  connect(530+70, 1100, 670, 1100);  // diamond → comment
  lineLabel(420, 1085, '1');
  lineLabel(640, 1085, 'n');

  // 用户 —— 进行 —— 测评记录
  const r7 = rel(1050, 920, '进行');
  connect(900, 728, 1050, 920-35);   // user → diamond
  connect(1050, 920+35, 1200, 1072); // diamond → assess
  lineLabel(960, 820, '1');
  lineLabel(1150, 1000, 'n');

  // 用户 —— 触发 —— 风险预警
  const r8 = rel(1250, 700, '触发');
  connect(980, 700, 1250-70, 700);   // user → diamond
  connect(1250+70, 700, 1470, 700);  // diamond → risk
  lineLabel(1100, 685, '1');
  lineLabel(1400, 685, 'n');

  writeDiagram('psych-er', W, H, body);
}

buildER();
