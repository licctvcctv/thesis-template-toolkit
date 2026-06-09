// Prompt evolution board — prompt → promptv1 → promptv2 (newest version on top)

const PANEL_VERSION = 4;
const TICK_MS = 500;
const PROMPT_VERSION_ORDER = ['promptv2', 'promptv1', 'prompt'];

function escapeHtml(value) {
  return String(value ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function renderPromptBox(label, text) {
  const body = String(text || '').trim();
  return `
    <article class="app-prompt-version-card">
      <header class="app-prompt-version-head">
        <span class="app-prompt-badge app-prompt-badge--new">${escapeHtml(label)}</span>
      </header>
      <pre class="app-prompt-version-body">${escapeHtml(body || '（空）')}</pre>
    </article>
  `;
}

export default class AgentPromptPanel {
  constructor({ stateStore, i18n, mountEl = null, document: doc = document, window: win = window } = {}) {
    this.stateStore = stateStore;
    this.i18n = i18n;
    this.mountEl = mountEl;
    this.document = doc;
    this.window = win;
    this.selectedAgentId = null;
    this.lastSignature = '';
    this.tickHandle = null;
    console.log(`[AgentPromptPanel v${PANEL_VERSION}] init`);
    this._build();
    this._bind();
    this._tick();
    this.tickHandle = win.setInterval(() => this._tick(), TICK_MS);
  }

  _t(key, vars) {
    return this.i18n ? this.i18n.t(key, vars) : key;
  }

  _build() {
    const doc = this.document;
    this.root = doc.createElement('section');
    this.root.id = 'agent-prompt-panel';
    this.root.dataset.empty = '1';
    this.root.setAttribute('aria-label', this._t('agentPrompt.aria'));

    this.headEl = doc.createElement('div');
    this.headEl.className = 'app-prompt-head';
    this.headEl.innerHTML = `
      <div>
        <h2 class="app-prompt-title">${escapeHtml(this._t('agentPrompt.title'))}</h2>
        <p class="app-prompt-subtitle">${escapeHtml(this._t('agentPrompt.subtitle'))}</p>
      </div>
    `;

    this.tabsEl = doc.createElement('div');
    this.tabsEl.className = 'app-prompt-tabs';
    this.tabsEl.setAttribute('role', 'tablist');

    this.bodyEl = doc.createElement('div');
    this.bodyEl.className = 'app-prompt-body';

    this.root.appendChild(this.headEl);
    this.root.appendChild(this.tabsEl);
    this.root.appendChild(this.bodyEl);
    (this.mountEl || doc.body).appendChild(this.root);
  }

  _bind() {
    this.tabsEl.addEventListener('click', ev => {
      const tab = ev.target?.closest?.('.app-prompt-tab');
      if (!tab?.dataset?.agentId) return;
      this.selectedAgentId = tab.dataset.agentId;
      this._applyTabSelection();
      this._renderAgentBody();
      this.window.dispatchEvent(new CustomEvent('agent-selected', {
        bubbles: true,
        detail: { sessionId: tab.dataset.agentId }
      }));
    });

    this._onSelected = ev => {
      const sessionId = ev?.detail?.sessionId;
      if (sessionId && sessionId !== this.selectedAgentId) {
        this.selectedAgentId = sessionId;
        this._applyTabSelection();
        this._renderAgentBody();
      }
    };
    this.window.addEventListener('agent-selected', this._onSelected);
  }

  _applyTabSelection() {
    this.tabsEl.querySelectorAll('.app-prompt-tab').forEach(tab => {
      tab.dataset.active = tab.dataset.agentId === this.selectedAgentId ? '1' : '0';
      tab.setAttribute('aria-selected', tab.dataset.active === '1' ? 'true' : 'false');
    });
  }

  _collectBoard() {
    const trading = this.stateStore?.state?.meta?.trading;
    const board = trading?.promptBoard;
    const agents = Array.isArray(board?.agents) ? board.agents : [];
    return { trading, board, agents };
  }

  _currentLabel(agent) {
    return agent.promptLabel || 'prompt';
  }

  _buildPromptVersions(agent) {
    const iterations = Array.isArray(agent.iterations) ? agent.iterations : [];
    const byLabel = new Map();
    byLabel.set('prompt', agent.basePrompt || agent.currentPrompt || '');
    for (const iter of iterations) {
      if (iter.fromLabel && iter.from) byLabel.set(iter.fromLabel, iter.from);
      if (iter.toLabel && iter.to) byLabel.set(iter.toLabel, iter.to);
    }
    const currentLabel = this._currentLabel(agent);
    byLabel.set(currentLabel, agent.currentPrompt || agent.basePrompt || '');

    const versions = [];
    for (const label of PROMPT_VERSION_ORDER) {
      const text = byLabel.get(label);
      if (!text) continue;
      versions.push({ label, text });
    }
    if (!versions.length && agent.currentPrompt) {
      versions.push({ label: currentLabel, text: agent.currentPrompt });
    }
    return versions;
  }

  _tick() {
    const { trading, agents } = this._collectBoard();
    const isTrading = trading?.mode === 'futures-agent-simulation';
    if (!isTrading || !agents.length) {
      this.root.dataset.empty = '1';
      return;
    }

    const sig = agents.map(a => {
      const iters = Array.isArray(a.iterations) ? a.iterations : [];
      return `${a.agentId}|${this._currentLabel(a)}|${iters.length}|${iters.map(i => i.id).join(',')}|${(a.currentPrompt || '').length}`;
    }).join(';');
    const fullSig = `${sig}:${this.selectedAgentId || ''}`;
    if (fullSig === this.lastSignature) return;
    this.lastSignature = fullSig;

    if (!this.selectedAgentId || !agents.some(a => a.agentId === this.selectedAgentId)) {
      this.selectedAgentId = agents[0].agentId;
    }

    this.root.dataset.empty = '0';
    this._renderTabs(agents);
    this._applyTabSelection();
    this._renderAgentBody();
  }

  _renderTabs(agents) {
    this.tabsEl.innerHTML = agents.map(agent => {
      const label = this._currentLabel(agent);
      const iterCount = Array.isArray(agent.iterations) ? agent.iterations.length : 0;
      return `
        <button type="button" class="app-prompt-tab" role="tab"
          data-agent-id="${escapeHtml(agent.agentId)}"
          aria-selected="false">
          <span class="app-prompt-tab-role">${escapeHtml(agent.role || agent.agentId)}</span>
          <span class="app-prompt-tab-meta">
            <span class="app-prompt-tab-ver">${escapeHtml(label)}</span>
            ${iterCount ? `<span class="app-prompt-tab-iters">${escapeHtml(this._t('agentPrompt.tabIterations', { count: iterCount }))}</span>` : ''}
          </span>
        </button>
      `;
    }).join('');
  }

  _renderAgentBody() {
    const { agents } = this._collectBoard();
    const agent = agents.find(item => item.agentId === this.selectedAgentId) || agents[0];
    if (!agent) {
      this.bodyEl.innerHTML = `<div class="app-prompt-placeholder">${escapeHtml(this._t('agentPrompt.empty'))}</div>`;
      return;
    }

    const versions = this._buildPromptVersions(agent);
    const label = this._currentLabel(agent);

    if (!versions.length) {
      this.bodyEl.innerHTML = `
        <div class="app-prompt-card">
          <div class="app-prompt-card-head">
            <span class="app-prompt-badge app-prompt-badge--current">${escapeHtml(this._t('agentPrompt.currentVersion', { label }))}</span>
            <span class="app-prompt-card-note">${escapeHtml(this._t('agentPrompt.noIterations'))}</span>
          </div>
        </div>
      `;
      return;
    }

    this.bodyEl.innerHTML = `
      <div class="app-prompt-card">
        <div class="app-prompt-card-head">
          <span class="app-prompt-badge app-prompt-badge--current">${escapeHtml(this._t('agentPrompt.currentVersion', { label }))}</span>
          <span class="app-prompt-card-note">${escapeHtml(this._t('agentPrompt.versionStackHint'))}</span>
        </div>
        <div class="app-prompt-version-stack">
          ${versions.map(item => renderPromptBox(item.label, item.text)).join('')}
        </div>
      </div>
    `;
  }

  destroy() {
    if (this.tickHandle) this.window.clearInterval(this.tickHandle);
    this.window.removeEventListener('agent-selected', this._onSelected);
    if (this.root?.parentNode) this.root.parentNode.removeChild(this.root);
  }
}
