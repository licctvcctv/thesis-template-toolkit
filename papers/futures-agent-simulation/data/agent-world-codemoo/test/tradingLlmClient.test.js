const test = require('node:test');
const assert = require('node:assert/strict');
const { createSiliconFlowTradingClient } = require('../server/tradingLlmClient');

test('SiliconFlow trading client parses structured model decisions', async () => {
  const requests = [];
  const client = createSiliconFlowTradingClient({
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
    profile: { role: '均衡型', style: '分批进出' },
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
  assert.match(requests[0].url, /chat\/completions$/);
  assert.equal(JSON.parse(requests[0].options.body).model, 'deepseek-ai/DeepSeek-V4-Flash');
  assert.equal(decision.action, 'SELL');
  assert.equal(decision.confidence, 81);
  assert.equal(decision.usage.totalTokens, 16);
});

test('SiliconFlow trading client falls back across model candidates', async () => {
  const models = [];
  const client = createSiliconFlowTradingClient({
    apiKey: 'test-key',
    models: ['deepseek-ai/DeepSeek-V4-Flash', 'deepseek-ai/DeepSeek-V3.2'],
    fetchImpl: async (_url, options) => {
      const body = JSON.parse(options.body);
      models.push(body.model);
      if (body.model === 'deepseek-ai/DeepSeek-V4-Flash') {
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
    profile: { role: '保守型', style: '保守', modelChain: ['deepseek-ai/DeepSeek-V4-Flash', 'deepseek-ai/DeepSeek-V3.2'] },
    round: { date: '2016-02-11', regime: '避险冲击', prices: {}, news: [], memory: [] },
    simulatedDecision: { action: 'HOLD' }
  });

  assert.deepEqual(models, ['deepseek-ai/DeepSeek-V4-Flash', 'deepseek-ai/DeepSeek-V3.2']);
  assert.equal(decision.action, 'BUY');
  assert.equal(decision.model, 'deepseek-ai/DeepSeek-V3.2');
  assert.equal(decision.attempts.length, 2);
  assert.equal(decision.attempts[0].ok, false);
  assert.equal(decision.attempts[1].ok, true);
});
