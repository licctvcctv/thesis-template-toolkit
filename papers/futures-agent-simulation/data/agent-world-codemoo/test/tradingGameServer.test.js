const test = require('node:test');
const assert = require('node:assert/strict');
const { createServer } = require('../server/index');

test('server can boot directly into trading simulation mode', async () => {
  const runtime = createServer({
    security: { enabled: false },
    claudeSync: { enabled: false },
    tradingDemo: {
      enabled: true,
      llmEnabled: false,
      tickMs: 60_000,
      now: () => 1_780_000_000_000
    }
  });

  try {
    assert.equal(runtime.worldState.meta.trading.mode, 'futures-agent-simulation');
    assert.equal(Object.keys(runtime.worldState.agents).length, 4);
    assert.equal(runtime.worldState.meta.claude.enabled, false);
  } finally {
    await runtime.stopBackgroundWorkers();
    await new Promise(resolve => runtime.wss.close(() => resolve()));
  }
});

test('server wires trading simulation to an llm client when provided', async () => {
  const fakeClient = {
    provider: 'test-llm',
    model: 'deepseek-ai/DeepSeek-V4-Flash',
    async decide() {
      return {
        action: 'HOLD',
        confidence: 66,
        reason: '服务器测试中的真实模型决策。',
        evidence: ['测试证据'],
        strategyPatchNotes: ['服务器测试策略补丁'],
        memoryLesson: '服务器测试记忆'
      };
    }
  };
  const runtime = createServer({
    security: { enabled: false },
    claudeSync: { enabled: false },
    tradingDemo: {
      enabled: true,
      tickMs: 60_000,
      now: () => 1_780_000_000_000,
      llmClient: fakeClient
    }
  });

  try {
    await new Promise(resolve => setTimeout(resolve, 20));
    assert.equal(runtime.worldState.meta.trading.llm.status, 'live');
    assert.equal(runtime.worldState.agents['conservative-hedger'].decision.source, 'llm');
    assert.match(runtime.worldState.agents['conservative-hedger'].decision.reason, /服务器测试/);
  } finally {
    await runtime.stopBackgroundWorkers();
    await new Promise(resolve => runtime.wss.close(() => resolve()));
  }
});
