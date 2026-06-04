const test = require('node:test');
const assert = require('node:assert/strict');
const { createTradingWorldState } = require('../adapter/tradingWorldState');
const {
  AGENT_IDS,
  ROUNDS,
  TRAINING_TRADE_COUNT,
  applyTradingGameRound,
  updateTradingGameWithLlm,
  buildDebateRound,
  buildExecutionGate
} = require('../adapter/simulationEngine');

test('trading rounds define 36 readable historical scenarios', () => {
  assert.equal(ROUNDS.length, 36);
  assert.equal(TRAINING_TRADE_COUNT, 6);
  for (const round of ROUNDS) {
    assert.ok(round.regime.length >= 20, `regime too short for ${round.date}`);
    assert.equal(round.news.length, 3);
    for (const item of round.news) {
      assert.ok(item.length >= 12, `news too short for ${round.date}`);
    }
  }
});

function createEmptyWorldState() {
  return createTradingWorldState();
}

test('trading demo projects four strategy agents with debate and execution gate', () => {
  const worldState = createEmptyWorldState();

  applyTradingGameRound({ worldState, roundIndex: 0, nowMs: 1_780_000_000_000 });

  assert.deepEqual(Object.keys(worldState.agents).sort(), AGENT_IDS.slice().sort());
  assert.equal(worldState.meta.trading.mode, 'futures-agent-simulation');
  assert.equal(worldState.meta.trading.commodities.length, 3);
  assert.equal(worldState.meta.trading.news.length, 3);
  assert.equal(worldState.meta.trading.evaluation.rankings.length, 4);
  assert.match(worldState.meta.trading.evaluation.method, /累计评分/);
  assert.equal(worldState.meta.trading.debate.entries.length, 4);
  assert.match(worldState.meta.trading.debate.summary, /轮/);
  assert.equal(worldState.meta.trading.execution.orders.length, 4);
  assert.match(worldState.meta.trading.execution.summary, /交易执行门/);

  const balanced = worldState.agents['balanced-strategist'];
  assert.equal(balanced.role, '均衡型');
  assert.equal(balanced.strategy.promptStage, 0);
  assert.equal(balanced.strategy.promptLabel, 'prompt');
  assert.ok(balanced.decision.reason.includes('价格'));
  assert.ok(Array.isArray(balanced.memory.retrieved));
  assert.equal(balanced.memory.retrieved.length, 3);
  assert.equal(typeof balanced.score.total, 'number');
});

test('trading timeline carries per-round prices for market charts', () => {
  const worldState = createEmptyWorldState();
  applyTradingGameRound({ worldState, roundIndex: 2, nowMs: 1_780_000_000_000 });
  const timeline = worldState.meta.trading.timeline;
  assert.equal(timeline.length, 3);
  for (const entry of timeline) {
    assert.ok(entry.prices, `timeline entry ${entry.index} missing prices`);
    assert.ok(Number.isFinite(entry.prices.gold));
    assert.ok(Number.isFinite(entry.prices.soybean));
    assert.ok(Number.isFinite(entry.prices.crude_oil));
  }
});

test('trading demo advances decisions and strategy patch notes by round', () => {
  const worldState = createEmptyWorldState();

  applyTradingGameRound({ worldState, roundIndex: 0, nowMs: 1_780_000_000_000 });
  const firstDate = worldState.meta.trading.currentDate;
  const firstAction = worldState.agents['aggressive-breakout'].decision.action;

  applyTradingGameRound({ worldState, roundIndex: 3, nowMs: 1_780_000_090_000 });

  assert.notEqual(worldState.meta.trading.currentDate, firstDate);
  assert.notEqual(worldState.agents['aggressive-breakout'].decision.action, firstAction);
  assert.equal(worldState.agents['aggressive-breakout'].strategy.promptStage, 1);
  assert.equal(worldState.agents['aggressive-breakout'].strategy.promptLabel, 'promptv1');
  assert.ok(
    worldState.agents['aggressive-breakout'].strategy.patchNotes.some(note =>
      note.includes('v2：')
    )
  );
  assert.equal(worldState.meta.trading.timeline.length, 4);
});

test('trading demo exposes prompt board and risk snapshot for UI panels', () => {
  const worldState = createEmptyWorldState();

  applyTradingGameRound({ worldState, roundIndex: 0, nowMs: 1_780_000_000_000 });
  const promptBoard = worldState.meta.trading.promptBoard;
  const risk = worldState.meta.trading.risk;

  assert.equal(promptBoard.agents.length, 4);
  assert.ok(promptBoard.agents.every(item => typeof item.currentPrompt === 'string'));
  assert.equal(risk.agents.length, 4);
  assert.ok(risk.summary.includes('回撤'));
  assert.ok(risk.agents.every(item => item.drawdown > 0));
  assert.ok(risk.agents.every(item => item.confidence >= 40));

  applyTradingGameRound({ worldState, roundIndex: 1, nowMs: 1_780_000_050_000 });
  assert.equal(worldState.agents['conservative-hedger'].strategy.promptIterations.length, 0);

  applyTradingGameRound({ worldState, roundIndex: 3, nowMs: 1_780_000_090_000 });
  const aggressive = worldState.agents['aggressive-breakout'].strategy;
  assert.ok(Array.isArray(aggressive.promptIterations));
  assert.equal(aggressive.promptIterations.length, 1);
  assert.ok(aggressive.promptIterations.every(item => item.from !== item.to));
  const firstIter = aggressive.promptIterations[0];
  assert.equal(firstIter.id, 'promptv1');
  assert.equal(firstIter.fromLabel, 'prompt');
  assert.equal(firstIter.toLabel, 'promptv1');
  assert.equal(
    worldState.meta.trading.promptBoard.agents.find(item => item.agentId === 'aggressive-breakout').iterations.length,
    aggressive.promptIterations.length
  );
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
    model: 'deepseek-chat',
    provider: 'deepseek',
    async decide({ agentId, roundIndex }) {
      return {
        action: roundIndex % 2 === 0
          ? (agentId === 'memory-auditor' ? 'HOLD' : 'BUY')
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

test('llm strategy patches accumulate during training and freeze in test phase', async () => {
  const worldState = createEmptyWorldState();
  applyTradingGameRound({ worldState, roundIndex: 0, nowMs: 1_780_000_000_000, skipPresetScoring: true });
  await updateTradingGameWithLlm({
    worldState,
    roundIndex: 0,
    llmClient: {
      async decide() {
        return {
          action: 'HOLD',
          confidence: 70,
          reason: '训练轮决策',
          evidence: ['证据'],
          strategyPatchNotes: ['提高库存新闻权重'],
          memoryLesson: '库存上升阶段应降低多头敞口'
        };
      }
    },
    nowMs: 1_780_000_060_000
  });

  applyTradingGameRound({ worldState, roundIndex: 1, nowMs: 1_780_000_090_000, skipPresetScoring: true });
  const strategist = worldState.agents['balanced-strategist'];
  assert.ok(
    strategist.strategy.pendingLlmPatchNotes?.some(note => note.includes('提高库存新闻权重'))
  );
  assert.equal(strategist.memory.lesson, '库存上升阶段应降低多头敞口');

  applyTradingGameRound({ worldState, roundIndex: 3, nowMs: 1_780_000_150_000, skipPresetScoring: true });
  assert.ok(
    worldState.agents['balanced-strategist'].strategy.patchNotes.some(note =>
      note.includes('提高库存新闻权重')
    )
  );

  applyTradingGameRound({ worldState, roundIndex: 6, nowMs: 1_780_000_300_000, skipPresetScoring: true });
  const frozen = worldState.agents['balanced-strategist'].strategy;
  const patchCountBefore = frozen.patchNotes.length;
  await updateTradingGameWithLlm({
    worldState,
    roundIndex: 6,
    llmClient: {
      async decide() {
        return {
          action: 'BUY',
          confidence: 65,
          reason: '测试轮决策',
          evidence: ['证据'],
          strategyPatchNotes: ['测试段不应追加的新规则'],
          memoryLesson: '测试段新记忆'
        };
      }
    },
    nowMs: 1_780_000_360_000
  });
  assert.equal(
    worldState.agents['balanced-strategist'].strategy.patchNotes.length,
    patchCountBefore
  );
  assert.ok(
    !worldState.agents['balanced-strategist'].strategy.patchNotes.some(note =>
      note.includes('测试段不应追加')
    )
  );
});

test('trading demo can replace simulated decisions with llm decisions', async () => {
  const worldState = createEmptyWorldState();
  applyTradingGameRound({ worldState, roundIndex: 1, nowMs: 1_780_000_000_000 });

  const fakeClient = {
    model: 'deepseek-chat',
    provider: 'deepseek',
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
  assert.equal(worldState.meta.trading.llm.model, 'deepseek-chat');
  assert.equal(worldState.agents['aggressive-breakout'].decision.source, 'llm');
  assert.equal(worldState.agents['aggressive-breakout'].decision.actionLabel, '买入');
  assert.match(worldState.agents['aggressive-breakout'].decision.reason, /真实模型/);
  assert.ok(
    worldState.agents['balanced-strategist'].strategy.pendingLlmPatchNotes?.some(note =>
      note.includes('模型建议提高新闻权重')
    )
  );
  assert.equal(worldState.meta.trading.debate.entries.length, 4);
  assert.equal(worldState.meta.trading.execution.orders.length, 4);
});

test('trading demo does not advance rounds while llm decisions are pending', () => {
  const worldState = createEmptyWorldState();
  const pendingClient = {
    model: 'deepseek-chat',
    provider: 'deepseek',
    decide: () => new Promise(() => {})
  };
  const { createSimulationEngine } = require('../adapter/simulationEngine');
  const demo = createSimulationEngine({
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
    model: 'deepseek-chat',
    provider: 'deepseek',
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

  assert.equal(result.updated, AGENT_IDS.length);
  assert.equal(result.failed, 1);
  assert.equal(worldState.meta.trading.llm.status, 'partial');
  assert.equal(worldState.agents['balanced-strategist'].decision.source, 'fallback');
  assert.match(worldState.agents['balanced-strategist'].decision.reason, /回退预设/);
  assert.equal(worldState.agents['conservative-hedger'].decision.source, 'llm');
});

test('trading llm fallback decisions still accumulate evaluation scores', async () => {
  const worldState = createEmptyWorldState();
  const failingClient = {
    model: 'deepseek-chat',
    provider: 'deepseek',
    decide: async () => {
      throw new Error('LLM unavailable');
    }
  };

  for (let roundIndex = 0; roundIndex < 8; roundIndex += 1) {
    applyTradingGameRound({
      worldState,
      roundIndex,
      nowMs: 1_780_000_000_000 + roundIndex * 1000,
      skipPresetScoring: true
    });
    await updateTradingGameWithLlm({
      worldState,
      roundIndex,
      llmClient: failingClient,
      nowMs: 1_780_000_000_000 + roundIndex * 1000
    });
  }

  assert.equal(worldState.meta.trading.llmDecisionLedger.length, AGENT_IDS.length * 8);
  const rankings = worldState.meta.trading.evaluation.rankings;
  assert.equal(rankings.length, 4);
  assert.ok(rankings.every(item => Array.isArray(item.trades) && item.trades.length === 8));
  assert.ok(rankings.every(item => item.lastTrade));
  assert.ok(rankings.some(item => Number.isFinite(item.totalScore) && item.totalScore !== 0));
});

test('memory auditor runs after peers and receives peer review context', async () => {
  const worldState = createEmptyWorldState();
  applyTradingGameRound({ worldState, roundIndex: 2, nowMs: 1_780_000_000_000, skipPresetScoring: true });

  const callOrder = [];
  const fakeClient = {
    provider: 'deepseek',
    model: 'deepseek-chat',
    async decide(input) {
      callOrder.push(input.agentId);
      const peerCount = Array.isArray(input.peerDecisions) ? input.peerDecisions.length : 0;
      return {
        action: input.agentId === 'memory-auditor' ? 'HOLD' : 'BUY',
        confidence: input.agentId === 'memory-auditor' ? 58 : 70,
        reason: input.agentId === 'memory-auditor'
          ? `审阅 ${peerCount} 位同业观点后保持观望`
          : `${input.agentId} 决策`,
        evidence: ['证据'],
        strategyPatchNotes: [],
        memoryLesson: '记忆',
        model: input.agentId === 'memory-auditor' ? 'deepseek-v4-flash' : 'deepseek-v4-flash',
        provider: 'deepseek'
      };
    }
  };

  await updateTradingGameWithLlm({
    worldState,
    roundIndex: 2,
    llmClient: fakeClient,
    nowMs: 1_780_000_060_000
  });

  assert.deepEqual(callOrder.slice(0, 3), [
    'conservative-hedger',
    'balanced-strategist',
    'aggressive-breakout'
  ]);
  assert.equal(callOrder[3], 'memory-auditor');
  assert.equal(worldState.meta.trading.peerReview.peers.length, 3);
  assert.match(worldState.agents['memory-auditor'].decision.reason, /审阅 3 位同业/);
  assert.ok(
    worldState.agents['conservative-hedger'].strategy.basePrompt.includes('【定位】')
  );
});

test('simulation engine stops after 36 rounds instead of looping', async () => {
  const worldState = createEmptyWorldState();
  const { ROUNDS, createSimulationEngine } = require('../adapter/simulationEngine');
  const engine = createSimulationEngine({
    worldState,
    tickMs: 1,
    llmClient: {
      provider: 'test',
      model: 'deepseek-v4-flash',
      async decide() {
        return {
          action: 'HOLD',
          confidence: 55,
          reason: '测试决策',
          evidence: ['测试'],
          strategyPatchNotes: [],
          memoryLesson: '测试'
        };
      }
    },
    now: () => 1_780_000_000_000
  });
  engine.start();
  for (let i = 0; i < ROUNDS.length + 2; i += 1) {
    await new Promise(resolve => setTimeout(resolve, 30));
  }
  assert.equal(worldState.meta.trading.simulationComplete, true);
  assert.equal(worldState.meta.trading.totalRounds, ROUNDS.length);
  assert.equal(worldState.agents['conservative-hedger'].status, 'Finished');
  engine.stop();
});
