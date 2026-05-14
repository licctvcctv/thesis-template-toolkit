// "?" button + shortcut legend. Single overlay listing every keyboard
// affordance in plain DOM. Both "?" and "Shift+/" trigger it so Korean
// two-bul keyboards work too. Now uses i18n for translations.

const HELP_VERSION = 2;

function injectStyles(doc) {
  if (doc.getElementById('help-overlay-styles')) return;
  const style = doc.createElement('style');
  style.id = 'help-overlay-styles';
  style.textContent = `
    #help-button {
      position: fixed; top: 12px; right: 294px;
      width: 30px; height: 30px;
      background: rgba(15, 23, 42, 0.88);
      color: #fbbf24;
      border: 1px solid rgba(148, 163, 184, 0.35);
      border-radius: 50%;
      font: 700 15px/1 Menlo, monospace;
      cursor: pointer; z-index: 11;
      display: flex; align-items: center; justify-content: center;
      transition: background 0.12s ease, transform 0.12s ease;
      padding: 0;
    }
    #help-button:hover { background: rgba(56, 189, 248, 0.18); transform: scale(1.07); }
    #help-overlay {
      position: fixed; inset: 0; z-index: 25;
      background: rgba(2, 6, 23, 0.75);
      backdrop-filter: blur(4px);
      display: none;
      align-items: center; justify-content: center;
      padding: 18px;
    }
    #help-overlay[data-open="1"] { display: flex; }
    #help-overlay .help-card {
      max-width: 640px; width: 100%;
      max-height: calc(100vh - 48px); overflow: auto;
      background: #0f172a; color: #e2e8f0;
      border: 1px solid rgba(251, 191, 36, 0.35);
      border-radius: 12px;
      padding: 22px 26px;
      font: 12px/1.55 Menlo, Monaco, monospace;
      box-shadow: 0 24px 60px rgba(0,0,0,0.6);
    }
    #help-overlay h2 {
      margin: 0 0 4px; font-size: 16px; color: #fbbf24;
      letter-spacing: 0.02em;
    }
    #help-overlay .help-sub {
      color: #94a3b8; font-size: 11px; margin-bottom: 16px;
    }
    #help-overlay h3 {
      font-size: 12px; color: #38bdf8;
      margin: 18px 0 6px; text-transform: uppercase; letter-spacing: 0.06em;
    }
    #help-overlay dl {
      display: grid;
      grid-template-columns: max-content 1fr;
      gap: 4px 14px;
      margin: 0;
    }
    #help-overlay dt {
      color: #fbbf24;
      font-weight: 600;
      white-space: nowrap;
      padding: 2px 6px;
      background: rgba(251, 191, 36, 0.08);
      border-radius: 4px;
      align-self: start;
    }
    #help-overlay dd {
      margin: 0;
      color: #cbd5e1;
      align-self: center;
    }
    #help-overlay .help-close {
      position: sticky; top: -22px;
      float: right;
      background: none; border: none; color: #94a3b8;
      font: 14px/1 Menlo, monospace; cursor: pointer;
      padding: 0 4px;
    }
    #help-overlay .help-footer {
      margin-top: 18px; padding-top: 10px;
      border-top: 1px solid rgba(148, 163, 184, 0.18);
      color: #64748b; font-size: 10px;
      display: flex; justify-content: space-between; gap: 12px; flex-wrap: wrap;
    }
  `;
  doc.head.appendChild(style);
}

export default class HelpOverlay {
  constructor({ i18n, document: doc = document, window: win = window } = {}) {
    this.i18n = i18n;
    this.document = doc;
    this.window = win;
    this.isOpen = false;
    console.log(`[HelpOverlay v${HELP_VERSION}] init`);

    injectStyles(doc);
    this._build();
    this._bind();
    
    // Re-render when locale changes
    if (this.i18n) {
      this._unsubscribe = this.i18n.onChange(() => this._rebuild());
    }
  }

  _build() {
    const doc = this.document;
    const t = (key, vars) => this.i18n ? this.i18n.t(key, vars) : key;
    
    this.button = doc.createElement('button');
    this.button.id = 'help-button';
    this.button.textContent = '?';
    this.button.setAttribute('aria-label', t('help.shortcuts.showHelp'));
    this.button.setAttribute('title', t('help.shortcuts.showHelp') + ' (?)');
    doc.body.appendChild(this.button);

    this.overlay = doc.createElement('div');
    this.overlay.id = 'help-overlay';
    this.overlay.setAttribute('role', 'dialog');
    this.overlay.setAttribute('aria-modal', 'true');
    this.overlay.setAttribute('aria-labelledby', 'help-title');

    const card = doc.createElement('div');
    card.className = 'help-card';

    const close = doc.createElement('button');
    close.className = 'help-close';
    close.textContent = '✕';
    close.setAttribute('aria-label', t('session.actions.close'));
    card.appendChild(close);
    close.addEventListener('click', () => this.close());

    const h2 = doc.createElement('h2');
    h2.id = 'help-title';
    h2.textContent = t('help.title');
    card.appendChild(h2);

    const sub = doc.createElement('div');
    sub.className = 'help-sub';
    sub.textContent = t('help.subtitle');
    card.appendChild(sub);

    // Define sections with translation keys
    const sections = [
      {
        titleKey: 'help.sections.global',
        rows: [
          ['?', 'help.shortcuts.showHelp'],
          ['1–9', 'help.shortcuts.focusAgent'],
          ['0', 'help.shortcuts.closePanel'],
          ['Esc', 'help.shortcuts.closePanels'],
          ['N', 'help.shortcuts.toggleNames'],
          ['M', 'help.shortcuts.toggleMinimal'],
          ['E', 'help.shortcuts.toggleEditor'],
          ['← →', 'help.shortcuts.scrubTimeline'],
          ['Space', 'help.shortcuts.playPause']
        ]
      },
      {
        titleKey: 'help.sections.agentPanel',
        rows: [
          ['click sprite', 'help.shortcuts.clickSprite'],
          ['T', 'help.shortcuts.openTranscript'],
          ['L', 'help.shortcuts.switchLive'],
          ['聚焦终端', 'help.shortcuts.focusTerminal']
        ]
      },
      {
        titleKey: 'help.sections.editor',
        rows: [
          ['Ctrl+Z / Cmd+Z', 'help.shortcuts.undo'],
          ['Ctrl+Shift+Z / Cmd+Y', 'help.shortcuts.redo'],
          ['Ctrl+S / Cmd+S', 'help.shortcuts.save'],
          ['Delete / Backspace', 'help.shortcuts.remove'],
          ['← ↑ → ↓', 'help.shortcuts.nudge'],
          ['F / Shift+F', 'help.shortcuts.flip']
        ]
      }
    ];

    for (const sec of sections) {
      const h3 = doc.createElement('h3');
      h3.textContent = t(sec.titleKey);
      card.appendChild(h3);
      const dl = doc.createElement('dl');
      for (const [key, descKey] of sec.rows) {
        const dt = doc.createElement('dt'); 
        dt.textContent = key;
        const dd = doc.createElement('dd'); 
        dd.textContent = t(descKey);
        dl.appendChild(dt); 
        dl.appendChild(dd);
      }
      card.appendChild(dl);
    }

    const footer = doc.createElement('div');
    footer.className = 'help-footer';
    footer.innerHTML = `<span>${t('help.footer')}</span><span>${t('help.closeHint')}</span>`;
    card.appendChild(footer);

    this.overlay.appendChild(card);
    doc.body.appendChild(this.overlay);
  }

  _rebuild() {
    // Remove old overlay and button
    if (this.overlay && this.overlay.parentNode) {
      this.overlay.parentNode.removeChild(this.overlay);
    }
    if (this.button && this.button.parentNode) {
      this.button.parentNode.removeChild(this.button);
    }
    // Rebuild with new translations
    this._build();
  }

  _bind() {
    this.button.addEventListener('click', () => this.toggle());
    this.overlay.addEventListener('click', (ev) => {
      if (ev.target === this.overlay) this.close();
    });
    // Both "?" and Shift+/ map to the same KeyboardEvent on all layouts,
    // but bind both just in case. Ignore when typing in a text field.
    this._onKey = (ev) => {
      const tag = ev.target?.tagName || '';
      if (/^(INPUT|TEXTAREA|SELECT)$/.test(tag)) return;
      if (ev.metaKey || ev.ctrlKey || ev.altKey) return;
      if (ev.key === '?' || (ev.shiftKey && ev.key === '/')) {
        ev.preventDefault();
        this.toggle();
      } else if (this.isOpen && ev.key === 'Escape') {
        this.close();
      }
    };
    this.window.addEventListener('keydown', this._onKey);
  }

  open() {
    this.isOpen = true;
    this.overlay.dataset.open = '1';
  }

  close() {
    this.isOpen = false;
    this.overlay.dataset.open = '0';
  }

  toggle() {
    if (this.isOpen) this.close();
    else this.open();
  }

  destroy() {
    if (this._unsubscribe) this._unsubscribe();
    this.window.removeEventListener('keydown', this._onKey);
    if (this.button.parentNode) this.button.parentNode.removeChild(this.button);
    if (this.overlay.parentNode) this.overlay.parentNode.removeChild(this.overlay);
  }
}
