const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

const DEFAULT_ROOT = path.join(__dirname, '..', 'runs');

function ensureDir(dirPath) {
  fs.mkdirSync(dirPath, { recursive: true });
}

function writeJson(filePath, value) {
  ensureDir(path.dirname(filePath));
  fs.writeFileSync(filePath, `${JSON.stringify(value, null, 2)}\n`, 'utf8');
}

function writeText(filePath, text) {
  ensureDir(path.dirname(filePath));
  fs.writeFileSync(filePath, text, 'utf8');
}

function safeSegment(value, fallback = 'unknown') {
  const raw = String(value || fallback).trim();
  return raw.replace(/[^a-zA-Z0-9._-]+/g, '-').replace(/^-+|-+$/g, '') || fallback;
}

function createRunId(now = new Date()) {
  const stamp = now.toISOString().replace(/[:.]/g, '-');
  const suffix = crypto.randomBytes(3).toString('hex');
  return `${stamp}_${suffix}`;
}

function roundDirName(roundIndex, date) {
  const idx = String(Number(roundIndex) + 1).padStart(3, '0');
  return `${idx}-${safeSegment(date, `round-${idx}`)}`;
}

function cloneJson(value) {
  return JSON.parse(JSON.stringify(value ?? null));
}

function buildAgentCallRecord({ outcome, strategyAfter, memoryAfter }) {
  const before = outcome.contextBefore || {};
  return {
    agentId: outcome.agentId,
    role: outcome.role || null,
    callOrder: outcome.callOrder ?? null,
    phase: outcome.isAuditor ? 'audit' : 'peer',
    source: outcome.source || (outcome.error ? 'fallback' : 'llm'),
    error: outcome.error || null,
    model: outcome.llmDecision?.model || null,
    provider: outcome.llmDecision?.provider || null,
    usage: outcome.llmDecision?.usage || null,
    attempts: outcome.llmDecision?.attempts || [],
    peerDecisionsInput: outcome.peerDecisionsInput || null,
    promptMessages: outcome.llmDecision?.messages || null,
    rawModelContent: outcome.llmDecision?.rawContent || null,
    baselineDecision: cloneJson(before.baselineDecision),
    strategyBefore: cloneJson(before.strategy),
    strategyAfter: cloneJson(strategyAfter),
    memoryBefore: cloneJson(before.memory),
    memoryAfter: cloneJson(memoryAfter),
    decision: outcome.llmDecision
      ? {
        action: outcome.llmDecision.action,
        confidence: outcome.llmDecision.confidence,
        reason: outcome.llmDecision.reason,
        evidence: outcome.llmDecision.evidence,
        strategyPatchNotes: outcome.llmDecision.strategyPatchNotes,
        memoryLesson: outcome.llmDecision.memoryLesson
      }
      : null
  };
}

function buildPresetExport({ worldState, runId, roundsCompleted }) {
  const trading = worldState?.meta?.trading || {};
  const agents = worldState?.agents || {};
  const agentIds = Object.keys(agents);
  const suggestedPresetActions = {};
  const suggestedPresetCommodities = {};
  const ledger = Array.isArray(trading.llmDecisionLedger) ? trading.llmDecisionLedger : [];

  for (const agentId of agentIds) {
    suggestedPresetActions[agentId] = ledger
      .filter(entry => entry.agentId === agentId)
      .sort((a, b) => Number(a.roundIndex) - Number(b.roundIndex))
      .map(entry => entry.action);
    suggestedPresetCommodities[agentId] = ledger
      .filter(entry => entry.agentId === agentId)
      .sort((a, b) => Number(a.roundIndex) - Number(b.roundIndex))
      .map(entry => entry.commodity);
  }

  return {
    generatedAt: new Date().toISOString(),
    sourceRunId: runId,
    roundsCompleted,
    trainingTradeCount: 6,
    agents: Object.fromEntries(
      agentIds.map(agentId => {
        const agent = agents[agentId];
        const strategy = agent?.strategy || {};
        return [
          agentId,
          {
            role: agent?.role || null,
            finalPromptText: strategy.promptText || strategy.basePrompt || null,
            basePrompt: strategy.basePrompt || null,
            promptLabel: strategy.promptLabel || null,
            promptStage: strategy.promptStage ?? null,
            patchNotes: Array.isArray(strategy.patchNotes) ? strategy.patchNotes : [],
            promptIterations: Array.isArray(strategy.promptIterations)
              ? strategy.promptIterations
              : [],
            memoryLesson: agent?.memory?.lesson || null,
            decisionLedger: ledger.filter(entry => entry.agentId === agentId)
          }
        ];
      })
    ),
    evaluation: cloneJson(trading.evaluation || null),
    suggestedPresetActions,
    suggestedPresetCommodities,
    usageNotes: [
      'suggestedPresetActions 可用于替换 adapter/simulationEngine.js 中 ACTIONS_BY_AGENT 的对应序列（仅 LLM 来源轮次）。',
      'suggestedPresetCommodities 可用于替换 adapter/simulationEngine.js 中 COMMODITIES_BY_AGENT 的对应序列。',
      'agents.*.patchNotes 与 promptIterations 可用于更新真实 prompt 迭代展示与 composePromptText 规则。',
      'evaluation.rankings 可直接用于论文图表与策略评分章节。'
    ]
  };
}

function buildPaperMarkdown({ manifest, summary, presetExport }) {
  const lines = [];
  lines.push('# 期货多智能体 LLM 仿真实验记录');
  lines.push('');
  lines.push(`- 运行 ID：\`${manifest.runId}\``);
  lines.push(`- 开始时间：${manifest.startedAt}`);
  if (manifest.finishedAt) lines.push(`- 结束时间：${manifest.finishedAt}`);
  lines.push(`- LLM：${manifest.llm?.provider || '--'} / ${manifest.llm?.model || '--'}`);
  lines.push(`- 完成轮次：${summary.roundsRecorded}/${summary.totalRounds}`);
  lines.push('');

  lines.push('## 综合评分（相对 alpha）');
  lines.push('');
  const rankings = summary.evaluation?.rankings || [];
  for (const item of rankings) {
    lines.push(
      `- **${item.role}**：总分 ${item.totalScore}（训练 ${item.trainingScore} / 测试 ${item.testScore}），命中率 ${item.hitRate}%`
    );
  }
  lines.push('');

  lines.push('## Prompt 迭代摘要');
  lines.push('');
  for (const [agentId, agentData] of Object.entries(presetExport.agents || {})) {
    const iterations = agentData.promptIterations || [];
    if (!iterations.length) {
      lines.push(`- ${agentData.role || agentId}：本轮运行未触发 prompt 版本切换`);
      continue;
    }
    for (const iter of iterations) {
      lines.push(
        `- ${agentData.role || agentId}：第 ${Number(iter.roundIndex) + 1} 轮 ${iter.fromLabel} → ${iter.toLabel}（${iter.date || '--'}）`
      );
      if (iter.reason) lines.push(`  - 原因：${iter.reason}`);
    }
  }
  lines.push('');

  lines.push('## 辩论与审计（末轮快照）');
  lines.push('');
  const lastRound = summary.lastRound || {};
  if (lastRound.debate?.summary) {
    lines.push(`### 辩论场`);
    lines.push('');
    lines.push(lastRound.debate.summary);
    lines.push('');
    for (const entry of lastRound.debate.entries || []) {
      lines.push(
        `- ${entry.role}：${entry.actionLabel} ${entry.symbol || ''}（置信度 ${entry.confidence}%）— ${entry.reason}`
      );
    }
    lines.push('');
  }
  if (lastRound.audit?.decision?.reason) {
    lines.push('### 记忆审计');
    lines.push('');
    lines.push(lastRound.audit.decision.reason);
    lines.push('');
  }

  lines.push('## 数据文件说明');
  lines.push('');
  lines.push('- `rounds/<轮次>/llm-calls.json`：各智能体 LLM 输入输出、token 用量');
  lines.push('- `rounds/<轮次>/debate.json`：辩论场过程与共识/异议');
  lines.push('- `rounds/<轮次>/audit-process.json`：审计官收到的同业观点与审计结论');
  lines.push('- `rounds/<轮次>/scores.json`：该轮累计评分快照');
  lines.push('- `preset-export.json`：用于回写预设的可机读摘要');
  lines.push('');

  return `${lines.join('\n')}\n`;
}

function createRunRecorder({
  rootDir = DEFAULT_ROOT,
  enabled = true,
  runId = null,
  now = () => Date.now()
} = {}) {
  if (!enabled) {
    return {
      enabled: false,
      runId: null,
      runDir: null,
      startRun() {},
      async recordRound() {},
      finalizeRun() {}
    };
  }

  const resolvedRunId = runId || createRunId(new Date(now()));
  const runDir = path.join(rootDir, resolvedRunId);
  let started = false;
  let roundsRecorded = 0;
  let manifest = {
    runId: resolvedRunId,
    startedAt: null,
    finishedAt: null,
    status: 'pending',
    llm: null,
    config: {},
    roundsRecorded: 0
  };
  let lastRoundSnapshot = null;

  function persistManifest() {
    writeJson(path.join(runDir, 'manifest.json'), manifest);
  }

  return {
    enabled: true,
    runId: resolvedRunId,
    runDir,

    startRun({
      llm = null,
      tickMs = null,
      llmParallel = false,
      trainingTradeCount = 6,
      totalRounds = 36
    } = {}) {
      if (started) return;
      started = true;
      manifest = {
        ...manifest,
        startedAt: new Date(now()).toISOString(),
        status: 'running',
        llm: llm ? cloneJson(llm) : null,
        config: {
          tickMs,
          llmParallel: Boolean(llmParallel),
          trainingTradeCount,
          totalRounds
        },
        roundsRecorded: 0
      };
      ensureDir(path.join(runDir, 'rounds'));
      persistManifest();
    },

    async recordRound({
      roundIndex,
      round,
      outcomes = [],
      failures = [],
      trading = {},
      agents = {},
      nowMs = now()
    }) {
      if (!started) {
        this.startRun();
      }

      const roundName = roundDirName(roundIndex, round?.date);
      const roundDir = path.join(runDir, 'rounds', roundName);
      const agentMap = agents || {};

      const llmCalls = outcomes.map((outcome, index) =>
        buildAgentCallRecord({
          outcome: { ...outcome, callOrder: index + 1 },
          strategyAfter: agentMap[outcome.agentId]?.strategy,
          memoryAfter: agentMap[outcome.agentId]?.memory
        })
      );

      const auditorCall = llmCalls.find(item => item.phase === 'audit') || null;
      const peerCalls = llmCalls.filter(item => item.phase === 'peer');

      const roundMeta = {
        roundIndex,
        roundNumber: roundIndex + 1,
        date: round?.date || null,
        regime: round?.regime || null,
        phase: roundIndex < (manifest.config.trainingTradeCount || 6) ? 'training' : 'test',
        prices: cloneJson(round?.prices),
        news: cloneJson(round?.news),
        dataSource: round?.dataSource || null,
        recordedAt: new Date(nowMs).toISOString()
      };

      writeJson(path.join(roundDir, 'round-meta.json'), roundMeta);
      writeJson(path.join(roundDir, 'llm-calls.json'), {
        round: roundMeta,
        failures: cloneJson(failures),
        calls: llmCalls
      });
      writeJson(path.join(roundDir, 'decisions.json'), {
        round: roundMeta,
        ledger: cloneJson(trading.llmDecisionLedger),
        agents: Object.fromEntries(
          Object.entries(agentMap).map(([agentId, agent]) => [
            agentId,
            {
              role: agent?.role || null,
              decision: cloneJson(agent?.decision),
              score: cloneJson(agent?.score),
              strategy: {
                promptLabel: agent?.strategy?.promptLabel,
                promptStage: agent?.strategy?.promptStage,
                patchNotes: agent?.strategy?.patchNotes
              }
            }
          ])
        )
      });
      writeJson(path.join(roundDir, 'debate.json'), cloneJson(trading.debate || null));
      writeJson(path.join(roundDir, 'peer-review.json'), cloneJson(trading.peerReview || null));
      writeJson(path.join(roundDir, 'audit-process.json'), {
        round: roundMeta,
        peerReview: cloneJson(trading.peerReview || null),
        peerCalls,
        auditorCall,
        auditorDecision: auditorCall?.decision || null,
        crowding: trading.debate?.consensus || null,
        dissent: trading.debate?.dissent || []
      });
      writeJson(path.join(roundDir, 'execution-gate.json'), cloneJson(trading.execution || null));
      writeJson(path.join(roundDir, 'scores.json'), cloneJson(trading.evaluation || null));
      writeJson(path.join(roundDir, 'prompt-iteration.json'), cloneJson(trading.promptBoard || null));
      writeJson(path.join(roundDir, 'risk.json'), cloneJson(trading.risk || null));

      roundsRecorded += 1;
      manifest.roundsRecorded = roundsRecorded;
      manifest.lastRoundIndex = roundIndex;
      manifest.lastRoundDate = round?.date || null;
      persistManifest();

      lastRoundSnapshot = {
        roundIndex,
        debate: cloneJson(trading.debate || null),
        audit: {
          peerReview: cloneJson(trading.peerReview || null),
          decision: auditorCall?.decision || null
        },
        evaluation: cloneJson(trading.evaluation || null)
      };
    },

    finalizeRun({ worldState, status = 'completed' } = {}) {
      if (!started) return null;
      manifest.finishedAt = new Date(now()).toISOString();
      manifest.status = status;
      manifest.roundsRecorded = roundsRecorded;
      persistManifest();

      const trading = worldState?.meta?.trading || {};
      const summary = {
        runId: resolvedRunId,
        roundsRecorded,
        totalRounds: manifest.config.totalRounds || 36,
        evaluation: cloneJson(trading.evaluation || null),
        llm: cloneJson(trading.llm || manifest.llm),
        lastRound: lastRoundSnapshot
      };
      writeJson(path.join(runDir, 'summary.json'), summary);

      const presetExport = buildPresetExport({
        worldState,
        runId: resolvedRunId,
        roundsCompleted: roundsRecorded
      });
      writeJson(path.join(runDir, 'preset-export.json'), presetExport);
      writeText(
        path.join(runDir, 'paper-export.md'),
        buildPaperMarkdown({ manifest, summary, presetExport })
      );

      return { runDir, summary, presetExport };
    }
  };
}

function listRuns(rootDir = DEFAULT_ROOT) {
  if (!fs.existsSync(rootDir)) return [];
  return fs
    .readdirSync(rootDir, { withFileTypes: true })
    .filter(entry => entry.isDirectory())
    .map(entry => {
      const manifestPath = path.join(rootDir, entry.name, 'manifest.json');
      if (!fs.existsSync(manifestPath)) {
        return { runId: entry.name, status: 'unknown' };
      }
      try {
        return JSON.parse(fs.readFileSync(manifestPath, 'utf8'));
      } catch (_) {
        return { runId: entry.name, status: 'corrupt' };
      }
    })
    .sort((a, b) => String(b.startedAt || '').localeCompare(String(a.startedAt || '')));
}

module.exports = {
  DEFAULT_ROOT,
  createRunId,
  createRunRecorder,
  listRuns,
  buildPresetExport,
  buildPaperMarkdown
};
