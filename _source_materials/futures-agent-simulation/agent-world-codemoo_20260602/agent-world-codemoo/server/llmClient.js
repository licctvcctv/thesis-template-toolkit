const DEFAULT_MODEL = 'deepseek-v4-flash';
const DEFAULT_MODEL_CHAIN = Object.freeze([
  'deepseek-v4-flash',
  'deepseek-v4-pro'
]);
const DEFAULT_BASE_URL = 'https://api.deepseek.com';
const DEFAULT_TIMEOUT_MS = 60_000;
const MEMORY_AUDITOR_ID = 'memory-auditor';

const { COMMODITIES, normalizeCommodityId, resolveCommodity } = require('../adapter/simulationEngine');

function clampConfidence(value) {
  const numeric = Number(value);
  if (!Number.isFinite(numeric)) return 55;
  return Math.max(1, Math.min(99, Math.round(numeric)));
}

function normalizeAction(value) {
  const raw = String(value || '').trim().toUpperCase();
  if (raw === 'BUY' || raw === 'SELL' || raw === 'HOLD') return raw;
  if (/买|做多|加仓/.test(raw)) return 'BUY';
  if (/卖|做空|减仓|反手/.test(raw)) return 'SELL';
  return 'HOLD';
}

function extractJsonObject(text) {
  if (!text || typeof text !== 'string') return {};
  try {
    return JSON.parse(text);
  } catch (_) {
    const match = text.match(/\{[\s\S]*\}/);
    if (!match) throw new Error('Model response did not contain JSON.');
    return JSON.parse(match[0]);
  }
}

function normalizeList(value) {
  if (Array.isArray(value)) {
    return value.map(item => String(item || '').trim()).filter(Boolean).slice(0, 5);
  }
  if (typeof value === 'string' && value.trim()) return [value.trim()];
  return [];
}

function normalizeUsage(usage) {
  return {
    promptTokens: Number(usage?.prompt_tokens || usage?.promptTokens || 0),
    completionTokens: Number(usage?.completion_tokens || usage?.completionTokens || 0),
    totalTokens: Number(usage?.total_tokens || usage?.totalTokens || 0)
  };
}

function normalizeModelName(value) {
  const raw = String(value || '').trim();
  if (!raw) return DEFAULT_MODEL;
  const lower = raw.toLowerCase();
  if (lower === 'deepseek-chat' || lower.includes('v4-flash')) return 'deepseek-v4-flash';
  if (lower === 'deepseek-reasoner' || lower.includes('v4-pro')) return 'deepseek-v4-pro';
  if (/^deepseek-/i.test(raw)) return raw;
  return DEFAULT_MODEL;
}

function normalizeModelList(value, fallback) {
  const source = Array.isArray(value) ? value : [value];
  const list = source
    .flatMap(item => typeof item === 'string' ? item.split(',') : [])
    .map(item => normalizeModelName(item.trim()))
    .filter(Boolean);
  const unique = [];
  for (const model of list.length ? list : fallback) {
    const normalized = normalizeModelName(model);
    if (normalized && !unique.includes(normalized)) unique.push(normalized);
  }
  return unique.length ? unique : [...fallback];
}

function pickModelForAgent(agentId, profile = null) {
  if (profile?.preferredModel) {
    return normalizeModelName(profile.preferredModel);
  }
  if (agentId === MEMORY_AUDITOR_ID) return 'deepseek-v4-flash';
  return DEFAULT_MODEL;
}

function modelCandidatesForAgent(agentId, profile, defaultModels) {
  const primary = pickModelForAgent(agentId, profile);
  const chain = normalizeModelList(
    profile?.modelChain || profile?.models || defaultModels,
    defaultModels
  );
  const ordered = [primary, ...chain.filter(model => model !== primary)];
  return ordered.length ? ordered : [DEFAULT_MODEL];
}

function resolveRequestOptions({ agentId, profile, selectedModel }) {
  const model = normalizeModelName(selectedModel);
  const auditor =
    agentId === MEMORY_AUDITOR_ID ||
    normalizeModelName(profile?.preferredModel) === 'deepseek-v4-pro' ||
    selectedModel === 'deepseek-reasoner';

  if (auditor) {
    return {
      model: model === 'deepseek-v4-pro' ? 'deepseek-v4-pro' : 'deepseek-v4-flash',
      max_tokens: 1200,
      thinking: { type: 'enabled' },
      reasoning_effort: 'high'
    };
  }

  return {
    model,
    max_tokens: 900
  };
}

function extractMessageContent(message) {
  if (!message || typeof message !== 'object') return '';
  return String(message.content || message.reasoning_content || '').trim();
}

function buildMessages({
  agentId,
  profile,
  round,
  simulatedDecision,
  memory = null,
  strategy = null,
  roundIndex = 0,
  trainingTradeCount = 6,
  peerDecisions = null
}) {
  const inTraining = Number.isFinite(roundIndex) && roundIndex < trainingTradeCount;
  const isAuditor = agentId === MEMORY_AUDITOR_ID;
  const peers = Array.isArray(peerDecisions) ? peerDecisions.filter(Boolean) : [];
  const preferredCommodity = resolveCommodity({ profile });
  const availableCommodities = COMMODITIES.map(item => ({
    id: item.id,
    name: item.name,
    unit: item.unit
  }));

  const system = [
    '你是一个期货长线交易智能体，只能按交易日做决策。',
    '你必须基于给定的历史价格、市场资讯、检索记忆和智能体角色设定输出结构化 JSON。',
    '不要编造未给出的外部数据。动作只能是 BUY、SELL、HOLD。',
    '每轮必须且只能选择一个交易品种（黄金期货 / 原油期货 / 大豆期货），再给出对该品种的方向动作。',
    profile?.mandate ? `【角色定位】${profile.mandate}` : null,
    profile?.riskFramework ? `【风控框架】${profile.riskFramework}` : null,
    Array.isArray(profile?.decisionPrinciples) && profile.decisionPrinciples.length
      ? `【决策原则】${profile.decisionPrinciples.join('；')}`
      : null,
    `【品种偏好】${preferredCommodity.name}（默认倾向，但可依据资讯与记忆改选其他品种）`,
    isAuditor
      ? '你是记忆审计官：必须先审阅 peerDecisions 中其他智能体的观点，识别拥挤交易、一致预期与历史失败模式的相似性，再给出独立第三方动作。若三者高度同向，应优先质疑并倾向 HOLD 或反向减仓。'
      : null,
    inTraining
      ? '当前处于训练段：请根据本轮证据输出 strategyPatchNotes，这些规则会在下一轮写入你的 prompt。'
      : '当前处于测试段：prompt 已冻结，不要提出新的 strategyPatchNotes，只做决策。',
    '输出必须是一个 JSON 对象，不要 Markdown，不要解释 JSON 外的内容。'
  ].filter(Boolean).join('\n');

  const user = {
    task: isAuditor && peers.length
      ? '在审阅其他智能体本轮观点后，为本交易日生成独立的期货交易决策'
      : '为一个交易日生成期货交易决策',
    phase: inTraining ? 'training' : 'test',
    roundIndex: Number.isFinite(roundIndex) ? roundIndex + 1 : null,
    agent: {
      id: agentId,
      role: profile?.role,
      style: profile?.style,
      mandate: profile?.mandate || null,
      commodityBias: profile?.commodityBias,
      preferredCommodity: preferredCommodity.name,
      promptVersion: strategy?.promptVersion || 1,
      activeStrategyRules: Array.isArray(strategy?.patchNotes) ? strategy.patchNotes : [],
      accumulatedMemoryLesson: memory?.lesson || null
    },
    availableCommodities,
    tradingDay: {
      date: round?.date,
      regime: round?.regime,
      prices: round?.prices,
      news: round?.news,
      retrievedMemory: Array.isArray(memory?.retrieved)
        ? memory.retrieved.map(item => item.text)
        : round?.memory
    },
    baselineDecision: simulatedDecision,
    peerDecisions: isAuditor && peers.length ? peers : undefined,
    requiredJsonSchema: {
      commodity: 'gold | crude_oil | soybean，或中文：黄金期货 | 原油期货 | 大豆期货',
      action: 'BUY | SELL | HOLD',
      confidence: '1-99 integer',
      reason: isAuditor && peers.length
        ? '中文，1-2 句，说明如何审阅同业观点、记忆与行情后给出独立动作'
        : '中文，1-2 句，说明资讯、价格走势和记忆如何影响动作',
      evidence: ['中文证据点 1', '中文证据点 2'],
      strategyPatchNotes: inTraining
        ? ['本轮学习后要修正的 prompt/策略规则']
        : [],
      memoryLesson: '本轮写入长期记忆的一句话'
    }
  };

  return [
    { role: 'system', content: system },
    { role: 'user', content: JSON.stringify(user, null, 2) }
  ];
}

function createDeepSeekTradingClient({
  apiKey,
  model = DEFAULT_MODEL,
  models = null,
  baseUrl = DEFAULT_BASE_URL,
  timeoutMs = DEFAULT_TIMEOUT_MS,
  fetchImpl = globalThis.fetch
} = {}) {
  if (!apiKey) throw new Error('DeepSeek API key is required.');
  if (typeof fetchImpl !== 'function') throw new Error('fetch runtime is required.');

  const defaultModels = normalizeModelList(models || model, DEFAULT_MODEL_CHAIN);

  async function requestDecision(input, selectedModel) {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), timeoutMs);
    const requestOptions = resolveRequestOptions({
      agentId: input?.agentId,
      profile: input?.profile,
      selectedModel
    });
    try {
      const response = await fetchImpl(`${baseUrl.replace(/\/+$/, '')}/chat/completions`, {
        method: 'POST',
        headers: {
          authorization: `Bearer ${apiKey}`,
          'content-type': 'application/json'
        },
        signal: controller.signal,
        body: JSON.stringify({
          model: requestOptions.model,
          messages: buildMessages(input),
          temperature: 0.2,
          max_tokens: requestOptions.max_tokens,
          response_format: { type: 'json_object' },
          ...(requestOptions.thinking ? { thinking: requestOptions.thinking } : {}),
          ...(requestOptions.reasoning_effort
            ? { reasoning_effort: requestOptions.reasoning_effort }
            : {})
        })
      });
      const payload = await response.json().catch(() => ({}));
      if (!response.ok) {
        const message = payload?.error?.message || payload?.message || `HTTP ${response.status}`;
        throw new Error(`DeepSeek request failed: ${message}`);
      }
      const content = extractMessageContent(payload?.choices?.[0]?.message);
      const parsed = extractJsonObject(content);
      const messages = buildMessages(input);
      const commodityId = normalizeCommodityId(parsed.commodity) ||
        normalizeCommodityId(parsed.symbol) ||
        input?.profile?.commodityBias ||
        'gold';
      const commodity = resolveCommodity({ profile: input?.profile, commodityId });
      return {
        action: normalizeAction(parsed.action),
        commodity: commodity.id,
        commodityLabel: commodity.name,
        confidence: clampConfidence(parsed.confidence),
        reason: String(parsed.reason || '').trim(),
        evidence: normalizeList(parsed.evidence),
        strategyPatchNotes: normalizeList(parsed.strategyPatchNotes || parsed.patchNotes),
        memoryLesson: String(parsed.memoryLesson || '').trim(),
        usage: normalizeUsage(payload.usage),
        model: requestOptions.model,
        provider: 'deepseek',
        messages,
        rawContent: content
      };
    } finally {
      clearTimeout(timeout);
    }
  }

  async function decide(input) {
    const candidateModels = modelCandidatesForAgent(
      input?.agentId,
      input?.profile,
      defaultModels
    );
    const attempts = [];
    for (const selectedModel of candidateModels) {
      try {
        const decision = await requestDecision(input, selectedModel);
        attempts.push({ model: selectedModel, ok: true });
        return { ...decision, attempts };
      } catch (err) {
        attempts.push({ model: selectedModel, ok: false, error: err.message });
      }
    }
    const error = new Error(`All DeepSeek trading models failed: ${attempts.map(item => `${item.model}: ${item.error}`).join('; ')}`);
    error.attempts = attempts;
    throw error;
  }

  return {
    provider: 'deepseek',
    model: defaultModels[0],
    models: defaultModels,
    timeoutMs,
    handlesTimeouts: true,
    decide,
    pickModelForAgent: (agentId, profile) => pickModelForAgent(agentId, profile)
  };
}

/** @deprecated Use createDeepSeekTradingClient */
function createSiliconFlowTradingClient(options = {}) {
  return createDeepSeekTradingClient(options);
}

module.exports = {
  DEFAULT_MODEL,
  DEFAULT_MODEL_CHAIN,
  MEMORY_AUDITOR_ID,
  normalizeModelName,
  normalizeCommodityId,
  pickModelForAgent,
  createDeepSeekTradingClient,
  createSiliconFlowTradingClient,
  buildMessages
};
