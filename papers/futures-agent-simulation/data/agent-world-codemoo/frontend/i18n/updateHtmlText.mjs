// Helper to update HTML text content based on i18n
// Called after i18n is initialized

export function updateHtmlText(i18n, document = window.document) {
  if (!i18n || !document) return;
  
  const t = (key) => i18n.t(key);
  document.title = t('app.title');
  
  // Update page title
  const titleEl = document.getElementById('page-title');
  if (titleEl) {
    titleEl.textContent = t('app.title');
  }
  
  // Update demo title
  const demoTitle = document.querySelector('#demo-title strong');
  if (demoTitle) {
    demoTitle.textContent = t('app.title');
  }
  
  const demoSubtitle = document.querySelector('#demo-title span');
  if (demoSubtitle) {
    demoSubtitle.textContent = t('app.subtitle');
  }
  
  // Update assets link
  const assetsLink = document.getElementById('assets-link');
  if (assetsLink) {
    assetsLink.textContent = t('app.worldEditor');
  }
  
  // Update connection status
  const connStatus = document.getElementById('connection-status');
  if (connStatus) {
    const state = connStatus.dataset.state || 'connecting';
    if (state === 'connecting') {
      connStatus.textContent = t('app.connecting');
    } else if (state === 'live') {
      connStatus.textContent = t('connection.live');
    } else if (state === 'reconnecting') {
      connStatus.textContent = t('connection.reconnecting');
    } else if (state === 'error') {
      connStatus.textContent = t('connection.error');
    }
  }
}
