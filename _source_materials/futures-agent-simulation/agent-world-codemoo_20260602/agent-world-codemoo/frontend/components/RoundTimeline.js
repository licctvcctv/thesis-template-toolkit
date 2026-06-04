// Footer round scrubber — matches shell light theme in app-theme.css.

const ROUND_TIMELINE_VERSION = 3;
const MAX_ROUND_SNAPSHOTS = 80;

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

export default class RoundTimeline {
  constructor({ stateStore, mountEl = null, document: doc = document, window: win = window } = {}) {
    this.stateStore = stateStore;
    this.mountEl = mountEl;
    this.document = doc;
    this.window = win;
    this.snapshots = [];
    this.isLive = true;
    this.dragging = false;
    this.currentIndex = -1;
    this._syncingSelect = false;
    console.log(`[RoundTimeline v${ROUND_TIMELINE_VERSION}] init`);

    this._build();
    this._bind();
    this._render();
  }

  _build() {
    const doc = this.document;
    this.root = doc.createElement('div');
    this.root.id = 'round-timeline';
    this.root.dataset.live = '1';
    this.root.dataset.empty = '1';

    const top = doc.createElement('div');
    top.className = 'rt-top';
    top.innerHTML = `
      <div class="rt-title">
        <span class="rt-title-icon" aria-hidden="true">⏱</span>
        <span>仿真轮次</span>
      </div>
    `;
    this.liveBadge = doc.createElement('span');
    this.liveBadge.className = 'rt-live';
    this.liveBadge.textContent = '● 当前轮';
    top.appendChild(this.liveBadge);
    this.root.appendChild(top);

    const bar = doc.createElement('div');
    bar.className = 'rt-bar';

    const picker = doc.createElement('div');
    picker.className = 'rt-picker';
    const pickerLabel = doc.createElement('label');
    pickerLabel.textContent = '跳转轮次';
    pickerLabel.setAttribute('for', 'rt-round-select');
    picker.appendChild(pickerLabel);
    this.roundSelect = doc.createElement('select');
    this.roundSelect.className = 'rt-select';
    this.roundSelect.id = 'rt-round-select';
    this.roundSelect.title = '选择已播放轮次查看历史数据';
    this.roundSelect.innerHTML = '<option value="">等待情景…</option>';
    picker.appendChild(this.roundSelect);
    this.summaryEl = doc.createElement('p');
    this.summaryEl.className = 'rt-summary';
    this.summaryEl.textContent = '仿真启动后将在此显示市场阶段摘要。';
    picker.appendChild(this.summaryEl);
    bar.appendChild(picker);

    this.track = doc.createElement('div');
    this.track.className = 'rt-track';
    this.track.setAttribute('role', 'slider');
    this.track.setAttribute('aria-label', '轮次进度');
    this.rail = doc.createElement('div');
    this.rail.className = 'rt-rail';
    this.fill = doc.createElement('div');
    this.fill.className = 'rt-fill';
    this.thumb = doc.createElement('div');
    this.thumb.className = 'rt-thumb';
    this.thumb.style.left = '100%';
    this.track.appendChild(this.rail);
    this.track.appendChild(this.fill);
    this.track.appendChild(this.thumb);
    bar.appendChild(this.track);

    const actions = doc.createElement('div');
    actions.className = 'rt-actions';
    this.liveBtn = doc.createElement('button');
    this.liveBtn.type = 'button';
    this.liveBtn.className = 'rt-btn rt-btn--primary';
    this.liveBtn.textContent = '回到当前轮';
    actions.appendChild(this.liveBtn);
    bar.appendChild(actions);

    this.root.appendChild(bar);
    (this.mountEl || doc.body).appendChild(this.root);
  }

  _bind() {
    this.thumb.addEventListener('mousedown', ev => this._beginDrag(ev));
    this.track.addEventListener('mousedown', ev => {
      if (ev.target === this.thumb) return;
      this._beginDrag(ev);
    });
    this.liveBtn.addEventListener('click', () => this.goLive());
    this.roundSelect.addEventListener('change', () => {
      if (this._syncingSelect) return;
      const idx = Number(this.roundSelect.value);
      if (!Number.isFinite(idx) || idx < 0) return;
      const pct = this.snapshots.length < 2 ? 0 : idx / (this.snapshots.length - 1);
      this._applyIndex(idx, pct);
      if (idx === this.snapshots.length - 1) this.goLive();
      else this._goHistory();
    });

    this._onWorldState = ev => this._capture(ev?.detail);
    this.window.addEventListener('world-state', this._onWorldState);

    this._onMouseMove = ev => this._onDrag(ev);
    this._onMouseUp = () => this._endDrag();
  }

  _optionLabel(snap) {
    const ym = formatYearMonth(snap.date);
    return `第 ${snap.round + 1} 轮 · ${ym}`;
  }

  _updateSummary(snap, state) {
    if (!this.summaryEl) return;
    const trading = state?.meta?.trading;
    if (trading?.simulationComplete) {
      this.summaryEl.textContent = `全部 ${trading.totalRounds || 36} 轮仿真已完成，运行记录已写入 runs/ 目录。`;
      return;
    }
    if (!snap) {
      this.summaryEl.textContent = '仿真启动后将在此显示市场阶段摘要。';
      return;
    }
    const ym = formatYearMonth(snap.date);
    const regime = String(snap.regime || '').trim() || '—';
    this.summaryEl.textContent = `第 ${snap.round + 1} 轮（${ym}）· ${regime}`;
  }

  _rebuildSelect(state = null) {
    const doc = this.document;
    const prev = this.roundSelect.value;
    this.roundSelect.textContent = '';
    if (!this.snapshots.length) {
      const opt = doc.createElement('option');
      opt.value = '';
      opt.textContent = '等待情景…';
      this.roundSelect.appendChild(opt);
      this._updateSummary(null, state);
      return;
    }
    for (let i = 0; i < this.snapshots.length; i += 1) {
      const snap = this.snapshots[i];
      const opt = doc.createElement('option');
      opt.value = String(i);
      opt.textContent = this._optionLabel(snap);
      opt.title = snap.regime || snap.date || '';
      this.roundSelect.appendChild(opt);
    }
    const restore = prev !== '' && Number(prev) < this.snapshots.length
      ? prev
      : String(Math.max(0, this.currentIndex >= 0 ? this.currentIndex : this.snapshots.length - 1));
    this._syncingSelect = true;
    this.roundSelect.value = restore;
    this._syncingSelect = false;
    const idx = Number(restore);
    if (Number.isFinite(idx) && this.snapshots[idx]) {
      this._updateSummary(this.snapshots[idx], state);
    }
  }

  _capture(state) {
    if (!state?.meta?.trading) return;
    const round = Number(state.meta.trading.currentRound);
    if (!Number.isFinite(round)) return;

    if (state.meta.trading.simulationComplete) {
      this.root.dataset.complete = '1';
      this.root.dataset.live = '0';
      this.isLive = false;
      this.liveBadge.textContent = '✓ 仿真已完成';
      this.liveBtn.disabled = true;
      this.liveBtn.textContent = '已完成 36 轮';
      this._updateSummary(this.snapshots[this.snapshots.length - 1] || null, state);
      return;
    }

    const last = this.snapshots[this.snapshots.length - 1];
    if (last && last.round === round) return;

    this.snapshots.push({
      round,
      date: state.meta.trading.currentDate || '',
      regime: state.meta.trading.regime || '',
      state: JSON.parse(JSON.stringify(state))
    });
    if (this.snapshots.length > MAX_ROUND_SNAPSHOTS) {
      this.snapshots.shift();
      if (this.currentIndex > 0) this.currentIndex -= 1;
    }
    if (this.isLive) {
      this.currentIndex = this.snapshots.length - 1;
    }
    this._rebuildSelect(state);
    this._render();
  }

  _beginDrag(ev) {
    if (this.root.dataset.empty === '1') return;
    this.dragging = true;
    this.window.addEventListener('mousemove', this._onMouseMove);
    this.window.addEventListener('mouseup', this._onMouseUp);
    this._onDrag(ev);
  }

  _onDrag(ev) {
    if (!this.dragging || this.snapshots.length < 2) return;
    const rect = this.track.getBoundingClientRect();
    const px = ev.clientX - rect.left;
    const pct = Math.max(0, Math.min(1, px / rect.width));
    const idx = Math.round(pct * (this.snapshots.length - 1));
    this._applyIndex(idx, pct);
    if (idx === this.snapshots.length - 1) this.goLive();
    else this._goHistory();
  }

  _endDrag() {
    this.dragging = false;
    this.window.removeEventListener('mousemove', this._onMouseMove);
    this.window.removeEventListener('mouseup', this._onMouseUp);
  }

  _applyIndex(idx, pct) {
    const snap = this.snapshots[idx];
    if (!snap) return;
    this.currentIndex = idx;
    this.thumb.style.left = `${pct * 100}%`;
    this.fill.style.width = `${pct * 100}%`;
    this._syncingSelect = true;
    this.roundSelect.value = String(idx);
    this._syncingSelect = false;
    this._updateSummary(snap, snap?.state || null);

    if (this.stateStore?.setWorldState) {
      this.stateStore.setWorldState(snap.state);
    }
    try {
      this.window.dispatchEvent(new CustomEvent('world-state', { detail: snap.state }));
    } catch (_) { /* ignore */ }
    try {
      this.window.dispatchEvent(new CustomEvent('show-history-snapshot', {
        bubbles: true,
        detail: {
          snapshot: { trading: snap.state?.meta?.trading || null },
          round: snap.round
        }
      }));
    } catch (_) { /* ignore */ }
  }

  _goHistory() {
    this.isLive = false;
    this.root.dataset.live = '0';
    this.liveBadge.textContent = '⏸ 历史回放';
  }

  goLive() {
    if (!this.snapshots.length) return;
    this.isLive = true;
    this.root.dataset.live = '1';
    this.liveBadge.textContent = '● 当前轮';
    this.currentIndex = this.snapshots.length - 1;
    this._applyIndex(this.currentIndex, 1);
    const snap = this.snapshots[this.currentIndex];
    try {
      this.window.dispatchEvent(new CustomEvent('show-history-snapshot', {
        bubbles: true,
        detail: { snapshot: null, round: snap.round, live: true }
      }));
    } catch (_) { /* ignore */ }
  }

  _render() {
    const n = this.snapshots.length;
    this.root.dataset.empty = n < 2 ? '1' : '0';
    if (!n) {
      this._rebuildSelect();
      return;
    }
    if (this.isLive) {
      this.thumb.style.left = '100%';
      this.fill.style.width = '100%';
      this.currentIndex = n - 1;
    }
    const idx = Math.max(0, this.currentIndex >= 0 ? this.currentIndex : n - 1);
    this._syncingSelect = true;
    this.roundSelect.value = String(idx);
    this._syncingSelect = false;
    this._updateSummary(this.snapshots[idx], this.snapshots[idx]?.state || null);
  }

  destroy() {
    this.window.removeEventListener('world-state', this._onWorldState);
    this.window.removeEventListener('mousemove', this._onMouseMove);
    this.window.removeEventListener('mouseup', this._onMouseUp);
    if (this.root?.parentNode) this.root.parentNode.removeChild(this.root);
  }
}
