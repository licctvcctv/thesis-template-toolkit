// i18n core module - lightweight internationalization system
// Supports nested keys, variable interpolation, and localStorage persistence

const I18N_VERSION = 1;
const STORAGE_KEY = 'futures-agent-simulation-locale';
const DEFAULT_LOCALE = 'zh-CN';
const SUPPORTED_LOCALES = ['en', 'zh-CN'];

class I18n {
  constructor() {
    this.locale = this._loadLocale();
    this.translations = {};
    this.fallbackTranslations = {};
    this._listeners = new Set();
    console.log(`[I18n v${I18N_VERSION}] init with locale: ${this.locale}`);
  }

  _loadLocale() {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored && SUPPORTED_LOCALES.includes(stored)) return stored;
    } catch (e) {
      console.warn('[I18n] localStorage not available');
    }
    
    // Auto-detect from browser
    const browserLang = navigator.language || navigator.userLanguage || DEFAULT_LOCALE;
    if (browserLang.startsWith('zh')) return 'zh-CN';
    return DEFAULT_LOCALE;
  }

  _saveLocale(locale) {
    try {
      localStorage.setItem(STORAGE_KEY, locale);
    } catch (e) {
      console.warn('[I18n] failed to save locale');
    }
  }

  async loadTranslations(locale) {
    try {
      const response = await fetch(`/i18n/locales/${locale}.json?v=${Date.now()}`);
      if (!response.ok) throw new Error(`Failed to load ${locale}`);
      const data = await response.json();
      
      if (locale === DEFAULT_LOCALE) {
        this.fallbackTranslations = data;
      }
      if (locale === this.locale) {
        this.translations = data;
      }
      
      return data;
    } catch (err) {
      console.error(`[I18n] failed to load ${locale}:`, err.message);
      return {};
    }
  }

  async init() {
    // Load default locale as fallback
    if (this.locale !== DEFAULT_LOCALE) {
      await this.loadTranslations(DEFAULT_LOCALE);
    }
    // Load current locale
    await this.loadTranslations(this.locale);
    this._notifyListeners();
  }

  async setLocale(locale) {
    if (!SUPPORTED_LOCALES.includes(locale)) {
      console.warn(`[I18n] unsupported locale: ${locale}`);
      return;
    }
    
    this.locale = locale;
    this._saveLocale(locale);
    await this.loadTranslations(locale);
    this._notifyListeners();
  }

  getLocale() {
    return this.locale;
  }

  getSupportedLocales() {
    return [...SUPPORTED_LOCALES];
  }

  // Get translation by key path (e.g., "help.title")
  t(key, vars = {}) {
    const value = this._getValue(key, this.translations) 
                  || this._getValue(key, this.fallbackTranslations);
    
    if (value == null) {
      console.warn(`[I18n] missing translation: ${key}`);
      return key;
    }

    return this._interpolate(value, vars);
  }

  _getValue(key, obj) {
    const keys = key.split('.');
    let current = obj;
    
    for (const k of keys) {
      if (current == null || typeof current !== 'object') return null;
      current = current[k];
    }
    
    return current;
  }

  _interpolate(str, vars) {
    if (typeof str !== 'string') return str;
    
    return str.replace(/\{(\w+)\}/g, (match, key) => {
      return vars[key] != null ? vars[key] : match;
    });
  }

  // Subscribe to locale changes
  onChange(callback) {
    this._listeners.add(callback);
    return () => this._listeners.delete(callback);
  }

  _notifyListeners() {
    this._listeners.forEach(cb => {
      try {
        cb(this.locale);
      } catch (e) {
        console.error('[I18n] listener error:', e);
      }
    });
  }
}

// Singleton instance
const i18n = new I18n();

export default i18n;
export { I18N_VERSION, SUPPORTED_LOCALES };
