// Event log panel — grouped by simulation round with category filters.

const LOG_VERSION = 5;
const TRAINING_ROUND_COUNT = 6;
const AGENT_IDS = [
  'conservative-hedger',
  'balanced-strategist',
  'aggressive-breakout',
  'memory-auditor'
];

const KIND_META = {
  session_started: { category: 'system', order: 10, accent: '#047857' },
  session_ended:   { category: 'system', order: 11, accent: '#64748b' },
  status_changed:  { category: 'system', order: 12, accent: '#0284c7' },
  tool_invoked:    { category: 'system', order: 13, accent: '#b45309' },
  agent_decision:  { category: 'decision', order: 1, accent: '#2563eb' },
  llm_decision:    { category: 'decision', order: 1, accent: '#2563eb' },
  debate_round:    { category: 'debate', order: 2, accent: '#7c3aed' },
  trade_executed:  { category: 'execution', order: 3, accent: '#059669' }
};

const FILTER_KEYS = ['all', 'decision', 'debate', 'execution', 'system'];

const KIND_ORDER = Object.fromEntries(
  Object.entries(KIND_META).map(([kind, meta]) => [kind, meta.order])
);

function injectStyles(doc) {
  if (doc.getElementById('event-log-styles')) return;
  const style = doc.createElement('style');
  style.id = 'event-log-styles';
  style.textContent = `
    #event-log {
      position: fixed; left: 12px; bottom: 64px;
      width: 360px; max-width: calc(100vw - 24px);
      background: rgba(15, 23, 42, 0.92);
      border: 1px solid rgba(148, 163, 184, 0.3);
      border-radius: 12px;
      box-shadow: 0 10px 28px rgba(0,0,0,0.42);
      color: #e2e8f0;
      font: 12px/1.45 var(--font, system-ui, sans-serif);
      z-index: 10;
      display: flex; flex-direction: column;
      max-height: 320px;
      overflow: hidden;
    }
    #event-log[data-collapsed="1"] .event-log-body,
    #event-log[data-collapsed="1"] .event-log-toolbar { display: none; }
  `;
  doc.head.appendChild(style);
}

function escapeHtml(value) {
  return String(value ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');
}

function relativeAge(ts, now, i18n) {
  const s = Math.max(0, Math.round((now - ts) / 1000));
  const t = (key, vars) => i18n ? i18n.t(key, vars) : key;

  if (s < 5) return t('eventLog.time.now');
  if (s < 60) return t('eventLog.time.seconds', { n: s });
  if (s < 3600) return t('eventLog.time.minutes', { n: Math.floor(s / 60) });
  return t('eventLog.time.hours', { n: Math.floor(s / 3600) });
}

function stripRoundPrefix(text) {
  return String(text || '').replace(/^第\s*\d+\s*轮[：:]\s*/, '').trim();
}

function clonePayload(value) {
  try {
    return JSON.parse(JSON.stringify(value ?? null));
  } catch (_) {
    return null;
  }
}

function isPendingSummary(text) {
  return /等待/.test(String(text || ''));
}

export default class EventLog {
  constructor({ history, stateStore, i18n, mountEl = null, document: doc = document, window: win = window } = {}) {
    this.history = history || null;
    this.stateStore = stateStore || null;
    this.i18n = i18n;
    this.mountEl = mountEl;
    this.document = doc;
    this.window = win;
    this.embedded = Boolean(mountEl);
    this.collapsed = false;
    this.filter = 'all';
    this.selectedEventId = null;
    this._ageTick = null;
    this.events = [];
    this._eventIndex = new Map();
    this._lastTradingKey = '';
    this._tradingSnapshot = null;
    console.log(`[EventLog v${LOG_VERSION}] init`);

    if (!this.embedded) injectStyles(doc);
    this._build();
    this._bind();
    this._render();
    this._ageTick = win.setInterval(() => this._refreshAges(), 5000);
  }

  _t(key, vars) {
    return this.i18n ? this.i18n.t(key, vars) : key;
  }

  _build() {
    const doc = this.document;

    this.root = doc.createElement('aside');
    this.root.id = 'event-log';
    this.root.className = this.embedded ? 'event-log-panel ui-card' : '';
    this.root.dataset.collapsed = '0';
    this.root.dataset.empty = '1';
    this.root.setAttribute('aria-label', this._t('eventLog.aria'));

    this.header = doc.createElement('div');
    this.header.className = 'event-log-header event-header';
    this.header.innerHTML = `
      <div class="event-log-header-main">
        <span class="event-log-title">${escapeHtml(this._t('eventLog.panelTitle'))}</span>
        <span class="event-count event-log-count">0</span>
      </div>
      <button type="button" class="event-log-toggle" aria-expanded="true" aria-label="${escapeHtml(this._t('eventLog.toggle'))}">
        <span class="chev" aria-hidden="true"></span>
      </button>
    `;
    this.countEl = this.header.querySelector('.event-count');
    this.toggleBtn = this.header.querySelector('.event-log-toggle');
    this.root.appendChild(this.header);

    this.toolbar = doc.createElement('div');
    this.toolbar.className = 'event-log-toolbar';
    this.toolbar.setAttribute('role', 'tablist');
    this.filterButtons = new Map();
    for (const key of FILTER_KEYS) {
      const btn = doc.createElement('button');
      btn.type = 'button';
      btn.className = 'event-log-filter';
      btn.dataset.filter = key;
      btn.setAttribute('role', 'tab');
      btn.textContent = this._t(`eventLog.filters.${key}`);
      if (key === this.filter) btn.dataset.active = '1';
      this.toolbar.appendChild(btn);
      this.filterButtons.set(key, btn);
    }
    this.root.appendChild(this.toolbar);

    this.body = doc.createElement('div');
    this.body.className = 'event-log-body event-body';
    this.root.appendChild(this.body);

    (this.mountEl || doc.body).appendChild(this.root);
  }

  _bind() {
    this.header.addEventListener('click', ev => {
      if (ev.target.closest('.event-log-filter')) return;
      if (ev.target.closest('.event-log-toggle') || ev.target === this.header || ev.target.closest('.event-log-header-main')) {
        this.toggle();
      }
    });
    this.toggleBtn.addEventListener('click', ev => {
      ev.stopPropagation();
      this.toggle();
    });
    this.toolbar.addEventListener('click', ev => {
      const btn = ev.target?.closest?.('.event-log-filter');
      if (!btn) return;
      this.setFilter(btn.dataset.filter || 'all');
    });
    this.body.addEventListener('click', ev => {
      const row = ev.target?.closest?.('.event-log-item');
      if (!row) return;
      const eventId = row.dataset.eventId;
      const event = eventId ? this._eventIndex.get(eventId) : null;
      if (!event) return;

      this.selectedEventId = eventId;
      this.body.querySelectorAll('.event-log-item[data-selected="1"]').forEach(el => {
        el.dataset.selected = '0';
      });
      row.dataset.selected = '1';

      this.window.dispatchEvent(new CustomEvent('journal-event-selected', {
        bubbles: true,
        detail: { event: clonePayload(event) }
      }));
    });
    this._onHistoryEvent = () => this._render();
    this.window.addEventListener('history-event', this._onHistoryEvent);
    this._onWorldState = ev => {
      this._ingestTradingState(ev?.detail || null);
      this._render();
    };
    this.window.addEventListener('world-state', this._onWorldState);
    this._onEditor = ev => {
      const active = Boolean(ev?.detail?.active);
      if (this.root) this.root.style.display = active ? 'none' : '';
    };
    this.window.addEventListener('editor-mode', this._onEditor);
  }

  toggle() {
    this.collapsed = !this.collapsed;
    this.root.dataset.collapsed = this.collapsed ? '1' : '0';
    if (this.toggleBtn) {
      this.toggleBtn.setAttribute('aria-expanded', this.collapsed ? 'false' : 'true');
    }
  }

  setFilter(filter) {
    this.filter = FILTER_KEYS.includes(filter) ? filter : 'all';
    for (const [key, btn] of this.filterButtons) {
      btn.dataset.active = key === this.filter ? '1' : '0';
    }
    this._render();
  }

  _upsertEvent(eventKey, event) {
    const id = eventKey;
    const next = { ...event, id, eventKey };
    const existingIndex = this.events.findIndex(item => item.eventKey === eventKey);
    if (existingIndex >= 0) {
      this.events[existingIndex] = next;
    } else {
      this.events.push(next);
      if (this.events.length > 260) {
        const removed = this.events.splice(0, this.events.length - 260);
        for (const item of removed) this._eventIndex.delete(item.id);
      }
    }
    this._eventIndex.set(id, next);
  }

  _resolveRoundMeta(trading) {
    const roundIndex = Number.isFinite(trading?.debate?.round)
      ? trading.debate.round
      : Number.isFinite(trading?.execution?.round)
        ? trading.execution.round
        : Number.isFinite(trading?.currentRound)
          ? trading.currentRound
          : null;
    const roundDate = trading?.debate?.date || trading?.execution?.date || trading?.currentDate || null;
    const regime = trading?.debate?.regime || trading?.regime || null;
    return { roundIndex, roundDate, regime };
  }

  _ingestTradingState(state) {
    const trading = state?.meta?.trading;
    if (!trading) return;
    const key = `${trading.currentRound}:${trading.updatedAt || ''}:${trading.debate?.updatedAt || ''}:${trading.execution?.updatedAt || ''}:${trading.llmDecisionLedger?.length || 0}:${JSON.stringify(Object.values(state.agents || {}).map(a => a?.decision?.action || ''))}`;
    if (key === this._lastTradingKey) return;
    this._lastTradingKey = key;
    this._tradingSnapshot = trading;

    const { roundIndex, roundDate, regime } = this._resolveRoundMeta(trading);
    if (!Number.isFinite(roundIndex)) return;

    const ts = Date.parse(trading.updatedAt || '') || Date.now();
    const phase = roundIndex < TRAINING_ROUND_COUNT ? 'training' : 'test';

    const debate = trading.debate;
    if (
      debate?.summary &&
      !isPendingSummary(debate.summary) &&
      Array.isArray(debate.entries) &&
      debate.entries.length > 0
    ) {
      this._upsertEvent(`debate:${roundIndex}`, {
        kind: 'debate_round',
        ts: Date.parse(debate.updatedAt || '') || ts,
        label: stripRoundPrefix(debate.summary),
        sessionId: null,
        roundIndex,
        roundDate: debate.date || roundDate,
        regime: debate.regime || regime,
        phase,
        payload: { debate: clonePayload(debate) }
      });
    }

    const execution = trading.execution;
    if (
      execution?.summary &&
      !isPendingSummary(execution.summary) &&
      Array.isArray(execution.orders) &&
      execution.orders.length > 0
    ) {
      this._upsertEvent(`execution:${roundIndex}`, {
        kind: 'trade_executed',
        ts: Date.parse(execution.updatedAt || '') || ts,
        label: execution.summary,
        sessionId: null,
        roundIndex,
        roundDate: execution.date || roundDate,
        regime,
        phase,
        payload: { execution: clonePayload(execution) }
      });
    }

    for (const agentId of AGENT_IDS) {
      const agent = state.agents?.[agentId];
      const decision = agent?.decision;
      if (!decision?.action) continue;

      this._upsertEvent(`decision:${roundIndex}:${agentId}`, {
        kind: 'agent_decision',
        ts: Date.parse(decision.recordedAt || trading.updatedAt || '') || ts,
        label: `${agent.role || agentId} · ${decision.actionLabel || decision.action} ${decision.symbol || ''} · ${decision.confidence || ''}%`,
        sessionId: agentId,
        name: agent.role || agentId,
        roundIndex,
        roundDate,
        regime,
        phase,
        payload: {
          agentId,
          role: agent.role || agentId,
          decision: clonePayload(decision),
          score: clonePayload(agent.score)
        }
      });
    }
  }

  _categoryForEvent(ev) {
    const kind = ev.kind === 'llm_decision' ? 'agent_decision' : ev.kind;
    return KIND_META[kind]?.category || 'system';
  }

  _filterEvents(events) {
    if (this.filter === 'all') return events;
    return events.filter(ev => this._categoryForEvent(ev) === this.filter);
  }

  _groupEvents(events) {
    const groups = new Map();
    for (const ev of events) {
      const roundIndex = Number.isFinite(ev.roundIndex) ? ev.roundIndex : null;
      const groupKey = roundIndex === null ? 'system' : String(roundIndex);
      if (!groups.has(groupKey)) {
        groups.set(groupKey, {
          key: groupKey,
          roundIndex,
          roundDate: ev.roundDate || null,
          regime: ev.regime || null,
          phase: ev.phase || null,
          events: []
        });
      }
      const group = groups.get(groupKey);
      if (!group.roundDate && ev.roundDate) group.roundDate = ev.roundDate;
      if (!group.regime && ev.regime) group.regime = ev.regime;
      if (!group.phase && ev.phase) group.phase = ev.phase;
      group.events.push(ev);
    }

    for (const group of groups.values()) {
      group.events.sort((a, b) => {
        const kindA = a.kind === 'llm_decision' ? 'agent_decision' : a.kind;
        const kindB = b.kind === 'llm_decision' ? 'agent_decision' : b.kind;
        const orderDiff = (KIND_ORDER[kindA] || 99) - (KIND_ORDER[kindB] || 99);
        if (orderDiff !== 0) return orderDiff;
        return (a.ts || 0) - (b.ts || 0);
      });
    }

    return [...groups.values()].sort((a, b) => {
      if (a.key === 'system') return 1;
      if (b.key === 'system') return -1;
      return Number(b.roundIndex) - Number(a.roundIndex);
    });
  }

  _refreshAges() {
    const now = Date.now();
    this.body.querySelectorAll('.event-log-item').forEach(row => {
      const ts = Number(row.dataset.ts || 0);
      if (!ts) return;
      const age = row.querySelector('.event-age');
      if (age) age.textContent = relativeAge(ts, now, this.i18n);
    });
  }

  _formatStatus(status) {
    if (!status) return '';
    const key = {
      Working: 'session.status.working',
      Waiting: 'session.status.waiting',
      Errored: 'session.status.errored',
      Idle: 'session.status.idle',
      IdleStale: 'session.status.idleStale',
      Finished: 'session.status.finished'
    }[status] || null;
    return key && this.i18n ? this.i18n.t(key) : status;
  }

  _formatEventLabel(ev) {
    const name = ev.name || ev.sessionId || '';
    if (ev.kind === 'session_started') {
      return this._t('eventLog.labels.sessionStarted', { name }) || `${name} started`;
    }
    if (ev.kind === 'session_ended') {
      return this._t('eventLog.labels.sessionEnded', { name }) || `${name} signed off`;
    }
    if (ev.kind === 'status_changed') {
      return this._t('eventLog.labels.statusChanged', {
        name,
        from: this._formatStatus(ev.fromStatus),
        to: this._formatStatus(ev.toStatus || ev.status)
      }) || `${name} · ${ev.fromStatus || ''} → ${ev.toStatus || ev.status || ''}`;
    }
    if (ev.kind === 'tool_invoked') {
      return this._t('eventLog.labels.toolInvoked', {
        name,
        icon: ev.toolIcon || '·',
        tool: ev.toolName || this._t('eventLog.toolFallback')
      }) || `${name} · ${ev.toolName || 'tool'}`;
    }
    return ev.label || ev.kind;
  }

  _renderRoundHeader(group, doc) {
    const header = doc.createElement('div');
    header.className = 'event-log-round';

    if (group.key === 'system') {
      header.innerHTML = `<span class="event-log-round-label">${escapeHtml(this._t('eventLog.systemGroup'))}</span>`;
      return header;
    }

    const roundNo = Number(group.roundIndex) + 1;
    const phaseLabel = group.phase === 'training'
      ? this._t('eventLog.phase.training')
      : group.phase === 'test'
        ? this._t('eventLog.phase.test')
        : '';

    header.innerHTML = `
      <div class="event-log-round-main">
        <span class="event-log-round-badge">${escapeHtml(this._t('eventLog.roundLabel', { n: roundNo }))}</span>
        ${group.roundDate ? `<span class="event-log-round-date">${escapeHtml(group.roundDate)}</span>` : ''}
        ${phaseLabel ? `<span class="event-log-round-phase" data-phase="${escapeHtml(group.phase)}">${escapeHtml(phaseLabel)}</span>` : ''}
      </div>
      ${group.regime ? `<p class="event-log-round-regime">${escapeHtml(group.regime)}</p>` : ''}
    `;
    return header;
  }

  _renderEventItem(ev, doc, now) {
    const kind = ev.kind === 'llm_decision' ? 'agent_decision' : ev.kind;
    const meta = KIND_META[kind] || KIND_META.status_changed;
    const category = this._categoryForEvent(ev);
    const row = doc.createElement('button');
    row.type = 'button';
    row.className = 'event-log-item event-row';
    row.dataset.eventId = ev.id || '';
    row.dataset.sessionId = ev.sessionId || '';
    row.dataset.ts = String(ev.ts || '');
    row.dataset.kind = ev.kind || '';
    row.dataset.selected = ev.id === this.selectedEventId ? '1' : '0';

    const label = this._formatEventLabel(ev);
    const typeLabel = this._t(`eventLog.categories.${category}`);

    row.innerHTML = `
      <span class="event-log-marker" style="--event-accent:${meta.accent}"></span>
      <span class="event-log-content">
        <span class="event-log-type" data-category="${category}">${escapeHtml(typeLabel)}</span>
        <span class="event-text">${escapeHtml(label)}</span>
      </span>
      <span class="event-age">${escapeHtml(relativeAge(ev.ts, now, this.i18n))}</span>
    `;
    return row;
  }

  _render() {
    const allEvents = this.history ? this.history.getEvents() : this.events;
    this._eventIndex = new Map(allEvents.map(ev => [ev.id, ev]));
    const events = this._filterEvents(allEvents);
    const groups = this._groupEvents(events);
    const doc = this.document;
    const now = Date.now();

    this.countEl.textContent = String(allEvents.length);
    this.root.dataset.empty = events.length === 0 ? '1' : '0';
    this.body.textContent = '';

    if (!events.length) {
      const empty = doc.createElement('p');
      empty.className = 'event-log-empty';
      empty.textContent = this._t('eventLog.empty');
      this.body.appendChild(empty);
      return;
    }

    for (const group of groups) {
      this.body.appendChild(this._renderRoundHeader(group, doc));
      const list = doc.createElement('div');
      list.className = 'event-log-round-items';
      for (const ev of group.events) {
        list.appendChild(this._renderEventItem(ev, doc, now));
      }
      this.body.appendChild(list);
    }
  }

  destroy() {
    if (this._ageTick) this.window.clearInterval(this._ageTick);
    this.window.removeEventListener('history-event', this._onHistoryEvent);
    this.window.removeEventListener('world-state', this._onWorldState);
    this.window.removeEventListener('editor-mode', this._onEditor);
    if (this.root.parentNode) this.root.parentNode.removeChild(this.root);
  }
}
