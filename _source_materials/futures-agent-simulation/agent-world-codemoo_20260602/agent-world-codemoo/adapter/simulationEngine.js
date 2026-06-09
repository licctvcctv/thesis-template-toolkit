const { ensureWorldState } = require('./tradingWorldState');
const LocalDataLoader = require('./localDataLoader');

const DEFAULT_LLM_MODEL = 'deepseek-v4-flash';
const MEMORY_AUDITOR_ID = 'memory-auditor';
let localDataLoader = null;

function getLocalDataLoader() {
  if (!localDataLoader) {
    localDataLoader = new LocalDataLoader();
  }
  return localDataLoader;
}

const AGENT_IDS = Object.freeze([
  'conservative-hedger',
  'balanced-strategist',
  'aggressive-breakout',
  'memory-auditor'
]);

const PEER_AGENT_IDS = Object.freeze(
  AGENT_IDS.filter(agentId => agentId !== MEMORY_AUDITOR_ID)
);

const AGENT_PROFILES = Object.freeze({
  'conservative-hedger': {
    role: '保守型',
    mandate: '资本保全优先的长线期货配置官，偏好黄金期货，但可在黄金/原油/大豆期货中择一建仓，追求稳健的风险调整后收益。',
    style: '先保本金。至少等待宏观与技术面两个独立信号互相确认后，才逐步增加仓位；波动放大时优先降杠杆而非追趋势。',
    riskFramework: '单笔名义风险预算≤组合 1.5%，累计回撤触及 12% 时强制降仓至基准的一半。',
    decisionPrinciples: [
      '未出现双信号确认前默认 HOLD',
      '实际利率与美元指数同向压制金价时谨慎做多',
      '引用 2011/2020 等 risk-off 历史案例验证当前是否真避险'
    ],
    commodityBias: 'gold',
    model: DEFAULT_LLM_MODEL,
    preferredModel: 'deepseek-v4-flash',
    modelChain: ['deepseek-v4-flash', 'deepseek-v4-pro'],
    color: '#38bdf8'
  },
  'balanced-strategist': {
    role: '均衡型',
    mandate: '多因子均衡型CTA策略官，偏好原油期货，但可在三种期货中择一，在宏观、价格趋势与记忆样本间做权重平衡。',
    style: '综合宏观资讯、价格趋势和回撤压力，偏好分批进出；多品种信号冲突时降低总杠杆。',
    riskFramework: '目标波动率 10–14%，敞口随置信度线性缩放，禁止单一因子驱动满仓。',
    decisionPrinciples: [
      '宏观、价格、记忆三因子至少两项一致才调仓',
      '利好兑现前分批减仓，防止预期反转',
      '训练段积累规则，测试段验证泛化而非追加规则'
    ],
    commodityBias: 'crude_oil',
    model: DEFAULT_LLM_MODEL,
    preferredModel: 'deepseek-v4-flash',
    modelChain: ['deepseek-v4-flash', 'deepseek-v4-pro'],
    color: '#4ade80'
  },
  'aggressive-breakout': {
    role: '激进型',
    mandate: '动量突破型交易官，偏好大豆期货，但可在三种期货中择一，在资讯与价格共振时争取超额收益。',
    style: '当动量与资讯共振时提前行动，接受更大的阶段性回撤；但单日回撤扩大时禁止同向加仓。',
    riskFramework: '允许更高名义敞口（系数 1.25），但连续同向亏损两笔后强制冷静期一轮。',
    decisionPrinciples: [
      '动量未确认时不要抢先手',
      '突破需结合持仓/库存/产量等基本面证据',
      '测试段降低杠杆，优先验证止损纪律'
    ],
    commodityBias: 'soybean',
    model: DEFAULT_LLM_MODEL,
    preferredModel: 'deepseek-v4-flash',
    modelChain: ['deepseek-v4-flash', 'deepseek-v4-pro'],
    color: '#f97316'
  },
  'memory-auditor': {
    role: '记忆审计',
    mandate: '跨智能体记忆审计官：审阅保守/均衡/激进三方的本轮观点，识别拥挤交易与历史失败模式，给出独立第三方动作。',
    style: '质疑拥挤交易与一致预期，检索相似失败案例后再决策；对激进型建议进行反向压力测试。',
    riskFramework: '审计官默认低敞口（系数 0.75）；当三者同向且置信度均高时，优先 HOLD 或反向减仓。',
    decisionPrinciples: [
      '必须先阅读 peerDecisions 再给出动作',
      '三智能体同向 BUY/SELL 时重点检查是否拥挤交易',
      '引用检索记忆中的历史失败案例支持审计结论'
    ],
    commodityBias: 'gold',
    model: 'deepseek-v4-flash',
    preferredModel: 'deepseek-v4-flash',
    modelChain: ['deepseek-v4-flash', 'deepseek-v4-pro'],
    color: '#eab308'
  }
});

const COMMODITIES = Object.freeze([
  { id: 'gold', name: '黄金期货', symbol: 'GC', unit: '美元/盎司' },
  { id: 'soybean', name: '大豆期货', symbol: 'ZS', unit: '美分/蒲式耳' },
  { id: 'crude_oil', name: '原油期货', symbol: 'CL', unit: '美元/桶' }
]);

function normalizeCommodityId(value) {
  const raw = String(value || '').trim().toLowerCase();
  if (!raw) return null;
  if (raw === 'gold' || raw === 'gc' || raw === '黄金' || raw === '黄金期货') return 'gold';
  if (raw === 'soybean' || raw === 'zs' || raw === '大豆' || raw === '大豆期货') return 'soybean';
  if (raw === 'crude_oil' || raw === 'crude' || raw === 'oil' || raw === 'cl' || raw === '原油' || raw === '原油期货') {
    return 'crude_oil';
  }
  const byId = COMMODITIES.find(item => item.id === raw);
  if (byId) return byId.id;
  const bySymbol = COMMODITIES.find(item => item.symbol.toLowerCase() === raw);
  if (bySymbol) return bySymbol.id;
  const byName = COMMODITIES.find(item => item.name === String(value || '').trim());
  if (byName) return byName.id;
  return null;
}

function resolveCommodity({ commodityId, profile, decision }) {
  const requested = normalizeCommodityId(decision?.commodity) ||
    normalizeCommodityId(decision?.symbol) ||
    normalizeCommodityId(commodityId);
  if (requested) {
    return COMMODITIES.find(item => item.id === requested) || COMMODITIES[0];
  }
  return COMMODITIES.find(item => item.id === profile?.commodityBias) || COMMODITIES[0];
}

const STATIONS = Object.freeze([
  { id: 'news', label: '资讯采集台', x: 4, y: 11, locationId: 'store', activity: '抓取市场新闻' },
  { id: 'memory', label: '记忆档案馆', x: 25, y: 21, locationId: 'library', activity: '检索相似历史案例' },
  { id: 'price', label: '价格趋势墙', x: 24, y: 3, locationId: 'home_ne', activity: '读取价格趋势' },
  { id: 'risk', label: '风险控制室', x: 4, y: 21, locationId: 'home_sw', activity: '检查回撤边界' },
  { id: 'debate', label: '智能体辩论场', x: 14, y: 14, locationId: null, activity: '辩论信号质量' },
  { id: 'trade', label: '交易执行门', x: 11, y: 3, locationId: 'office', activity: '生成交易指令' }
]);

const { ROUNDS } = require('./tradingRounds');


// 本地模拟预设动作 — 来源 LLM 真实运行 2026-06-01T13-38-51-040Z_b98e03（runs/.../preset-export.json）
const ACTIONS_BY_AGENT = Object.freeze({
  'conservative-hedger': ['BUY', 'HOLD', 'HOLD', 'HOLD', 'BUY', 'HOLD', 'HOLD', 'HOLD', 'BUY', 'BUY', 'HOLD', 'HOLD', 'HOLD', 'HOLD', 'HOLD', 'HOLD', 'BUY', 'HOLD', 'HOLD', 'HOLD', 'BUY', 'HOLD', 'HOLD', 'HOLD', 'BUY', 'HOLD', 'BUY', 'HOLD', 'HOLD', 'BUY', 'BUY', 'HOLD', 'BUY', 'HOLD', 'HOLD', 'HOLD'],
  'balanced-strategist': ['SELL', 'BUY', 'HOLD', 'HOLD', 'HOLD', 'HOLD', 'BUY', 'SELL', 'BUY', 'SELL', 'HOLD', 'HOLD', 'SELL', 'BUY', 'BUY', 'BUY', 'BUY', 'BUY', 'BUY', 'SELL', 'BUY', 'BUY', 'SELL', 'BUY', 'SELL', 'BUY', 'HOLD', 'SELL', 'BUY', 'HOLD', 'BUY', 'SELL', 'BUY', 'HOLD', 'BUY', 'BUY'],
  'aggressive-breakout': ['BUY', 'BUY', 'HOLD', 'HOLD', 'HOLD', 'BUY', 'BUY', 'SELL', 'BUY', 'BUY', 'BUY', 'HOLD', 'HOLD', 'BUY', 'BUY', 'BUY', 'BUY', 'BUY', 'BUY', 'HOLD', 'BUY', 'BUY', 'HOLD', 'HOLD', 'BUY', 'BUY', 'BUY', 'SELL', 'BUY', 'BUY', 'BUY', 'HOLD', 'BUY', 'BUY', 'BUY', 'HOLD'],
  'memory-auditor': ['BUY', 'HOLD', 'HOLD', 'HOLD', 'BUY', 'HOLD', 'HOLD', 'HOLD', 'HOLD', 'HOLD', 'HOLD', 'HOLD', 'HOLD', 'HOLD', 'HOLD', 'HOLD', 'HOLD', 'HOLD', 'HOLD', 'HOLD', 'HOLD', 'HOLD', 'SELL', 'HOLD', 'HOLD', 'HOLD', 'HOLD', 'HOLD', 'HOLD', 'HOLD', 'HOLD', 'HOLD', 'HOLD', 'HOLD', 'HOLD', 'BUY']
});

// 来源 LLM 真实运行 2026-06-01T13-38-51-040Z_b98e03 — 每轮择一品种（与 suggestedPresetCommodities 对应）
const COMMODITIES_BY_AGENT = Object.freeze({
  'conservative-hedger': ['gold', 'gold', 'gold', 'gold', 'gold', 'gold', 'gold', 'gold', 'gold', 'gold', 'gold', 'gold', 'gold', 'gold', 'gold', 'gold', 'gold', 'gold', 'gold', 'gold', 'gold', 'gold', 'gold', 'gold', 'gold', 'gold', 'gold', 'gold', 'gold', 'gold', 'gold', 'gold', 'gold', 'gold', 'gold', 'gold'],
  'balanced-strategist': ['crude_oil', 'crude_oil', 'crude_oil', 'crude_oil', 'crude_oil', 'crude_oil', 'crude_oil', 'crude_oil', 'crude_oil', 'crude_oil', 'crude_oil', 'crude_oil', 'crude_oil', 'gold', 'soybean', 'crude_oil', 'crude_oil', 'crude_oil', 'gold', 'gold', 'crude_oil', 'crude_oil', 'crude_oil', 'crude_oil', 'crude_oil', 'crude_oil', 'crude_oil', 'gold', 'crude_oil', 'crude_oil', 'gold', 'soybean', 'gold', 'crude_oil', 'soybean', 'crude_oil'],
  'aggressive-breakout': ['gold', 'crude_oil', 'soybean', 'soybean', 'soybean', 'gold', 'crude_oil', 'soybean', 'gold', 'gold', 'soybean', 'soybean', 'soybean', 'gold', 'gold', 'crude_oil', 'crude_oil', 'soybean', 'gold', 'soybean', 'crude_oil', 'crude_oil', 'soybean', 'crude_oil', 'gold', 'crude_oil', 'gold', 'gold', 'crude_oil', 'gold', 'gold', 'soybean', 'gold', 'gold', 'soybean', 'soybean'],
  'memory-auditor': ['gold', 'gold', 'gold', 'gold', 'gold', 'gold', 'gold', 'gold', 'gold', 'gold', 'gold', 'gold', 'gold', 'gold', 'gold', 'gold', 'gold', 'gold', 'gold', 'gold', 'gold', 'gold', 'gold', 'gold', 'gold', 'gold', 'gold', 'gold', 'gold', 'gold', 'gold', 'gold', 'gold', 'gold', 'gold', 'gold']
});

function presetCommodityForRound(agentId, roundIndex) {
  const list = COMMODITIES_BY_AGENT[agentId];
  const commodityId = list?.[roundIndex % ROUNDS.length] ||
    AGENT_PROFILES[agentId]?.commodityBias ||
    'gold';
  return COMMODITIES.find(item => item.id === commodityId) || COMMODITIES[0];
}

const TOOL_BY_STATION = Object.freeze({
  news: { name: '资讯抓取', icon: 'N' },
  memory: { name: '记忆检索', icon: 'M' },
  price: { name: '趋势读取', icon: 'P' },
  risk: { name: '风险校验', icon: 'R' },
  debate: { name: '智能体辩论', icon: 'D' },
  trade: { name: '交易指令', icon: 'T' }
});

const STATION_OFFSET_BY_AGENT = Object.freeze({
  'conservative-hedger': 0,
  'balanced-strategist': 2,
  'aggressive-breakout': 1,
  'memory-auditor': 3
});

const EXPOSURE_SCALE_BY_AGENT = Object.freeze({
  'conservative-hedger': 0.65,
  'balanced-strategist': 0.9,
  'aggressive-breakout': 1.25,
  'memory-auditor': 0.75
});

const TRAINING_TRADE_COUNT = 6;
const PROMPT_SEASON_LENGTH = 3;
const RISK_LIMITS = Object.freeze({
  maxDrawdownPct: 18,
  minConfidence: 40,
  maxExposurePct: 82
});

const SIMULATED_DRAWDOWN_BASE_BY_AGENT = Object.freeze({
  'conservative-hedger': 1.6,
  'balanced-strategist': 2.4,
  'aggressive-breakout': 4.1,
  'memory-auditor': 1.1
});

const SIMULATED_VERSION_RULES = Object.freeze({
  'conservative-hedger': {
    1: ['v1：宏观 risk-off 与金价同向时才试多', '改变仓位前必须得到记忆模块确认'],
    2: ['v2：连亏两笔后强制降仓至基准的一半', '优先引用 2011/2020 避险案例做类比'],
    3: ['v3：测试段前冻结新增规则，只保留回撤护栏']
  },
  'balanced-strategist': {
    1: ['v1：宏观、价格、记忆三因子至少两项一致才调仓', '分批进出，避免单笔满仓'],
    2: ['v2：原油与黄金信号冲突时默认降杠杆', '把最近两轮的亏损案例写入反思样本'],
    3: ['v3：测试段只验证泛化，不再追加规则']
  },
  'aggressive-breakout': {
    1: ['v1：动量与资讯共振时可提前行动', '波动冲击后限制加仓次数'],
    2: ['v2：单日回撤超 3% 时禁止同向加仓', '大豆/原油突破需带成交量确认'],
    3: ['v3：测试段降低杠杆，优先验证止损纪律']
  },
  'memory-auditor': {
    1: ['v1：检索相似失败案例后再给出动作', '质疑拥挤交易与一致预期'],
    2: ['v2：把连续失误模式写入审计清单', '对激进型建议进行反向压力测试'],
    3: ['v3：测试段只做记忆一致性检查，不改核心规则']
  }
});

const SIMULATED_STYLE_DELTA = Object.freeze({
  'conservative-hedger': {
    2: '追加：连续亏损后下一笔仓位减半。',
    3: '追加：测试段前不再增加新约束，专注执行回撤护栏。'
  },
  'balanced-strategist': {
    2: '追加：多品种信号冲突时优先降杠杆。',
    3: '追加：测试段以验证泛化为主，减少规则变更。'
  },
  'aggressive-breakout': {
    2: '追加：单日回撤扩大时禁止同向加仓。',
    3: '追加：测试段降低杠杆，优先验证止损。'
  },
  'memory-auditor': {
    2: '追加：把连续失误模式写入审计清单。',
    3: '追加：测试段只做一致性检查，不改核心规则。'
  }
});

const SIMULATED_SEASON_LESSONS = Object.freeze({
  'conservative-hedger': {
    1: '2016 初流动性冲击：先保本金，等待两个确认信号后再加仓。',
    2: '2016 英退公投后：避险脉冲可持续，但需防利好出尽回落。',
    3: '2017 末税改预期：训练段收官，冻结 prompt 进入测试段验证。'
  },
  'balanced-strategist': {
    1: '2016 初多因子分歧：原油与黄金背离时，降低总杠杆。',
    2: '2016 秋 OPEC 预期：利好兑现前减仓，防止预期反转。',
    3: '2017 末宏观同步：训练段收官，保留得分最高的规则组合。'
  },
  'aggressive-breakout': {
    1: '2016 初反转失败：动量未确认时不要抢先手。',
    2: '2016 秋假突破：资讯高潮后警惕反向波动。',
    3: '2017 末训练收官：把高波动日的失误写入测试段样本。'
  },
  'memory-auditor': {
    1: '2016 初：检索 2015 夏相似失败案例，提示勿追一致预期。',
    2: '2016 秋：OPEC 预期与库存数据冲突时的审计结论。',
    3: '2017 末：汇总训练段失误模式，供测试段对照。'
  }
});

function promptLabelForStage(stage) {
  const n = Number(stage) || 0;
  return n === 0 ? 'prompt' : `promptv${n}`;
}

function promptStageForRoundIndex(roundIndex) {
  if (roundIndex < PROMPT_SEASON_LENGTH) return 0;
  if (roundIndex < TRAINING_TRADE_COUNT) return 1;
  return 2;
}

function seasonForRoundIndex(roundIndex) {
  if (roundIndex < PROMPT_SEASON_LENGTH) return 1;
  if (roundIndex < TRAINING_TRADE_COUNT) return 2;
  return 3;
}

function isPromptIterationRound(roundIndex) {
  return roundIndex === PROMPT_SEASON_LENGTH || roundIndex === TRAINING_TRADE_COUNT;
}

function stablePatchNotes(notes) {
  return [...new Set((Array.isArray(notes) ? notes : []).map(note => String(note).trim()).filter(Boolean))]
    .sort((a, b) => a.localeCompare(b, 'zh-CN'));
}

function normalizePromptText(text) {
  return String(text || '')
    .split('\n')
    .map(line => line.trim())
    .filter(Boolean)
    .join('\n');
}

function hasMeaningfulPromptDiff(previousText, nextText) {
  if (previousText === nextText) return false;
  return normalizePromptText(previousText) !== normalizePromptText(nextText);
}

function extractPromptVersion(text, fallback = null) {
  const match = String(text || '').match(/【提示词版本】(\S+)/);
  if (match) {
    const token = match[1];
    if (token === 'prompt') return 0;
    const v = token.match(/^promptv(\d+)$/);
    if (v) return Number(v[1]);
  }
  return fallback;
}

function buildSimulatedPatchNotes({ agentId, season, previousStrategy = null, extraNotes = [] }) {
  const versionRules = SIMULATED_VERSION_RULES[agentId]?.[season] ||
    [`v${season}：提高与当前市场阶段相似的历史案例权重`];
  const inheritedLlmNotes = Array.isArray(previousStrategy?.patchNotes)
    ? previousStrategy.patchNotes.filter(note =>
      !/^v\d+：/.test(note) &&
      !/^第 \d+ 季：/.test(note) &&
      !/^第\d+轮反思：/.test(note)
    )
    : [];
  const extras = Array.isArray(extraNotes) ? extraNotes : [];
  return stablePatchNotes([...inheritedLlmNotes, ...extras, ...versionRules]);
}

function buildSimulatedMemoryLesson({ agentId, round, roundIndex, previousMemory = null }) {
  if (previousMemory?.lessonSource === 'llm' && previousMemory.lesson) {
    return previousMemory.lesson;
  }
  const profile = AGENT_PROFILES[agentId];
  const season = seasonForRoundIndex(roundIndex);
  const preset = SIMULATED_SEASON_LESSONS[agentId]?.[season];
  if (preset) return preset;
  return `${profile.role}将“${round.regime}”与历史记忆“${round.memory[0]}”进行类比`;
}

function filterMeaningfulIterations(iterations) {
  return (Array.isArray(iterations) ? iterations : []).filter(item =>
    item && hasMeaningfulPromptDiff(item.from, item.to)
  );
}

function buildSimulatedStyle({ agentId, profile, season }) {
  const delta = SIMULATED_STYLE_DELTA[agentId]?.[season];
  return delta ? `${profile.style} ${delta}` : profile.style;
}

function presetSimulatedDrawdown({ agentId, roundIndex, decision }) {
  const base = SIMULATED_DRAWDOWN_BASE_BY_AGENT[agentId] ?? 2;
  const action = decision?.action || 'HOLD';
  const actionBoost = action === 'SELL' ? 1.1 : action === 'BUY' ? 0.6 : 0.15;
  const seasonBump = Math.floor(roundIndex / PROMPT_SEASON_LENGTH) * 0.75;
  return Number((base + roundIndex * 0.38 + actionBoost + seasonBump).toFixed(2));
}

function composePromptText({ profile, strategy, memory }) {
  const style = strategy?.style || profile.style;
  const label = strategy?.promptLabel || promptLabelForStage(strategy?.promptStage ?? 0);
  const lines = [
    `【角色】${profile.role}`,
    profile.mandate ? `【定位】${profile.mandate}` : null,
    `【风格】${style}`,
    `【品种偏好】${resolveCommodity({ profile }).name}（可改选：${COMMODITIES.map(item => item.name).join(' / ')}）`,
    profile.riskFramework ? `【风控框架】${profile.riskFramework}` : null,
    `【提示词版本】${label}`
  ].filter(Boolean);
  if (Array.isArray(profile.decisionPrinciples) && profile.decisionPrinciples.length) {
    lines.push('【决策原则】');
    profile.decisionPrinciples.forEach(note => lines.push(`- ${note}`));
  }
  const notes = stablePatchNotes(strategy?.patchNotes);
  if (notes.length) {
    lines.push('【策略规则】');
    notes.forEach(note => lines.push(`- ${note}`));
  }
  if (memory?.lesson) {
    lines.push(`【记忆教训】${memory.lesson}`);
  }
  return lines.join('\n');
}

function attachPromptState({ profile, strategy, memory, previousStrategy, roundIndex, round }) {
  const promptText = composePromptText({ profile, strategy, memory });
  if (!previousStrategy) {
    return {
      ...strategy,
      basePrompt: promptText,
      promptText,
      promptIterations: []
    };
  }

  const basePrompt = previousStrategy.basePrompt || previousStrategy.promptText || promptText;
  const iterations = filterMeaningfulIterations(previousStrategy.promptIterations);
  const prevText = previousStrategy.promptText || basePrompt;
  const prevStage = previousStrategy.promptStage ?? 0;
  const nextStage = strategy.promptStage ?? promptStageForRoundIndex(roundIndex);

  if (
    isPromptIterationRound(roundIndex) &&
    nextStage > prevStage &&
    hasMeaningfulPromptDiff(prevText, promptText)
  ) {
    const last = iterations[iterations.length - 1];
    const duplicate = last && last.to === promptText && last.roundIndex === roundIndex;
    if (!duplicate) {
      const toLabel = promptLabelForStage(nextStage);
      iterations.push({
        id: toLabel,
        roundIndex,
        date: round?.date || null,
        fromLabel: promptLabelForStage(prevStage),
        toLabel,
        from: prevText,
        to: promptText,
        reason: `完成 3 轮训练 · ${promptLabelForStage(prevStage)} → ${toLabel}`
      });
    }
  }

  return {
    ...strategy,
    basePrompt,
    promptText,
    promptIterations: iterations
  };
}

function buildPromptBoard({ worldState, roundIndex, round, nowMs = Date.now() }) {
  return {
    round: roundIndex,
    date: round?.date || null,
    agents: AGENT_IDS.map(agentId => {
      const agent = worldState.agents?.[agentId];
      const profile = AGENT_PROFILES[agentId];
      const strategy = agent?.strategy || {};
      const basePrompt = strategy.basePrompt ||
        composePromptText({ profile, strategy: { ...strategy, patchNotes: [] }, memory: null });
      const currentPrompt = strategy.promptText || basePrompt;
      return {
        agentId,
        role: profile.role,
        promptStage: strategy.promptStage ?? 0,
        promptLabel: strategy.promptLabel || promptLabelForStage(strategy.promptStage ?? 0),
        promptVersion: strategy.promptVersion || 1,
        basePrompt,
        currentPrompt,
        iterations: filterMeaningfulIterations(strategy.promptIterations)
      };
    }),
    updatedAt: new Date(nowMs).toISOString()
  };
}

function buildRiskSnapshot({ worldState, roundIndex, round, evaluation, nowMs = Date.now() }) {
  const byAgent = evaluation?.byAgent || {};
  const agents = AGENT_IDS.map(agentId => {
    const agent = worldState.agents?.[agentId];
    const profile = AGENT_PROFILES[agentId];
    const rank = byAgent[agentId] || {};
    let drawdown = Number(rank.maxDrawdown ?? agent?.score?.drawdown ?? 0);
    if (
      drawdown === 0 &&
      (agent?.decision?.source === 'simulated' || worldState.meta?.trading?.llm?.status === 'simulated')
    ) {
      drawdown = presetSimulatedDrawdown({ agentId, roundIndex, decision: agent?.decision });
    }
    const confidence = Number(agent?.decision?.confidence ?? 55);
    const action = agent?.decision?.action || 'HOLD';
    const exposureScale = EXPOSURE_SCALE_BY_AGENT[agentId] || 1;
    const exposurePct = action === 'HOLD'
      ? 0
      : Math.round(Math.min(99, exposureScale * confidence * (action === 'SELL' ? 0.85 : 1)));
    let status = '通过';
    let note = '回撤与置信度在控制范围内';
    if (drawdown > RISK_LIMITS.maxDrawdownPct) {
      status = '预警';
      note = `累计回撤 ${drawdown.toFixed(1)}% 超过 ${RISK_LIMITS.maxDrawdownPct}% 阈值`;
    } else if (confidence < RISK_LIMITS.minConfidence) {
      status = '复核';
      note = `决策置信度 ${confidence}% 低于 ${RISK_LIMITS.minConfidence}% 门槛`;
    } else if (exposurePct > RISK_LIMITS.maxExposurePct) {
      status = '限仓';
      note = `敞口估算 ${exposurePct}% 超过 ${RISK_LIMITS.maxExposurePct}% 上限`;
    }
    return {
      agentId,
      role: profile.role,
      drawdown: Number(drawdown.toFixed(2)),
      confidence,
      exposurePct,
      action: agent?.decision?.actionLabel || actionLabel(action),
      symbol: agent?.decision?.symbol || '--',
      status,
      note
    };
  });
  const portfolioAverageDrawdown = Number(
    average(agents.map(item => item.drawdown)).toFixed(2)
  );
  const alertCount = agents.filter(item => item.status !== '通过').length;
  return {
    round: roundIndex,
    date: round?.date || null,
    limits: { ...RISK_LIMITS },
    portfolioAverageDrawdown,
    alertCount,
    summary: alertCount
      ? `${alertCount} 个智能体触发风控复核，组合平均回撤 ${portfolioAverageDrawdown.toFixed(1)}%`
      : `四智能体风控检查通过，组合平均回撤 ${portfolioAverageDrawdown.toFixed(1)}%`,
    agents,
    regimeHint: round?.regime ? String(round.regime).slice(0, 48) : '',
    updatedAt: new Date(nowMs).toISOString()
  };
}

function clampRoundIndex(roundIndex) {
  const numeric = Number.isFinite(roundIndex) ? Math.floor(roundIndex) : 0;
  const wrapped = numeric % ROUNDS.length;
  return wrapped < 0 ? wrapped + ROUNDS.length : wrapped;
}

function rethemeWorld(world) {
  const names = {
    store: '资讯采集台',
    library: '记忆档案馆',
    home_ne: '价格趋势墙',
    home_sw: '风险控制室',
    office: '交易执行门',
    cafe: '策略休息区',
    home_nw: '研究工作室'
  };
  if (!Array.isArray(world?.locations)) return;
  for (const location of world.locations) {
    if (names[location.id]) location.name = names[location.id];
  }
}

function actionLabel(action) {
  return action === 'BUY' ? '买入' : action === 'SELL' ? '卖出' : '观望';
}

function normalizeAction(action) {
  const raw = String(action || '').trim().toUpperCase();
  return raw === 'BUY' || raw === 'SELL' || raw === 'HOLD' ? raw : 'HOLD';
}

function clampConfidence(value) {
  const numeric = Number(value);
  if (!Number.isFinite(numeric)) return 55;
  return Math.max(1, Math.min(99, Math.round(numeric)));
}

function buildDecision({ agentId, round, roundIndex }) {
  const profile = AGENT_PROFILES[agentId];
  const action = ACTIONS_BY_AGENT[agentId][roundIndex % ROUNDS.length];
  const commodity = presetCommodityForRound(agentId, roundIndex);
  const price = round.prices[commodity.id];
  const confidence = Math.max(
    42,
    Math.min(92, 58 + roundIndex * 5 + (action === 'HOLD' ? -6 : 7))
  );
  const exposure =
    action === 'BUY' ? '+1 做多' :
    action === 'SELL' ? '-1 减仓/反手' :
    '空仓观察';

  return {
    action,
    actionLabel: actionLabel(action),
    commodity: commodity.id,
    symbol: commodity.name,
    price,
    confidence,
    source: 'simulated',
    exposure,
    reason: `${actionLabel(action)} ${commodity.name}：价格 ${price}，结合“${round.regime}”资讯、历史相似案例和${profile.role}风险规则后给出该动作。`,
    evidence: [
      round.news[roundIndex % round.news.length],
      `${commodity.name}趋势检查点：${price} ${commodity.unit}`,
      round.memory[(roundIndex + 1) % round.memory.length]
    ]
  };
}

function buildMemory({ agentId, round, roundIndex, previousMemory = null }) {
  const profile = AGENT_PROFILES[agentId];
  const lesson = buildSimulatedMemoryLesson({ agentId, round, roundIndex, previousMemory });
  return {
    archive: profile.commodityBias,
    retrieved: round.memory.map((text, index) => ({
      id: `${agentId}-m${roundIndex}-${index}`,
      date: ROUNDS[Math.max(0, roundIndex - index)]?.date || round.date,
      weight: Number((0.86 - index * 0.13).toFixed(2)),
      text
    })),
    lesson,
    lessonSource: previousMemory?.lessonSource === 'llm' && lesson === previousMemory.lesson
      ? 'llm'
      : 'simulated'
  };
}

function buildStrategy({ agentId, roundIndex, previousStrategy = null }) {
  const profile = AGENT_PROFILES[agentId];
  const inTraining = roundIndex < TRAINING_TRADE_COUNT;
  const season = seasonForRoundIndex(roundIndex);
  const stage = promptStageForRoundIndex(roundIndex);
  const flushPending = isPromptIterationRound(roundIndex);
  const pendingNotes = flushPending
    ? (previousStrategy?.pendingLlmPatchNotes || [])
    : [];

  if (!inTraining && previousStrategy) {
    if (roundIndex === TRAINING_TRADE_COUNT && (previousStrategy.promptStage ?? 0) < 2) {
      const finalSeason = 3;
      return {
        ...previousStrategy,
        promptStage: 2,
        promptLabel: promptLabelForStage(2),
        promptVersion: finalSeason,
        style: buildSimulatedStyle({ agentId, profile, season: finalSeason }),
        patchNotes: buildSimulatedPatchNotes({
          agentId,
          season: finalSeason,
          previousStrategy,
          extraNotes: pendingNotes
        }),
        pendingLlmPatchNotes: [],
        nextMutation: '测试段冻结 prompt，只验证泛化'
      };
    }
    return {
      ...previousStrategy,
      nextMutation: '测试段冻结 prompt，只验证泛化'
    };
  }

  return {
    promptStage: stage,
    promptLabel: promptLabelForStage(stage),
    promptVersion: season,
    style: buildSimulatedStyle({ agentId, profile, season }),
    patchNotes: buildSimulatedPatchNotes({
      agentId,
      season,
      previousStrategy,
      extraNotes: pendingNotes
    }),
    pendingLlmPatchNotes: flushPending ? [] : (previousStrategy?.pendingLlmPatchNotes || []),
    nextMutation: isPromptIterationRound(roundIndex + 1)
      ? '即将进入下一轮 prompt 迭代'
      : '本版本 prompt 保持不变，继续收集交易样本'
  };
}

function stationFor(agentId, roundIndex) {
  const agentOffset = STATION_OFFSET_BY_AGENT[agentId] ?? 0;
  return STATIONS[(roundIndex + agentOffset) % STATIONS.length];
}

function roundWithLocalPrices(round, loader) {
  const prices = { ...round.prices };
  const realPrices = {};
  let realCount = 0;

  if (loader?.isLoaded?.()) {
    for (const commodity of COMMODITIES) {
      const price = loader.getPriceAtDate(commodity.id, round.date);
      if (Number.isFinite(price)) {
        prices[commodity.id] = Number(price);
        realPrices[commodity.id] = Number(price);
        realCount += 1;
      }
    }
  }

  return {
    ...round,
    prices,
    dataSource:
      realCount === COMMODITIES.length ? 'local-real' :
      realCount > 0 ? 'mixed-real-scenario' :
      'scenario',
    realPrices
  };
}

function getHistoricalRounds() {
  try {
    const loader = getLocalDataLoader();
    return ROUNDS.map(round => roundWithLocalPrices(round, loader));
  } catch (error) {
    console.warn('[trading-demo] historical data unavailable:', error.message);
    return ROUNDS.map(round => ({ ...round, prices: { ...round.prices }, dataSource: 'scenario', realPrices: {} }));
  }
}

function clampScore(value) {
  return Number(Math.max(-18, Math.min(22, value)).toFixed(2));
}

function calculateTradeScore({ action, currentPrice, nextPrice, exposureScale }) {
  if (!Number.isFinite(currentPrice) || !Number.isFinite(nextPrice)) return 0;
  const priceMovePct = ((nextPrice - currentPrice) / Math.max(1, Math.abs(currentPrice))) * 100;
  if (action === 'HOLD') {
    return clampScore(Math.abs(priceMovePct) < 3 ? 0.6 : -Math.abs(priceMovePct) * 0.08);
  }
  const direction = action === 'SELL' ? -1 : 1;
  return clampScore(direction * priceMovePct * exposureScale);
}

function average(values) {
  const nums = values.filter(Number.isFinite);
  if (!nums.length) return 0;
  return nums.reduce((sum, value) => sum + value, 0) / nums.length;
}

function buildAgentActionDistribution(trades) {
  const distribution = { BUY: 0, SELL: 0, HOLD: 0 };
  for (const trade of trades) {
    if (Object.prototype.hasOwnProperty.call(distribution, trade.action)) {
      distribution[trade.action] += 1;
    }
  }
  return distribution;
}

function buildFailurePoints(trades) {
  return trades
    .filter(trade => Number(trade.scoreDelta || 0) < 0)
    .slice()
    .sort((a, b) => Number(a.scoreDelta || 0) - Number(b.scoreDelta || 0))
    .slice(0, 3)
    .map(trade => ({
      round: Number(trade.index || 0) + 1,
      date: trade.date,
      exitDate: trade.exitDate,
      regime: trade.regime,
      action: trade.action,
      actionLabel: trade.actionLabel || actionLabel(trade.action),
      symbol: trade.symbol,
      scoreDelta: Number(Number(trade.scoreDelta || 0).toFixed(2)),
      entry: trade.entry,
      exit: trade.exit,
      reason: `第 ${Number(trade.index || 0) + 1} 轮 ${trade.actionLabel || actionLabel(trade.action)} ${trade.symbol} 后记 ${Number(trade.scoreDelta || 0).toFixed(2)} 分。`
    }));
}

function buildFailureSummary({ role, trades, failures, worstTrade }) {
  if (!trades.length) return `${role} 尚未形成可评分交易，等待更多轮次。`;
  if (!failures.length) return `${role} 当前没有亏损交易，继续累计后续轮次表现。`;
  return `${role} 累计 ${failures.length}/${trades.length} 轮失分，最大失分来自第 ${Number(worstTrade.index || 0) + 1} 轮 ${worstTrade.actionLabel || actionLabel(worstTrade.action)} ${worstTrade.symbol}。`;
}

function buildRepairPlan({ item, failures }) {
  const plans = [];
  if (failures.length > 0) plans.push('把最大失分回合加入记忆检索，遇到相似价格结构时先降权。');
  if (Number(item.maxDrawdown || 0) > 8) plans.push('降低连续同向开仓权重，先控制回撤再追求收益。');
  if (Number(item.testScore || 0) < Number(item.trainingScore || 0)) plans.push('提高测试段样本权重，避免只适配前段行情。');
  if (!plans.length) plans.push('保留当前策略骨架，继续累计样本后再调整 prompt。');
  return plans.slice(0, 2).join(' ');
}

function buildAgentBreakdown(item) {
  const trades = Array.isArray(item.trades) ? item.trades : [];
  const failures = trades.filter(trade => Number(trade.scoreDelta || 0) < 0);
  const wins = trades.filter(trade => Number(trade.scoreDelta || 0) > 0);
  const worstTrade = failures
    .slice()
    .sort((a, b) => Number(a.scoreDelta || 0) - Number(b.scoreDelta || 0))[0] || null;
  const bestTrade = trades
    .slice()
    .sort((a, b) => Number(b.scoreDelta || 0) - Number(a.scoreDelta || 0))[0] || null;

  return {
    agentId: item.agentId,
    role: item.role,
    style: item.style,
    symbol: item.symbol,
    totalScore: Number(item.totalScore || 0),
    rawScore: Number(item.rawScore ?? item.totalScore ?? 0),
    trainingScore: Number(item.trainingScore || 0),
    testScore: Number(item.testScore || 0),
    maxDrawdown: Number(item.maxDrawdown || 0),
    hitRate: Number(item.hitRate || 0),
    tradeCount: trades.length,
    winCount: wins.length,
    lossCount: failures.length,
    failureRate: trades.length ? Number(((failures.length / trades.length) * 100).toFixed(1)) : 0,
    actionDistribution: buildAgentActionDistribution(trades),
    bestTrade: bestTrade ? {
      round: Number(bestTrade.index || 0) + 1,
      actionLabel: bestTrade.actionLabel || actionLabel(bestTrade.action),
      symbol: bestTrade.symbol,
      scoreDelta: Number(Number(bestTrade.scoreDelta || 0).toFixed(2))
    } : null,
    worstTrade: worstTrade ? {
      round: Number(worstTrade.index || 0) + 1,
      actionLabel: worstTrade.actionLabel || actionLabel(worstTrade.action),
      symbol: worstTrade.symbol,
      scoreDelta: Number(Number(worstTrade.scoreDelta || 0).toFixed(2))
    } : null,
    failurePoints: buildFailurePoints(trades),
    failureSummary: buildFailureSummary({ role: item.role, trades, failures, worstTrade }),
    repairPlan: buildRepairPlan({ item, failures })
  };
}

function buildEvaluationAnalysis({ rankings, completedTradeCount, rounds }) {
  const ranked = Array.isArray(rankings) ? rankings.slice() : [];
  const best = ranked[0] || null;
  const worst = ranked[ranked.length - 1] || null;
  const allTrades = ranked.flatMap(item => Array.isArray(item.trades) ? item.trades : []);
  const actionDistribution = { BUY: 0, SELL: 0, HOLD: 0 };
  for (const trade of allTrades) {
    if (Object.prototype.hasOwnProperty.call(actionDistribution, trade.action)) {
      actionDistribution[trade.action] += 1;
    }
  }

  const topTrades = Array.isArray(best?.trades) ? best.trades : [];
  const topEquityCurve = [
    {
      date: rounds[0]?.date || '--',
      value: 0,
      phase: 'start',
      label: '起点'
    },
    ...topTrades.map(trade => ({
      date: trade.exitDate || trade.date,
      value: Number(Number(trade.equity || 0).toFixed(2)),
      phase: trade.phase,
      action: trade.action,
      scoreDelta: Number(Number(trade.scoreDelta || 0).toFixed(2))
    }))
  ];

  const trainingLeaders = ranked
    .slice()
    .sort((a, b) => Number(b.trainingScore || 0) - Number(a.trainingScore || 0));
  const testLeaders = ranked
    .slice()
    .sort((a, b) => Number(b.testScore || 0) - Number(a.testScore || 0));
  const averageHitRate = Number(average(ranked.map(item => Number(item.hitRate))).toFixed(1));
  const averageDrawdown = Number(average(ranked.map(item => Number(item.maxDrawdown))).toFixed(2));
  const alphaSpread = Number((Number(best?.totalScore || 0) - Number(worst?.totalScore || 0)).toFixed(2));
  const bestTrain = trainingLeaders[0] || best;
  const bestTest = testLeaders[0] || best;
  const worstDrawdown = ranked
    .slice()
    .sort((a, b) => Number(b.maxDrawdown || 0) - Number(a.maxDrawdown || 0))[0] || worst;

  const conclusions = [];
  if (best) {
    conclusions.push(`${best.role}当前综合得分最高。`);
  }
  if (bestTrain && bestTest) {
    conclusions.push(`训练段优势来自${bestTrain.role}，测试段表现最好的是${bestTest.role}，用于判断策略是否泛化。`);
  }
  if (worstDrawdown) {
    conclusions.push(`${worstDrawdown.role}最大回撤为 ${Number(worstDrawdown.maxDrawdown || 0).toFixed(2)}，是后续 prompt 修正的主要风险样本。`);
  }

  return {
    sampleCount: completedTradeCount,
    completedRoundCount: completedTradeCount,
    totalScenarioRounds: Math.max(0, rounds.length - 1),
    totalAgentDecisions: allTrades.length,
    trainingTrades: Math.min(completedTradeCount, TRAINING_TRADE_COUNT),
    testTrades: Math.max(0, completedTradeCount - TRAINING_TRADE_COUNT),
    agentCount: ranked.length,
    scope: `累计统计至第 ${completedTradeCount} 轮，共 ${allTrades.length} 条智能体交易决策。`,
    bestAgentId: best?.agentId || null,
    bestRole: best?.role || null,
    worstAgentId: worst?.agentId || null,
    worstRole: worst?.role || null,
    averageHitRate,
    averageDrawdown,
    alphaSpread,
    actionDistribution,
    scoreBars: ranked.map(item => ({
      agentId: item.agentId,
      role: item.role,
      symbol: item.symbol,
      totalScore: Number(item.totalScore || 0),
      trainingScore: Number(item.trainingScore || 0),
      testScore: Number(item.testScore || 0),
      maxDrawdown: Number(item.maxDrawdown || 0),
      hitRate: Number(item.hitRate || 0),
      tradeCount: Array.isArray(item.trades) ? item.trades.length : 0,
      lossCount: Array.isArray(item.trades) ? item.trades.filter(trade => Number(trade.scoreDelta || 0) < 0).length : 0
    })),
    agentBreakdowns: ranked.map(buildAgentBreakdown),
    topEquityCurve,
    conclusions
  };
}

function scoreAgent({ agentId, rounds, completedTradeCount }) {
  const profile = AGENT_PROFILES[agentId];
  const exposureScale = EXPOSURE_SCALE_BY_AGENT[agentId] || 1;
  const trades = [];
  let equity = 0;
  let peak = 0;
  let maxDrawdown = 0;

  for (let i = 0; i < completedTradeCount; i += 1) {
    const current = rounds[i];
    const next = rounds[i + 1];
    if (!current || !next) continue;
    const action = ACTIONS_BY_AGENT[agentId][i % ROUNDS.length];
    const commodity = presetCommodityForRound(agentId, i);
    const currentPrice = Number(current.prices?.[commodity.id]);
    const nextPrice = Number(next.prices?.[commodity.id]);
    const delta = calculateTradeScore({ action, currentPrice, nextPrice, exposureScale });
    equity = Number((equity + delta).toFixed(2));
    peak = Math.max(peak, equity);
    maxDrawdown = Math.max(maxDrawdown, Number((peak - equity).toFixed(2)));
    trades.push({
      index: i,
      phase: i < TRAINING_TRADE_COUNT ? 'training' : 'test',
      date: current.date,
      exitDate: next.date,
      regime: current.regime,
      action,
      actionLabel: actionLabel(action),
      symbol: commodity.name,
      commodity: commodity.id,
      entry: currentPrice,
      exit: nextPrice,
      scoreDelta: delta,
      equity
    });
  }

  const trainingScore = trades
    .filter(item => item.phase === 'training')
    .reduce((sum, item) => sum + item.scoreDelta, 0);
  const testScore = trades
    .filter(item => item.phase === 'test')
    .reduce((sum, item) => sum + item.scoreDelta, 0);
  const totalScore = trades.reduce((sum, item) => sum + item.scoreDelta, 0);
  const evaluatedTrades = trades.length || 1;
  const hitRate = trades.filter(item => item.scoreDelta > 0).length / evaluatedTrades;
  const summaryCommodity = trades.length
    ? presetCommodityForRound(agentId, trades[trades.length - 1].index)
    : presetCommodityForRound(agentId, 0);

  return {
    agentId,
    role: profile.role,
    style: profile.style,
    symbol: summaryCommodity.name,
    commodity: summaryCommodity.id,
    totalScore: Number(totalScore.toFixed(2)),
    trainingScore: Number(trainingScore.toFixed(2)),
    testScore: Number(testScore.toFixed(2)),
    maxDrawdown: Number(maxDrawdown.toFixed(2)),
    hitRate: Number((hitRate * 100).toFixed(1)),
    trades,
    lastTrade: trades[trades.length - 1] || null
  };
}

// Build evaluation based on actual LLM decisions stored in agent.decision
function buildLlmEvaluation({ worldState, rounds, roundIndex }) {
  const completedTradeCount = Math.max(1, Math.min(roundIndex + 1, rounds.length - 1));
  const ledger = Array.isArray(worldState.meta?.trading?.llmDecisionLedger)
    ? worldState.meta.trading.llmDecisionLedger
    : [];
  const ledgerByRound = new Map();
  for (const entry of ledger) {
    if (!entry || !entry.agentId || !Number.isFinite(Number(entry.roundIndex))) continue;
    ledgerByRound.set(`${entry.agentId}:${Number(entry.roundIndex)}`, entry);
  }
  const rankings = AGENT_IDS.map(agentId => {
    const profile = AGENT_PROFILES[agentId];
    const defaultCommodity = COMMODITIES.find(item => item.id === profile.commodityBias) || COMMODITIES[0];
    const exposureScale = EXPOSURE_SCALE_BY_AGENT[agentId] || 1;
    const trades = [];
    let equity = 0;
    let peak = 0;
    let maxDrawdown = 0;

    for (let i = 0; i < completedTradeCount; i += 1) {
      const current = rounds[i];
      const next = rounds[i + 1];
      if (!current || !next) continue;
      const ledgerEntry = ledgerByRound.get(`${agentId}:${i}`);
      const commodity = ledgerEntry
        ? (COMMODITIES.find(item =>
          item.id === ledgerEntry.commodity ||
          item.symbol === ledgerEntry.commodity ||
          item.symbol === ledgerEntry.symbol ||
          item.name === ledgerEntry.symbol ||
          item.name === ledgerEntry.commodityLabel
        ) || defaultCommodity)
        : presetCommodityForRound(agentId, i);
      const action = ledgerEntry
        ? normalizeAction(ledgerEntry.action)
        : ACTIONS_BY_AGENT[agentId][i % ROUNDS.length];
      const currentPrice = Number(current.prices?.[commodity.id]);
      const nextPrice = Number(next.prices?.[commodity.id]);
      if (!Number.isFinite(currentPrice) || !Number.isFinite(nextPrice)) continue;

      const delta = calculateTradeScore({ action, currentPrice, nextPrice, exposureScale });
      equity = Number((equity + delta).toFixed(2));
      peak = Math.max(peak, equity);
      maxDrawdown = Math.max(maxDrawdown, Number((peak - equity).toFixed(2)));

      trades.push({
        index: i,
        phase: i < TRAINING_TRADE_COUNT ? 'training' : 'test',
        date: current.date,
        exitDate: next.date,
        regime: current.regime,
        action,
        actionLabel: actionLabel(action),
        symbol: commodity.name,
        commodity: commodity.id,
        entry: currentPrice,
        exit: nextPrice,
        scoreDelta: delta,
        equity,
        confidence: ledgerEntry?.confidence,
        source: ledgerEntry?.source || 'preset'
      });
    }
    
    const trainingScore = trades.filter(item => item.phase === 'training').reduce((sum, item) => sum + item.scoreDelta, 0);
    const testScore = trades.filter(item => item.phase === 'test').reduce((sum, item) => sum + item.scoreDelta, 0);
    const totalScore = trades.reduce((sum, item) => sum + item.scoreDelta, 0);
    const evaluatedTrades = trades.length || 1;
    const hitRate = trades.filter(item => item.scoreDelta > 0).length / evaluatedTrades;

    return {
      agentId,
      role: profile.role,
      style: profile.style,
      symbol: trades[trades.length - 1]?.symbol || defaultCommodity.name,
      commodity: trades[trades.length - 1]?.commodity || defaultCommodity.id,
      totalScore: Number(totalScore.toFixed(2)),
      trainingScore: Number(trainingScore.toFixed(2)),
      testScore: Number(testScore.toFixed(2)),
      maxDrawdown: Number(maxDrawdown.toFixed(2)),
      hitRate: Number((hitRate * 100).toFixed(1)),
      trades,
      lastTrade: trades[trades.length - 1] || null,
      rawScore: totalScore,
      rawTrainingScore: trainingScore,
      rawTestScore: testScore
    };
  }).sort((a, b) => b.totalScore - a.totalScore);

  // Normalize scores (subtract mean)
  const meanTotal = rankings.reduce((sum, item) => sum + item.totalScore, 0) / rankings.length;
  const meanTraining = rankings.reduce((sum, item) => sum + item.trainingScore, 0) / rankings.length;
  const meanTest = rankings.reduce((sum, item) => sum + item.testScore, 0) / rankings.length;
  rankings.forEach(item => {
    item.totalScore = Number((item.totalScore - meanTotal).toFixed(2));
    item.trainingScore = Number((item.trainingScore - meanTraining).toFixed(2));
    item.testScore = Number((item.testScore - meanTest).toFixed(2));
  });
  rankings.sort((a, b) => b.totalScore - a.totalScore);

  const hasLedgerTrades = rankings.some(item => Array.isArray(item.trades) && item.trades.length > 0);
  const method = hasLedgerTrades
    ? (ledger.some(entry => entry?.source === 'llm')
      ? '基于模型真实决策的累计评分（含 LLM 回退轮次的预设决策补全）'
      : '基于模型真实决策的累计评分')
    : '累计评分：价格曲线固定，智能体的买入/卖出/观望时间点决定收益；面板显示相对 alpha 分，训练段用于修正 prompt，测试段用于验证泛化。';

  return {
    byAgent: Object.fromEntries(rankings.map(item => [item.agentId, item])),
    rankings,
    method,
    dataSource: hasLedgerTrades ? '模型累计决策' : (rounds.some(round => round.dataSource === 'local-real' || round.dataSource === 'mixed-real-scenario')
      ? '真实价格曲线'
      : '内置情景价格'),
    completedTradeCount,
    trainingWindow: `${rounds[0]?.date || '--'} → ${rounds[Math.min(TRAINING_TRADE_COUNT, rounds.length - 1)]?.date || '--'}`,
    testWindow: `${rounds[Math.min(TRAINING_TRADE_COUNT, rounds.length - 1)]?.date || '--'} → ${rounds[rounds.length - 1]?.date || '--'}`,
    analysis: buildEvaluationAnalysis({ rankings, completedTradeCount, rounds })
  };
}

function buildDebateRound({ worldState, roundIndex, round, nowMs = Date.now() }) {
  const entries = AGENT_IDS.map(agentId => {
    const agent = worldState.agents?.[agentId];
    const profile = AGENT_PROFILES[agentId];
    const decision = agent?.decision;
    if (!decision) return null;
    return {
      agentId,
      role: profile?.role || agentId,
      action: decision.action,
      actionLabel: decision.actionLabel || actionLabel(decision.action),
      symbol: decision.symbol,
      commodity: decision.commodity,
      confidence: decision.confidence,
      reason: decision.reason || '',
      evidence: Array.isArray(decision.evidence) ? decision.evidence.slice(0, 5) : [],
      source: decision.source || 'simulated',
      stance: 'pending'
    };
  }).filter(Boolean);

  if (!entries.length) {
    return {
      round: roundIndex,
      date: round?.date || null,
      summary: '等待各智能体提交论点…',
      entries: [],
      consensus: null,
      dissent: [],
      updatedAt: new Date(nowMs).toISOString()
    };
  }

  const actionCounts = {};
  for (const entry of entries) {
    const key = `${entry.action}:${entry.commodity || entry.symbol || ''}`;
    actionCounts[key] = (actionCounts[key] || 0) + 1;
  }
  const ranked = Object.entries(actionCounts).sort((a, b) => b[1] - a[1]);
  const [consensusKey, supportCount] = ranked[0];
  const [consensusAction] = consensusKey.split(':');

  for (const entry of entries) {
    const key = `${entry.action}:${entry.commodity || entry.symbol || ''}`;
    if (key === consensusKey) entry.stance = 'support';
    else if (entry.action === consensusAction) entry.stance = 'neutral';
    else entry.stance = 'oppose';
  }

  const dissent = entries
    .filter(entry => entry.stance === 'oppose')
    .map(entry => ({
      agentId: entry.agentId,
      role: entry.role,
      action: entry.actionLabel,
      symbol: entry.symbol,
      summary: (entry.reason || '').slice(0, 120)
    }));

  const summary = dissent.length
    ? `第 ${roundIndex + 1} 轮：${supportCount}/${entries.length} 位智能体倾向${actionLabel(consensusAction)}，${dissent.map(item => item.role).join('、')}提出异议。`
    : `第 ${roundIndex + 1} 轮：四智能体就「${actionLabel(consensusAction)}」方向形成共识。`;

  return {
    round: roundIndex,
    date: round?.date || null,
    regime: round?.regime || null,
    summary,
    entries,
    consensus: {
      action: consensusAction,
      actionLabel: actionLabel(consensusAction),
      supportCount,
      total: entries.length
    },
    dissent,
    updatedAt: new Date(nowMs).toISOString()
  };
}

function buildExecutionGate({ worldState, roundIndex, round, nowMs = Date.now() }) {
  const orders = AGENT_IDS.map(agentId => {
    const agent = worldState.agents?.[agentId];
    const profile = AGENT_PROFILES[agentId];
    const decision = agent?.decision;
    if (!decision) {
      return {
        agentId,
        role: profile?.role || agentId,
        status: 'pending',
        action: null,
        symbol: null,
        confidence: null
      };
    }
    const drawdown = Number(agent.score?.drawdown ?? 0);
    const confidence = Number(decision.confidence ?? 0);
    const riskOk = drawdown <= 25;
    const confOk = confidence >= 40;
    const approved = riskOk && confOk;
    return {
      agentId,
      role: profile?.role || agentId,
      status: approved ? 'approved' : 'held',
      action: decision.actionLabel || actionLabel(decision.action),
      rawAction: decision.action,
      symbol: decision.symbol,
      commodity: decision.commodity,
      confidence: decision.confidence,
      price: decision.price,
      source: decision.source || 'simulated',
      note: approved
        ? '风险与置信度检查通过，指令已放行。'
        : '置信度或回撤未达门槛，暂挂起复核。'
    };
  });

  const approved = orders.filter(order => order.status === 'approved').length;
  const pending = orders.filter(order => order.status === 'pending').length;
  const held = orders.filter(order => order.status === 'held').length;
  const gateStatus = pending > 0 ? 'pending' : approved === orders.length ? 'executed' : 'partial';
  const summary = pending
    ? `交易执行门等待 ${pending} 条指令…`
    : `交易执行门已放行 ${approved}/${orders.length} 条指令${held ? `，${held} 条挂起` : ''}。`;

  return {
    round: roundIndex,
    date: round?.date || null,
    gateStatus,
    summary,
    orders,
    metrics: { approved, pending, held, total: orders.length },
    updatedAt: new Date(nowMs).toISOString()
  };
}

function buildEvaluation({ rounds, roundIndex }) {
  const completedTradeCount = Math.max(1, Math.min(roundIndex + 1, rounds.length - 1));
  const rankings = AGENT_IDS
    .map(agentId => scoreAgent({ agentId, rounds, completedTradeCount }))
    .sort((a, b) => b.totalScore - a.totalScore);
  const meanTotal = rankings.reduce((sum, item) => sum + item.totalScore, 0) / rankings.length;
  const meanTraining = rankings.reduce((sum, item) => sum + item.trainingScore, 0) / rankings.length;
  const meanTest = rankings.reduce((sum, item) => sum + item.testScore, 0) / rankings.length;
  rankings.forEach(item => {
    item.rawScore = item.totalScore;
    item.rawTrainingScore = item.trainingScore;
    item.rawTestScore = item.testScore;
    item.totalScore = Number((item.totalScore - meanTotal).toFixed(2));
    item.trainingScore = Number((item.trainingScore - meanTraining).toFixed(2));
    item.testScore = Number((item.testScore - meanTest).toFixed(2));
  });
  rankings.sort((a, b) => b.totalScore - a.totalScore);
  const byAgent = Object.fromEntries(rankings.map(item => [item.agentId, item]));
  const dataSource = rounds.some(round => round.dataSource === 'local-real' || round.dataSource === 'mixed-real-scenario')
    ? '真实价格曲线'
    : '内置情景价格';

  return {
    method: '累计评分：价格曲线固定，智能体的买入/卖出/观望时间点决定收益；面板显示相对 alpha 分，训练段用于修正 prompt，测试段用于验证泛化。',
    dataSource,
    completedTradeCount,
    trainingWindow: `${rounds[0]?.date || '--'} → ${rounds[Math.min(TRAINING_TRADE_COUNT, rounds.length - 1)]?.date || '--'}`,
    testWindow: `${rounds[Math.min(TRAINING_TRADE_COUNT, rounds.length - 1)]?.date || '--'} → ${rounds[rounds.length - 1]?.date || '--'}`,
    rankings,
    byAgent,
    analysis: buildEvaluationAnalysis({ rankings, completedTradeCount, rounds })
  };
}

function applyTradingGameRound({ worldState, roundIndex = 0, nowMs = Date.now(), skipPresetScoring = false }) {
  ensureWorldState(worldState);
  rethemeWorld(worldState.world);

  const idx = clampRoundIndex(roundIndex);
  const historicalRounds = getHistoricalRounds();
  const round = historicalRounds[idx];
  const previousLlmLedger = Array.isArray(worldState.meta?.trading?.llmDecisionLedger)
    ? worldState.meta.trading.llmDecisionLedger.slice()
    : [];
  
  const baselineEvaluation = buildEvaluation({ rounds: historicalRounds, roundIndex: idx });
  const evaluation = skipPresetScoring
    ? {
      ...baselineEvaluation,
      method: 'LLM真实决策生成中：先显示累计策略基线统计；模型返回后自动覆盖为真实模型决策评分。',
      dataSource: `${baselineEvaluation.dataSource} · LLM待返回`
    }
    : baselineEvaluation;
  const timeline = historicalRounds.slice(0, idx + 1).map((entry, entryIndex) => ({
    index: entryIndex,
    date: entry.date,
    regime: entry.regime,
    event: entry.news[0],
    prices: { ...entry.prices },
    score: entry.scoreboard,
    dataSource: entry.dataSource
  }));

  worldState.meta.trading = {
    mode: 'futures-agent-simulation',
    currentRound: idx,
    currentDate: round.date,
    regime: round.regime,
    commodities: COMMODITIES,
    prices: round.prices,
    news: round.news,
    dataSource: round.dataSource,
    priceSource: evaluation.dataSource,
    evaluation,
    timeline,
    llmDecisionLedger: previousLlmLedger,
    llm: {
      enabled: false,
      provider: null,
      model: DEFAULT_LLM_MODEL,
      status: 'simulated'
    },
    updatedAt: new Date(nowMs).toISOString()
  };
  worldState.meta.sessions = {
    enabled: false,
    sessionsObserved: AGENT_IDS.length,
    lastSnapshotAt: new Date(nowMs).toISOString()
  };

  for (const agentId of AGENT_IDS) {
    const profile = AGENT_PROFILES[agentId];
    const station = stationFor(agentId, idx);
    const previousAgent = worldState.agents?.[agentId] || null;
    const decision = skipPresetScoring ? null : buildDecision({ agentId, round, roundIndex: idx });
    const memory = buildMemory({
      agentId,
      round,
      roundIndex: idx,
      previousMemory: previousAgent?.memory || null
    });
    const strategy = attachPromptState({
      profile,
      strategy: buildStrategy({
        agentId,
        roundIndex: idx,
        previousStrategy: previousAgent?.strategy || null
      }),
      memory,
      previousStrategy: previousAgent?.strategy || null,
      roundIndex: idx,
      round
    });
    const scoreSummary = evaluation ? evaluation.byAgent[agentId] : null;

    const agent = {
      id: agentId,
      sessionId: agentId,
      name: profile.role,
      role: profile.role,
      zone: station.id,
      activity: '决策中',
      status: 'Working',
      lastEventAt: new Date(nowMs).toISOString(),
      model: profile.model,
      tool: decision ? {
        ...TOOL_BY_STATION[station.id],
        inputPreview: `${decision.symbol} ${round.date}`
      } : TOOL_BY_STATION[station.id],
      decision,
      memory,
      strategy,
      score: {
        total: scoreSummary?.totalScore ?? 0,
        training: scoreSummary?.trainingScore ?? 0,
        test: scoreSummary?.testScore ?? 0,
        drawdown: scoreSummary?.maxDrawdown ?? 0,
        hitRate: scoreSummary?.hitRate ?? 0
      },
      lastAssistantSnippet: decision ? `${decision.reason} 记忆模块提示：${memory.retrieved[0].text}` : `等待LLM决策... 记忆模块提示：${memory.retrieved[0].text}`
    };
    worldState.agents[agentId] = agent;
  }

  worldState.meta.trading.debate = buildDebateRound({ worldState, roundIndex: idx, round, nowMs });
  worldState.meta.trading.execution = buildExecutionGate({ worldState, roundIndex: idx, round, nowMs });
  worldState.meta.trading.risk = buildRiskSnapshot({
    worldState,
    roundIndex: idx,
    round,
    evaluation,
    nowMs
  });
  worldState.meta.trading.promptBoard = buildPromptBoard({ worldState, roundIndex: idx, round, nowMs });

  return worldState;
}

function commodityForDecision(profile, decision) {
  return resolveCommodity({ profile, decision });
}

function applyLlmDecisionToAgent({
  worldState,
  agentId,
  llmDecision,
  round,
  roundIndex = 0,
  nowMs = Date.now(),
  model,
  provider
}) {
  const agent = worldState.agents?.[agentId];
  const profile = AGENT_PROFILES[agentId];
  if (!agent || !profile || !llmDecision) return false;

  const action = normalizeAction(llmDecision.action);
  const commodity = commodityForDecision(profile, llmDecision);
  const price = round.prices[commodity.id];
  const confidence = clampConfidence(llmDecision.confidence);
  const evidence = Array.isArray(llmDecision.evidence) && llmDecision.evidence.length
    ? llmDecision.evidence.map(item => String(item)).slice(0, 5)
    : (Array.isArray(agent.decision?.evidence) ? agent.decision.evidence : []);
  const reason = String(llmDecision.reason || '').trim() ||
    `${actionLabel(action)} ${commodity.name}：真实模型结合资讯、价格走势和记忆后给出该动作。`;

  const resolvedModel = llmDecision.model || model || agent.model || DEFAULT_LLM_MODEL;
  const resolvedProvider = llmDecision.provider || provider || 'llm';
  agent.model = resolvedModel;
  agent.decision = {
    ...(agent.decision || {}),
    action,
    actionLabel: actionLabel(action),
    commodity: commodity.id,
    symbol: commodity.name,
    price,
    confidence,
    source: 'llm',
    provider: resolvedProvider,
    model: resolvedModel,
    reason,
    evidence,
    usage: llmDecision.usage || null,
    attempts: Array.isArray(llmDecision.attempts) ? llmDecision.attempts : []
  };
  agent.memory = {
    ...agent.memory,
    lesson: String(llmDecision.memoryLesson || '').trim() || agent.memory.lesson,
    lessonSource: String(llmDecision.memoryLesson || '').trim() ? 'llm' : (agent.memory.lessonSource || 'simulated')
  };
  if (Array.isArray(llmDecision.strategyPatchNotes) && llmDecision.strategyPatchNotes.length > 0) {
    const idx = clampRoundIndex(roundIndex);
    const inTraining = idx < TRAINING_TRADE_COUNT;
    if (inTraining && isPromptIterationRound(idx)) {
      const pending = Array.isArray(agent.strategy?.pendingLlmPatchNotes)
        ? agent.strategy.pendingLlmPatchNotes
        : [];
      const merged = [
        ...(Array.isArray(agent.strategy?.patchNotes) ? agent.strategy.patchNotes : []),
        ...pending,
        ...llmDecision.strategyPatchNotes.map(item => String(item)).slice(0, 5)
      ];
      agent.strategy = {
        ...agent.strategy,
        patchNotes: stablePatchNotes(merged).slice(0, 10),
        pendingLlmPatchNotes: []
      };
    } else if (inTraining) {
      const pending = Array.isArray(agent.strategy?.pendingLlmPatchNotes)
        ? agent.strategy.pendingLlmPatchNotes.slice()
        : [];
      agent.strategy = {
        ...agent.strategy,
        pendingLlmPatchNotes: stablePatchNotes([
          ...pending,
          ...llmDecision.strategyPatchNotes.map(item => String(item)).slice(0, 5)
        ]).slice(0, 8)
      };
    }
  }
  agent.lastEventAt = new Date(nowMs).toISOString();
  agent.lastAssistantSnippet = `${reason} 记忆模块提示：${agent.memory.lesson}`;
  return true;
}

function clonePeerDecisions(peers) {
  return JSON.parse(JSON.stringify(peers || []));
}

function buildPeerDecisionsForAuditor(worldState) {
  return PEER_AGENT_IDS.map(agentId => {
    const agent = worldState.agents?.[agentId];
    const profile = AGENT_PROFILES[agentId];
    const decision = agent?.decision;
    if (!decision) return null;
    return {
      agentId,
      role: profile?.role || agentId,
      action: decision.action,
      actionLabel: decision.actionLabel || actionLabel(decision.action),
      symbol: decision.symbol,
      commodity: decision.commodity,
      confidence: decision.confidence,
      reason: String(decision.reason || '').slice(0, 240),
      evidence: Array.isArray(decision.evidence) ? decision.evidence.slice(0, 3) : [],
      source: decision.source || 'simulated'
    };
  }).filter(Boolean);
}

function recordLlmDecision({ worldState, agentId, roundIndex, round, nowMs = Date.now() }) {
  const agent = worldState.agents?.[agentId];
  const source = agent?.decision?.source;
  if (!agent?.decision || (source !== 'llm' && source !== 'fallback')) return;
  if (!worldState.meta) worldState.meta = {};
  if (!worldState.meta.trading) worldState.meta.trading = {};
  const ledger = Array.isArray(worldState.meta.trading.llmDecisionLedger)
    ? worldState.meta.trading.llmDecisionLedger.filter(entry =>
      !(entry.agentId === agentId && Number(entry.roundIndex) === Number(roundIndex))
    )
    : [];

  ledger.push({
    agentId,
    roundIndex,
    date: round?.date || agent.decision.date || null,
    action: agent.decision.action,
    actionLabel: agent.decision.actionLabel || actionLabel(agent.decision.action),
    commodity: agent.decision.commodity,
    symbol: agent.decision.symbol,
    commodityLabel: agent.decision.symbol,
    confidence: agent.decision.confidence,
    model: agent.decision.model,
    provider: agent.decision.provider,
    source,
    reason: agent.decision.reason,
    recordedAt: new Date(nowMs).toISOString()
  });
  ledger.sort((a, b) => Number(a.roundIndex) - Number(b.roundIndex) || String(a.agentId).localeCompare(String(b.agentId)));
  worldState.meta.trading.llmDecisionLedger = ledger;
}

async function updateTradingGameWithLlm({
  worldState,
  roundIndex = 0,
  llmClient,
  nowMs = Date.now(),
  onProgress = null,
  llmParallel = false,
  runRecorder = null
}) {
  if (!llmClient || typeof llmClient.decide !== 'function') {
    return { updated: 0, failed: 0 };
  }

  const idx = clampRoundIndex(roundIndex);
  const historicalRounds = getHistoricalRounds();
  const round = historicalRounds[idx];
  const strategyAtRoundStart = Object.fromEntries(
    AGENT_IDS.map(agentId => [
      agentId,
      JSON.parse(JSON.stringify(worldState.agents?.[agentId]?.strategy || {}))
    ])
  );
  const failures = [];
  let updated = 0;
  const provider = llmClient.provider || 'llm';
  const model = llmClient.model || DEFAULT_LLM_MODEL;
  const timeoutMs = !llmClient.handlesTimeouts && Number.isFinite(Number(llmClient.timeoutMs))
    ? Number(llmClient.timeoutMs)
    : 0;

  async function decideWithOptionalTimeout(input) {
    const promise = llmClient.decide(input);
    if (!timeoutMs || timeoutMs <= 0) return promise;
    let timeout = null;
    try {
      return await Promise.race([
        promise,
        new Promise((_, reject) => {
          timeout = setTimeout(() => {
            reject(new Error(`LLM decision timed out after ${timeoutMs}ms.`));
          }, timeoutMs);
        })
      ]);
    } finally {
      if (timeout) clearTimeout(timeout);
    }
  }

  if (worldState.meta?.trading) {
    worldState.meta.trading.llm = {
      enabled: true,
      provider,
      model,
      status: 'running',
      updatedAt: new Date(nowMs).toISOString()
    };
  }

  async function decideOneAgent(agentId, { peerDecisions = null } = {}) {
    const agent = worldState.agents?.[agentId];
    const profile = AGENT_PROFILES[agentId];
    if (!agent || !profile) return { agentId, ok: false, skipped: true };
    const contextBefore = {
      strategy: JSON.parse(JSON.stringify(strategyAtRoundStart[agentId] || agent.strategy || {})),
      memory: JSON.parse(JSON.stringify(agent.memory || {})),
      baselineDecision: JSON.parse(JSON.stringify(agent.decision || null))
    };
    try {
      const llmDecision = await decideWithOptionalTimeout({
        agentId,
        profile,
        round,
        roundIndex: idx,
        commodities: COMMODITIES,
        simulatedDecision: agent.decision,
        memory: agent.memory,
        strategy: agent.strategy,
        trainingTradeCount: TRAINING_TRADE_COUNT,
        peerDecisions
      });
      return {
        agentId,
        role: profile.role,
        ok: true,
        llmDecision,
        source: 'llm',
        isAuditor: agentId === MEMORY_AUDITOR_ID,
        peerDecisionsInput: peerDecisions ? clonePeerDecisions(peerDecisions) : null,
        contextBefore
      };
    } catch (err) {
      const fallback = buildDecision({ agentId, round, roundIndex: idx });
      const { buildMessages } = require('../server/llmClient');
      let fallbackMessages = null;
      try {
        fallbackMessages = buildMessages({
          agentId,
          profile,
          round,
          simulatedDecision: agent.decision,
          memory: agent.memory,
          strategy: agent.strategy,
          roundIndex: idx,
          trainingTradeCount: TRAINING_TRADE_COUNT,
          peerDecisions
        });
      } catch (_) {
        fallbackMessages = null;
      }
      return {
        agentId,
        role: profile.role,
        ok: false,
        error: err.message,
        llmDecision: {
          action: fallback.action,
          commodity: fallback.commodity,
          confidence: fallback.confidence,
          reason: `${fallback.reason}（LLM 不可用，已回退预设决策）`,
          evidence: fallback.evidence,
          strategyPatchNotes: agent.strategy?.patchNotes || [],
          memoryLesson: agent.memory?.lesson || fallback.reason,
          messages: fallbackMessages,
          rawContent: null
        },
        source: 'fallback',
        isAuditor: agentId === MEMORY_AUDITOR_ID,
        peerDecisionsInput: peerDecisions ? clonePeerDecisions(peerDecisions) : null,
        contextBefore
      };
    }
  }

  function applyLlmOutcome(outcome) {
    if (outcome.skipped) return false;
    if (outcome.error) failures.push({ agentId: outcome.agentId, message: outcome.error });
    const applied = applyLlmDecisionToAgent({
      worldState,
      agentId: outcome.agentId,
      llmDecision: outcome.llmDecision,
      round,
      roundIndex: idx,
      nowMs,
      model: outcome.llmDecision?.model || model,
      provider: outcome.llmDecision?.provider || provider
    });
    if (applied) {
      const agent = worldState.agents?.[outcome.agentId];
      const profile = AGENT_PROFILES[outcome.agentId];
      if (agent && profile) {
        agent.strategy = attachPromptState({
          profile,
          strategy: agent.strategy,
          memory: agent.memory,
          previousStrategy: strategyAtRoundStart[outcome.agentId] || agent.strategy,
          roundIndex: idx,
          round
        });
        agent.gitBranch = `提示词-${agent.strategy.promptLabel || promptLabelForStage(agent.strategy.promptStage ?? 0)}`;
      }
      if (agent?.decision) agent.decision.source = outcome.source;
      recordLlmDecision({ worldState, agentId: outcome.agentId, roundIndex: idx, round, nowMs });
      updated += 1;
    }
    if (typeof onProgress === 'function') {
      onProgress({ agentId: outcome.agentId, updated, failed: failures.length });
    }
    return applied;
  }

  const outcomes = [];

  async function runPeerDecisions() {
    if (llmParallel) {
      const peerOutcomes = await Promise.all(
        PEER_AGENT_IDS.map(agentId => decideOneAgent(agentId))
      );
      for (const outcome of peerOutcomes) {
        applyLlmOutcome(outcome);
        outcomes.push(outcome);
      }
      return;
    }
    for (const agentId of PEER_AGENT_IDS) {
      const outcome = await decideOneAgent(agentId);
      applyLlmOutcome(outcome);
      outcomes.push(outcome);
    }
  }

  await runPeerDecisions();

  const peerDecisions = buildPeerDecisionsForAuditor(worldState);
  const auditorOutcome = await decideOneAgent(MEMORY_AUDITOR_ID, { peerDecisions });
  applyLlmOutcome(auditorOutcome);
  outcomes.push(auditorOutcome);

  if (worldState.meta?.trading && peerDecisions.length) {
    worldState.meta.trading.peerReview = {
      round: idx,
      date: round?.date || null,
      peers: peerDecisions,
      auditorReady: true,
      updatedAt: new Date(nowMs).toISOString()
    };
  }

  if (worldState.meta?.trading) {
    const evaluation = worldState.meta.trading.evaluation;
    worldState.meta.trading.debate = buildDebateRound({ worldState, roundIndex: idx, round, nowMs });
    worldState.meta.trading.execution = buildExecutionGate({ worldState, roundIndex: idx, round, nowMs });
    worldState.meta.trading.risk = buildRiskSnapshot({
      worldState,
      roundIndex: idx,
      round,
      evaluation,
      nowMs
    });
    worldState.meta.trading.promptBoard = buildPromptBoard({ worldState, roundIndex: idx, round, nowMs });
  }

  // After LLM decisions, recalculate scores based on actual LLM decisions
  if (updated > 0 && worldState.meta?.trading) {
    const idx = clampRoundIndex(roundIndex);
    const historicalRounds = getHistoricalRounds();
    const round = historicalRounds[idx];
    
    // Build evaluation based on LLM decisions
    const llmEvaluation = buildLlmEvaluation({ worldState, rounds: historicalRounds, roundIndex: idx });
    
    worldState.meta.trading.evaluation = llmEvaluation;
    worldState.meta.trading.priceSource = '模型累计决策';
    worldState.meta.trading.llm = {
      enabled: true,
      provider,
      model,
      status: failures.length === 0 ? 'live' : updated > 0 ? 'partial' : 'error',
      updatedAt: new Date(nowMs).toISOString(),
      errors: failures
    };
    worldState.meta.trading.updatedAt = new Date(nowMs).toISOString();
    
    // Update agent scores with LLM-based evaluation
    for (const agentId of AGENT_IDS) {
      const agent = worldState.agents?.[agentId];
      const scoreSummary = llmEvaluation.byAgent[agentId];
      if (agent && scoreSummary) {
        agent.score = {
          total: scoreSummary.totalScore,
          training: scoreSummary.trainingScore,
          test: scoreSummary.testScore,
          drawdown: scoreSummary.maxDrawdown,
          hitRate: scoreSummary.hitRate
        };
      }
    }
    worldState.meta.trading.risk = buildRiskSnapshot({
      worldState,
      roundIndex: idx,
      round,
      evaluation: llmEvaluation,
      nowMs
    });
    worldState.meta.trading.promptBoard = buildPromptBoard({ worldState, roundIndex: idx, round, nowMs });
  } else if (worldState.meta?.trading) {
    worldState.meta.trading.llm = {
      enabled: true,
      provider,
      model,
      status: failures.length === 0 ? 'live' : updated > 0 ? 'partial' : 'error',
      updatedAt: new Date(nowMs).toISOString(),
      errors: failures
    };
    worldState.meta.trading.updatedAt = new Date(nowMs).toISOString();
  }

  if (runRecorder && typeof runRecorder.recordRound === 'function') {
    await runRecorder.recordRound({
      roundIndex: idx,
      round,
      outcomes,
      failures,
      trading: worldState.meta?.trading || {},
      agents: worldState.agents || {},
      nowMs
    });
  }

  return { updated, failed: failures.length, failures };
}

function createSimulationEngine({
  worldState,
  broadcastState,
  tickMs = 4500,
  now = () => Date.now(),
  llmClient = null,
  llmParallel = false,
  onLlmError = null,
  runRecorder = null
}) {
  let roundIndex = 0;
  let timer = null;
  let inFlight = false;
  let running = false;

  if (runRecorder && llmClient && typeof runRecorder.startRun === 'function') {
    runRecorder.startRun({
      llm: {
        provider: llmClient.provider || 'llm',
        model: llmClient.model || DEFAULT_LLM_MODEL,
        models: llmClient.models || null
      },
      tickMs,
      llmParallel,
      trainingTradeCount: TRAINING_TRADE_COUNT,
      totalRounds: ROUNDS.length
    });
  }

  function scheduleNextTick() {
    if (!running) return;
    if (timer) clearTimeout(timer);
    timer = setTimeout(tick, tickMs);
    if (timer.unref) timer.unref();
  }

  function completeSimulation() {
    running = false;
    if (timer) {
      clearTimeout(timer);
      timer = null;
    }
    if (worldState.meta?.trading) {
      worldState.meta.trading.simulationComplete = true;
      worldState.meta.trading.completedAt = new Date(now()).toISOString();
      worldState.meta.trading.totalRounds = ROUNDS.length;
      worldState.meta.trading.llm = {
        ...(worldState.meta.trading.llm || {}),
        status: llmClient ? 'completed' : 'simulated-complete'
      };
    }
    for (const agentId of AGENT_IDS) {
      const agent = worldState.agents?.[agentId];
      if (agent) {
        agent.status = 'Finished';
        agent.activity = '本轮仿真已完成';
      }
    }
    if (runRecorder && typeof runRecorder.finalizeRun === 'function') {
      runRecorder.finalizeRun({ worldState, status: 'completed' });
    }
    if (typeof broadcastState === 'function') broadcastState();
  }

  function tick() {
    if (llmClient && inFlight) {
      scheduleNextTick();
      return;
    }
    if (roundIndex >= ROUNDS.length || worldState.meta?.trading?.simulationComplete) {
      return;
    }
    const currentRound = roundIndex;
    const isLastRound = currentRound >= ROUNDS.length - 1;
    // Skip preset scoring when LLM is enabled - we'll score after LLM decisions
    applyTradingGameRound({ worldState, roundIndex: currentRound, nowMs: now(), skipPresetScoring: Boolean(llmClient) });
    roundIndex = currentRound + 1;
    if (llmClient && !inFlight) {
      inFlight = true;
      if (worldState.meta?.trading) {
        worldState.meta.trading.llm = {
          enabled: true,
          provider: llmClient.provider || 'llm',
          model: llmClient.model || DEFAULT_LLM_MODEL,
          status: 'running',
          updatedAt: new Date(now()).toISOString()
        };
      }
      if (typeof broadcastState === 'function') broadcastState();
      updateTradingGameWithLlm({
        worldState,
        roundIndex: currentRound,
        llmClient,
        llmParallel,
        runRecorder,
        nowMs: now(),
        onProgress: () => {
          if (typeof broadcastState === 'function') broadcastState();
        }
      }).then(() => {
        if (isLastRound) {
          completeSimulation();
          return;
        }
        if (typeof broadcastState === 'function') broadcastState();
      }).catch(err => {
        if (worldState.meta?.trading) {
          worldState.meta.trading.llm = {
            enabled: true,
            provider: llmClient.provider || 'llm',
            model: llmClient.model || DEFAULT_LLM_MODEL,
            status: 'error',
            error: err.message,
            updatedAt: new Date(now()).toISOString()
          };
        }
        if (typeof onLlmError === 'function') onLlmError(err);
      }).finally(() => {
        inFlight = false;
        if (!worldState.meta?.trading?.simulationComplete) {
          scheduleNextTick();
        }
      });
    } else if (typeof broadcastState === 'function') {
      broadcastState();
      if (isLastRound) {
        completeSimulation();
      } else {
        scheduleNextTick();
      }
    }
  }

  return {
    start() {
      if (running) return;
      running = true;
      tick();
    },
    stop() {
      running = false;
      if (timer) {
        clearTimeout(timer);
        timer = null;
      }
      if (runRecorder && typeof runRecorder.finalizeRun === 'function' && !worldState.meta?.trading?.simulationComplete) {
        runRecorder.finalizeRun({ worldState, status: 'stopped' });
      }
    },
    tick
  };
}

module.exports = {
  AGENT_IDS,
  PEER_AGENT_IDS,
  MEMORY_AUDITOR_ID,
  AGENT_PROFILES,
  COMMODITIES,
  normalizeCommodityId,
  resolveCommodity,
  ROUNDS,
  STATIONS,
  DEFAULT_LLM_MODEL,
  TRAINING_TRADE_COUNT,
  PROMPT_SEASON_LENGTH,
  getHistoricalRounds,
  buildEvaluation,
  buildDebateRound,
  buildExecutionGate,
  buildRiskSnapshot,
  buildPromptBoard,
  buildPeerDecisionsForAuditor,
  composePromptText,
  attachPromptState,
  applyTradingGameRound,
  updateTradingGameWithLlm,
  createSimulationEngine
};
