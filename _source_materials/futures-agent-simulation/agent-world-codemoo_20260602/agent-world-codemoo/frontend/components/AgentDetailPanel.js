// Agent detail sidebar — driven by AgentRoster `agent-selected` events.

const PANEL_VERSION = 2;

function h(tag, attrs = {}, children = []) {
  const el = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (v == null || v === false) continue;
    if (k === 'class') el.className = v;
    else if (k === 'style' && typeof v === 'object') Object.assign(el.style, v);
    else if (k.startsWith('on') && typeof v === 'function') {
      el.addEventListener(k.slice(2).toLowerCase(), v);
    } else {
      el.setAttribute(k, v === true ? '' : String(v));
    }
  }
  for (const c of [].concat(children)) {
    if (c == null) continue;
    el.appendChild(typeof c === 'string' ? document.createTextNode(c) : c);
  }
  return el;
}

const STATUS_COLORS = {
  Working:   '#4ade80',
  Waiting:   '#fbbf24',
  Errored:   '#f87171',
  Idle:      '#94a3b8',
  IdleStale: '#64748b',
  Finished:  '#7280a0'
};

export default class AgentDetailPanel {
  constructor({
    stateStore,
    apiBaseUrl,
    authToken,
    fetchImpl,
    i18n,
    mount = null,
    mountAgents = null,
    mountJournal = null,
    appShell = null,
    embedded = false
  }) {
    this.embedded = embedded || Boolean(mountAgents || mountJournal || mount);
    this.mount = mount;
    this.mountAgents = mountAgents;
    this.mountJournal = mountJournal;
    this.appShell = appShell;
    this.activePage = 'agents';
    this.stateStore = stateStore;
    this.apiBaseUrl = apiBaseUrl || '';
    this.authToken = authToken || '';
    const rawFetch = fetchImpl || (typeof window !== 'undefined' ? window.fetch : null);
    this.fetch = rawFetch ? rawFetch.bind(typeof window !== 'undefined' ? window : null) : null;

    this.i18n = i18n;
    this.currentSessionId = null;
    this.journalContext = null;
    this.latestState = null;

    console.log(`[AgentDetailPanel v${PANEL_VERSION}] init`);

    this._buildUI();
    this._bindEvents();
  }

  _buildUI() {
    const panelStyle = this.embedded
      ? {
          position: 'relative',
          width: '100%',
          maxHeight: 'calc(100vh - 200px)',
          overflow: 'auto',
          padding: '14px 16px',
          background: '#ffffff',
          color: '#111827',
          border: '1px solid #d1d5db',
          borderRadius: '8px',
          boxShadow: '0 1px 2px rgba(15, 23, 42, 0.06)',
          zIndex: 1,
          fontFamily: 'Menlo, Monaco, monospace',
          fontSize: '12px',
          display: 'none',
          lineHeight: '1.5'
        }
      : {
          position: 'fixed', top: '56px', right: '268px',
          width: 'min(340px, calc(100vw - 300px))',
          maxHeight: 'calc(100vh - 100px)',
          overflow: 'auto',
          padding: '12px 14px',
          background: 'rgba(15,23,42,0.94)',
          color: '#e2e8f0',
          border: '1px solid #38bdf8',
          borderRadius: '10px',
          boxShadow: '0 10px 28px rgba(0,0,0,0.45)',
          zIndex: 12,
          fontFamily: 'Menlo, Monaco, monospace', fontSize: '12px',
          display: 'none',
          lineHeight: '1.5'
        };

    this.panel = h('aside', {
      id: 'session-detail-panel',
      class: this.embedded ? 'panel-embedded' : '',
      style: panelStyle
    });
    const initialMount = this.mountAgents || this.mount || null;
    if (initialMount) {
      initialMount.appendChild(this.panel);
    } else if (!this.embedded) {
      document.body.appendChild(this.panel);
    }

    this.closeBtn = null;
    if (!this.embedded) {
      this.closeBtn = h('button', {
        type: 'button',
        style: {
          position: 'absolute', top: '8px', right: '10px',
          background: 'none', border: 'none', color: '#94a3b8',
          cursor: 'pointer', fontSize: '14px', padding: '0'
        },
        'aria-label': '关闭详情'
      }, '✕');
      this.closeBtn.addEventListener('click', ev => {
        ev.preventDefault();
        ev.stopPropagation();
        this._close();
      });
      this.panel.appendChild(this.closeBtn);
    }

    this.body = h('div', { id: 'session-detail-body' });
    this.panel.appendChild(this.body);
  }

  _bindEvents() {
    // Listen on window — AgentRoster dispatches selection events.
    // bubbles to window since we use `bubbles: true`.
    this._onSelect = (e) => this._onAgentSelected(e);
    window.addEventListener('agent-selected', this._onSelect);
    this._onJournalEvent = (e) => this._onJournalEventSelected(e);
    window.addEventListener('journal-event-selected', this._onJournalEvent);

    this._onPageChange = (e) => {
      const page = e?.detail?.page;
      const prev = this.activePage;
      this.activePage = page;
      if (page !== 'agents' && page !== 'journal') {
        this._close();
        return;
      }
      if (this.currentSessionId && this.panel.style.display !== 'none') {
        this._setSplitDetailOpen(prev === 'journal' ? 'journal' : 'agents', false);
        this._attachToPage(page);
      }
    };
    window.addEventListener('app-page-change', this._onPageChange);

    this._onKey = (e) => {
      if (!this.currentSessionId) return;
      const tag = e.target?.tagName || '';
      if (/^(INPUT|TEXTAREA|SELECT)$/.test(tag)) return;
      if (e.key === 'Escape') this._close();
    };
    window.addEventListener('keydown', this._onKey);
  }

  _detailMountForPage(page) {
    if (page === 'journal') return this.mountJournal;
    if (page === 'agents') return this.mountAgents;
    return this.mountAgents || this.mount;
  }

  _splitRootForMount(mount) {
    return mount?.closest?.('.page-split') || null;
  }

  _setSplitDetailOpen(page, open) {
    const mount = this._detailMountForPage(page);
    const split = this._splitRootForMount(mount);
    if (split) split.classList.toggle('page-split--detail-open', open);
  }

  /** Shell 嵌入模式：用语义 class 替代深色内联块 */
  _sdpBlock(modifier, children, darkStyle) {
    if (this.embedded) {
      const cls = modifier ? `sdp-block ${modifier}` : 'sdp-block';
      return h('div', { class: cls }, children);
    }
    return h('div', { style: darkStyle }, children);
  }

  _attachToPage(page) {
    const mount = this._detailMountForPage(page);
    if (!mount) return;
    if (this.panel.parentNode !== mount) {
      mount.appendChild(this.panel);
    }
    this._setSplitDetailOpen(page, true);
  }

  _onAgentSelected(event) {
    const sessionId = event?.detail?.sessionId;
    if (!sessionId) {
      this._close();
      return;
    }
    this.journalContext = null;
    const page = this.activePage === 'journal' ? 'journal' : 'agents';
    this.currentSessionId = sessionId;
    this._open(page);
    this._render();
  }

  _onJournalEventSelected(event) {
    const journalEvent = event?.detail?.event;
    if (!journalEvent) {
      this._close();
      return;
    }
    this.journalContext = journalEvent;
    this.currentSessionId = journalEvent.sessionId || null;
    this._open('journal');
    this._renderJournalDetail(journalEvent);
  }

  _open(page = this.activePage) {
    if (this.embedded && this.appShell?.setPage) {
      if (page === 'journal' && this.activePage !== 'journal') {
        this.appShell.setPage('journal');
      } else if (page === 'agents' && this.activePage !== 'agents') {
        this.appShell.setPage('agents');
      }
    }
    this._attachToPage(page);
    this.panel.style.display = 'block';
  }

  _close() {
    this.document.querySelectorAll('.page-split--detail-open').forEach(el => {
      el.classList.remove('page-split--detail-open');
    });
    this.panel.style.display = 'none';
    this.currentSessionId = null;
    this.journalContext = null;
    if (this.stateStore) this.stateStore.selectedAgent = null;
    try {
      window.dispatchEvent(new CustomEvent('agent-selected', {
        bubbles: true,
        detail: { sessionId: null, avatar: null }
      }));
    } catch (_) { /* ignore */ }
  }

  handleStateUpdate(state) {
    this.latestState = state;
    if (this.journalContext && this.activePage === 'journal') {
      this._renderJournalDetail(this.journalContext);
      return;
    }
    if (this.currentSessionId) this._render();
  }

  focusSession(sessionId) {
    if (!sessionId) return;
    this.currentSessionId = sessionId;
    this._open(this.activePage === 'journal' ? 'journal' : 'agents');
    this._render();
  }

  _render() {
    if (this.journalContext && this.activePage === 'journal') {
      this._renderJournalDetail(this.journalContext);
      return;
    }
    const sid = this.currentSessionId;
    if (!sid) {
      this.body.textContent = '';
      return;
    }
    const agent = this.latestState?.agents?.[sid] || null;
    const t = (key, vars) => this.i18n ? this.i18n.t(key, vars) : key;
    const statusKey = {
      Working: 'session.status.working',
      Waiting: 'session.status.waiting',
      Errored: 'session.status.errored',
      Idle: 'session.status.idle',
      IdleStale: 'session.status.idleStale',
      Finished: 'session.status.finished'
    };
    const statusText = agentStatus => t(statusKey[agentStatus] || 'session.status.idle');

    this.body.innerHTML = '';
    this.body.style.paddingTop = this.embedded ? '40px' : '';

    if (!agent) {
      this.body.appendChild(h('div', { style: { opacity: '0.6' } }, [
        t('session.labels.noLongerActive', { id: sid.slice(0, 8) })
      ]));
      return;
    }

    const statusColor = STATUS_COLORS[agent.status] || '#94a3b8';
    const headerStyle = this.embedded
      ? { display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '12px' }
      : { display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' };
    const nameStyle = this.embedded
      ? { fontSize: '16px', color: '#1f2937' }
      : { fontSize: '14px', color: '#f1f5f9' };
    const statusStyle = this.embedded
      ? { color: '#6b7280', fontSize: '13px' }
      : { color: '#94a3b8', fontSize: '11px' };
    const header = h('div', { class: this.embedded ? 'sdp-header' : undefined, style: headerStyle }, [
      h('span', { style: {
        display: 'inline-block', width: '10px', height: '10px',
        borderRadius: '50%', background: statusColor,
        boxShadow: this.embedded ? 'none' : `0 0 8px ${statusColor}`
      } }),
      this.embedded
        ? h('strong', { class: 'ui-role-chip sdp-header-name' }, agent.name || 'session')
        : h('strong', { style: nameStyle }, agent.name || 'session'),
      h('span', { class: this.embedded ? 'sdp-header-status' : undefined, style: statusStyle }, statusText(agent.status))
    ]);
    this.body.appendChild(header);

    const isTradingAgent = Boolean(agent.decision && agent.memory && agent.strategy);
    if (isTradingAgent) {
      const decision = agent.decision || {};
      const score = agent.score || {};
      const memoryItems = Array.isArray(agent.memory?.retrieved)
        ? agent.memory.retrieved.slice(0, 3)
        : [];
      const patchNotes = Array.isArray(agent.strategy?.patchNotes)
        ? agent.strategy.patchNotes.slice(0, 3)
        : [];
      const llmStatus = this.latestState?.metadata?.trading?.llm?.status ||
        this.latestState?.meta?.trading?.llm?.status;
      const sourceLabel = decision.source === 'llm'
        ? t('trading.source.llm', { model: decision.model || agent.model || 'DeepSeek' })
        : llmStatus === 'running'
          ? t('trading.source.pending')
        : t('trading.source.simulated');
      const sourceColor = decision.source === 'llm' ? '#86efac' : llmStatus === 'running' ? '#7dd3fc' : '#fbbf24';

      const decisionChildren = this.embedded
        ? [
          h('div', { class: 'sdp-block-title' }, t('trading.decision')),
          h('div', { class: 'sdp-value', style: { fontWeight: '700', marginBottom: '8px' } },
            `${decision.actionLabel || t(`trading.actions.${decision.action || 'HOLD'}`)} ${decision.symbol || ''}`),
          h('div', { class: 'sdp-label', style: { display: 'inline-block', marginBottom: '8px', padding: '3px 8px', borderRadius: '6px', background: '#f3f4f6' } }, sourceLabel),
          h('div', { class: 'sdp-value', style: { marginBottom: '10px', lineHeight: '1.6' } }, decision.reason || t('trading.noDecision')),
          h('div', { class: 'sdp-metric', style: { display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '8px' } }, [
            h('span', {}, t('trading.confidence', { value: decision.confidence || 0 })),
            h('span', {}, t('trading.pnl', { value: score.total ?? '--' })),
            h('span', {}, t('trading.drawdown', { value: score.drawdown ?? '--' }))
          ])
        ]
        : [
          h('div', { style: { display: 'flex', justifyContent: 'space-between', gap: '8px', marginBottom: '6px' } }, [
            h('span', { style: { color: '#7dd3fc', fontWeight: '700', textTransform: 'uppercase', letterSpacing: '0.06em' } }, t('trading.decision')),
            h('span', { style: { color: '#fbbf24', fontWeight: '700' } }, `${decision.actionLabel || t(`trading.actions.${decision.action || 'HOLD'}`)} ${decision.symbol || ''}`)
          ]),
          h('div', { style: { display: 'inline-block', marginBottom: '7px', padding: '2px 6px', borderRadius: '999px', border: `1px solid ${sourceColor}`, color: sourceColor, fontSize: '10px' } }, sourceLabel),
          h('div', { style: { color: '#cbd5e1', marginBottom: '7px' } }, decision.reason || t('trading.noDecision')),
          h('div', { style: { display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '5px', color: '#dbeafe', fontSize: '10px' } }, [
            h('span', {}, t('trading.confidence', { value: decision.confidence || 0 })),
            h('span', {}, t('trading.pnl', { value: score.total ?? '--' })),
            h('span', {}, t('trading.drawdown', { value: score.drawdown ?? '--' }))
          ])
        ];
      this.body.appendChild(this._sdpBlock(
        'sdp-block--decision',
        decisionChildren,
        {
          marginTop: '8px', padding: '9px 10px', borderRadius: '8px',
          background: 'linear-gradient(135deg, rgba(56,189,248,0.14), rgba(15,23,42,0.72))',
          border: '1px solid rgba(56,189,248,0.34)'
        }
      ));

      const memoryTitle = this.embedded
        ? h('div', { class: 'sdp-block-title' }, t('trading.memory'))
        : h('div', { style: { color: '#7dd3fc', fontWeight: '700', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: '6px' } }, t('trading.memory'));
      this.body.appendChild(this._sdpBlock(
        'sdp-block--memory',
        [
          memoryTitle,
          ...memoryItems.map(item => h('div', {
            class: this.embedded ? 'sdp-memory-item' : undefined,
            style: this.embedded ? undefined : {
              padding: '6px 0',
              borderTop: '1px solid rgba(148,163,184,0.12)',
              color: '#cbd5e1'
            }
          }, [
            h('span', {
              class: this.embedded ? 'sdp-memory-date' : undefined,
              style: this.embedded ? undefined : { color: '#fbbf24', marginRight: '6px' }
            }, `${item.date || ''}`),
            h('span', { class: this.embedded ? 'sdp-memory-text' : undefined }, item.text || '')
          ]))
        ],
        {
          marginTop: '8px',
          padding: '9px 10px',
          borderRadius: '8px',
          background: 'rgba(2,6,23,0.42)',
          border: '1px solid rgba(148,163,184,0.22)'
        }
      ));

      const strategyHead = this.embedded
        ? h('div', { class: 'sdp-block-title-row' }, [
          h('span', { class: 'sdp-block-title' }, t('trading.strategy')),
          h('span', { class: 'sdp-block-meta' }, t('trading.promptVersion', { version: agent.strategy.promptVersion || 1 }))
        ])
        : h('div', { style: { display: 'flex', justifyContent: 'space-between', marginBottom: '6px' } }, [
          h('span', { style: { color: '#86efac', fontWeight: '700', textTransform: 'uppercase', letterSpacing: '0.06em' } }, t('trading.strategy')),
          h('span', { style: { color: '#bbf7d0' } }, t('trading.promptVersion', { version: agent.strategy.promptVersion || 1 }))
        ]);
      this.body.appendChild(this._sdpBlock(
        'sdp-block--strategy',
        [
          strategyHead,
          ...patchNotes.map(note => h('div', {
            class: this.embedded ? 'sdp-patch-item' : undefined,
            style: this.embedded ? undefined : { color: '#cbd5e1', marginBottom: '4px' }
          }, `- ${note}`))
        ],
        {
          marginTop: '8px',
          padding: '9px 10px',
          borderRadius: '8px',
          background: 'rgba(74,222,128,0.08)',
          border: '1px solid rgba(74,222,128,0.24)'
        }
      ));
      if (this.embedded) {
        this.body.appendChild(h('div', { class: 'sdp-actions' }, [
          h('button', {
            type: 'button',
            class: 'sdp-btn sdp-btn--ghost',
            onclick: () => this._close()
          }, t('session.actions.close'))
        ]));
      }
      return;
    }

    this.body.appendChild(h('div', { style: { opacity: '0.6' } }, agent.name || sid));
  }

  _renderJournalDetail(event) {
    const t = (key, vars) => this.i18n ? this.i18n.t(key, vars) : key;
    const roundNo = Number.isFinite(event.roundIndex) ? Number(event.roundIndex) + 1 : null;

    this.body.innerHTML = '';
    this.body.style.paddingTop = this.embedded ? '8px' : '';

    const header = h('div', { class: 'sdp-header journal-detail-header' }, [
      h('strong', { class: 'ui-role-chip sdp-header-name' },
        roundNo ? t('eventLog.detail.roundTitle', { n: roundNo }) : t('eventLog.panelTitle')),
      event.roundDate
        ? h('span', { class: 'sdp-header-status journal-detail-date' }, event.roundDate)
        : null
    ]);
    this.body.appendChild(header);

    if (event.regime) {
      this.body.appendChild(h('p', { class: 'journal-detail-regime' }, event.regime));
    }

    const kind = event.kind === 'llm_decision' ? 'agent_decision' : event.kind;

    if (kind === 'agent_decision') {
      const payload = event.payload || {};
      const decision = payload.decision || {};
      const score = payload.score || {};
      const sourceLabel = decision.source === 'llm'
        ? t('trading.source.llm', { model: decision.model || 'DeepSeek' })
        : t('trading.source.simulated');

      this.body.appendChild(this._sdpBlock('sdp-block--decision', [
        h('div', { class: 'sdp-block-title' }, t('eventLog.detail.decisionTitle', { role: payload.role || event.name || '' })),
        h('div', { class: 'sdp-value', style: { fontWeight: '700', marginBottom: '8px' } },
          `${decision.actionLabel || t(`trading.actions.${decision.action || 'HOLD'}`)} ${decision.symbol || ''}`),
        h('div', { class: 'sdp-label', style: { display: 'inline-block', marginBottom: '8px' } }, sourceLabel),
        h('div', { class: 'sdp-value', style: { marginBottom: '10px', lineHeight: '1.6' } },
          decision.reason || t('trading.noDecision')),
        h('div', { class: 'sdp-metric', style: { display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '8px' } }, [
          h('span', {}, t('trading.confidence', { value: decision.confidence || 0 })),
          h('span', {}, t('trading.pnl', { value: score.total ?? '--' })),
          h('span', {}, t('trading.drawdown', { value: score.drawdown ?? '--' }))
        ])
      ], {}));

      const evidence = Array.isArray(decision.evidence) ? decision.evidence.slice(0, 3) : [];
      if (evidence.length) {
        this.body.appendChild(this._sdpBlock('sdp-block--memory', [
          h('div', { class: 'sdp-block-title' }, t('eventLog.detail.evidence')),
          ...evidence.map(text => h('div', { class: 'sdp-memory-item' }, [
            h('span', { class: 'sdp-memory-text' }, text)
          ]))
        ], {}));
      }
    }

    if (kind === 'debate_round') {
      const debate = event.payload?.debate || {};
      if (debate.summary) {
        this.body.appendChild(this._sdpBlock('sdp-block--decision', [
          h('div', { class: 'sdp-block-title' }, t('eventLog.detail.debateSummary')),
          h('div', { class: 'sdp-value', style: { lineHeight: '1.6' } }, debate.summary)
        ], {}));
      }

      const entries = Array.isArray(debate.entries) ? debate.entries : [];
      this.body.appendChild(this._sdpBlock('sdp-block--memory', [
        h('div', { class: 'sdp-block-title' }, t('eventLog.detail.debateEntries')),
        ...entries.map(entry => h('div', { class: 'journal-debate-entry' }, [
          h('div', { class: 'journal-debate-head' }, [
            h('strong', { class: 'ui-role-chip' }, entry.role || entry.agentId || ''),
            h('span', { class: 'journal-debate-action' },
              `${entry.actionLabel || entry.action || ''} ${entry.symbol || ''} · ${entry.confidence || 0}%`)
          ]),
          h('p', { class: 'journal-debate-reason' }, entry.reason || t('trading.noDecision'))
        ]))
      ], {}));

      const dissent = Array.isArray(debate.dissent) ? debate.dissent : [];
      if (dissent.length) {
        this.body.appendChild(this._sdpBlock('sdp-block--strategy', [
          h('div', { class: 'sdp-block-title' }, t('eventLog.detail.dissent')),
          ...dissent.map(item => h('div', { class: 'sdp-patch-item' },
            `${item.role || item.agentId || ''}：${item.action || ''} ${item.symbol || ''} — ${item.summary || ''}`))
        ], {}));
      }
    }

    if (kind === 'trade_executed') {
      const execution = event.payload?.execution || {};
      if (execution.summary) {
        this.body.appendChild(this._sdpBlock('sdp-block--decision', [
          h('div', { class: 'sdp-block-title' }, t('eventLog.detail.executionSummary')),
          h('div', { class: 'sdp-value', style: { lineHeight: '1.6' } }, execution.summary)
        ], {}));
      }

      const orders = Array.isArray(execution.orders) ? execution.orders : [];
      this.body.appendChild(this._sdpBlock('sdp-block--memory', [
        h('div', { class: 'sdp-block-title' }, t('eventLog.detail.executionOrders')),
        ...orders.map(order => {
          const statusLabel = t(`eventLog.detail.orderStatus.${order.status || 'pending'}`);
          return h('div', { class: 'journal-exec-order', 'data-status': order.status || 'pending' }, [
            h('div', { class: 'journal-exec-head' }, [
              h('strong', { class: 'ui-role-chip' }, order.role || order.agentId || ''),
              h('span', { class: 'journal-exec-status' }, statusLabel)
            ]),
            h('div', { class: 'journal-exec-action' },
              `${order.action || order.rawAction || t('trading.actions.HOLD')} ${order.symbol || ''}` +
              (order.confidence != null ? ` · ${order.confidence}%` : '')),
            order.note ? h('p', { class: 'journal-exec-note' }, order.note) : null
          ]);
        })
      ], {}));
    }

    if (this.embedded) {
      this.body.appendChild(h('div', { class: 'sdp-actions' }, [
        h('button', {
          type: 'button',
          class: 'sdp-btn sdp-btn--ghost',
          onclick: () => this._close()
        }, t('session.actions.close'))
      ]));
    }
  }

  destroy() {
    window.removeEventListener('agent-selected', this._onSelect);
    window.removeEventListener('journal-event-selected', this._onJournalEvent);
    window.removeEventListener('app-page-change', this._onPageChange);
    window.removeEventListener('keydown', this._onKey);
    if (this.panel?.parentNode) this.panel.parentNode.removeChild(this.panel);
  }
}
