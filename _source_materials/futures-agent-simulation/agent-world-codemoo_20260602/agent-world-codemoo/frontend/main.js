const v = `${Date.now()}`;

const runtimeConfig =
  typeof window !== 'undefined' &&
  window.__FUTURES_SIM_RUNTIME__ &&
  typeof window.__FUTURES_SIM_RUNTIME__ === 'object'
    ? window.__FUTURES_SIM_RUNTIME__
    : typeof window !== 'undefined' &&
        window.__AGENT_WORLD_RUNTIME__ &&
        typeof window.__AGENT_WORLD_RUNTIME__ === 'object'
      ? window.__AGENT_WORLD_RUNTIME__
      : {};

Promise.all([
  import(`./i18n/i18n.mjs?v=${v}`),
  import(`./i18n/updateHtmlText.mjs?v=${v}`),
  import(`./bootstrap.mjs?v=${v}`),
  import(`./stateStore.js?v=${v}`),
  import(`./components/AgentDetailPanel.js?v=${v}`),
  import(`./components/AgentRoster.js?v=${v}`),
  import(`./components/AgentPromptPanel.js?v=${v}`),
  import(`./components/EventLog.js?v=${v}`),
  import(`./components/MarketStrategyPanel.js?v=${v}`),
  import(`./components/WorkflowDashboard.js?v=${v}`),
  import(`./components/OverviewPanel.js?v=${v}`),
  import(`./components/AppShell.js?v=${v}`),
  import(`./components/RoundTimeline.js?v=${v}`),
  import(`./connectionConfig.mjs?v=${v}`)
]).then(async ([i18nMod, htmlTextMod, boot, store, agentDetail, roster, agentPrompt, log, marketPanel, workflow, overview, appShell, roundTimeline, cc]) => {
  const i18n = i18nMod.default;
  await i18n.init();
  htmlTextMod.updateHtmlText(i18n);

  boot.bootstrapFrontendApp({
    i18n,
    layoutShell: true,
    AppShellClass: appShell.default,
    OverviewPanelClass: overview.default,
    StateStoreClass: store.default,
    AgentDetailPanelClass: agentDetail.default,
    AgentRosterClass: roster.default,
    AgentPromptPanelClass: agentPrompt.default,
    EventLogClass: log.default,
    RoundTimelineClass: roundTimeline.default,
    MarketStrategyPanelClass: marketPanel.default,
    WorkflowDashboardClass: workflow.default,
    connectionConfigOptions: runtimeConfig,
    connectionConfigFactory: cc.createConnectionConfig
  });
});
