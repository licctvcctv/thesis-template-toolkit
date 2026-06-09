const HUD_VERSION = 4;
const TRADING_SNAPSHOT_KEY = 'futures-agent-simulation.trading-summary.v2';

function injectStyles(doc) {
  if (doc.getElementById('trading-hud-styles')) return;
  const style = doc.createElement('style');
  style.id = 'trading-hud-styles';
  style.textContent = `
    #trading-hud,
    #strategy-scoreboard,
    #prediction-report {
      position: fixed;
      overflow: auto;
      z-index: 9;
      color: #e7f4ff;
      font: 11px/1.45 Menlo, Monaco, Consolas, monospace;
      border-radius: 10px;
      backdrop-filter: blur(10px);
    }
    #trading-hud {
      left: 12px;
      top: 198px;
      background:
        linear-gradient(180deg, rgba(10, 20, 28, 0.94), rgba(7, 13, 18, 0.88)),
        radial-gradient(circle at 15% 0%, rgba(56, 189, 248, 0.20), transparent 38%);
      border: 1px solid rgba(125, 211, 252, 0.32);
      box-shadow: 0 16px 40px rgba(0, 0, 0, 0.42);
    }
    #strategy-scoreboard {
      right: 12px;
      top: 12px;
      background:
        linear-gradient(180deg, rgba(14, 17, 24, 0.96), rgba(8, 11, 16, 0.90)),
        radial-gradient(circle at 92% 4%, rgba(251, 191, 36, 0.16), transparent 34%),
        radial-gradient(circle at 8% 100%, rgba(74, 222, 128, 0.13), transparent 38%);
      border: 1px solid rgba(251, 191, 36, 0.28);
      box-shadow: 0 18px 42px rgba(0, 0, 0, 0.46);
    }
    #trading-hud {
      width: var(--panel-left-width, 260px);
      max-height: calc(100vh - 220px);
    }
    #strategy-scoreboard {
      width: min(var(--panel-right-width, 360px), calc(100vw - 300px));
      max-height: calc(100vh - 88px);
    }
    #prediction-report {
      left: 50%;
      top: 50%;
      bottom: auto;
      transform: translate(-50%, -50%);
      width: min(1360px, calc(100vw - 48px));
      height: min(820px, calc(100vh - 48px));
      max-height: calc(100vh - 48px);
      z-index: 18;
      background:
        linear-gradient(180deg, rgba(10, 18, 25, 0.97), rgba(6, 10, 15, 0.92)),
        radial-gradient(circle at 0% 0%, rgba(56, 189, 248, 0.14), transparent 32%),
        radial-gradient(circle at 100% 100%, rgba(74, 222, 128, 0.12), transparent 30%);
      border: 1px solid rgba(125, 211, 252, 0.24);
      border-radius: 12px;
      box-shadow:
        0 0 0 9999px rgba(2, 6, 23, 0.48),
        0 28px 80px rgba(0, 0, 0, 0.62);
    }
    #trading-hud[data-empty="1"],
    #strategy-scoreboard[data-empty="1"],
    #prediction-report[data-empty="1"] { display: none; }
    #prediction-report[data-collapsed="1"] {
      left: auto;
      right: 18px;
      top: auto;
      bottom: 16px;
      transform: none;
      width: min(420px, calc(100vw - 24px));
      height: auto;
      max-height: 56px;
      overflow: hidden;
      box-shadow: 0 18px 44px rgba(0, 0, 0, 0.48);
    }
    body[data-trading-report-open="1"] #trading-hud,
    body[data-trading-report-open="1"] #strategy-scoreboard,
    body[data-trading-report-open="1"] #event-log,
    body[data-trading-report-open="1"] #timeline-scrubber,
    body[data-trading-report-open="1"] #agent-roster {
      opacity: 0;
      pointer-events: none;
      transition: opacity 0.14s ease;
    }
    body[data-trading-report-open="1"] #prediction-report {
      opacity: 1;
      pointer-events: auto;
    }
    #trading-hud .th-head,
    #strategy-scoreboard .sb-head,
    #prediction-report .pr-head {
      padding: 11px 13px 9px;
      border-bottom: 1px solid rgba(148, 163, 184, 0.18);
      background: rgba(15, 23, 42, 0.42);
    }
    #prediction-report .pr-head {
      padding: 18px 22px 15px;
      position: sticky;
      top: 0;
      z-index: 1;
      background: rgba(8, 14, 22, 0.92);
      backdrop-filter: blur(12px);
    }
    #trading-hud .th-title,
    #strategy-scoreboard .sb-title,
    #prediction-report .pr-title {
      display: flex;
      justify-content: space-between;
      align-items: baseline;
      gap: 10px;
      margin-bottom: 5px;
    }
    #trading-hud .th-title strong,
    #strategy-scoreboard .sb-title strong,
    #prediction-report .pr-title strong {
      color: #f8fafc;
      font-size: 13px;
      letter-spacing: 0.04em;
      text-transform: uppercase;
    }
    #prediction-report .pr-title strong {
      font-size: 18px;
      letter-spacing: 0.08em;
    }
    #trading-hud .th-date,
    #strategy-scoreboard .sb-source {
      color: #fbbf24;
      font-variant-numeric: tabular-nums;
      white-space: nowrap;
    }
    #trading-hud .th-regime,
    #strategy-scoreboard .sb-subtitle,
    #prediction-report .pr-subtitle {
      color: #9fb5c8;
      font-size: 10px;
    }
    #prediction-report .pr-subtitle {
      font-size: 12px;
    }
    #trading-hud .th-flow {
      display: grid;
      grid-template-columns: repeat(5, minmax(0, 1fr));
      gap: 5px;
      padding: 10px 12px;
      border-bottom: 1px solid rgba(148, 163, 184, 0.14);
    }
    #trading-hud .th-step {
      padding: 6px 5px;
      border-radius: 7px;
      background: rgba(15, 23, 42, 0.64);
      border: 1px solid rgba(148, 163, 184, 0.16);
      min-width: 0;
    }
    #trading-hud .th-step b {
      display: block;
      color: #38bdf8;
      font-size: 9px;
      margin-bottom: 2px;
    }
    #trading-hud .th-step span {
      display: block;
      color: #dbeafe;
      font-size: 9px;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
    #trading-hud .th-section,
    #strategy-scoreboard .sb-section {
      padding: 10px 12px;
      border-bottom: 1px solid rgba(148, 163, 184, 0.12);
    }
    #trading-hud .th-label,
    #strategy-scoreboard .sb-label {
      color: #7dd3fc;
      text-transform: uppercase;
      letter-spacing: 0.06em;
      font-size: 10px;
      font-weight: 700;
      margin-bottom: 7px;
    }
    #trading-hud .th-prices {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 6px;
    }
    #trading-hud .th-price {
      border-radius: 7px;
      background: rgba(2, 6, 23, 0.48);
      border: 1px solid rgba(148, 163, 184, 0.16);
      padding: 7px;
    }
    #trading-hud .th-symbol {
      color: #fbbf24;
      font-weight: 700;
      margin-bottom: 3px;
    }
    #trading-hud .th-value {
      color: #f8fafc;
      font-size: 13px;
      font-variant-numeric: tabular-nums;
    }
    #trading-hud .th-news {
      display: flex;
      flex-direction: column;
      gap: 6px;
    }
    #trading-hud .th-news-item {
      padding: 7px 8px;
      border-radius: 7px;
      background: rgba(14, 165, 233, 0.08);
      border-left: 2px solid rgba(251, 191, 36, 0.78);
      color: #cbd5e1;
    }
    #strategy-scoreboard .sb-windows {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 7px;
    }
    #strategy-scoreboard .sb-window {
      border-radius: 7px;
      background: rgba(2, 6, 23, 0.45);
      border: 1px solid rgba(148, 163, 184, 0.14);
      padding: 7px;
    }
    #strategy-scoreboard .sb-window b {
      display: block;
      color: #f8fafc;
      font-size: 12px;
      margin-bottom: 2px;
    }
    #strategy-scoreboard .sb-window span {
      color: #94a3b8;
      font-size: 10px;
    }
    #strategy-scoreboard .sb-ranks {
      display: flex;
      flex-direction: column;
      gap: 8px;
    }
    #strategy-scoreboard .sb-agent {
      border-radius: 9px;
      background: rgba(15, 23, 42, 0.62);
      border: 1px solid rgba(148, 163, 184, 0.16);
      padding: 9px;
    }
    #strategy-scoreboard .sb-score-card--best {
      border-color: rgba(56, 189, 248, 0.42);
      box-shadow: inset 3px 0 0 rgba(56, 189, 248, 0.72);
    }
    #strategy-scoreboard .sb-agent-head {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 8px;
      margin-bottom: 7px;
    }
    #strategy-scoreboard .sb-agent-name {
      color: #f8fafc;
      font-weight: 700;
      font-size: 12px;
    }
    #strategy-scoreboard .sb-rank {
      color: #38bdf8;
      margin-right: 5px;
    }
    #strategy-scoreboard .sb-metrics {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 5px;
      margin-bottom: 7px;
    }
    #strategy-scoreboard .sb-metric {
      min-width: 0;
      border-radius: 6px;
      background: rgba(2, 6, 23, 0.42);
      padding: 6px 5px;
    }
    #strategy-scoreboard .sb-metric span {
      display: block;
      color: #94a3b8;
      font-size: 9px;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
    #strategy-scoreboard .sb-metric b {
      display: block;
      color: #f8fafc;
      font-size: 11px;
      font-variant-numeric: tabular-nums;
      margin-top: 2px;
    }
    #strategy-scoreboard .sb-note,
    #strategy-scoreboard .sb-trade {
      color: #cbd5e1;
      font-size: 10px;
    }
    #strategy-scoreboard .sb-trade {
      margin-top: 5px;
      color: #93c5fd;
    }
    #prediction-report .pr-toggle {
      border: 1px solid rgba(125, 211, 252, 0.26);
      border-radius: 999px;
      color: #dbeafe;
      background: rgba(15, 23, 42, 0.65);
      padding: 6px 12px;
      font: inherit;
      font-size: 12px;
      cursor: pointer;
      white-space: nowrap;
    }
    #prediction-report .pr-toggle:hover {
      border-color: rgba(125, 211, 252, 0.62);
      background: rgba(30, 41, 59, 0.78);
    }
    #prediction-report .pr-report-shell {
      padding: 18px 20px 22px;
    }
    #prediction-report .pr-grid {
      display: grid;
      grid-template-columns: minmax(260px, 0.82fr) minmax(430px, 1.18fr) minmax(320px, 0.92fr);
      gap: 14px;
      align-items: start;
      padding: 0;
    }
    #prediction-report .pr-card {
      min-width: 0;
      border-radius: 9px;
      background: rgba(2, 6, 23, 0.42);
      border: 1px solid rgba(148, 163, 184, 0.14);
      padding: 14px;
    }
    #prediction-report .pr-card-title {
      color: #7dd3fc;
      font-size: 11px;
      font-weight: 800;
      letter-spacing: 0.06em;
      text-transform: uppercase;
      margin-bottom: 11px;
    }
    #prediction-report .pr-kpis {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 9px;
    }
    #prediction-report .pr-kpi {
      border-radius: 8px;
      background: rgba(15, 23, 42, 0.62);
      padding: 11px;
      min-width: 0;
    }
    #prediction-report .pr-kpi span,
    #prediction-report .pr-action-label,
    #prediction-report .pr-axis-note {
      display: block;
      color: #94a3b8;
      font-size: 10px;
    }
    #prediction-report .pr-kpi b {
      display: block;
      color: #f8fafc;
      font-size: 20px;
      font-variant-numeric: tabular-nums;
      margin-top: 4px;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
    #prediction-report .pr-bars {
      display: flex;
      flex-direction: column;
      gap: 10px;
    }
    #prediction-report .pr-bar-row {
      display: grid;
      grid-template-columns: 74px 1fr 64px;
      gap: 10px;
      align-items: center;
    }
    #prediction-report .pr-bar-name {
      color: #e2e8f0;
      font-weight: 700;
      font-size: 12px;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
    #prediction-report .pr-bar-track {
      position: relative;
      height: 26px;
      border-radius: 999px;
      background: rgba(15, 23, 42, 0.82);
      overflow: hidden;
      border: 1px solid rgba(148, 163, 184, 0.12);
    }
    #prediction-report .pr-bar-track::before {
      content: '';
      position: absolute;
      left: 50%;
      top: 0;
      bottom: 0;
      width: 1px;
      background: rgba(226, 232, 240, 0.28);
    }
    #prediction-report .pr-bar {
      position: absolute;
      top: 4px;
      height: 8px;
      min-width: 2px;
      border-radius: 999px;
    }
    #prediction-report .pr-bar.train { background: #38bdf8; }
    #prediction-report .pr-bar.test { top: 14px; background: #fbbf24; }
    #prediction-report .pr-bar.pos { left: 50%; }
    #prediction-report .pr-bar.neg { right: 50%; }
    #prediction-report .pr-bar-score {
      color: #cbd5e1;
      text-align: right;
      font-variant-numeric: tabular-nums;
      white-space: nowrap;
      font-size: 12px;
    }
    #prediction-report .pr-legend {
      display: flex;
      gap: 14px;
      color: #94a3b8;
      font-size: 10px;
      margin-top: 12px;
    }
    #prediction-report .pr-dot {
      display: inline-block;
      width: 7px;
      height: 7px;
      border-radius: 99px;
      margin-right: 4px;
      vertical-align: 1px;
    }
    #prediction-report .pr-dot.train { background: #38bdf8; }
    #prediction-report .pr-dot.test { background: #fbbf24; }
    #prediction-report .pr-curve {
      width: 100%;
      height: 168px;
      display: block;
      border-radius: 8px;
      background: rgba(15, 23, 42, 0.44);
      border: 1px solid rgba(148, 163, 184, 0.12);
    }
    #prediction-report .pr-actions {
      display: grid;
      grid-template-columns: 1fr;
      gap: 9px;
      margin: 12px 0;
    }
    #prediction-report .pr-action-track {
      height: 12px;
      border-radius: 999px;
      background: rgba(15, 23, 42, 0.8);
      overflow: hidden;
      display: flex;
    }
    #prediction-report .pr-action {
      min-width: 2px;
      height: 100%;
    }
    #prediction-report .pr-action.buy { background: #4ade80; }
    #prediction-report .pr-action.sell { background: #f97316; }
    #prediction-report .pr-action.hold { background: #94a3b8; }
    #prediction-report .pr-conclusions {
      margin: 0;
      padding-left: 16px;
      color: #dbeafe;
      font-size: 12px;
    }
    #prediction-report .pr-conclusions li {
      margin-bottom: 8px;
    }
    #prediction-report .pr-note {
      color: #fef3c7;
      background: rgba(251, 191, 36, 0.08);
      border-left: 2px solid rgba(251, 191, 36, 0.72);
      border-radius: 7px;
      padding: 9px 10px;
      margin-top: 10px;
      font-size: 11px;
    }
    #prediction-report .pr-scope {
      color: #bae6fd;
      background: rgba(56, 189, 248, 0.08);
      border: 1px solid rgba(125, 211, 252, 0.18);
      border-radius: 8px;
      padding: 9px 10px;
      margin: 10px 0 0;
      font-size: 11px;
    }
    #prediction-report .pr-agent-section {
      margin-top: 16px;
    }
    #prediction-report .pr-section-head {
      display: flex;
      justify-content: space-between;
      align-items: baseline;
      gap: 14px;
      margin: 0 0 10px;
      color: #e0f2fe;
    }
    #prediction-report .pr-section-head strong {
      font-size: 13px;
      letter-spacing: 0.08em;
      text-transform: uppercase;
    }
    #prediction-report .pr-section-head span {
      color: #93c5fd;
      font-size: 11px;
    }
    #prediction-report .pr-agent-grid {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 12px;
    }
    #prediction-report .pr-agent-card {
      min-width: 0;
      border-radius: 10px;
      background:
        linear-gradient(180deg, rgba(15, 23, 42, 0.72), rgba(2, 6, 23, 0.58));
      border: 1px solid rgba(148, 163, 184, 0.16);
      padding: 13px;
      box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.03);
    }
    #prediction-report .pr-agent-head {
      display: grid;
      grid-template-columns: 1fr auto;
      gap: 10px;
      align-items: start;
      margin-bottom: 10px;
    }
    #prediction-report .pr-agent-role {
      display: flex;
      align-items: center;
      gap: 8px;
      color: #f8fafc;
      font-size: 14px;
      font-weight: 800;
    }
    #prediction-report .pr-agent-rank {
      color: #38bdf8;
      font-variant-numeric: tabular-nums;
    }
    #prediction-report .pr-agent-meta {
      color: #94a3b8;
      font-size: 10px;
      margin-top: 2px;
    }
    #prediction-report .pr-agent-score {
      color: #f8fafc;
      font-size: 21px;
      font-weight: 900;
      font-variant-numeric: tabular-nums;
      text-align: right;
    }
    #prediction-report .pr-agent-badge {
      display: inline-block;
      margin-left: 6px;
      border-radius: 999px;
      padding: 2px 7px;
      font-size: 10px;
      color: #082f49;
      background: #7dd3fc;
      vertical-align: 2px;
    }
    #prediction-report .pr-agent-metrics {
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 6px;
      margin-bottom: 10px;
    }
    #prediction-report .pr-agent-metric {
      min-width: 0;
      border-radius: 7px;
      background: rgba(2, 6, 23, 0.45);
      padding: 7px 8px;
    }
    #prediction-report .pr-agent-metric span {
      display: block;
      color: #94a3b8;
      font-size: 9px;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
    #prediction-report .pr-agent-metric b {
      display: block;
      color: #f8fafc;
      font-size: 12px;
      font-variant-numeric: tabular-nums;
      margin-top: 2px;
    }
    #prediction-report .pr-failure-box,
    #prediction-report .pr-repair-box {
      border-radius: 8px;
      padding: 9px 10px;
      font-size: 11px;
    }
    #prediction-report .pr-failure-box {
      background: rgba(127, 29, 29, 0.20);
      border: 1px solid rgba(248, 113, 113, 0.20);
      color: #fee2e2;
      margin-top: 8px;
    }
    #prediction-report .pr-repair-box {
      background: rgba(20, 83, 45, 0.18);
      border: 1px solid rgba(74, 222, 128, 0.18);
      color: #dcfce7;
      margin-top: 8px;
    }
    #prediction-report .pr-box-title {
      display: block;
      color: #fef3c7;
      font-weight: 800;
      margin-bottom: 5px;
    }
    #prediction-report .pr-failure-list {
      margin: 7px 0 0;
      padding-left: 16px;
    }
    #prediction-report .pr-failure-list li {
      margin-bottom: 4px;
    }
    @media (max-width: 1080px) {
      #strategy-scoreboard {
        right: auto;
        left: 12px;
        top: 466px;
        max-height: calc(100vh - 478px);
      }
      #prediction-report {
        width: min(880px, calc(100vw - 28px));
        height: calc(100vh - 52px);
        max-height: calc(100vh - 52px);
      }
      #prediction-report .pr-grid {
        grid-template-columns: 1fr;
      }
      #prediction-report .pr-agent-grid {
        grid-template-columns: 1fr;
      }
    }
    @media (max-width: 900px) {
      #trading-hud {
        top: 48px;
        max-height: 35vh;
      }
      #strategy-scoreboard {
        top: calc(35vh + 58px);
        max-height: calc(65vh - 76px);
      }
      #prediction-report {
        width: calc(100vw - 20px);
        height: calc(100vh - 20px);
        max-height: calc(100vh - 20px);
      }
      #prediction-report[data-collapsed="1"] { display: none; }
      #trading-hud .th-flow { grid-template-columns: repeat(5, 76px); overflow-x: auto; }
      #strategy-scoreboard .sb-metrics { grid-template-columns: repeat(2, 1fr); }
      #prediction-report .pr-agent-metrics,
      #prediction-report .pr-kpis { grid-template-columns: repeat(2, minmax(0, 1fr)); }
    }
  `;
  doc.head.appendChild(style);
}

function escapeHtml(value) {
  return String(value ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

function fmtPrice(value, locale = 'zh-CN') {
  if (!Number.isFinite(value)) return '--';
  if (Math.abs(value) >= 1000) return value.toLocaleString(locale, { maximumFractionDigits: 0 });
  return value.toLocaleString(locale, { maximumFractionDigits: 2 });
}

function fmtScore(value, locale = 'zh-CN') {
  if (!Number.isFinite(value)) return '--';
  const prefix = value > 0 ? '+' : '';
  return prefix + value.toLocaleString(locale, { maximumFractionDigits: 2 });
}

function pct(value, total) {
  if (!Number.isFinite(value) || !Number.isFinite(total) || total <= 0) return 0;
  return Math.max(0, Math.min(100, (value / total) * 100));
}

const SPARKLINE_POINTS = 6;

function timelinePriceSeries(trading, commodityId) {
  const timeline = Array.isArray(trading?.timeline) ? trading.timeline : [];
  const series = [];
  for (const entry of timeline) {
    const price = Number(entry?.prices?.[commodityId]);
    if (Number.isFinite(price)) series.push(price);
  }
  if (!series.length) {
    const current = Number(trading?.prices?.[commodityId]);
    if (Number.isFinite(current)) series.push(current);
  }
  return series;
}

function priceSeriesFromTimeline(trading, commodityId) {
  const series = timelinePriceSeries(trading, commodityId);
  if (series.length >= SPARKLINE_POINTS) {
    return series.slice(-SPARKLINE_POINTS);
  }
  return series;
}

function previousPriceFromTimeline(trading, commodityId) {
  const series = timelinePriceSeries(trading, commodityId);
  if (series.length >= 2) return series[series.length - 2];
  return null;
}

function formatPriceDelta(current, previous, locale = 'zh-CN') {
  if (!Number.isFinite(current) || !Number.isFinite(previous)) {
    return { text: '—', direction: 'flat' };
  }
  const delta = current - previous;
  const arrow = delta > 0 ? '↑' : delta < 0 ? '↓' : '→';
  const sign = delta > 0 ? '+' : delta < 0 ? '-' : '';
  const direction = delta > 0 ? 'up' : delta < 0 ? 'down' : 'flat';
  const absText = fmtPrice(Math.abs(delta), locale);
  if (Math.abs(delta) < 0.0001) {
    return { text: '较上轮持平', direction: 'flat' };
  }
  return {
    text: `较上轮 ${arrow} ${sign}${absText}`,
    direction
  };
}

function renderSparkline(values, { stroke = '#1d4ed8' } = {}) {
  const pts = values.filter(Number.isFinite);
  if (pts.length < 2) {
    return '<svg class="th-spark" viewBox="0 0 88 32" aria-hidden="true"></svg>';
  }
  const w = 88;
  const h = 32;
  const min = Math.min(...pts);
  const max = Math.max(...pts);
  const span = max - min || 1;
  const coords = pts.map((v, i) => {
    const x = (i / (pts.length - 1)) * (w - 8) + 4;
    const y = h - 5 - ((v - min) / span) * (h - 10);
    return `${x.toFixed(1)},${y.toFixed(1)}`;
  });
  const last = pts[pts.length - 1];
  const first = pts[0];
  const trendUp = last >= first;
  const color = trendUp ? '#16a34a' : '#dc2626';
  return `<svg class="th-spark" viewBox="0 0 ${w} ${h}" role="img" aria-hidden="true">
    <polyline fill="none" stroke="${stroke || color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" points="${coords.join(' ')}"/>
  </svg>`;
}

function readJsonStorage(win, key) {
  try {
    const raw = win.localStorage.getItem(key);
    return raw ? JSON.parse(raw) : null;
  } catch (_) {
    return null;
  }
}

function writeJsonStorage(win, key, value) {
  try {
    win.localStorage.setItem(key, JSON.stringify(value));
  } catch (_) {
    /* localStorage can be unavailable in privacy modes */
  }
}

export default class MarketStrategyPanel {
  constructor({
    i18n,
    mountHud = null,
    mountScoreboard = null,
    mountReport = null,
    layoutShell = false,
    document: doc = document,
    window: win = window
  } = {}) {
    this.i18n = i18n;
    this.mountHud = mountHud;
    this.mountScoreboard = mountScoreboard;
    this.mountReport = mountReport;
    this.layoutShell = layoutShell;
    this.document = doc;
    this.window = win;
    this.state = null;
    this.historicalTrading = null; // Trading state from historical snapshot
    this.persistedTrading = readJsonStorage(win, TRADING_SNAPSHOT_KEY);
    console.log(`[MarketStrategyPanel v${HUD_VERSION}] init`);

    if (!this.layoutShell) {
      injectStyles(doc);
    }
    this._build();
    this._bind();
  }

  _build() {
    const doc = this.document;
    this.root = doc.createElement('aside');
    this.root.id = 'trading-hud';
    this.root.dataset.empty = '1';
    this.root.setAttribute('aria-label', this._t('tradingHud.aria'));
    (this.mountHud || doc.body).appendChild(this.root);

    this.scoreRoot = doc.createElement('aside');
    this.scoreRoot.id = 'strategy-scoreboard';
    this.scoreRoot.dataset.empty = '1';
    this.scoreRoot.setAttribute('aria-label', this._t('tradingHud.scoreAria'));
    (this.mountScoreboard || doc.body).appendChild(this.scoreRoot);

    this.reportRoot = doc.createElement('aside');
    this.reportRoot.id = 'prediction-report';
    this.reportRoot.dataset.empty = '1';
    this.reportRoot.dataset.collapsed = '0';
    this.reportRoot.setAttribute('aria-label', this._t('tradingHud.reportAria'));
    (this.mountReport || doc.body).appendChild(this.reportRoot);
  }

  _bind() {
    this._onWorldState = ev => {
      this.state = ev?.detail || null;
      // Clear historical trading state when receiving live updates
      this.historicalTrading = null;
      this._render();
    };
    this.window.addEventListener('world-state', this._onWorldState);
    
    // Listen for historical snapshot events
    this._onHistorySnapshot = ev => {
      const detail = ev?.detail || {};
      if (detail.live) {
        this.historicalTrading = null;
        this._render();
        return;
      }
      const snapshot = detail.snapshot;
      if (snapshot && snapshot.trading) {
        this.historicalTrading = snapshot.trading;
        this._render();
      }
    };
    this.window.addEventListener('show-history-snapshot', this._onHistorySnapshot);

  }

  handleStateUpdate(state) {
    this.state = state || null;
    this._render();
  }

  _t(key, vars) {
    return this.i18n ? this.i18n.t(key, vars) : key;
  }

  _render() {
    // Use historical trading data if available, otherwise use current state
    const liveTrading = this.state?.meta?.trading || null;
    const cachedTrading = this.persistedTrading?.trading || null;
    const trading = this.historicalTrading || liveTrading || cachedTrading;
    const isHistorical = Boolean(this.historicalTrading);
    const isCached = !this.historicalTrading && !liveTrading && Boolean(cachedTrading);
    
    if (!trading) {
      this.root.dataset.empty = '1';
      this.scoreRoot.dataset.empty = '1';
      this.reportRoot.dataset.empty = '1';
      delete this.document.body.dataset.tradingReportOpen;
      return;
    }
    this.root.dataset.empty = '0';
    this.scoreRoot.dataset.empty = '0';
    this.reportRoot.dataset.empty = '0';
    delete this.reportRoot.dataset.collapsed;
    delete this.document.body.dataset.tradingReportOpen;
    if (!isHistorical && liveTrading) {
      this.persistedTrading = {
        savedAt: new Date().toISOString(),
        trading: liveTrading
      };
      writeJsonStorage(this.window, TRADING_SNAPSHOT_KEY, this.persistedTrading);
    }
    const commodities = Array.isArray(trading.commodities) ? trading.commodities : [];
    const prices = trading.prices || {};
    const news = Array.isArray(trading.news) ? trading.news : [];
    const evaluation = trading.evaluation || {};
    const rankings = Array.isArray(evaluation.rankings) ? evaluation.rankings : [];
    const locale = this.i18n?.getLocale?.() || 'zh-CN';

    this.root.innerHTML = `
      <div class="th-head">
        <div class="th-title">
          <strong>${escapeHtml(this._t('app.title'))}${isHistorical ? ' <span style="color:#fbbf24;font-size:10px">(历史)</span>' : ''}</strong>
          <span class="th-date">${escapeHtml(trading.currentDate || '--')}</span>
        </div>
        <div class="th-regime">${escapeHtml(this._t('tradingHud.trainingSlice', {
          regime: trading.regime || this._t('tradingHud.unknown')
        }))}</div>
      </div>
      <div class="th-flow" aria-label="${escapeHtml(this._t('tradingHud.flowAria'))}">
        <div class="th-step"><b>01</b><span>${escapeHtml(this._t('tradingHud.steps.news'))}</span></div>
        <div class="th-step"><b>02</b><span>${escapeHtml(this._t('tradingHud.steps.memory'))}</span></div>
        <div class="th-step"><b>03</b><span>${escapeHtml(this._t('tradingHud.steps.debate'))}</span></div>
        <div class="th-step"><b>04</b><span>${escapeHtml(this._t('tradingHud.steps.trade'))}</span></div>
        <div class="th-step"><b>05</b><span>${escapeHtml(this._t('tradingHud.steps.patch'))}</span></div>
      </div>
      <div class="th-section">
        <div class="th-label">${escapeHtml(this._t('tradingHud.marketBoard'))} ${isHistorical ? `<span style="color:#94a3b8;font-size:9px">（情景日期：${escapeHtml(trading.currentDate || '--')}）</span>` : ''}</div>
        <div class="th-prices">
          ${this._renderMarketPrices({ trading, commodities, prices, locale })}
        </div>
      </div>
      <div class="th-section">
        <div class="th-label">${escapeHtml(this._t('tradingHud.newsMemory'))}</div>
        <div class="th-news">
          ${news.slice(0, 3).map(item => `<div class="th-news-item">${escapeHtml(item)}</div>`).join('')}
        </div>
      </div>
    `;

    this.scoreRoot.innerHTML = `
      <div class="sb-head">
        <div class="sb-title">
          <strong>${escapeHtml(this._t('tradingHud.scoreTitle'))}</strong>
          <span class="sb-source">${escapeHtml(trading.priceSource || evaluation.dataSource || '--')}</span>
        </div>
        <div class="sb-subtitle">${escapeHtml(this._t('tradingHud.scoreSubtitle'))}</div>
      </div>
      <div class="sb-section">
        <div class="sb-label">${escapeHtml(this._t('tradingHud.scoreMethod'))}</div>
        <div class="sb-note">${escapeHtml(evaluation.method || this._t('tradingHud.noScores'))}</div>
      </div>
      <div class="sb-section">
        <div class="sb-windows">
          <div class="sb-window">
            <b>${escapeHtml(this._t('tradingHud.trainingWindow'))}</b>
            <span>${escapeHtml(evaluation.trainingWindow || '--')}</span>
          </div>
          <div class="sb-window">
            <b>${escapeHtml(this._t('tradingHud.testWindow'))}</b>
            <span>${escapeHtml(evaluation.testWindow || '--')}</span>
          </div>
        </div>
      </div>
      <div class="sb-section">
        <div class="sb-label">${escapeHtml(this._t('tradingHud.agentScores'))}</div>
        <div class="sb-ranks">
          ${rankings.length ? rankings.map((item, index) => this._renderScoreCard(item, index, locale)).join('') : `<div class="sb-note">${escapeHtml(this._t('tradingHud.noScores'))}</div>`}
        </div>
      </div>
    `;

    this.reportRoot.innerHTML = this._renderReport({
      trading,
      evaluation,
      locale,
      isCached
    });
  }

  _renderMarketPrices({ trading, commodities, prices, locale }) {
    const list = commodities.length
      ? commodities
      : Object.keys(prices).map(id => ({ id, name: id }));
    return list.map(item => {
      const id = item.id;
      const series = priceSeriesFromTimeline(trading, id);
      const current = Number.isFinite(series[series.length - 1])
        ? series[series.length - 1]
        : Number(prices[id]);
      const previous = previousPriceFromTimeline(trading, id);
      const delta = formatPriceDelta(current, previous, locale);
      const spark = renderSparkline(series);
      return `
            <div class="th-price-row">
              <div class="th-price-main">
                <div class="th-symbol">${escapeHtml(item.name || item.symbol || id)}</div>
                <div class="th-value-line">
                  <span class="th-value">${escapeHtml(fmtPrice(current, locale))}</span>
                  <span class="th-delta th-delta--${delta.direction}">${escapeHtml(delta.text)}</span>
                </div>
              </div>
              <div class="th-spark-wrap" title="近${SPARKLINE_POINTS}轮价格走势">${spark}</div>
            </div>
          `;
    }).join('');
  }

  _renderScoreCard(item, index, locale) {
    const last = item.lastTrade;
    const lastTrade = last
      ? this._t('tradingHud.lastTrade', {
        action: last.actionLabel || last.action,
        symbol: last.symbol,
        score: fmtScore(Number(last.scoreDelta), locale)
      })
      : this._t('tradingHud.noTrade');
    const bestClass = index === 0 ? ' sb-score-card--best' : '';
    return `
      <div class="sb-score-card sb-agent${bestClass}">
        <div class="sb-agent-head">
          <div class="sb-agent-name"><span class="sb-rank">#${index + 1}</span>${escapeHtml(item.role || item.agentId)}</div>
        </div>
        <div class="sb-metrics">
          <div class="sb-metric"><span>${escapeHtml(this._t('tradingHud.score'))}</span><b>${escapeHtml(fmtScore(Number(item.totalScore), locale))}</b></div>
          <div class="sb-metric"><span>${escapeHtml(this._t('tradingHud.trainingScore'))}</span><b>${escapeHtml(fmtScore(Number(item.trainingScore), locale))}</b></div>
          <div class="sb-metric"><span>${escapeHtml(this._t('tradingHud.testScore'))}</span><b>${escapeHtml(fmtScore(Number(item.testScore), locale))}</b></div>
          <div class="sb-metric"><span>${escapeHtml(this._t('tradingHud.hitRate'))}</span><b>${escapeHtml(fmtPrice(Number(item.hitRate), locale))}%</b></div>
        </div>
        <div class="sb-trade">${escapeHtml(lastTrade)} · ${escapeHtml(this._t('tradingHud.drawdown', { value: fmtScore(-Number(item.maxDrawdown || 0), locale) }))}</div>
      </div>
    `;
  }

  _renderReport({ trading, evaluation, locale, isCached }) {
    const analysis = evaluation?.analysis || {};
    const rankings = Array.isArray(evaluation?.rankings) ? evaluation.rankings : [];
    const scoreBars = Array.isArray(analysis.scoreBars) && analysis.scoreBars.length
      ? analysis.scoreBars
      : rankings.map(item => ({
        agentId: item.agentId,
        role: item.role,
        symbol: item.symbol,
        totalScore: Number(item.totalScore || 0),
        trainingScore: Number(item.trainingScore || 0),
        testScore: Number(item.testScore || 0),
        maxDrawdown: Number(item.maxDrawdown || 0),
        hitRate: Number(item.hitRate || 0)
      }));
    const best = rankings[0] || scoreBars[0] || {};
    const maxAbs = Math.max(
      1,
      ...scoreBars.flatMap(item => [
        Math.abs(Number(item.trainingScore || 0)),
        Math.abs(Number(item.testScore || 0))
      ])
    );
    const actions = analysis.actionDistribution || {};
    const actionTotal = Number(actions.BUY || 0) + Number(actions.SELL || 0) + Number(actions.HOLD || 0);
    const conclusions = Array.isArray(analysis.conclusions) && analysis.conclusions.length
      ? analysis.conclusions
      : [
        best.role ? `${best.role}当前排名最高，可作为下一轮策略候选。` : '等待更多回合后生成策略结论。',
        '训练段用于修正 prompt，测试段用于验证策略能否泛化。'
      ];
    const cachedLabel = isCached ? ` · ${this._t('tradingHud.reportCached')}` : '';
    const completedRounds = analysis.completedRoundCount ?? analysis.sampleCount ?? evaluation?.completedTradeCount ?? 0;
    const totalRounds = analysis.totalScenarioRounds ?? '--';
    const totalAgentDecisions = analysis.totalAgentDecisions ?? actionTotal;
    const agentBreakdowns = Array.isArray(analysis.agentBreakdowns) && analysis.agentBreakdowns.length
      ? analysis.agentBreakdowns
      : scoreBars.map(item => ({
        ...item,
        tradeCount: item.tradeCount || 0,
        winCount: 0,
        lossCount: item.lossCount || 0,
        failureRate: 0,
        actionDistribution: {},
        failurePoints: [],
        failureSummary: this._t('tradingHud.noFailures'),
        repairPlan: this._t('tradingHud.defaultRepairPlan')
      }));
    const reportScope = analysis.scope || this._t('tradingHud.reportScope', {
      rounds: completedRounds,
      total: totalRounds,
      decisions: totalAgentDecisions
    });

    return `
      <div class="pr-head">
        <div class="pr-title">
          <strong>${escapeHtml(this._t('tradingHud.reportTitle'))}</strong>
        </div>
        <p class="pr-subtitle">${escapeHtml(this._t('tradingHud.reportSubtitle', {
          date: trading.currentDate || '--',
          rounds: completedRounds,
          total: totalRounds,
          decisions: totalAgentDecisions
        }) + cachedLabel)}</p>
      </div>
      <div class="pr-report-shell">
        <div class="pr-grid">
          <div class="pr-card">
            <div class="pr-card-title">${escapeHtml(this._t('tradingHud.reportKpi'))}</div>
            <div class="pr-kpis">
              <div class="pr-kpi"><span>${escapeHtml(this._t('tradingHud.bestAgent'))}</span><b>${escapeHtml(analysis.bestRole || best.role || '--')}</b></div>
              <div class="pr-kpi"><span>${escapeHtml(this._t('tradingHud.cumulativeRounds'))}</span><b>${escapeHtml(`${completedRounds}/${totalRounds}`)}</b></div>
              <div class="pr-kpi"><span>${escapeHtml(this._t('tradingHud.agentDecisionCount'))}</span><b>${escapeHtml(String(totalAgentDecisions || '--'))}</b></div>
              <div class="pr-kpi"><span>${escapeHtml(this._t('tradingHud.avgHitRate'))}</span><b>${escapeHtml(fmtPrice(Number(analysis.averageHitRate), locale))}%</b></div>
              <div class="pr-kpi"><span>${escapeHtml(this._t('tradingHud.alphaSpread'))}</span><b>${escapeHtml(fmtScore(Number(analysis.alphaSpread), locale))}</b></div>
              <div class="pr-kpi"><span>${escapeHtml(this._t('tradingHud.avgDrawdown'))}</span><b>${escapeHtml(fmtScore(-Number(analysis.averageDrawdown || 0), locale))}</b></div>
            </div>
            <div class="pr-scope">${escapeHtml(reportScope)}</div>
          </div>
          <div class="pr-card">
            <div class="pr-card-title">${escapeHtml(this._t('tradingHud.scoreChart'))}</div>
            <div class="pr-bars">
              ${scoreBars.map(item => this._renderScoreBar(item, maxAbs, locale)).join('')}
            </div>
            <div class="pr-legend">
              <span><i class="pr-dot train"></i>${escapeHtml(this._t('tradingHud.trainingWindow'))}</span>
              <span><i class="pr-dot test"></i>${escapeHtml(this._t('tradingHud.testWindow'))}</span>
            </div>
          </div>
          <div class="pr-card">
            <div class="pr-card-title">${escapeHtml(this._t('tradingHud.equityChart'))}</div>
            ${this._renderEquityCurve(analysis.topEquityCurve || [])}
            <div class="pr-actions">
              <span class="pr-action-label">${escapeHtml(this._t('tradingHud.actionDistribution'))} · BUY ${actions.BUY || 0} / SELL ${actions.SELL || 0} / HOLD ${actions.HOLD || 0}</span>
              <div class="pr-action-track" aria-label="${escapeHtml(this._t('tradingHud.actionDistribution'))}">
                <span class="pr-action buy" style="width:${pct(Number(actions.BUY || 0), actionTotal)}%"></span>
                <span class="pr-action sell" style="width:${pct(Number(actions.SELL || 0), actionTotal)}%"></span>
                <span class="pr-action hold" style="width:${pct(Number(actions.HOLD || 0), actionTotal)}%"></span>
              </div>
            </div>
            <ul class="pr-conclusions">
              ${conclusions.slice(0, 3).map(item => `<li>${escapeHtml(item)}</li>`).join('')}
            </ul>
          </div>
        </div>
        <div class="pr-agent-section">
          <div class="pr-section-head">
            <strong>${escapeHtml(this._t('tradingHud.agentBreakdownTitle'))}</strong>
            <span>${escapeHtml(this._t('tradingHud.agentBreakdownHint', { rounds: completedRounds, decisions: totalAgentDecisions }))}</span>
          </div>
          <div class="pr-agent-grid">
            ${agentBreakdowns.map((item, index) => this._renderAgentBreakdown(item, index, locale)).join('')}
          </div>
        </div>
      </div>
    `;
  }

  _renderAgentBreakdown(item, index, locale) {
    const actions = item.actionDistribution || {};
    const actionTotal = Number(actions.BUY || 0) + Number(actions.SELL || 0) + Number(actions.HOLD || 0);
    const failures = Array.isArray(item.failurePoints) ? item.failurePoints : [];
    const bestTrade = item.bestTrade
      ? `${item.bestTrade.actionLabel || ''} ${item.bestTrade.symbol || ''} / ${fmtScore(Number(item.bestTrade.scoreDelta), locale)}`
      : '--';
    const worstTrade = item.worstTrade
      ? `${item.worstTrade.actionLabel || ''} ${item.worstTrade.symbol || ''} / ${fmtScore(Number(item.worstTrade.scoreDelta), locale)}`
      : '--';

    return `
      <div class="pr-agent-card">
        <div class="pr-agent-head">
          <div>
            <div class="pr-agent-role">
              <span class="pr-agent-rank">#${index + 1}</span>
              <span>${escapeHtml(item.role || item.agentId || '--')}</span>
            </div>
            <div class="pr-agent-meta">${escapeHtml(item.symbol || '--')} · ${escapeHtml(this._t('tradingHud.tradeCount', { count: item.tradeCount || 0 }))}</div>
          </div>
          <div class="pr-agent-score">${escapeHtml(fmtScore(Number(item.totalScore || 0), locale))}</div>
        </div>
        <div class="pr-agent-metrics">
          <div class="pr-agent-metric"><span>${escapeHtml(this._t('tradingHud.trainingScore'))}</span><b>${escapeHtml(fmtScore(Number(item.trainingScore || 0), locale))}</b></div>
          <div class="pr-agent-metric"><span>${escapeHtml(this._t('tradingHud.testScore'))}</span><b>${escapeHtml(fmtScore(Number(item.testScore || 0), locale))}</b></div>
          <div class="pr-agent-metric"><span>${escapeHtml(this._t('tradingHud.winsLosses'))}</span><b>${escapeHtml(`${item.winCount || 0}/${item.lossCount || 0}`)}</b></div>
          <div class="pr-agent-metric"><span>${escapeHtml(this._t('tradingHud.hitRate'))}</span><b>${escapeHtml(fmtPrice(Number(item.hitRate || 0), locale))}%</b></div>
          <div class="pr-agent-metric"><span>${escapeHtml(this._t('tradingHud.avgDrawdown'))}</span><b>${escapeHtml(fmtScore(-Number(item.maxDrawdown || 0), locale))}</b></div>
          <div class="pr-agent-metric"><span>${escapeHtml(this._t('tradingHud.failureRate'))}</span><b>${escapeHtml(fmtPrice(Number(item.failureRate || 0), locale))}%</b></div>
          <div class="pr-agent-metric"><span>${escapeHtml(this._t('tradingHud.bestTrade'))}</span><b>${escapeHtml(bestTrade)}</b></div>
          <div class="pr-agent-metric"><span>${escapeHtml(this._t('tradingHud.worstTrade'))}</span><b>${escapeHtml(worstTrade)}</b></div>
        </div>
        <div class="pr-actions">
          <span class="pr-action-label">${escapeHtml(this._t('tradingHud.actionDistribution'))} · BUY ${actions.BUY || 0} / SELL ${actions.SELL || 0} / HOLD ${actions.HOLD || 0}</span>
          <div class="pr-action-track" aria-label="${escapeHtml(this._t('tradingHud.actionDistribution'))}">
            <span class="pr-action buy" style="width:${pct(Number(actions.BUY || 0), actionTotal)}%"></span>
            <span class="pr-action sell" style="width:${pct(Number(actions.SELL || 0), actionTotal)}%"></span>
            <span class="pr-action hold" style="width:${pct(Number(actions.HOLD || 0), actionTotal)}%"></span>
          </div>
        </div>
        <div class="pr-failure-box">
          <span class="pr-box-title">${escapeHtml(this._t('tradingHud.failurePoints'))}</span>
          <div>${escapeHtml(item.failureSummary || this._t('tradingHud.noFailures'))}</div>
          ${failures.length ? `
            <ul class="pr-failure-list">
              ${failures.map(point => `<li>${escapeHtml(point.reason || `${point.actionLabel || point.action} ${point.symbol || ''} ${fmtScore(Number(point.scoreDelta), locale)}`)}</li>`).join('')}
            </ul>
          ` : ''}
        </div>
        <div class="pr-repair-box">
          <span class="pr-box-title">${escapeHtml(this._t('tradingHud.repairPlan'))}</span>
          <div>${escapeHtml(item.repairPlan || this._t('tradingHud.defaultRepairPlan'))}</div>
        </div>
      </div>
    `;
  }

  _renderScoreBar(item, maxAbs, locale) {
    const train = Number(item.trainingScore || 0);
    const test = Number(item.testScore || 0);
    const trainWidth = Math.max(2, Math.min(50, Math.abs(train) / maxAbs * 50));
    const testWidth = Math.max(2, Math.min(50, Math.abs(test) / maxAbs * 50));
    return `
      <div class="pr-bar-row">
        <div class="pr-bar-name">${escapeHtml(item.role || item.agentId || '--')}</div>
        <div class="pr-bar-track">
          <span class="pr-bar train ${train >= 0 ? 'pos' : 'neg'}" style="width:${trainWidth}%"></span>
          <span class="pr-bar test ${test >= 0 ? 'pos' : 'neg'}" style="width:${testWidth}%"></span>
        </div>
        <div class="pr-bar-score">${escapeHtml(fmtScore(Number(item.totalScore || 0), locale))}</div>
      </div>
    `;
  }

  _renderEquityCurve(points) {
    const series = Array.isArray(points) && points.length ? points : [{ date: '--', value: 0 }];
    const values = series.map(item => Number(item.value || 0));
    const min = Math.min(...values, 0);
    const max = Math.max(...values, 0);
    const span = Math.max(1, max - min);
    const width = 300;
    const height = 118;
    const pad = 14;
    const coords = series.map((item, index) => {
      const x = pad + (series.length === 1 ? 0 : (index / (series.length - 1)) * (width - pad * 2));
      const y = height - pad - ((Number(item.value || 0) - min) / span) * (height - pad * 2);
      return `${x.toFixed(1)},${y.toFixed(1)}`;
    });
    const zeroY = height - pad - ((0 - min) / span) * (height - pad * 2);
    return `
      <svg class="pr-curve" viewBox="0 0 ${width} ${height}" role="img" aria-label="${escapeHtml(this._t('tradingHud.equityChart'))}">
        <line x1="${pad}" y1="${zeroY.toFixed(1)}" x2="${width - pad}" y2="${zeroY.toFixed(1)}" stroke="rgba(226,232,240,0.24)" stroke-width="1" />
        <polyline points="${coords.join(' ')}" fill="none" stroke="#4ade80" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" />
        ${coords.map(point => {
          const [x, y] = point.split(',');
          return `<circle cx="${x}" cy="${y}" r="2.4" fill="#fbbf24" />`;
        }).join('')}
      </svg>
      <span class="pr-axis-note">${escapeHtml(this._t('tradingHud.equityAxis', {
        min: fmtScore(min),
        max: fmtScore(max)
      }))}</span>
    `;
  }

  destroy() {
    this.window.removeEventListener('world-state', this._onWorldState);
    this.window.removeEventListener('show-history-snapshot', this._onHistorySnapshot);
    delete this.document.body.dataset.tradingReportOpen;
    if (this.root?.parentNode) this.root.parentNode.removeChild(this.root);
    if (this.scoreRoot?.parentNode) this.scoreRoot.parentNode.removeChild(this.scoreRoot);
    if (this.reportRoot?.parentNode) this.reportRoot.parentNode.removeChild(this.reportRoot);
  }
}
