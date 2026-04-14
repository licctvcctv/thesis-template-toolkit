import { createRuntime, parseArgs } from './runtime.mjs';

const args = parseArgs();
const R = createRuntime(args);
const { rect, diamond, cylinder, vLine, hLine, pathLine, text, writeDiagram, BOLD, STROKE } = R;

// ===== 图2-5 用户注册与登录流程图 =====
function buildLoginFlow() {
  const body = [];
  const W = 1200, H = 1100;
  const cx = 500, stepW = 280, stepH = 64;

  body.push(rect(cx - 110, 50, 220, 60, '开始', { rounded: true, size: 26 }));
  body.push(vLine(cx, 110, 160, { arrow: true }));

  body.push(rect(cx - stepW/2, 160, stepW, stepH, '用户输入登录信息\n（用户名+密码+验证码）', { size: 19 }));
  body.push(vLine(cx, 160+stepH, 280, { arrow: true }));

  body.push(rect(cx - stepW/2, 280, stepW, stepH, '系统验证身份信息\n校验JWT令牌有效性', { size: 19 }));
  body.push(vLine(cx, 280+stepH, 400, { arrow: true }));

  body.push(diamond(cx, 450, 320, 120, '验证通过？\n角色权限匹配？', { size: 19 }));

  // 否 → 右
  body.push(hLine(cx + 160, 850, 450, { arrow: true }));
  body.push(text(720, 425, '否', { size: 22 }));
  body.push(rect(850, 415, 240, stepH, '返回错误提示\n要求重新登录', { size: 19 }));
  // 回到输入
  body.push(pathLine([[970, 415], [970, 120], [cx + stepW/2, 190]], { arrow: true }));

  // 是 → 下
  body.push(text(cx + 20, 525, '是', { size: 22 }));
  body.push(vLine(cx, 510, 570, { arrow: true }));

  // 数据库
  body.push(cylinder(100, 390, 130, 100, '用户表\nRedis会话', { size: 17 }));
  body.push(hLine(cx - 160, 230, 450, { arrow: false }));
  body.push(pathLine([[165, 490], [165, 620], [cx - stepW/2, 620]], { arrow: true }));

  body.push(rect(cx - stepW/2, 570, stepW, stepH+10, '生成JWT令牌\n缓存会话到Redis', { size: 19 }));
  body.push(vLine(cx, 644, 710, { arrow: true }));

  body.push(rect(cx - stepW/2, 710, stepW, stepH, '跳转到对应角色首页', { size: 20 }));
  body.push(vLine(cx, 710+stepH, 840, { arrow: true }));

  body.push(rect(cx - 110, 840, 220, 60, '流程结束', { rounded: true, size: 26 }));

  writeDiagram('psych-login-flow', W, H, body);
}

// ===== 图2-6 咨询师预约流程图 =====
function buildAppointmentFlow() {
  const body = [];
  const W = 1200, H = 1300;
  const cx = 500, stepW = 280, stepH = 60;

  body.push(rect(cx - 110, 40, 220, 56, '开始', { rounded: true, size: 26 }));
  body.push(vLine(cx, 96, 140, { arrow: true }));

  body.push(rect(cx - stepW/2, 140, stepW, stepH, '学生浏览咨询师列表', { size: 20 }));
  body.push(vLine(cx, 200, 240, { arrow: true }));

  body.push(rect(cx - stepW/2, 240, stepW, stepH, '选择可预约时段', { size: 20 }));
  body.push(vLine(cx, 300, 340, { arrow: true }));

  body.push(rect(cx - stepW/2, 340, stepW, stepH, '提交预约请求', { size: 20 }));
  body.push(vLine(cx, 400, 450, { arrow: true }));

  // 判断1: 时段冲突
  body.push(diamond(cx, 500, 300, 110, '时段是否冲突？', { size: 20 }));
  body.push(text(cx + 20, 570, '否', { size: 22 }));

  // 是 → 右 → 回到选择
  body.push(hLine(cx + 150, 850, 500, { arrow: true }));
  body.push(text(720, 475, '是', { size: 22 }));
  body.push(rect(850, 470, 220, stepH, '建议选择\n其他时段', { size: 19 }));
  body.push(pathLine([[960, 470], [960, 270], [cx + stepW/2, 270]], { arrow: true }));

  body.push(vLine(cx, 555, 610, { arrow: true }));
  body.push(rect(cx - stepW/2, 610, stepW, stepH, '预约创建成功', { size: 20 }));
  body.push(vLine(cx, 670, 710, { arrow: true }));

  body.push(rect(cx - stepW/2, 710, stepW, stepH, '咨询师确认/拒绝', { size: 20 }));
  body.push(vLine(cx, 770, 820, { arrow: true }));

  // 判断2: 咨询师确认
  body.push(diamond(cx, 870, 300, 110, '咨询师是否确认？', { size: 19 }));

  // 否 → 右
  body.push(hLine(cx + 150, 850, 870, { arrow: true }));
  body.push(text(720, 845, '否', { size: 22 }));
  body.push(rect(850, 840, 220, stepH, '预约被拒绝\n建议重新预约', { size: 19 }));

  // 是 → 下
  body.push(text(cx + 20, 940, '是', { size: 22 }));
  body.push(vLine(cx, 925, 980, { arrow: true }));

  body.push(rect(cx - stepW/2, 980, stepW, stepH, '预约生效，推送通知', { size: 20 }));
  body.push(vLine(cx, 1040, 1070, { arrow: true }));

  body.push(rect(cx - stepW/2, 1070, stepW, stepH, '按时咨询 → 填写评价', { size: 20 }));
  body.push(vLine(cx, 1130, 1170, { arrow: true }));

  body.push(rect(cx - 110, 1170, 220, 56, '结束', { rounded: true, size: 26 }));

  writeDiagram('psych-appointment-flow', W, H, body);
}

// ===== 图2-7 AI智能对话流程图 =====
function buildAiChatFlow() {
  const body = [];
  const W = 1200, H = 1100;
  const cx = 500, stepW = 280, stepH = 60;

  body.push(rect(cx - 110, 40, 220, 56, '开始', { rounded: true, size: 26 }));
  body.push(vLine(cx, 96, 140, { arrow: true }));

  body.push(rect(cx - stepW/2, 140, stepW, stepH, '学生输入对话内容', { size: 20 }));
  body.push(vLine(cx, 200, 240, { arrow: true }));

  body.push(rect(cx - stepW/2, 240, stepW, stepH+10, '后端加载最近10轮\n对话历史作为上下文', { size: 19 }));
  body.push(vLine(cx, 310, 350, { arrow: true }));

  body.push(rect(cx - stepW/2, 350, stepW, stepH+10, '拼接System Prompt\n+ 历史 + 用户输入', { size: 19 }));
  body.push(vLine(cx, 420, 460, { arrow: true }));

  body.push(rect(cx - stepW/2, 460, stepW, stepH, '调用AI大模型API', { size: 20 }));
  body.push(vLine(cx, 520, 570, { arrow: true }));

  // 判断: 情绪检测
  body.push(diamond(cx, 620, 320, 110, '情绪风险词\n检测是否触发？', { size: 19 }));

  // 是 → 右
  body.push(hLine(cx + 160, 850, 620, { arrow: true }));
  body.push(text(720, 595, '是', { size: 22 }));
  body.push(rect(850, 585, 240, stepH+10, '触发预警通知\n建议联系真人咨询师', { size: 18 }));

  // 否 → 下
  body.push(text(cx + 20, 690, '否', { size: 22 }));
  body.push(vLine(cx, 675, 730, { arrow: true }));

  body.push(rect(cx - stepW/2, 730, stepW, stepH, 'AI回复返回前端显示', { size: 20 }));
  body.push(vLine(cx, 790, 830, { arrow: true }));

  // 数据库
  body.push(cylinder(100, 720, 130, 90, 'chat_messages\n对话记录落库', { size: 16 }));
  body.push(hLine(cx - stepW/2, 230, 760, {}));
  body.push(pathLine([[165, 720], [165, 760], [cx - stepW/2, 760]], { arrow: true }));

  body.push(rect(cx - stepW/2, 830, stepW, stepH, '学生继续对话或关闭', { size: 20 }));
  body.push(vLine(cx, 890, 940, { arrow: true }));

  body.push(rect(cx - 110, 940, 220, 56, '流程结束', { rounded: true, size: 26 }));

  writeDiagram('psych-ai-chat-flow', W, H, body);
}

buildLoginFlow();
buildAppointmentFlow();
buildAiChatFlow();
