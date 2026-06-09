const SHELL_VERSION = 2;

const PAGES = [
  { id: 'overview', label: '总览', icon: '◉', centered: true },
  { id: 'agents', label: '智能体', icon: '◎', split: true, hideIntro: false },
  { id: 'market', label: '市场行情', icon: '◇', centered: true, wide: true },
  { id: 'stations', label: '工作站', icon: '▣', centered: true, wide: true },
  { id: 'strategy', label: '策略评估', icon: '△', centered: true, wide: true },
  { id: 'journal', label: '运行日志', icon: '≡', split: true, hideIntro: true }
];

const PAGE_INTROS = {
  overview: '当前仿真轮次、市场阶段与决策流程概览。',
  agents: '四个交易智能体的状态、决策详情与 Prompt 迭代对比。',
  market: '训练切片下的行情、资讯与决策流水线。',
  stations: '六个功能工作站的数据展示面板。',
  strategy: '多智能体策略得分与预测统计报告。'
};

export default class AppShell {
  constructor({ document: doc = document, window: win = window } = {}) {
    this.document = doc;
    this.window = win;
    this.activePage = 'overview';
    this.mounts = {};
    console.log(`[AppShell v${SHELL_VERSION}] init`);
    this._build();
    this._bind();
  }

  _build() {
    const doc = this.document;
    doc.body.dataset.layout = 'shell';

    const link = doc.createElement('link');
    link.rel = 'stylesheet';
    link.href = `/styles/app-theme.css?v=${Date.now()}`;
    doc.head.appendChild(link);

    const shell = doc.getElementById('app-shell');
    if (!shell) throw new Error('#app-shell required');

    shell.innerHTML = '';

    const sidebar = doc.createElement('aside');
    sidebar.id = 'app-sidebar';
    sidebar.innerHTML = `
      <div class="app-brand">
        <strong>期货智能体模拟系统</strong>
        <span>记忆 · 决策 · 策略演化</span>
      </div>
      <nav id="app-nav" aria-label="功能导航"></nav>
    `;
    shell.appendChild(sidebar);

    const nav = sidebar.querySelector('#app-nav');
    this.navButtons = new Map();
    for (const page of PAGES) {
      const btn = doc.createElement('button');
      btn.type = 'button';
      btn.className = 'app-nav-btn';
      btn.dataset.page = page.id;
      btn.innerHTML = `<span aria-hidden="true">${page.icon}</span><span class="nav-label">${page.label}</span>`;
      if (page.id === this.activePage) btn.dataset.active = '1';
      nav.appendChild(btn);
      this.navButtons.set(page.id, btn);
    }

    const main = doc.createElement('div');
    main.id = 'app-main';

    const header = doc.createElement('header');
    header.id = 'app-header';
    this.headerTitle = doc.createElement('h1');
    this.headerTitle.textContent = PAGES[0].label;
    header.appendChild(this.headerTitle);
    const statusSlot = doc.createElement('div');
    statusSlot.id = 'app-header-status';
    header.appendChild(statusSlot);
    main.appendChild(header);

    const pagesWrap = doc.createElement('div');
    pagesWrap.id = 'app-pages';

    for (const page of PAGES) {
      const section = doc.createElement('section');
      section.className = 'app-page';
      section.dataset.page = page.id;
      section.dataset.active = page.id === this.activePage ? '1' : '0';
      section.setAttribute('role', 'tabpanel');

      if (!page.hideIntro && PAGE_INTROS[page.id]) {
        const intro = doc.createElement('p');
        intro.className = 'page-intro';
        intro.textContent = PAGE_INTROS[page.id];
        section.appendChild(intro);
      }

      const body = doc.createElement('div');
      body.className = 'page-body';
      if (page.wide) body.classList.add('page-body--wide');
      if (page.centered) body.classList.add('page-body--centered');

      if (page.split) {
        const split = doc.createElement('div');
        split.className = 'page-split';

        const mainCol = doc.createElement('div');
        mainCol.className = 'page-split-main';
        mainCol.id = `mount-${page.id}`;

        const aside = doc.createElement('aside');
        aside.className = 'page-split-aside';
        aside.id = `mount-${page.id}-detail`;
        aside.setAttribute('aria-label', page.id === 'agents' ? '智能体详情' : '事件详情');

        split.appendChild(mainCol);
        split.appendChild(aside);
        body.appendChild(split);

        this.mounts[page.id] = mainCol;
        this.mounts[`${page.id}-detail`] = aside;
      } else if (page.id === 'strategy') {
        body.classList.add('page-stack');
        body.id = `mount-${page.id}`;
        this.mounts[page.id] = body;
      } else {
        body.id = `mount-${page.id}`;
        this.mounts[page.id] = body;
      }

      section.appendChild(body);
      pagesWrap.appendChild(section);
    }

    main.appendChild(pagesWrap);

    const footer = doc.createElement('footer');
    footer.id = 'app-footer';
    this.mounts.footer = footer;
    main.appendChild(footer);

    shell.appendChild(main);

    const statusEl = doc.getElementById('connection-status');
    if (statusEl && statusSlot) {
      statusSlot.appendChild(statusEl);
    }
  }

  _bind() {
    for (const [pageId, btn] of this.navButtons) {
      btn.addEventListener('click', () => this.setPage(pageId));
    }
  }

  setPage(pageId) {
    if (!this.mounts[pageId] && !PAGES.some(p => p.id === pageId)) return;
    this.activePage = pageId;
    const label = PAGES.find(p => p.id === pageId)?.label || pageId;
    if (this.headerTitle) this.headerTitle.textContent = label;

    for (const [id, btn] of this.navButtons) {
      btn.dataset.active = id === pageId ? '1' : '0';
    }
    this.document.querySelectorAll('.app-page').forEach(el => {
      el.dataset.active = el.dataset.page === pageId ? '1' : '0';
    });

    try {
      this.window.dispatchEvent(new CustomEvent('app-page-change', {
        detail: { page: pageId }
      }));
    } catch (_) { /* ignore */ }
  }

  getMount(name) {
    return this.mounts[name] || null;
  }

  destroy() {
    delete this.document.body.dataset.layout;
  }
}
