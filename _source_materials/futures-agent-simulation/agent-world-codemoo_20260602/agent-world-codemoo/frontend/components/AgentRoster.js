// DOM roster of live trading agents. Reads from stateStore on a short tick.

const ROSTER_VERSION = 3;

const STATUS_META = {
  Working:   { dot: '#4ade80', key: 'session.status.working' },
  Waiting:   { dot: '#fbbf24', key: 'session.status.waiting' },
  Errored:   { dot: '#f87171', key: 'session.status.errored' },
  Idle:      { dot: '#94a3b8', key: 'session.status.idle' },
  IdleStale: { dot: '#64748b', key: 'session.status.idleStale' },
  Finished:  { dot: '#7280a0', key: 'session.status.finished' }
};

const TICK_MS = 400;

function injectStyles(doc) {
  if (doc.getElementById('agent-roster-styles')) return;
  const style = doc.createElement('style');
  style.id = 'agent-roster-styles';
  style.textContent = `
    #agent-roster {
      position: relative;
      top: auto;
      left: auto;
      width: 100%;
      max-height: none;
      background: transparent;
      border: none;
      border-radius: 0;
      box-shadow: none;
      color: inherit;
      font: inherit;
      z-index: auto;
      display: flex;
      flex-direction: column;
      overflow: visible;
      transition: none;
    }
    #agent-roster[data-shell="1"] {
      background: var(--bg-card, rgba(15, 23, 42, 0.92));
      border: 1px solid var(--border, rgba(148, 163, 184, 0.35));
      border-radius: 12px;
      box-shadow: var(--shadow-card, 0 10px 28px rgba(0,0,0,0.08));
      overflow: hidden;
    }
    #agent-roster[data-empty="1"] { opacity: 0; pointer-events: none; transform: translateY(-4px); }
    /* Hide roster on narrow viewports — agents are still clickable in
       the canvas, and the DOM event log covers the list view. */
    @media (max-width: 900px) {
      #agent-roster { display: none; }
    }
    #agent-roster .roster-header {
      display: flex; align-items: center; justify-content: space-between;
      padding: 9px 12px;
      background: rgba(30, 41, 59, 0.6);
      border-bottom: 1px solid rgba(148, 163, 184, 0.2);
      font-weight: 600;
      color: #fbbf24;
      font-size: 11px;
      letter-spacing: 0.04em;
      text-transform: uppercase;
      user-select: none;
    }
    #agent-roster .roster-count {
      font-variant-numeric: tabular-nums;
      color: #cbd5e1;
      text-transform: none;
      font-weight: 500;
      font-size: 10px;
    }
    #agent-roster .roster-list {
      list-style: none; margin: 0; padding: 8px;
      overflow: visible;
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 10px;
    }
    #agent-roster[data-shell="1"] .roster-list {
      padding: 14px;
      gap: 12px;
    }
    #agent-roster .roster-row {
      display: flex;
      flex-direction: column;
      gap: 8px;
      align-items: stretch;
      padding: 12px 14px;
      cursor: pointer;
      border: 1px solid rgba(148, 163, 184, 0.18);
      border-radius: 10px;
      background: rgba(15, 23, 42, 0.35);
      border-left: 1px solid rgba(148, 163, 184, 0.18);
      transition: background 0.12s ease, border-color 0.12s ease, box-shadow 0.12s ease;
    }
    #agent-roster[data-shell="1"] .roster-row {
      background: #fff;
      border-color: var(--border, #e5e7eb);
    }
    #agent-roster .roster-row:hover {
      background: rgba(56, 189, 248, 0.10);
      border-color: rgba(56, 189, 248, 0.35);
    }
    #agent-roster .roster-row[data-selected="1"] {
      background: rgba(56, 189, 248, 0.12);
      border-color: rgba(56, 189, 248, 0.55);
      box-shadow: inset 0 0 0 1px rgba(56, 189, 248, 0.18);
    }
    #agent-roster .roster-row-top {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 8px;
    }
    #agent-roster .roster-row-main {
      display: flex;
      align-items: center;
      gap: 8px;
      min-width: 0;
    }
    #agent-roster .roster-row[data-status="Working"] .roster-status-dot { animation: roster-pulse 1.4s ease-in-out infinite; }
    #agent-roster .roster-row[data-status="Finished"],
    #agent-roster .roster-row[data-status="IdleStale"] {
      opacity: 0.55;
    }
    #agent-roster .roster-status-dot {
      width: 8px; height: 8px; border-radius: 50%;
      box-shadow: 0 0 0 2px rgba(15, 23, 42, 0.4);
    }
    #agent-roster .roster-main {
      display: flex; flex-direction: column; gap: 1px;
      min-width: 0;
    }
    #agent-roster .roster-name {
      font-weight: 600; color: #f1f5f9;
      white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
    }
    #agent-roster .roster-activity {
      color: rgba(148, 163, 184, 0.85);
      font-size: 10px;
      white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
    }
    #agent-roster .roster-row[data-status="Working"] .roster-activity {
      color: rgba(251, 191, 36, 0.9);
    }
    #agent-roster .roster-badge {
      font-size: 10px;
      color: rgba(226, 232, 240, 0.72);
      font-variant-numeric: tabular-nums;
      white-space: nowrap;
      flex-shrink: 0;
    }
    #agent-roster .roster-prompt-ver {
      display: inline-flex;
      align-items: center;
      padding: 2px 8px;
      border-radius: 999px;
      font-size: 10px;
      font-weight: 700;
      color: #0369a1;
      background: rgba(56, 189, 248, 0.14);
      border: 1px solid rgba(56, 189, 248, 0.25);
    }
    #agent-roster .roster-spinner {
      display: inline-block;
      width: 10px; height: 10px;
      margin-left: 2px;
      border: 1.5px solid rgba(251, 191, 36, 0.3);
      border-top-color: #fbbf24;
      border-radius: 50%;
      animation: roster-spin 0.8s linear infinite;
      vertical-align: middle;
    }
    @keyframes roster-spin { to { transform: rotate(360deg); } }
    @keyframes roster-pulse {
      0%, 100% { transform: scale(1); box-shadow: 0 0 0 2px rgba(15, 23, 42, 0.4); }
      50%      { transform: scale(1.25); box-shadow: 0 0 0 4px rgba(74, 222, 128, 0.18); }
    }
    #agent-roster .roster-empty {
      padding: 18px 14px;
      color: rgba(148, 163, 184, 0.7);
      text-align: center;
      font-size: 11px;
    }
  `;
  doc.head.appendChild(style);
}

// Stable sort key: Working first, then Waiting, then Idle bucket, then
// Finished/Stale; alphabetical within buckets. Using a fixed key
// prevents row jitter during reconnect storms.
const STATUS_ORDER = { Working: 0, Waiting: 1, Errored: 2, Idle: 3, IdleStale: 4, Finished: 5 };
function sortAgents(a, b) {
  const sa = STATUS_ORDER[a.status] ?? 9;
  const sb = STATUS_ORDER[b.status] ?? 9;
  if (sa !== sb) return sa - sb;
  const na = (a.name || '').toLowerCase();
  const nb = (b.name || '').toLowerCase();
  return na.localeCompare(nb);
}

export default class AgentRoster {
  constructor({ stateStore, worldMap, i18n, mountEl = null, document: doc = document, window: win = window } = {}) {
    this.stateStore = stateStore || worldMap;
    this.i18n = i18n;
    this.mountEl = mountEl;
    this.document = doc;
    this.window = win;
    this.tickHandle = null;
    this.selectedId = null;
    this.lastSignature = '';
    console.log(`[AgentRoster v${ROSTER_VERSION}] init`);

    if (!this.mountEl) {
      injectStyles(doc);
    }
    this._build();
    this._bind();
    this._tick(); // first paint
    this.tickHandle = win.setInterval(() => this._tick(), TICK_MS);
  }

  _build() {
    const doc = this.document;
    this.root = doc.createElement('aside');
    this.root.id = 'agent-roster';
    this.root.dataset.empty = '1';
    if (this.mountEl) this.root.dataset.shell = '1';
    this.root.setAttribute('aria-label', this.i18n ? this.i18n.t('roster.title') : '智能体列表');

    const header = doc.createElement('div');
    header.className = 'roster-header';
    this.titleEl = doc.createElement('span');
    this.titleEl.textContent = this.i18n ? this.i18n.t('roster.title') : '智能体';
    this.countEl = doc.createElement('span');
    this.countEl.className = 'roster-count';
    this.countEl.textContent = '0';
    header.appendChild(this.titleEl);
    header.appendChild(this.countEl);
    this.root.appendChild(header);

    this.list = doc.createElement('ul');
    this.list.className = 'roster-list';
    this.root.appendChild(this.list);

    (this.mountEl || doc.body).appendChild(this.root);
  }

  _bind() {
    // Click delegation — single handler for the whole list.
    this.list.addEventListener('click', ev => {
      const row = ev.target && ev.target.closest
        ? ev.target.closest('.roster-row')
        : null;
      if (!row || !row.dataset.sessionId) return;
      const sessionId = row.dataset.sessionId;
      if (this.selectedId === sessionId) {
        this._dispatchSelect(null);
        return;
      }
      this._dispatchSelect(sessionId);
    });

    // Track selection from AgentRoster so the active row stays highlighted.
    // highlights even when the user selects via sprite click or hotkey.
    this._onSelected = ev => {
      const detail = ev && ev.detail;
      const sessionId = detail?.sessionId;
      this.selectedId = sessionId ? sessionId : null;
      this._applySelection();
    };
    this.window.addEventListener('agent-selected', this._onSelected);

    // Hide the roster while the world editor is open — the editor
    // panel takes the full right edge and would visually sit on top.
    this._onEditor = ev => {
      const active = Boolean(ev && ev.detail && ev.detail.active);
      if (this.root) this.root.style.display = active ? 'none' : '';
    };
    this.window.addEventListener('editor-mode', this._onEditor);
  }

  _dispatchSelect(sessionId) {
    this.selectedId = sessionId || null;
    this._applySelection();
    const detail = { sessionId: sessionId || null };
    const ev = new CustomEvent('agent-selected', { bubbles: true, detail });
    this.window.dispatchEvent(ev);
  }

  _applySelection() {
    const rows = this.list.querySelectorAll('.roster-row');
    rows.forEach(row => {
      row.dataset.selected = row.dataset.sessionId === this.selectedId ? '1' : '0';
    });
  }

  _statusLabel(status) {
    const meta = STATUS_META[status] || STATUS_META.Idle;
    return this.i18n ? this.i18n.t(meta.key) : status || '空闲';
  }

  _collect() {
    const state = this.stateStore && this.stateStore.state;
    const agentsMap = (state && state.agents) || {};
    const out = [];
    for (const id of Object.keys(agentsMap)) {
      const a = agentsMap[id];
      if (!a || !a.sessionId) continue;
      const decision = a.decision;
      const strategyVersion = a.strategy?.promptLabel ||
        (a.strategy?.promptStage ? `promptv${a.strategy.promptStage}` : 'prompt');
      const activity = decision
        ? `${decision.actionLabel || decision.action || ''} ${decision.symbol || ''} · ${decision.confidence || ''}%`.trim()
        : (a.lastAssistantSnippet || '');
      out.push({
        id,
        sessionId: a.sessionId || id,
        name: a.name || a.role || 'session',
        status: a.status || 'Idle',
        toolIcon: a.tool?.icon || null,
        toolName: a.tool?.name || null,
        promptVersion: strategyVersion,
        activity
      });
    }
    out.sort(sortAgents);
    return out;
  }

  _tick() {
    const agents = this._collect();
    const isTradingMode = this.stateStore?.state?.meta?.trading?.mode === 'futures-agent-simulation';
    const t = (key) => this.i18n ? this.i18n.t(key) : key;
    
    if (this.titleEl) {
      this.titleEl.textContent = isTradingMode ? t('roster.tradingTitle') : t('roster.title');
    }
    
    // Signature dodges DOM churn when nothing meaningful changed.
    const sig = agents
      .map(a => `${a.id}|${a.status}|${a.promptVersion}|${a.toolName || ''}|${a.activity.slice(0, 40)}`)
      .join('\n');
    const countSig = `${agents.length}:${this.selectedId || ''}:${sig}`;
    if (countSig === this.lastSignature) return;
    this.lastSignature = countSig;

    this.root.dataset.empty = agents.length === 0 ? '1' : '0';
    this.countEl.textContent = this.i18n
      ? this.i18n.t('roster.count', { count: agents.length })
      : `${agents.length} 个`;

    const doc = this.document;
    // Map existing rows by sessionId so we can reuse rather than re-create.
    const existing = new Map();
    this.list.querySelectorAll('.roster-row').forEach(row => {
      existing.set(row.dataset.sessionId, row);
    });

    // Build in order, move into correct position.
    let prevRow = null;
    for (const a of agents) {
      let row = existing.get(a.id);
      if (!row) {
        row = doc.createElement('li');
        row.className = 'roster-row';
        row.dataset.sessionId = a.id;
        row.setAttribute('role', 'button');
        row.setAttribute('tabindex', '0');

        const top = doc.createElement('div');
        top.className = 'roster-row-top';

        const rowMain = doc.createElement('div');
        rowMain.className = 'roster-row-main';

        const dot = doc.createElement('span');
        dot.className = 'roster-status-dot';
        rowMain.appendChild(dot);

        const main = doc.createElement('div');
        main.className = 'roster-main';
        const name = doc.createElement('div');
        name.className = 'roster-name';
        main.appendChild(name);
        rowMain.appendChild(main);

        const promptVer = doc.createElement('span');
        promptVer.className = 'roster-prompt-ver';
        top.appendChild(rowMain);
        top.appendChild(promptVer);

        const act = doc.createElement('div');
        act.className = 'roster-activity';

        const badge = doc.createElement('div');
        badge.className = 'roster-badge';

        row.appendChild(top);
        row.appendChild(act);
        row.appendChild(badge);

        row.addEventListener('keydown', ev => {
          if (ev.key === 'Enter' || ev.key === ' ') {
            ev.preventDefault();
            this._dispatchSelect(row.dataset.sessionId);
          }
        });
      }

      row.dataset.status = a.status || 'Idle';
      row.dataset.selected = a.id === this.selectedId ? '1' : '0';

      const dot = row.querySelector('.roster-status-dot');
      const meta = STATUS_META[a.status] || STATUS_META.Idle;
      dot.style.background = meta.dot;

      const promptVer = row.querySelector('.roster-prompt-ver');
      if (promptVer) promptVer.textContent = a.promptVersion || 'prompt';

      const name = row.querySelector('.roster-name');
      name.textContent = '';
      const roleChip = doc.createElement('span');
      roleChip.className = this.mountEl ? 'ui-role-chip roster-role-chip' : 'roster-name-text';
      roleChip.textContent = a.name;
      name.appendChild(roleChip);

      const act = row.querySelector('.roster-activity');
      act.textContent = '';
      const actLine = doc.createElement('div');
      actLine.className = this.mountEl ? 'roster-activity-line' : 'roster-activity-inner';
      if (a.toolIcon || a.toolName) {
        const tool = doc.createElement('span');
        tool.className = this.mountEl ? 'roster-act-badge' : undefined;
        tool.textContent = `${a.toolIcon || '⚙'} ${a.toolName || ''}`.trim();
        if (!this.mountEl) tool.style.marginRight = '6px';
        actLine.appendChild(tool);
      }
      if (a.activity) {
        const label = doc.createElement('span');
        label.className = this.mountEl ? 'roster-act-detail' : undefined;
        label.textContent = a.toolIcon
          ? a.activity.replace(/^[^\s]+\s+[^\s]+\s+/, '')
          : a.activity;
        actLine.appendChild(label);
      }
      if (!a.toolName && !a.activity) {
        const status = doc.createElement('span');
        status.className = this.mountEl ? 'roster-act-detail' : undefined;
        status.textContent = this._statusLabel(a.status);
        actLine.appendChild(status);
      }
      if (actLine.childNodes.length) act.appendChild(actLine);

      const badge = row.querySelector('.roster-badge');
      badge.textContent = '';
      if (a.status === 'Working') {
        const spin = doc.createElement('span');
        spin.className = 'roster-spinner';
        spin.setAttribute('aria-label', this._statusLabel(a.status));
        badge.appendChild(spin);
      } else {
        badge.textContent = this._statusLabel(a.status);
      }

      // Reorder in place.
      if (prevRow) {
        if (prevRow.nextSibling !== row) this.list.insertBefore(row, prevRow.nextSibling);
      } else if (this.list.firstChild !== row) {
        this.list.insertBefore(row, this.list.firstChild);
      }
      prevRow = row;

      existing.delete(a.id);
    }

    // Remove rows for sessions that are gone.
    for (const stale of existing.values()) stale.remove();
  }

  destroy() {
    if (this.tickHandle) this.window.clearInterval(this.tickHandle);
    this.window.removeEventListener('agent-selected', this._onSelected);
    this.window.removeEventListener('editor-mode', this._onEditor);
    if (this.root && this.root.parentNode) this.root.parentNode.removeChild(this.root);
  }
}
