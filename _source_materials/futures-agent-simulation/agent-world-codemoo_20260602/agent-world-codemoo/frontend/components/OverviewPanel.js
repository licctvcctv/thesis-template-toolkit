const OVERVIEW_VERSION = 3;

function formatYearMonth(dateStr) {
  const raw = String(dateStr || '').trim();
  if (!raw) return '—';
  if (/^\d{4}-\d{2}/.test(raw)) return raw.slice(0, 7);
  const parsed = new Date(raw);
  if (Number.isNaN(parsed.getTime())) return raw;
  const y = parsed.getFullYear();
  const m = String(parsed.getMonth() + 1).padStart(2, '0');
  return `${y}-${m}`;
}

function escapeHtml(value) {
  return String(value ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');
}

/** 总览行情数值：统一保留两位小数 */
function fmtOverviewPrice(value) {
  const n = Number(value);
  if (!Number.isFinite(n)) return '—';
  return n.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

export default class OverviewPanel {
  constructor({ mountEl, document: doc = document, window: win = window } = {}) {
    this.mountEl = mountEl;
    this.document = doc;
    this.window = win;
    this.state = null;
    console.log(`[OverviewPanel v${OVERVIEW_VERSION}] init`);
    this._build();
    this._bind();
  }

  _build() {
    const doc = this.document;
    this.root = doc.createElement('section');
    this.root.id = 'overview-panel';
    this.root.dataset.empty = '1';
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

  _render() {
    const trading = this.state?.meta?.trading;
    if (!trading) {
      this.root.dataset.empty = '1';
      this.root.innerHTML = '<div class="ov-wrap"><p class="page-intro">等待仿真数据…</p></div>';
      return;
    }
    this.root.dataset.empty = '0';
    const agents = Object.values(this.state?.agents || {});
    const round = Number(trading.currentRound);
    const roundLabel = Number.isFinite(round) ? round + 1 : '—';

    const prices = trading.prices || {};
    const commodityOrder = ['gold', 'soybean', 'crude_oil'];
    const commodityMeta = new Map(
      (Array.isArray(trading.commodities) ? trading.commodities : []).map(c => [c.id, c])
    );
    const priceCardsHtml = commodityOrder.map(id => {
      const c = commodityMeta.get(id) || { id, name: id };
      return `
          <div class="ov-card ov-card--metric">
            <label>${escapeHtml(c.name || id)}</label>
            <b>${escapeHtml(fmtOverviewPrice(prices[id]))}</b>
          </div>
        `;
    }).join('');

    const steps = [
      ['01', '资讯采集'],
      ['02', '记忆检索'],
      ['03', '多空辩论'],
      ['04', '交易执行'],
      ['05', '策略修正']
    ];

    this.root.innerHTML = `
      <div class="ov-wrap">
        <div class="ov-dashboard">
          <div class="ov-metrics" aria-label="仿真指标">
            <div class="ov-card ov-card--highlight ov-card--metric">
              <label>当前轮次</label>
              <b>第 ${escapeHtml(roundLabel)} 轮</b>
            </div>
            <div class="ov-card ov-card--metric">
              <label>情景日期</label>
              <b class="ov-date">${escapeHtml(formatYearMonth(trading.currentDate))}</b>
            </div>
            <div class="ov-card ov-card--metric">
              <label>活跃智能体</label>
              <b>${escapeHtml(String(agents.length))}</b>
            </div>
            ${priceCardsHtml}
          </div>
          <aside class="ov-regime" aria-label="市场阶段">
            <label>市场阶段</label>
            <p class="ov-regime-text">${escapeHtml(trading.regime || '—')}</p>
          </aside>
        </div>
        <h2 class="ov-flow-title">决策流程</h2>
        <div class="ov-flow">
          ${steps.map(([n, t], i) => `
            <div class="ov-step${i === 0 ? ' ov-step--active' : ''}">
              <i>${n}</i>${escapeHtml(t)}
            </div>
          `).join('')}
        </div>
      </div>
    `;
  }

  destroy() {
    this.window.removeEventListener('world-state', this._onWorldState);
    if (this.root?.parentNode) this.root.parentNode.removeChild(this.root);
  }
}
