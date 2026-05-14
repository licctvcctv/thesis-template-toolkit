const DEFAULT_MODEL = 'deepseek-ai/DeepSeek-V4-Flash';
const DEFAULT_MODEL_CHAIN = Object.freeze([
  'deepseek-ai/DeepSeek-V4-Flash',
  'deepseek-ai/DeepSeek-V3.2',
  'deepseek-ai/DeepSeek-V3.1-Terminus',
  'Qwen/Qwen3.6-35B-A3B'
]);
const DEFAULT_BASE_URL = 'https://api.siliconflow.cn/v1';
const DEFAULT_TIMEOUT_MS = 45_000;

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

function normalizeModelList(value, fallback) {
  const source = Array.isArray(value) ? value : [value];
  const list = source
    .flatMap(item => typeof item === 'string' ? item.split(',') : [])
    .map(item => item.trim())
    .filter(Boolean);
  const unique = [];
  for (const model of list.length ? list : fallback) {
    if (model && !unique.includes(model)) unique.push(model);
  }
  return unique.length ? unique : [DEFAULT_MODEL];
}

function buildMessages({ agentId, profile, round, simulatedDecision }) {
  const system = [
    '你是一个期货长线交易智能体，只能按交易日做决策。',
    '你必须基于给定的历史价格、市场资讯、检索记忆和智能体风格输出结构化 JSON。',
    '不要编造未给出的外部数据。动作只能是 BUY、SELL、HOLD。',
    '输出必须是一个 JSON 对象，不要 Markdown，不要解释 JSON 外的内容。'
  ].join('\n');

  const user = {
    task: '为一个交易日生成期货交易决策',
    agent: {
      id: agentId,
      role: profile?.role,
      style: profile?.style,
      commodityBias: profile?.commodityBias
    },
    tradingDay: {
      date: round?.date,
      regime: round?.regime,
      prices: round?.prices,
      news: round?.news,
      retrievedMemory: round?.memory
    },
    baselineDecision: simulatedDecision,
    requiredJsonSchema: {
      action: 'BUY | SELL | HOLD',
      confidence: '1-99 integer',
      reason: '中文，1-2 句，说明资讯、价格走势和记忆如何影响动作',
      evidence: ['中文证据点 1', '中文证据点 2'],
      strategyPatchNotes: ['本轮学习后要修正的 prompt/策略规则'],
      memoryLesson: '本轮写入长期记忆的一句话'
    }
  };

  return [
    { role: 'system', content: system },
    { role: 'user', content: JSON.stringify(user, null, 2) }
  ];
}

function createSiliconFlowTradingClient({
  apiKey,
  model = DEFAULT_MODEL,
  models = null,
  baseUrl = DEFAULT_BASE_URL,
  timeoutMs = DEFAULT_TIMEOUT_MS,
  fetchImpl = globalThis.fetch
} = {}) {
  if (!apiKey) throw new Error('SiliconFlow API key is required.');
  if (typeof fetchImpl !== 'function') throw new Error('fetch runtime is required.');

  const defaultModels = normalizeModelList(models || model, DEFAULT_MODEL_CHAIN);

  async function requestDecision(input, selectedModel) {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), timeoutMs);
    try {
      const response = await fetchImpl(`${baseUrl.replace(/\/+$/, '')}/chat/completions`, {
        method: 'POST',
        headers: {
          authorization: `Bearer ${apiKey}`,
          'content-type': 'application/json'
        },
        signal: controller.signal,
        body: JSON.stringify({
          model: selectedModel,
          messages: buildMessages(input),
          temperature: 0.2,
          max_tokens: 900,
          response_format: { type: 'json_object' }
        })
      });
      const payload = await response.json().catch(() => ({}));
      if (!response.ok) {
        const message = payload?.error?.message || payload?.message || `HTTP ${response.status}`;
        throw new Error(`SiliconFlow request failed: ${message}`);
      }
      const content = payload?.choices?.[0]?.message?.content || '';
      const parsed = extractJsonObject(content);
      return {
        action: normalizeAction(parsed.action),
        confidence: clampConfidence(parsed.confidence),
        reason: String(parsed.reason || '').trim(),
        evidence: normalizeList(parsed.evidence),
        strategyPatchNotes: normalizeList(parsed.strategyPatchNotes || parsed.patchNotes),
        memoryLesson: String(parsed.memoryLesson || '').trim(),
        usage: normalizeUsage(payload.usage),
        model: selectedModel,
        provider: 'siliconflow'
      };
    } finally {
      clearTimeout(timeout);
    }
  }

  async function decide(input) {
    const candidateModels = normalizeModelList(
      input?.profile?.modelChain || input?.profile?.models || defaultModels,
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
    const error = new Error(`All SiliconFlow trading models failed: ${attempts.map(item => `${item.model}: ${item.error}`).join('; ')}`);
    error.attempts = attempts;
    throw error;
  }

  return {
    provider: 'siliconflow',
    model: defaultModels[0],
    models: defaultModels,
    timeoutMs,
    handlesTimeouts: true,
    decide
  };
}

module.exports = {
  DEFAULT_MODEL,
  DEFAULT_MODEL_CHAIN,
  createSiliconFlowTradingClient
};
