// Event log panel — bottom-left collapsible strip. Reads from
// HistoryBuffer; renders its `events` array as clickable rows.
// Click a row → dispatch agent-selected to that event's session.
// Now uses i18n for translations.

const LOG_VERSION = 2;

const KIND_META = {
  session_started: { icon: '▶', color: '#4ade80', titleKey: 'eventLog.kinds.sessionStarted' },
  session_ended:   { icon: '■', color: '#94a3b8', titleKey: 'eventLog.kinds.sessionEnded' },
  status_changed:  { icon: '↻', color: '#38bdf8', titleKey: 'eventLog.kinds.statusChanged' },
  tool_invoked:    { icon: '⚙', color: '#fbbf24', titleKey: 'eventLog.kinds.toolInvoked' }
};

function injectStyles(doc) {
  if (doc.getElementById('event-log-styles')) return;
  const style = doc.createElement('style');
  style.id = 'event-log-styles';
  style.textContent = `
    #event-log {
      /* Positioned above the timeline scrubber (bottom:12, h:42) with
         a small margin so they never overlap. width clamps so it can't
         extend into the centred scrubber on narrow viewports. */
      position: fixed; left: 12px; bottom: 68px;
      width: 320px; max-width: calc(100vw - 24px);
      background: rgba(15, 23, 42, 0.92);
      border: 1px solid rgba(148, 163, 184, 0.3);
      border-radius: 9px;
      box-shadow: 0 10px 28px rgba(0,0,0,0.42);
      color: #e2e8f0;
      font: 11px/1.4 Menlo, Monaco, monospace;
      z-index: 10;
      display: flex; flex-direction: column;
      max-height: 240px;
      overflow: hidden;
      transition: max-height 0.18s ease;
    }
    #event-log[data-collapsed="1"] { max-height: 36px; }
    @media (max-width: 900px) {
      #event-log { width: calc(100vw - 24px); max-height: 160px; }
    }
    #event-log .event-header {
      display: flex; align-items: center; justify-content: space-between;
      padding: 8px 12px;
      background: rgba(30, 41, 59, 0.6);
      border-bottom: 1px solid rgba(148, 163, 184, 0.18);
      cursor: pointer;
      user-select: none;
      font-size: 11px;
      font-weight: 600;
      color: #38bdf8;
      letter-spacing: 0.04em;
      text-transform: uppercase;
    }
    #event-log .event-header .chev {
      color: #64748b;
      font-size: 10px;
      transition: transform 0.18s ease;
    }
    #event-log[data-collapsed="0"] .event-header .chev { transform: rotate(180deg); }
    #event-log .event-body {
      flex: 1; overflow-y: auto;
      scrollbar-width: thin;
      padding: 2px 0;
    }
    #event-log .event-body::-webkit-scrollbar { width: 6px; }
    #event-log .event-body::-webkit-scrollbar-thumb { background: rgba(148,163,184,0.25); border-radius: 4px; }
    #event-log .event-row {
      display: grid;
      grid-template-columns: 16px 1fr max-content;
      gap: 6px;
      padding: 4px 12px;
      cursor: pointer;
      align-items: center;
      transition: background 0.1s ease;
    }
    #event-log .event-row:hover {
      background: rgba(56, 189, 248, 0.10);
    }
    #event-log .event-icon { text-align: center; }
    #event-log .event-text {
      white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
      color: #cbd5e1;
    }
    #event-log .event-age {
      color: #64748b; font-size: 9px;
      font-variant-numeric: tabular-nums;
    }
    #event-log[data-empty="1"] .event-body::before {
      content: var(--event-empty-label, '暂无事件');
      display: block; padding: 18px; color: #64748b; text-align: center; font-size: 10px;
    }
    #event-log .event-count {
      font-size: 10px;
      color: #94a3b8;
      text-transform: none;
      font-weight: 500;
      font-variant-numeric: tabular-nums;
    }
  `;
  doc.head.appendChild(style);
}

function relativeAge(ts, now, i18n) {
  const s = Math.max(0, Math.round((now - ts) / 1000));
  const t = (key, vars) => i18n ? i18n.t(key, vars) : key;
  
  if (s < 5)   return t('eventLog.time.now');
  if (s < 60)  return t('eventLog.time.seconds', { n: s });
  if (s < 3600) return t('eventLog.time.minutes', { n: Math.floor(s / 60) });
  return t('eventLog.time.hours', { n: Math.floor(s / 3600) });
}

export default class EventLog {
  constructor({ history, i18n, document: doc = document, window: win = window } = {}) {
    this.history = history;
    this.i18n = i18n;
    this.document = doc;
    this.window = win;
    this.collapsed = false;
    this._ageTick = null;
    console.log(`[EventLog v${LOG_VERSION}] init`);

    injectStyles(doc);
    this._build();
    this._bind();
    this._render();
    // Refresh "3s ago" labels every 5s — cheap, updates existing rows only.
    this._ageTick = win.setInterval(() => this._refreshAges(), 5000);
  }

  _build() {
    const doc = this.document;
    const t = (key) => this.i18n ? this.i18n.t(key) : key;
    
    this.root = doc.createElement('aside');
    this.root.id = 'event-log';
    this.root.dataset.collapsed = '0';
    this.root.dataset.empty = '1';
    this.root.setAttribute('aria-label', t('eventLog.aria'));
    this.root.style.setProperty('--event-empty-label', JSON.stringify(t('eventLog.empty')));

    this.header = doc.createElement('div');
    this.header.className = 'event-header';
    const title = doc.createElement('span');
    title.textContent = `📜 ${t('eventLog.title')}`;
    this.countEl = doc.createElement('span');
    this.countEl.className = 'event-count';
    this.countEl.textContent = '0';
    const chev = doc.createElement('span');
    chev.className = 'chev';
    chev.textContent = '▾';
    const left = doc.createElement('span');
    left.style.display = 'flex'; left.style.gap = '10px'; left.style.alignItems = 'center';
    left.appendChild(title);
    left.appendChild(this.countEl);
    this.header.appendChild(left);
    this.header.appendChild(chev);
    this.root.appendChild(this.header);

    this.body = doc.createElement('div');
    this.body.className = 'event-body';
    this.root.appendChild(this.body);

    doc.body.appendChild(this.root);
  }

  _bind() {
    this.header.addEventListener('click', () => this.toggle());
    this.body.addEventListener('click', ev => {
      const row = ev.target && ev.target.closest
        ? ev.target.closest('.event-row')
        : null;
      if (!row || !row.dataset.sessionId) return;
      
      // Navigate to the snapshot at the time of this event
      const eventTs = Number(row.dataset.ts || 0);
      if (eventTs && this.history) {
        const snapshot = this.history.getSnapshotAt(eventTs);
        if (snapshot) {
          // Dispatch event to show historical state
          this.window.dispatchEvent(new CustomEvent('show-history-snapshot', {
            bubbles: true,
            detail: { snapshot, eventTs }
          }));
        }
      }
      
      const detail = { sessionId: row.dataset.sessionId };
      this.window.dispatchEvent(new CustomEvent('agent-selected', { bubbles: true, detail }));
    });
    this._onHistoryEvent = () => this._render();
    this.window.addEventListener('history-event', this._onHistoryEvent);
    this._onEditor = ev => {
      const active = Boolean(ev && ev.detail && ev.detail.active);
      if (this.root) this.root.style.display = active ? 'none' : '';
    };
    this.window.addEventListener('editor-mode', this._onEditor);
  }

  toggle() { this.collapsed = !this.collapsed; this.root.dataset.collapsed = this.collapsed ? '1' : '0'; }

  _refreshAges() {
    const now = Date.now();
    const rows = this.body.querySelectorAll('.event-row');
    rows.forEach(row => {
      const ts = Number(row.dataset.ts || 0);
      if (!ts) return;
      const age = row.querySelector('.event-age');
      if (age) age.textContent = relativeAge(ts, now, this.i18n);
    });
  }

  _render() {
    const events = this.history ? this.history.getEvents() : [];
    const t = (key) => this.i18n ? this.i18n.t(key) : key;
    
    this.countEl.textContent = String(events.length);
    this.root.dataset.empty = events.length === 0 ? '1' : '0';
    // Render newest on top. Cap visible rows for DOM cost (events[] is
    // capped at 200; we show last 80).
    const slice = events.slice(-80).reverse();
    const doc = this.document;
    const now = Date.now();
    // Cheap full re-render — 80 rows of ~3 nodes each is fine.
    this.body.textContent = '';
    for (const ev of slice) {
      const meta = KIND_META[ev.kind] || KIND_META.status_changed;
      const row = doc.createElement('div');
      row.className = 'event-row';
      row.dataset.sessionId = ev.sessionId;
      row.dataset.ts = String(ev.ts);
      row.title = t(meta.titleKey);
      const icon = doc.createElement('span');
      icon.className = 'event-icon';
      icon.style.color = meta.color;
      icon.textContent = meta.icon;
      const text = doc.createElement('span');
      text.className = 'event-text';
      text.textContent = this._formatEventLabel(ev);
      const age = doc.createElement('span');
      age.className = 'event-age';
      age.textContent = relativeAge(ev.ts, now, this.i18n);
      row.appendChild(icon);
      row.appendChild(text);
      row.appendChild(age);
      this.body.appendChild(row);
    }
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
    const t = (key, vars) => this.i18n ? this.i18n.t(key, vars) : null;
    const name = ev.name || ev.sessionId || '';
    if (ev.kind === 'session_started') {
      return t('eventLog.labels.sessionStarted', { name }) || `${name} started`;
    }
    if (ev.kind === 'session_ended') {
      return t('eventLog.labels.sessionEnded', { name }) || `${name} signed off`;
    }
    if (ev.kind === 'status_changed') {
      return t('eventLog.labels.statusChanged', {
        name,
        from: this._formatStatus(ev.fromStatus),
        to: this._formatStatus(ev.toStatus || ev.status)
      }) || `${name} · ${ev.fromStatus || ''} → ${ev.toStatus || ev.status || ''}`;
    }
    if (ev.kind === 'tool_invoked') {
      return t('eventLog.labels.toolInvoked', {
        name,
        icon: ev.toolIcon || '⚙',
        tool: ev.toolName || t('eventLog.toolFallback') || '工具'
      }) || `${name} · ${ev.toolIcon || '⚙'} ${ev.toolName || 'tool'}`;
    }
    return ev.label || ev.kind;
  }

  destroy() {
    if (this._ageTick) this.window.clearInterval(this._ageTick);
    this.window.removeEventListener('history-event', this._onHistoryEvent);
    this.window.removeEventListener('editor-mode', this._onEditor);
    if (this.root.parentNode) this.root.parentNode.removeChild(this.root);
  }
}
