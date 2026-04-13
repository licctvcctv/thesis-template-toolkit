/**
 * 智学云课论文补充图生成器
 * 使用 thesis-studio 的 SVG 运行时生成统一风格的灰度图
 *
 * 用法: node generate.mjs
 */
import { createRuntime } from '../../../diagrams/runtime.mjs';

const runtime = createRuntime(new Map([
  ['--out-dir', '/Users/a136/vs/45425/thesis_project/papers/zhixue/images'],
  ['--src-dir', '/Users/a136/vs/45425/thesis_project/papers/zhixue/diagrams/svg-src'],
]));

const { rect, diamond, cylinder, ellipse, pathLine, vLine, hLine, text, multiline,
        actor, activation, snap, writeDiagram, STROKE, FONT, BOLD } = runtime;

// ========== 1. 类图 ==========
function buildClassDiagram() {
  const body = [];

  // 类框: x, y, w, h, 分三栏(类名、属性、方法)
  function classBox(x, y, w, name, attrs, methods) {
    const attrH = Math.max(attrs.length * 24, 24);
    const methH = Math.max(methods.length * 24, 24);
    const nameH = 40;
    const h = nameH + attrH + methH + 20;

    // 外框
    body.push(`<rect x="${snap(x)}" y="${snap(y)}" width="${snap(w)}" height="${snap(h)}" fill="#fff" stroke="${STROKE}" stroke-width="2.5"/>`);
    // 类名
    body.push(text(x + w/2, y + nameH/2 + 2, name, { size: 20, weight: '700', family: BOLD }));
    // 分隔线1
    const y1 = y + nameH;
    body.push(`<line x1="${snap(x)}" y1="${snap(y1)}" x2="${snap(x+w)}" y2="${snap(y1)}" stroke="${STROKE}" stroke-width="1.5"/>`);
    // 属性
    attrs.forEach((a, i) => {
      body.push(text(x + 12, y1 + 14 + i * 22, a, { size: 16, anchor: 'start' }));
    });
    // 分隔线2
    const y2 = y1 + attrH + 6;
    body.push(`<line x1="${snap(x)}" y1="${snap(y2)}" x2="${snap(x+w)}" y2="${snap(y2)}" stroke="${STROKE}" stroke-width="1.5"/>`);
    // 方法
    methods.forEach((m, i) => {
      body.push(text(x + 12, y2 + 14 + i * 22, m, { size: 16, anchor: 'start' }));
    });

    return { cx: x + w/2, cy: y + h/2, top: y, bottom: y + h, left: x, right: x + w };
  }

  // 关联线
  function assocLine(from, to, label, opts = {}) {
    body.push(pathLine([[from[0], from[1]], [to[0], to[1]]], { arrow: true, width: 2 }));
    if (label) {
      const mx = (from[0] + to[0]) / 2;
      const my = (from[1] + to[1]) / 2;
      body.push(text(mx, my - 12, label, { size: 14 }));
    }
  }

  // User (中心)
  const user = classBox(700, 30, 200, 'User',
    ['+id: INT', '+username: VARCHAR', '+role: VARCHAR', '+status: TINYINT'],
    ['+login()', '+register()']);

  // Course
  const course = classBox(200, 30, 200, 'Course',
    ['+id: INT', '+title: VARCHAR', '+category: VARCHAR', '+status: TINYINT'],
    ['+search()', '+getDetail()']);

  // Lesson
  const lesson = classBox(10, 300, 180, 'Lesson',
    ['+id: INT', '+courseId: INT', '+videoUrl: VARCHAR', '+duration: INT'],
    []);

  // Progress
  const progress = classBox(230, 300, 200, 'Progress',
    ['+userId: INT', '+lessonId: INT', '+watchedSeconds: INT', '+completed: BOOL'],
    ['+update()']);

  // Enrollment
  const enroll = classBox(480, 300, 180, 'Enrollment',
    ['+userId: INT', '+courseId: INT', '+enrolledAt: DATE'],
    []);

  // Post
  const post = classBox(1150, 30, 180, 'Post',
    ['+id: INT', '+userId: INT', '+content: TEXT', '+likes: INT'],
    ['+toggleLike()']);

  // Comment
  const comment = classBox(1150, 260, 180, 'Comment',
    ['+targetType: VARCHAR', '+targetId: INT', '+content: TEXT'],
    []);

  // Question
  const question = classBox(700, 300, 180, 'Question',
    ['+courseId: INT', '+title: VARCHAR', '+solved: BOOL'],
    []);

  // Answer
  const answer = classBox(920, 300, 180, 'Answer',
    ['+questionId: INT', '+accepted: BOOL', '+content: TEXT'],
    ['+accept()']);

  // Class
  const cls = classBox(700, 520, 180, 'Class',
    ['+name: VARCHAR', '+inviteCode: VARCHAR'],
    []);

  // ClassMember
  const clsMem = classBox(950, 520, 180, 'ClassMember',
    ['+classId: INT', '+userId: INT', '+joinedAt: DATE'],
    []);

  // 关联线
  // User -> Enrollment (1..*)
  assocLine([user.left, user.bottom], [enroll.right, enroll.top], '1..*');
  // User -> Progress
  assocLine([user.left - 50, user.bottom], [progress.cx, progress.top], '1..*');
  // User -> Post
  assocLine([user.right, user.cy], [post.left, post.cy], '1..*');
  // User -> Question
  assocLine([user.cx, user.bottom], [question.cx, question.top], '1..*');
  // Course -> Lesson
  assocLine([course.left, course.bottom], [lesson.cx, lesson.top], '1..*');
  // Course -> Enrollment
  assocLine([course.cx, course.bottom], [enroll.left, enroll.top], '1..*');
  // Course -> Question
  assocLine([course.right, course.bottom], [question.left, question.top], '1..*');
  // Lesson -> Progress
  assocLine([lesson.right, lesson.cy], [progress.left, progress.cy], '1..*');
  // Question -> Answer
  assocLine([question.right, question.cy], [answer.left, answer.cy], '1..*');
  // Post -> Comment
  assocLine([post.cx, post.bottom], [comment.cx, comment.top], '1..*');
  // User -> ClassMember
  assocLine([user.cx + 30, user.bottom], [clsMem.cx, clsMem.top], '1..*');
  // Class -> ClassMember
  assocLine([cls.right, cls.cy], [clsMem.left, clsMem.cy], '1..*');

  writeDiagram('zhixueyunke-class-diagram', 1400, 680, body);
}

// ========== 2. 登录时序图 ==========
function buildLoginSequence() {
  const body = [];

  const lifelines = [
    { x: 140, label: 'Flutter客户端' },
    { x: 440, label: 'AuthController' },
    { x: 740, label: 'AuthService' },
    { x: 1000, label: 'User表' },
    { x: 1260, label: 'JwtService' },
  ];

  lifelines.forEach(({ x, label }) => {
    body.push(rect(x - 100, 60, 200, 50, label, { size: 20, minSize: 14 }));
    body.push(`<line x1="${snap(x)}" y1="110" x2="${snap(x)}" y2="680" stroke="#888" stroke-width="2" stroke-dasharray="8 6"/>`);
  });

  // 激活条
  body.push(activation(440, 170, 80));
  body.push(activation(740, 250, 180));
  body.push(activation(1000, 300, 60));
  body.push(activation(1260, 450, 60));

  const msg = (from, to, y, label, dashed = false) => {
    body.push(pathLine([[from, y], [to, y]], { arrow: true, dashed, width: 2.2, color: dashed ? '#555' : STROKE }));
    body.push(text((from + to) / 2, y - 16, label, { size: 18 }));
  };

  msg(140, 428, 180, '1: POST /api/auth/login');
  msg(452, 728, 260, '2: login(username, pwd)');
  msg(752, 988, 310, '3: 查询用户记录');
  msg(988, 752, 360, '4: 返回User对象', true);
  msg(740, 740, 410, '5: bcrypt比对密码');
  body.push(text(890, 410, '5: bcrypt比对密码', { size: 16, anchor: 'start' }));
  // 删除重复的 text
  msg(752, 1248, 460, '6: 签发Token对');
  msg(1248, 752, 520, '7: accessToken + refreshToken', true);
  msg(728, 452, 580, '8: 返回令牌对', true);
  msg(428, 140, 640, '9: 存储令牌到本地', true);

  writeDiagram('zhixueyunke-login-sequence', 1400, 720, body);
}

// ========== 3. 报名时序图 ==========
function buildEnrollSequence() {
  const body = [];

  const lifelines = [
    { x: 140, label: 'Flutter客户端' },
    { x: 400, label: 'JwtGuard' },
    { x: 660, label: 'CourseController' },
    { x: 940, label: 'CourseService' },
    { x: 1220, label: 'SQLite' },
  ];

  lifelines.forEach(({ x, label }) => {
    body.push(rect(x - 100, 60, 200, 50, label, { size: 20, minSize: 14 }));
    body.push(`<line x1="${snap(x)}" y1="110" x2="${snap(x)}" y2="640" stroke="#888" stroke-width="2" stroke-dasharray="8 6"/>`);
  });

  body.push(activation(400, 170, 60));
  body.push(activation(660, 250, 60));
  body.push(activation(940, 320, 160));
  body.push(activation(1220, 370, 80));

  const msg = (from, to, y, label, dashed = false) => {
    body.push(pathLine([[from, y], [to, y]], { arrow: true, dashed, width: 2.2, color: dashed ? '#555' : STROKE }));
    body.push(text((from + to) / 2, y - 16, label, { size: 18 }));
  };

  msg(140, 388, 180, '1: POST /api/enrollments (Bearer Token)');
  msg(412, 648, 230, '2: 验证JWT，注入用户信息');
  msg(672, 928, 330, '3: createEnrollment(userId, courseId)');
  msg(952, 1208, 380, '4: 查询是否已报名');
  msg(1208, 952, 430, '5: 无重复记录', true);
  msg(952, 1208, 480, '6: 插入Enrollment记录');
  msg(928, 672, 540, '7: 返回报名结果', true);
  msg(648, 140, 600, '8: 200 {enrollment}', true);

  writeDiagram('zhixueyunke-enroll-sequence', 1400, 680, body);
}

// ========== 4. 核心业务流程图 ==========
function buildLearningFlow() {
  const body = [];
  const cx = 500;

  // 开始
  body.push(rect(cx - 100, 40, 200, 60, '用户登录', { rounded: true, size: 24 }));
  body.push(vLine(cx, 100, 140, { arrow: true }));

  // 浏览课程
  body.push(rect(cx - 140, 140, 280, 60, '浏览课程列表', { size: 24 }));
  body.push(vLine(cx, 200, 250, { arrow: true }));

  // 是否已报名
  body.push(diamond(cx, 310, 280, 110, '是否已报名?', { size: 20 }));

  // 否 -> 报名
  body.push(hLine(cx + 140, 820, 310, { arrow: true }));
  body.push(text(700, 294, '否', { size: 20 }));
  body.push(rect(740, 280, 200, 60, '点击报名', { size: 22 }));
  body.push(pathLine([[840, 340], [840, 420], [cx + 140, 420]], { arrow: true }));

  // 是 -> 课程详情
  body.push(vLine(cx, 365, 400, { arrow: true }));
  body.push(text(cx + 20, 388, '是', { size: 20, anchor: 'start' }));
  body.push(rect(cx - 140, 400, 280, 60, '进入课程详情', { size: 24 }));
  body.push(vLine(cx, 460, 510, { arrow: true }));

  // 选择课时
  body.push(rect(cx - 120, 510, 240, 60, '选择课时', { size: 24 }));
  body.push(vLine(cx, 570, 620, { arrow: true }));

  // 有无历史进度
  body.push(diamond(cx, 680, 300, 110, '有历史进度?', { size: 20 }));

  // 是 -> 断点续播
  body.push(hLine(cx - 150, 160, 680, { arrow: true }));
  body.push(text(240, 664, '是', { size: 20 }));
  body.push(rect(60, 650, 200, 60, '断点续播', { size: 22 }));
  body.push(pathLine([[160, 710], [160, 790], [cx - 140, 790]], { arrow: true }));

  // 否 -> 从头播放
  body.push(hLine(cx + 150, 820, 680, { arrow: true }));
  body.push(text(700, 664, '否', { size: 20 }));
  body.push(rect(740, 650, 200, 60, '从头播放', { size: 22 }));
  body.push(pathLine([[840, 710], [840, 790], [cx + 140, 790]], { arrow: true }));

  // 播放视频
  body.push(vLine(cx, 735, 770, { arrow: true }));
  body.push(rect(cx - 140, 770, 280, 60, '播放视频', { size: 24 }));
  body.push(vLine(cx, 830, 870, { arrow: true }));

  // 定时上报进度
  body.push(rect(cx - 140, 870, 280, 60, '每30秒上报进度', { size: 22 }));
  body.push(vLine(cx, 930, 980, { arrow: true }));

  // 退出?
  body.push(diamond(cx, 1040, 260, 100, '用户退出?', { size: 20 }));
  body.push(hLine(cx - 130, 60, 1040));
  body.push(text(120, 1024, '否', { size: 20 }));
  body.push(pathLine([[60, 1040], [60, 790], [cx - 140, 790]], { arrow: true }));

  body.push(vLine(cx, 1090, 1130, { arrow: true }));
  body.push(text(cx + 20, 1116, '是', { size: 20, anchor: 'start' }));

  // 保存位置
  body.push(rect(cx - 150, 1130, 300, 60, '保存当前播放位置', { size: 22 }));
  body.push(vLine(cx, 1190, 1240, { arrow: true }));

  // 全部完成?
  body.push(diamond(cx, 1300, 300, 110, '全部课时完成?', { size: 20 }));
  body.push(hLine(cx - 150, 60, 1300));
  body.push(text(120, 1284, '否', { size: 20 }));
  body.push(pathLine([[60, 1300], [60, 540], [cx - 120, 540]], { arrow: true }));

  body.push(vLine(cx, 1355, 1400, { arrow: true }));
  body.push(text(cx + 20, 1388, '是', { size: 20, anchor: 'start' }));
  body.push(rect(cx - 130, 1400, 260, 60, '课程标记已完成', { rounded: true, size: 22 }));

  writeDiagram('zhixueyunke-module-flow', 1000, 1520, body);
}

// 执行
buildClassDiagram();
buildLoginSequence();
buildEnrollSequence();
buildLearningFlow();
console.log('Done: 4 diagrams generated');

// ========== 5. 状态流转图 ==========
function buildStateDiagram() {
  const body = [];
  const cx = 500;

  // 课程状态
  body.push(text(250, 30, '课程状态流转', { size: 24, weight: '700', family: BOLD }));

  body.push(rect(100, 60, 140, 50, '草稿(0)', { rounded: true, size: 20 }));
  body.push(hLine(240, 360, 85, { arrow: true }));
  body.push(text(300, 72, '审核通过', { size: 16 }));

  body.push(rect(360, 60, 160, 50, '已上架(1)', { rounded: true, size: 20 }));
  body.push(hLine(520, 640, 85, { arrow: true }));
  body.push(text(580, 72, '下架操作', { size: 16 }));

  body.push(rect(640, 60, 160, 50, '已下架(2)', { rounded: true, size: 20 }));
  body.push(pathLine([[720, 110], [720, 140], [440, 140], [440, 110]], { arrow: true, dashed: true }));
  body.push(text(580, 154, '重新上架', { size: 16 }));

  // 报名学习状态
  body.push(text(250, 210, '报名学习状态流转', { size: 24, weight: '700', family: BOLD }));

  body.push(rect(60, 250, 140, 50, '未报名', { rounded: true, size: 20 }));
  body.push(hLine(200, 320, 275, { arrow: true }));
  body.push(text(260, 262, '点击报名', { size: 16 }));

  body.push(rect(320, 250, 140, 50, '已报名', { rounded: true, size: 20 }));
  body.push(hLine(460, 580, 275, { arrow: true }));
  body.push(text(520, 262, '开始学习', { size: 16 }));

  body.push(rect(580, 250, 140, 50, '学习中', { rounded: true, size: 20 }));
  body.push(hLine(720, 860, 275, { arrow: true }));
  body.push(text(790, 262, '全部完成', { size: 16 }));

  body.push(rect(860, 250, 140, 50, '已完成', { rounded: true, size: 20 }));

  writeDiagram('zhixueyunke-state-diagram', 1050, 330, body);
}

buildStateDiagram();
console.log('State diagram generated');
