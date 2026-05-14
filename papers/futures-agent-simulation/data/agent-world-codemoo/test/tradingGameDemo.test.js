const test = require('node:test');
const assert = require('node:assert/strict');
const { createWorldModel } = require('../adapter/worldModel');
const {
  AGENT_IDS,
  applyTradingGameRound,
  updateTradingGameWithLlm
} = require('../adapter/tradingGameDemo');

function createEmptyWorldState() {
  return {
    world: createWorldModel(),
    agents: {},
    avatars: {},
    zones: {},
    runs: {},
    meta: {}
  };
}

test('trading demo projects four strategy agents into the world', () => {
  const worldState = createEmptyWorldState();

  applyTradingGameRound({ worldState, roundIndex: 0, nowMs: 1_780_000_000_000 });

  assert.deepEqual(Object.keys(worldState.agents).sort(), AGENT_IDS.slice().sort());
  assert.deepEqual(Object.keys(worldState.avatars).sort(), AGENT_IDS.slice().sort());
  assert.equal(worldState.meta.trading.mode, 'futures-agent-simulation');
  assert.equal(worldState.meta.trading.commodities.length, 3);
  assert.equal(worldState.meta.trading.news.length, 3);
  assert.equal(worldState.meta.trading.evaluation.rankings.length, 4);
  assert.match(worldState.meta.trading.evaluation.method, /累计评分/);

  const balanced = worldState.agents['balanced-strategist'];
  assert.equal(balanced.role, '均衡型');
  assert.equal(balanced.strategy.promptVersion, 1);
  assert.ok(balanced.decision.reason.includes('价格'));
  assert.ok(Array.isArray(balanced.memory.retrieved));
  assert.equal(balanced.memory.retrieved.length, 3);
  assert.equal(typeof balanced.score.total, 'number');
  assert.ok(['采纳', '观察', '淘汰'].includes(balanced.score.recommendation.label));

  const avatar = worldState.avatars['balanced-strategist'];
  assert.equal(avatar.displayName, '均衡型');
  assert.equal(avatar.destination.locationName, '价格趋势墙');
  assert.match(avatar.bubbleText, /买入|卖出|观望/);
});

test('trading demo advances decisions and strategy patch notes by round', () => {
  const worldState = createEmptyWorldState();

  applyTradingGameRound({ worldState, roundIndex: 0, nowMs: 1_780_000_000_000 });
  const firstDate = worldState.meta.trading.currentDate;
  const firstAction = worldState.agents['aggressive-breakout'].decision.action;

  applyTradingGameRound({ worldState, roundIndex: 3, nowMs: 1_780_000_090_000 });

  assert.notEqual(worldState.meta.trading.currentDate, firstDate);
  assert.notEqual(worldState.agents['aggressive-breakout'].decision.action, firstAction);
  assert.equal(worldState.agents['aggressive-breakout'].strategy.promptVersion, 2);
  assert.ok(
    worldState.agents['aggressive-breakout'].strategy.patchNotes.some(note =>
      note.includes('第 2 季')
    )
  );
  assert.equal(worldState.meta.trading.timeline.length, 4);
});

test('trading demo evaluation includes report-ready analysis charts', () => {
  const worldState = createEmptyWorldState();

  applyTradingGameRound({ worldState, roundIndex: 15, nowMs: 1_780_000_000_000 });

  const analysis = worldState.meta.trading.evaluation.analysis;
  assert.equal(analysis.sampleCount, 16);
  assert.equal(analysis.completedRoundCount, 16);
  assert.equal(analysis.totalAgentDecisions, 64);
  assert.ok(analysis.totalScenarioRounds > analysis.completedRoundCount);
  assert.match(analysis.scope, /累计/);
  assert.doesNotMatch(analysis.scope, /历史|数据源|RAG/);
  assert.ok(analysis.bestAgentId);
  assert.ok(Array.isArray(analysis.scoreBars));
  assert.equal(analysis.scoreBars.length, AGENT_IDS.length);
  assert.ok(analysis.scoreBars.every(item =>
    typeof item.role === 'string' &&
    typeof item.trainingScore === 'number' &&
    typeof item.testScore === 'number'
  ));
  assert.ok(Array.isArray(analysis.agentBreakdowns));
  assert.equal(analysis.agentBreakdowns.length, AGENT_IDS.length);
  assert.ok(analysis.agentBreakdowns.every(item =>
    typeof item.tradeCount === 'number' &&
    typeof item.failureSummary === 'string' &&
    typeof item.repairPlan === 'string' &&
    Array.isArray(item.failurePoints)
  ));
  assert.ok(analysis.agentBreakdowns.some(item => item.failurePoints.length > 0));
  assert.ok(Array.isArray(analysis.topEquityCurve));
  assert.ok(analysis.topEquityCurve.length > 2);
  assert.ok(analysis.actionDistribution.BUY + analysis.actionDistribution.SELL + analysis.actionDistribution.HOLD > 0);
  assert.ok(Array.isArray(analysis.conclusions));
  assert.ok(analysis.conclusions.some(text => text.includes('测试段') || text.includes('训练段')));
});

test('trading llm evaluation accumulates model decisions across rounds', async () => {
  const worldState = createEmptyWorldState();
  const fakeClient = {
    model: 'deepseek-ai/DeepSeek-V4-Flash',
    provider: 'siliconflow',
    async decide({ agentId, roundIndex }) {
      return {
        action: roundIndex % 2 === 0
          ? (agentId === 'risk-memory-auditor' ? 'HOLD' : 'BUY')
          : (agentId === 'aggressive-breakout' ? 'SELL' : 'BUY'),
        confidence: 72,
        reason: `第 ${roundIndex + 1} 轮模型累计决策：${agentId}`,
        evidence: ['价格动量', '记忆样本'],
        strategyPatchNotes: ['把亏损回合加入下一轮反思样本'],
        memoryLesson: '记录本轮决策结果，供后续累计评分使用'
      };
    }
  };

  applyTradingGameRound({ worldState, roundIndex: 0, nowMs: 1_780_000_000_000, skipPresetScoring: true });
  await updateTradingGameWithLlm({
    worldState,
    roundIndex: 0,
    llmClient: fakeClient,
    nowMs: 1_780_000_060_000
  });
  assert.equal(worldState.meta.trading.evaluation.analysis.completedRoundCount, 1);
  assert.equal(worldState.meta.trading.evaluation.analysis.totalAgentDecisions, AGENT_IDS.length);

  applyTradingGameRound({ worldState, roundIndex: 1, nowMs: 1_780_000_090_000, skipPresetScoring: true });
  await updateTradingGameWithLlm({
    worldState,
    roundIndex: 1,
    llmClient: fakeClient,
    nowMs: 1_780_000_150_000
  });

  const analysis = worldState.meta.trading.evaluation.analysis;
  assert.equal(analysis.completedRoundCount, 2);
  assert.equal(analysis.totalAgentDecisions, AGENT_IDS.length * 2);
  assert.ok(analysis.agentBreakdowns.every(item => item.tradeCount === 2));
  assert.ok(worldState.meta.trading.llmDecisionLedger.length >= AGENT_IDS.length * 2);
});

test('trading demo can replace simulated decisions with llm decisions', async () => {
  const worldState = createEmptyWorldState();
  applyTradingGameRound({ worldState, roundIndex: 1, nowMs: 1_780_000_000_000 });

  const fakeClient = {
    model: 'deepseek-ai/DeepSeek-V4-Flash',
    provider: 'siliconflow',
    async decide({ agentId }) {
      return {
        action: agentId === 'aggressive-breakout' ? 'BUY' : 'HOLD',
        confidence: 77,
        reason: `真实模型基于新闻、价格和记忆给出 ${agentId} 决策。`,
        evidence: ['模型证据一', '模型证据二'],
        strategyPatchNotes: ['模型建议提高新闻权重'],
        memoryLesson: '模型检索到贸易摩擦阶段的相似案例'
      };
    }
  };

  const result = await updateTradingGameWithLlm({
    worldState,
    roundIndex: 1,
    llmClient: fakeClient,
    nowMs: 1_780_000_060_000
  });

  assert.equal(result.updated, AGENT_IDS.length);
  assert.equal(worldState.meta.trading.llm.status, 'live');
  assert.equal(worldState.meta.trading.llm.model, 'deepseek-ai/DeepSeek-V4-Flash');
  assert.equal(worldState.agents['aggressive-breakout'].decision.source, 'llm');
  assert.equal(worldState.agents['aggressive-breakout'].decision.actionLabel, '买入');
  assert.match(worldState.agents['aggressive-breakout'].decision.reason, /真实模型/);
  assert.deepEqual(
    worldState.agents['balanced-strategist'].strategy.patchNotes,
    ['模型建议提高新闻权重']
  );
  assert.equal(worldState.avatars['aggressive-breakout'].bubbleText, '买入 ZS · 77%');
});

test('trading demo does not advance rounds while llm decisions are pending', () => {
  const worldState = createEmptyWorldState();
  const pendingClient = {
    model: 'deepseek-ai/DeepSeek-V4-Flash',
    provider: 'siliconflow',
    decide: () => new Promise(() => {})
  };
  const { createTradingGameDemo } = require('../adapter/tradingGameDemo');
  const demo = createTradingGameDemo({
    worldState,
    broadcastState: () => {},
    tickMs: 60_000,
    now: () => 1_780_000_000_000,
    llmClient: pendingClient
  });

  demo.tick();
  const firstDate = worldState.meta.trading.currentDate;
  assert.match(worldState.meta.trading.evaluation.method, /LLM真实决策生成中/);
  assert.ok(worldState.meta.trading.evaluation.analysis.sampleCount > 0);
  demo.tick();

  assert.equal(worldState.meta.trading.currentDate, firstDate);
  assert.equal(worldState.meta.trading.llm.status, 'running');
});

test('trading llm update times out a stuck agent and marks partial results', async () => {
  const worldState = createEmptyWorldState();
  applyTradingGameRound({ worldState, roundIndex: 1, nowMs: 1_780_000_000_000 });

  const stuckClient = {
    model: 'deepseek-ai/DeepSeek-V4-Flash',
    provider: 'siliconflow',
    timeoutMs: 5,
    decide({ agentId }) {
      if (agentId === 'balanced-strategist') return new Promise(() => {});
      return Promise.resolve({
        action: 'HOLD',
        confidence: 61,
        reason: `模型完成 ${agentId}`,
        evidence: ['证据'],
        strategyPatchNotes: ['补丁'],
        memoryLesson: '记忆'
      });
    }
  };

  const result = await updateTradingGameWithLlm({
    worldState,
    roundIndex: 1,
    llmClient: stuckClient,
    nowMs: 1_780_000_010_000
  });

  assert.equal(result.updated, AGENT_IDS.length - 1);
  assert.equal(result.failed, 1);
  assert.equal(worldState.meta.trading.llm.status, 'partial');
  assert.equal(worldState.agents['balanced-strategist'].decision.source, 'simulated');
  assert.equal(worldState.agents['conservative-hedger'].decision.source, 'llm');
});
