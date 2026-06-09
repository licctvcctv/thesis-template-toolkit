const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('fs');
const os = require('os');
const path = require('path');
const { createRunRecorder } = require('../server/runRecorder');
const { createTradingWorldState } = require('../adapter/tradingWorldState');
const {
  applyTradingGameRound,
  updateTradingGameWithLlm
} = require('../adapter/simulationEngine');

test('run recorder writes per-round artifacts and preset export', async () => {
  const rootDir = fs.mkdtempSync(path.join(os.tmpdir(), 'futures-run-'));
  const recorder = createRunRecorder({ rootDir, runId: 'test-run-001' });
  recorder.startRun({
    llm: { provider: 'test', model: 'deepseek-chat' },
    tickMs: 1000,
    llmParallel: false,
    trainingTradeCount: 6,
    totalRounds: 36
  });

  const worldState = createTradingWorldState();
  applyTradingGameRound({ worldState, roundIndex: 0, nowMs: 1_780_000_000_000, skipPresetScoring: true });

  const fakeClient = {
    provider: 'deepseek',
    model: 'deepseek-chat',
    async decide(input) {
      return {
        action: input.agentId === 'memory-auditor' ? 'HOLD' : 'BUY',
        confidence: 72,
        reason: `${input.agentId} 真实模型决策`,
        evidence: ['证据A'],
        strategyPatchNotes: input.agentId === 'conservative-hedger' ? ['收紧止损规则'] : [],
        memoryLesson: '记忆更新',
        model: 'deepseek-chat',
        provider: 'deepseek',
        messages: [{ role: 'system', content: 'system' }],
        rawContent: '{"action":"BUY"}'
      };
    }
  };

  await updateTradingGameWithLlm({
    worldState,
    roundIndex: 0,
    llmClient: fakeClient,
    runRecorder: recorder,
    nowMs: 1_780_000_010_000
  });

  const finalized = recorder.finalizeRun({ worldState, status: 'completed' });
  const roundDir = path.join(rootDir, 'test-run-001', 'rounds');
  const roundFolders = fs.readdirSync(roundDir);
  assert.equal(roundFolders.length, 1);

  const llmCalls = JSON.parse(
    fs.readFileSync(path.join(roundDir, roundFolders[0], 'llm-calls.json'), 'utf8')
  );
  assert.equal(llmCalls.calls.length, 4);
  assert.ok(llmCalls.calls[0].promptMessages);
  assert.ok(fs.existsSync(path.join(roundDir, roundFolders[0], 'debate.json')));
  assert.ok(fs.existsSync(path.join(roundDir, roundFolders[0], 'audit-process.json')));
  assert.ok(fs.existsSync(path.join(rootDir, 'test-run-001', 'preset-export.json')));
  assert.ok(fs.existsSync(path.join(rootDir, 'test-run-001', 'paper-export.md')));
  assert.equal(finalized.presetExport.roundsCompleted, 1);
  assert.equal(
    finalized.presetExport.suggestedPresetActions['conservative-hedger'][0],
    'BUY'
  );

  fs.rmSync(rootDir, { recursive: true, force: true });
});
