const test = require('node:test');
const assert = require('node:assert/strict');
const {
  createDeepSeekTradingClient,
  buildMessages,
  pickModelForAgent
} = require('../server/llmClient');

test('DeepSeek trading client parses structured model decisions', async () => {
  const requests = [];
  const client = createDeepSeekTradingClient({
    apiKey: 'test-key',
    fetchImpl: async (url, options) => {
      requests.push({ url, options });
      return {
        ok: true,
        status: 200,
        async json() {
          return {
            usage: { prompt_tokens: 10, completion_tokens: 6, total_tokens: 16 },
            choices: [
              {
                message: {
                  content: JSON.stringify({
                    commodity: 'crude_oil',
                    action: 'SELL',
                    confidence: 81,
                    reason: '新闻和价格趋势转弱，模型建议降低敞口。',
                    evidence: ['价格跌破均线', '库存上升'],
                    strategyPatchNotes: ['提高库存新闻权重'],
                    memoryLesson: '2018 年相似阶段中追多胜率下降'
                  })
                }
              }
            ]
          };
        }
      };
    }
  });

  const decision = await client.decide({
    agentId: 'balanced-strategist',
    profile: { role: '均衡型', style: '分批进出', preferredModel: 'deepseek-chat' },
    round: {
      date: '2023-10-05',
      regime: '高利率更久',
      prices: { gold: 1831, soybean: 1278, crude_oil: 82.3 },
      news: ['实际收益率上行'],
      memory: ['2018 利率重定价']
    },
    simulatedDecision: { action: 'HOLD' }
  });

  assert.equal(requests.length, 1);
  assert.match(requests[0].url, /api\.deepseek\.com/);
  assert.match(requests[0].url, /chat\/completions$/);
  assert.equal(JSON.parse(requests[0].options.body).model, 'deepseek-v4-flash');
  assert.equal(decision.action, 'SELL');
  assert.equal(decision.commodity, 'crude_oil');
  assert.equal(decision.commodityLabel, '原油期货');
  assert.equal(decision.provider, 'deepseek');
  assert.equal(decision.usage.totalTokens, 16);
});

test('DeepSeek trading client falls back across model candidates', async () => {
  const models = [];
  const client = createDeepSeekTradingClient({
    apiKey: 'test-key',
    models: ['deepseek-v4-flash', 'deepseek-v4-pro'],
    fetchImpl: async (_url, options) => {
      const body = JSON.parse(options.body);
      models.push(body.model);
      if (body.model === 'deepseek-v4-flash') {
        return {
          ok: false,
          status: 504,
          async json() {
            return { error: { message: 'timeout' } };
          }
        };
      }
      return {
        ok: true,
        status: 200,
        async json() {
          return {
            choices: [
              {
                message: {
                  content: JSON.stringify({
                    action: 'BUY',
                    confidence: 73,
                    reason: '备用模型完成决策。',
                    evidence: ['备用证据'],
                    strategyPatchNotes: ['备用策略'],
                    memoryLesson: '备用记忆'
                  })
                }
              }
            ]
          };
        }
      };
    }
  });

  const decision = await client.decide({
    agentId: 'conservative-hedger',
    profile: { role: '保守型', style: '保守', preferredModel: 'deepseek-chat' },
    round: { date: '2016-02-11', regime: '避险冲击', prices: {}, news: [], memory: [] },
    simulatedDecision: { action: 'HOLD' }
  });

  assert.deepEqual(models, ['deepseek-v4-flash', 'deepseek-v4-pro']);
  assert.equal(decision.action, 'BUY');
  assert.equal(decision.model, 'deepseek-v4-pro');
  assert.equal(decision.attempts.length, 2);
  assert.equal(decision.attempts[0].ok, false);
  assert.equal(decision.attempts[1].ok, true);
});

test('DeepSeek picks thinking profile for memory auditor', () => {
  assert.equal(pickModelForAgent('memory-auditor', { preferredModel: 'deepseek-v4-pro' }), 'deepseek-v4-pro');
  assert.equal(pickModelForAgent('conservative-hedger', {}), 'deepseek-v4-flash');
  assert.equal(pickModelForAgent('aggressive-breakout', {}), 'deepseek-v4-flash');
});

test('LLM prompt includes accumulated strategy rules and memory lesson', () => {
  const messages = buildMessages({
    agentId: 'balanced-strategist',
    profile: { role: '均衡型', style: '分批进出', mandate: '多因子CTA' },
    round: { date: '2020-03-01', regime: '疫情冲击', prices: {}, news: [], memory: ['历史样本'] },
    simulatedDecision: { action: 'HOLD' },
    roundIndex: 2,
    trainingTradeCount: 6,
    strategy: { promptVersion: 1, patchNotes: ['提高库存新闻权重', 'v1：提高与当前市场阶段相似的历史案例权重'] },
    memory: { lesson: '库存上升阶段应降低多头敞口', retrieved: [{ text: '2018 相似案例' }] }
  });
  const user = JSON.parse(messages[1].content);
  assert.equal(user.phase, 'training');
  assert.deepEqual(user.agent.activeStrategyRules, ['提高库存新闻权重', 'v1：提高与当前市场阶段相似的历史案例权重']);
  assert.equal(user.agent.accumulatedMemoryLesson, '库存上升阶段应降低多头敞口');
  assert.match(messages[0].content, /训练段/);
  assert.match(messages[0].content, /多因子CTA/);
});

test('LLM prompt for memory auditor includes peer decisions', () => {
  const messages = buildMessages({
    agentId: 'memory-auditor',
    profile: {
      role: '记忆审计',
      style: '质疑拥挤交易',
      mandate: '跨智能体审计官'
    },
    round: { date: '2018-12-01', regime: '贸易战', prices: {}, news: [], memory: [] },
    simulatedDecision: { action: 'HOLD' },
    peerDecisions: [
      {
        agentId: 'aggressive-breakout',
        role: '激进型',
        action: 'BUY',
        actionLabel: '买入',
        symbol: '大豆期货',
        confidence: 82,
        reason: '动量突破'
      }
    ]
  });
  const user = JSON.parse(messages[1].content);
  assert.equal(user.peerDecisions.length, 1);
  assert.equal(user.peerDecisions[0].role, '激进型');
  assert.match(messages[0].content, /peerDecisions/);
  assert.match(messages[0].content, /记忆审计官/);
  assert.match(messages[0].content, /黄金期货/);
});

test('LLM prompt lists selectable commodities and requires commodity field', () => {
  const messages = buildMessages({
    agentId: 'conservative-hedger',
    profile: { role: '保守型', style: '保守', commodityBias: 'gold' },
    round: { date: '2016-02-11', regime: '避险', prices: {}, news: [], memory: [] },
    simulatedDecision: { action: 'HOLD' }
  });
  const user = JSON.parse(messages[1].content);
  assert.equal(user.availableCommodities.length, 3);
  assert.equal(user.requiredJsonSchema.commodity, 'gold | crude_oil | soybean，或中文：黄金期货 | 原油期货 | 大豆期货');
  assert.match(messages[0].content, /只能选择一个交易品种/);
});
