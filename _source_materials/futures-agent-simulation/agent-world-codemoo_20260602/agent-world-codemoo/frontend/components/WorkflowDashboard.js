// Functional workstation panels replacing the pixel-map "rooms".
// Each card surfaces live trading / agent data for thesis demos.

const DASH_VERSION = 1;

const STATION_DEFS = [
  { id: 'news', title: '资讯采集台', field: 'news' },
  { id: 'memory', title: '记忆档案馆', field: 'memory' },
  { id: 'price', title: '价格趋势墙', field: 'price' },
  { id: 'risk', title: '风险控制室', field: 'risk' },
  { id: 'debate', title: '智能体辩论场', field: 'debate' },
  { id: 'trade', title: '交易执行门', field: 'trade' }
];

function escapeHtml(value) {
  return String(value ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function fmtPrice(value) {
  const n = Number(value);
  if (!Number.isFinite(n)) return '--';
  if (Math.abs(n) >= 1000) return n.toLocaleString('zh-CN', { maximumFractionDigits: 0 });
  return n.toLocaleString('zh-CN', { maximumFractionDigits: 2 });
}

function injectStyles(doc) {
  if (doc.getElementById('workflow-dashboard-styles')) return;
  const style = doc.createElement('style');
  style.id = 'workflow-dashboard-styles';
  style.textContent = `
    #workflow-dashboard {
      position: fixed;
      left: calc(var(--panel-left-width, 260px) + 16px);
      right: calc(var(--panel-right-width, 360px) + 16px);
      top: 12px;
      bottom: 64px;
      z-index: 3;
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      grid-template-rows: repeat(2, minmax(0, 1fr));
      gap: 10px;
      pointer-events: none;
    }
    #workflow-dashboard[data-empty="1"] { display: none; }
    #workflow-dashboard .wf-card {
      pointer-events: auto;
      display: flex;
      flex-direction: column;
      min-height: 0;
      background: rgba(10, 18, 28, 0.88);
      border: 1px solid rgba(148, 163, 184, 0.22);
      border-radius: 10px;
      box-shadow: 0 10px 28px rgba(0,0,0,0.32);
      overflow: hidden;
      transition: border-color 0.15s ease, box-shadow 0.15s ease;
    }
    #workflow-dashboard .wf-card[data-active="1"] {
      border-color: rgba(56, 189, 248, 0.55);
      box-shadow: 0 0 0 1px rgba(56, 189, 248, 0.25), 0 12px 32px rgba(0,0,0,0.38);
    }
    #workflow-dashboard .wf-head {
      padding: 8px 10px 6px;
      border-bottom: 1px solid rgba(148, 163, 184, 0.14);
      background: rgba(15, 23, 42, 0.55);
    }
    #workflow-dashboard .wf-head strong {
      display: block;
      color: #f8fafc;
      font: 600 11px/1.3 Menlo, Monaco, monospace;
      letter-spacing: 0.04em;
    }
    #workflow-dashboard .wf-head span {
      color: #94a3b8;
      font: 10px/1.3 Menlo, Monaco, monospace;
    }
    #workflow-dashboard .wf-body {
      flex: 1;
      min-height: 0;
      padding: 8px 10px 10px;
      overflow: auto;
      color: #cbd5e1;
      font: 10px/1.45 Menlo, Monaco, monospace;
    }
    #workflow-dashboard .wf-list {
      margin: 0;
      padding-left: 14px;
    }
    #workflow-dashboard .wf-list li { margin: 0 0 4px; }
    #workflow-dashboard .wf-prices {
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 6px;
      margin-bottom: 8px;
    }
    #workflow-dashboard .wf-price-item {
      padding: 6px;
      border-radius: 6px;
      background: rgba(15, 23, 42, 0.72);
      border: 1px solid rgba(125, 211, 252, 0.18);
    }
    #workflow-dashboard .wf-price-item b {
      display: block;
      color: #7dd3fc;
      font-size: 11px;
      margin-top: 2px;
    }
    #workflow-dashboard .wf-spark {
      width: 100%;
      height: 42px;
      margin-top: 4px;
    }
    #workflow-dashboard .wf-agent-row {
      display: flex;
      justify-content: space-between;
      gap: 8px;
      padding: 3px 0;
      border-bottom: 1px solid rgba(148, 163, 184, 0.08);
    }
    #workflow-dashboard .wf-agent-row:last-child { border-bottom: none; }
    #workflow-dashboard .wf-tag {
      display: inline-block;
      padding: 1px 5px;
      border-radius: 4px;
      font-size: 9px;
      background: rgba(56, 189, 248, 0.14);
      color: #7dd3fc;
    }
    #workflow-dashboard .wf-risk-summary {
      color: #94a3b8;
      margin-bottom: 6px;
      line-height: 1.45;
    }
    #workflow-dashboard .wf-risk-row {
      padding: 4px 0;
      border-bottom: 1px solid rgba(148, 163, 184, 0.08);
    }
    #workflow-dashboard .wf-risk-row:last-child { border-bottom: none; }
    #workflow-dashboard .wf-risk-meta {
      color: #64748b;
      font-size: 9px;
      margin-top: 2px;
      line-height: 1.35;
    }
    #workflow-dashboard .wf-tag--pass { background: rgba(74, 222, 128, 0.16); color: #86efac; }
    #workflow-dashboard .wf-tag--warn { background: rgba(248, 113, 113, 0.16); color: #fca5a5; }
    #workflow-dashboard .wf-tag--review { background: rgba(251, 191, 36, 0.16); color: #fde68a; }
    #workflow-dashboard .wf-tag--limit { background: rgba(249, 115, 22, 0.16); color: #fdba74; }
    @media (max-width: 1100px) {
      #workflow-dashboard {
        grid-template-columns: repeat(2, minmax(0, 1fr));
        grid-template-rows: repeat(3, minmax(0, 1fr));
        right: 12px;
      }
    }
    @media (max-width: 760px) {
      #workflow-dashboard { display: none; }
    }
  `;
  doc.head.appendChild(style);
}

export default class WorkflowDashboard {
  constructor({ mountEl = null, document: doc = document, window: win = window } = {}) {
    this.mountEl = mountEl;
    this.document = doc;
    this.window = win;
    this.state = null;
    this.cards = new Map();
    console.log(`[WorkflowDashboard v${DASH_VERSION}] init`);

    if (!this.mountEl) {
      injectStyles(doc);
    }
    this._build();
    this._bind();
  }

  _build() {
    const doc = this.document;
    this.root = doc.createElement('section');
    this.root.id = 'workflow-dashboard';
    this.root.dataset.empty = '1';
    this.root.setAttribute('aria-label', '决策工作站看板');

    for (const def of STATION_DEFS) {
      const card = doc.createElement('article');
      card.className = 'wf-card';
      card.dataset.stationId = def.id;
      card.innerHTML = `
        <div class="wf-head">
          <strong>${escapeHtml(def.title)}</strong>
          <span class="wf-sub">—</span>
        </div>
        <div class="wf-body"></div>
      `;
      this.cards.set(def.id, card);
      this.root.appendChild(card);
    }

    (this.mountEl || doc.body).appendChild(this.root);
  }

  _bind() {
    this._onWorldState = ev => {
      this.state = ev?.detail || null;
      this._render();
    };
    this.window.addEventListener('world-state', this._onWorldState);
  }

  handleStateUpdate(state) {
    this.state = state || null;
    this._render();
  }

  _activeStationIds() {
    const agents = this.state?.agents || {};
    const ids = new Set();
    for (const agent of Object.values(agents)) {
      if (!agent) continue;
      const zone = agent.zone || agent.destination?.stationId;
      if (zone) ids.add(zone);
    }
    return ids;
  }

  _renderNews(trading) {
    const items = Array.isArray(trading.news) ? trading.news.slice(0, 4) : [];
    if (!items.length) return '<div class="wf-note">等待资讯流…</div>';
    return `<ul class="wf-list">${items.map(t => `<li>${escapeHtml(t)}</li>`).join('')}</ul>`;
  }

  _renderMemory(state) {
    const snippets = [];
    for (const agent of Object.values(state.agents || {})) {
      const mem = agent?.memory?.retrieved;
      if (Array.isArray(mem)) {
        for (const row of mem.slice(0, 1)) {
          const role = agent.role || agent.name;
          snippets.push({ role, text: row.text || row.id || '' });
        }
      }
    }
    if (!snippets.length) return '<div class="wf-note">暂无检索记忆</div>';
    return `<ul class="wf-list">${snippets.slice(0, 4).map(s => `
      <li class="wf-memory-line">
        <span class="ui-role-chip">${escapeHtml(s.role)}</span>
        <span class="wf-memory-text">${escapeHtml(s.text ? `：${s.text}` : '')}</span>
      </li>`).join('')}</ul>`;
  }

  _renderPrice(trading) {
    const prices = trading.prices || {};
    const commodities = Array.isArray(trading.commodities) ? trading.commodities : [];
    const timeline = Array.isArray(trading.timeline) ? trading.timeline : [];
    const goldSeries = timeline
      .map(entry => Number(entry?.prices?.gold ?? NaN))
      .filter(Number.isFinite);
    const priceCards = commodities.length
      ? commodities.map(c => `
          <div class="wf-price-item">
            <span>${escapeHtml(c.name || c.id)}</span>
            <b>${escapeHtml(fmtPrice(prices[c.id]))}</b>
            <span style="color:#64748b">${escapeHtml(c.unit || '')}</span>
          </div>
        `).join('')
      : Object.keys(prices).map(id => `
          <div class="wf-price-item">
            <span>${escapeHtml(id)}</span>
            <b>${escapeHtml(fmtPrice(prices[id]))}</b>
          </div>
        `).join('');

    const spark = this._sparkline(goldSeries.length ? goldSeries : Object.values(prices).map(Number));
    return `
      <div class="wf-prices">${priceCards}</div>
      <div style="color:#94a3b8;margin-bottom:4px">累计回合价格/得分走势</div>
      ${spark}
    `;
  }

  _sparkline(values) {
    const pts = values.filter(Number.isFinite);
    if (pts.length < 2) {
      return '<div style="color:#64748b">需要更多轮次数据</div>';
    }
    const w = 280;
    const h = 42;
    const min = Math.min(...pts);
    const max = Math.max(...pts);
    const span = max - min || 1;
    const coords = pts.map((v, i) => {
      const x = (i / (pts.length - 1)) * (w - 8) + 4;
      const y = h - 6 - ((v - min) / span) * (h - 12);
      return `${x.toFixed(1)},${y.toFixed(1)}`;
    });
    return `<svg class="wf-spark" viewBox="0 0 ${w} ${h}" role="img" aria-hidden="true">
      <polyline fill="none" stroke="#38bdf8" stroke-width="1.5" points="${coords.join(' ')}"/>
    </svg>`;
  }

  _renderRisk(trading, state) {
    const risk = trading.risk;
    if (risk?.agents?.length) {
      const statusClass = {
        '通过': 'pass',
        '预警': 'warn',
        '复核': 'review',
        '限仓': 'limit'
      };
      const header = risk.summary
        ? `<div class="wf-risk-summary">${escapeHtml(risk.summary)}</div>`
        : '';
      const portfolio = Number.isFinite(Number(risk.portfolioAverageDrawdown))
        ? `<div class="wf-note">组合平均回撤：${escapeHtml(fmtPrice(-Math.abs(Number(risk.portfolioAverageDrawdown))))}% · 阈值 ${escapeHtml(String(risk.limits?.maxDrawdownPct ?? 18))}%</div>`
        : '';
      const rows = risk.agents.map(item => `
        <div class="wf-risk-row">
          <div class="wf-agent-row">
            <span class="ui-role-chip">${escapeHtml(item.role)}</span>
            <span class="wf-tag wf-tag--${escapeHtml(statusClass[item.status] || 'pass')}">${escapeHtml(item.status)}</span>
          </div>
          <div class="wf-risk-meta">
            回撤 ${escapeHtml(fmtPrice(-Math.abs(Number(item.drawdown || 0))))}% ·
            置信度 ${escapeHtml(fmtPrice(item.confidence))}% ·
            ${escapeHtml(item.action || 'HOLD')} ${escapeHtml(item.symbol || '')} ·
            敞口 ${escapeHtml(fmtPrice(item.exposurePct))}%
          </div>
          <div class="wf-risk-meta">${escapeHtml(item.note || '')}</div>
        </div>
      `).join('');
      return header + portfolio + rows;
    }

    const evalData = trading.evaluation || {};
    const analysis = evalData.analysis || {};
    const rows = [];
    if (Number.isFinite(Number(analysis.averageDrawdown))) {
      rows.push(`组合平均回撤：${fmtPrice(-Number(analysis.averageDrawdown))}`);
    }
    for (const agent of Object.values(state.agents || {})) {
      const dd = agent?.score?.drawdown ?? agent?.decision?.drawdown;
      if (dd != null) rows.push(`${agent.role || agent.name}：回撤 ${fmtPrice(-Math.abs(Number(dd)))}`);
    }
    if (!rows.length) return '<div class="wf-note">回撤边界检查中…</div>';
    return `<ul class="wf-list">${rows.slice(0, 5).map(t => `<li>${escapeHtml(t)}</li>`).join('')}</ul>`;
  }

  _renderDebate(state) {
    const debate = state?.meta?.trading?.debate;
    if (debate?.entries?.length) {
      const header = debate.summary
        ? `<div class="wf-debate-summary">${escapeHtml(debate.summary)}</div>`
        : '';
      const rows = debate.entries.map(entry => `
        <div class="wf-agent-row">
          <span class="ui-role-chip">${escapeHtml(entry.role)}</span>
          <span class="wf-tag wf-tag--${escapeHtml(entry.stance || 'neutral')}">${escapeHtml(entry.actionLabel || entry.action || 'HOLD')} · ${escapeHtml(entry.symbol || '')}</span>
        </div>
        <div class="wf-debate-reason">${escapeHtml((entry.reason || '').slice(0, 120))}</div>
        ${Array.isArray(entry.evidence) && entry.evidence.length
          ? `<div class="wf-debate-evidence">${entry.evidence.map(item => `<span class="wf-ev-chip">${escapeHtml(item)}</span>`).join('')}</div>`
          : ''}
      `).join('');
      const dissent = Array.isArray(debate.dissent) && debate.dissent.length
        ? `<div class="wf-note">异议：${debate.dissent.map(item => escapeHtml(item.role)).join('、')}</div>`
        : '';
      return header + rows + dissent;
    }

    const rows = [];
    for (const agent of Object.values(state.agents || {})) {
      const d = agent?.decision;
      if (!d) continue;
      rows.push(`
        <div class="wf-agent-row">
          <span class="ui-role-chip">${escapeHtml(agent.role || agent.name)}</span>
          <span class="wf-tag">${escapeHtml(d.action || 'HOLD')} · ${escapeHtml(d.symbol || '')}</span>
        </div>
        <div class="wf-debate-reason">${escapeHtml((d.reason || '').slice(0, 72))}</div>
      `);
    }
    if (!rows.length) return '<div class="wf-note">等待辩论输出…</div>';
    return rows.join('');
  }

  _renderTrade(state) {
    const execution = state?.meta?.trading?.execution;
    if (execution?.orders?.length) {
      const header = execution.summary
        ? `<div class="wf-trade-summary">${escapeHtml(execution.summary)}</div>`
        : '';
      const rows = execution.orders.map(order => `
        <div class="wf-agent-row">
          <span class="ui-role-chip">${escapeHtml(order.role || order.agentId || '')}</span>
          <span class="wf-trade-action wf-trade-action--${escapeHtml(order.status || 'pending')}">
            <b>${escapeHtml(order.action || '等待')}</b> ${escapeHtml(order.symbol || '')}
            ${order.confidence != null ? ` · ${escapeHtml(fmtPrice(order.confidence))}%` : ''}
          </span>
        </div>
        ${order.note ? `<div class="wf-debate-reason">${escapeHtml(order.note)}</div>` : ''}
      `).join('');
      return header + rows;
    }

    const rows = [];
    for (const agent of Object.values(state.agents || {})) {
      const d = agent?.decision;
      if (!d) continue;
      const action = d.actionLabel || d.action || 'HOLD';
      rows.push(`
        <div class="wf-agent-row">
          <span class="ui-role-chip">${escapeHtml(agent.role || agent.name)}</span>
          <span class="wf-trade-action"><b>${escapeHtml(action)}</b> ${escapeHtml(d.symbol || '')} · ${escapeHtml(fmtPrice(d.confidence))}%</span>
        </div>
      `);
    }
    if (!rows.length) return '<div class="wf-note">等待交易指令…</div>';
    return rows.join('');
  }

  _render() {
    const trading = this.state?.meta?.trading;
    if (!trading) {
      this.root.dataset.empty = '1';
      return;
    }
    this.root.dataset.empty = '0';
    const active = this._activeStationIds();
    const regime = trading.regime || '';
    const date = trading.currentDate || '';

    for (const def of STATION_DEFS) {
      const card = this.cards.get(def.id);
      if (!card) continue;
      card.dataset.active = active.has(def.id) ? '1' : '0';
      const sub = card.querySelector('.wf-sub');
      if (sub) {
        sub.textContent = active.has(def.id)
          ? `进行中 · ${date}`
          : `${regime} · ${date}`;
      }
      const body = card.querySelector('.wf-body');
      if (!body) continue;
      if (def.field === 'news') body.innerHTML = this._renderNews(trading);
      else if (def.field === 'memory') body.innerHTML = this._renderMemory(this.state);
      else if (def.field === 'price') body.innerHTML = this._renderPrice(trading);
      else if (def.field === 'risk') body.innerHTML = this._renderRisk(trading, this.state);
      else if (def.field === 'debate') body.innerHTML = this._renderDebate(this.state);
      else if (def.field === 'trade') body.innerHTML = this._renderTrade(this.state);
    }
  }

  destroy() {
    this.window.removeEventListener('world-state', this._onWorldState);
    if (this.root?.parentNode) this.root.parentNode.removeChild(this.root);
  }
}
