// Language switcher component - compact dropdown for locale selection
// Positioned in top-right area, persists selection to localStorage

const SWITCHER_VERSION = 1;

const LOCALE_NAMES = {
  'en': 'English',
  'zh-CN': '简体中文'
};

function injectStyles(doc) {
  if (doc.getElementById('language-switcher-styles')) return;
  const style = doc.createElement('style');
  style.id = 'language-switcher-styles';
  style.textContent = `
    #language-switcher {
      position: fixed;
      top: 12px;
      right: 330px;
      z-index: 11;
      display: flex;
      align-items: center;
      gap: 6px;
      padding: 6px 10px;
      border-radius: 6px;
      background: rgba(15, 23, 42, 0.88);
      border: 1px solid rgba(148, 163, 184, 0.35);
      font: 11px/1 Menlo, Monaco, monospace;
      color: #e2e8f0;
      transition: background 0.12s ease;
    }
    #language-switcher:hover {
      background: rgba(30, 58, 74, 0.9);
    }
    #language-switcher .lang-icon {
      font-size: 14px;
    }
    #language-switcher select {
      background: transparent;
      border: none;
      color: #bae6fd;
      font: inherit;
      cursor: pointer;
      outline: none;
      padding: 0;
      appearance: none;
      -webkit-appearance: none;
      -moz-appearance: none;
    }
    #language-switcher select::-ms-expand {
      display: none;
    }
    #language-switcher select option {
      background: #0f172a;
      color: #e2e8f0;
    }
    @media (max-width: 1024px) {
      #language-switcher {
        right: 264px;
        padding: 4px 8px;
        font-size: 10px;
      }
    }
    @media (max-width: 600px) {
      #language-switcher {
        display: none;
      }
    }
  `;
  doc.head.appendChild(style);
}

export default class LanguageSwitcher {
  constructor({ i18n, document: doc = document, window: win = window } = {}) {
    this.i18n = i18n;
    this.document = doc;
    this.window = win;
    console.log(`[LanguageSwitcher v${SWITCHER_VERSION}] init`);

    injectStyles(doc);
    this._build();
    this._bind();
  }

  _build() {
    const doc = this.document;
    this.root = doc.createElement('div');
    this.root.id = 'language-switcher';
    this.root.setAttribute('aria-label', this.i18n ? this.i18n.t('language.selector') : '语言选择');

    const icon = doc.createElement('span');
    icon.className = 'lang-icon';
    icon.textContent = '🌐';
    this.root.appendChild(icon);

    this.select = doc.createElement('select');
    this.select.setAttribute('aria-label', this.i18n ? this.i18n.t('language.select') : '选择语言');
    
    const locales = this.i18n.getSupportedLocales();
    const currentLocale = this.i18n.getLocale();
    
    for (const locale of locales) {
      const option = doc.createElement('option');
      option.value = locale;
      option.textContent = LOCALE_NAMES[locale] || locale;
      if (locale === currentLocale) {
        option.selected = true;
      }
      this.select.appendChild(option);
    }

    this.root.appendChild(this.select);
    doc.body.appendChild(this.root);
  }

  _bind() {
    this.select.addEventListener('change', async (e) => {
      const newLocale = e.target.value;
      if (newLocale !== this.i18n.getLocale()) {
        await this.i18n.setLocale(newLocale);
        // Reload page to apply translations everywhere
        this.window.location.reload();
      }
    });

    // Update select when locale changes externally
    this._unsubscribe = this.i18n.onChange((locale) => {
      this.select.value = locale;
    });
  }

  destroy() {
    if (this._unsubscribe) this._unsubscribe();
    if (this.root && this.root.parentNode) {
      this.root.parentNode.removeChild(this.root);
    }
  }
}
