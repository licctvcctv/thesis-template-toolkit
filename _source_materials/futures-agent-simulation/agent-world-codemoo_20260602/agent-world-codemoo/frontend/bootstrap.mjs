import { createConnectionConfig } from './connectionConfig.mjs';

export function createFrontendApp({
  i18n,
  windowLike,
  documentLike,
  locationLike,
  fetchImpl,
  WebSocketImpl,
  StateStoreClass,
  AgentDetailPanelClass = null,
  AgentRosterClass = null,
  AgentPromptPanelClass = null,
  EventLogClass = null,
  MarketStrategyPanelClass = null,
  WorkflowDashboardClass = null,
  OverviewPanelClass = null,
  AppShellClass = null,
  RoundTimelineClass = null,
  layoutShell = false,
  connectionConfigOptions = {},
  connectionConfigFactory = createConnectionConfig
} = {}) {
  const resolvedWindow =
    windowLike || (typeof window !== 'undefined' ? window : null);
  const resolvedDocument =
    documentLike || (typeof document !== 'undefined' ? document : null);
  const resolvedLocation = locationLike || resolvedWindow?.location;
  const resolvedFetch =
    fetchImpl || (typeof fetch === 'function' ? fetch : null);
  const ResolvedWebSocket =
    WebSocketImpl || (typeof WebSocket !== 'undefined' ? WebSocket : null);

  if (!resolvedWindow || !resolvedDocument || !resolvedLocation) {
    throw new Error('Browser globals are required to bootstrap frontend app.');
  }

  if (!resolvedFetch || !ResolvedWebSocket) {
    throw new Error('fetch/WebSocket runtime is required to bootstrap frontend app.');
  }
  if (!StateStoreClass) {
    throw new Error('StateStore runtime class is required to bootstrap frontend app.');
  }

  const { authToken, apiBaseUrl, wsBaseUrl, wsUrl } =
    connectionConfigFactory(resolvedLocation, connectionConfigOptions);
  const resolvedWsBaseUrl = wsBaseUrl || wsUrl;

  const statusBadge = resolvedDocument.getElementById('connection-status');

  let appShell = null;
  if (layoutShell && AppShellClass && resolvedDocument.body) {
    appShell = new AppShellClass({
      document: resolvedDocument,
      window: resolvedWindow
    });
  }

  const stateStore = new StateStoreClass();

  let agentDetailPanel = null;
  if (AgentDetailPanelClass && resolvedDocument.body) {
    agentDetailPanel = new AgentDetailPanelClass({
      stateStore,
      apiBaseUrl,
      authToken,
      fetchImpl: resolvedFetch,
      i18n,
      mountAgents: appShell?.getMount('agents-detail') || null,
      mountJournal: appShell?.getMount('journal-detail') || null,
      appShell,
      embedded: Boolean(appShell)
    });
  }

  let agentHubWrap = null;
  const agentsMount = appShell?.getMount('agents');
  if (agentsMount && AgentPromptPanelClass) {
    agentHubWrap = resolvedDocument.createElement('div');
    agentHubWrap.id = 'agent-hub';
    agentHubWrap.className = 'agent-hub';
    agentsMount.appendChild(agentHubWrap);
  }

  let agentRoster = null;
  if (AgentRosterClass && resolvedDocument.body) {
    agentRoster = new AgentRosterClass({
      stateStore,
      i18n,
      mountEl: agentHubWrap || agentsMount || null,
      document: resolvedDocument,
      window: resolvedWindow
    });
  }

  let agentPromptPanel = null;
  if (AgentPromptPanelClass && resolvedDocument.body) {
    agentPromptPanel = new AgentPromptPanelClass({
      stateStore,
      i18n,
      mountEl: agentHubWrap || agentsMount || null,
      document: resolvedDocument,
      window: resolvedWindow
    });
  }

  let eventLog = null;
  if (EventLogClass && resolvedDocument.body) {
    eventLog = new EventLogClass({
      stateStore,
      i18n,
      mountEl: appShell?.getMount('journal'),
      document: resolvedDocument,
      window: resolvedWindow
    });
  }

  let roundTimeline = null;
  if (RoundTimelineClass && resolvedDocument.body) {
    roundTimeline = new RoundTimelineClass({
      stateStore,
      mountEl: appShell?.getMount('footer'),
      document: resolvedDocument,
      window: resolvedWindow
    });
  }

  let workflowDashboard = null;
  if (WorkflowDashboardClass && resolvedDocument.body) {
    workflowDashboard = new WorkflowDashboardClass({
      mountEl: appShell?.getMount('stations'),
      document: resolvedDocument,
      window: resolvedWindow
    });
  }

  let overviewPanel = null;
  if (OverviewPanelClass && resolvedDocument.body) {
    overviewPanel = new OverviewPanelClass({
      mountEl: appShell?.getMount('overview'),
      document: resolvedDocument,
      window: resolvedWindow
    });
  }

  let marketStrategyPanel = null;
  if (MarketStrategyPanelClass && resolvedDocument.body) {
    marketStrategyPanel = new MarketStrategyPanelClass({
      i18n,
      mountHud: appShell?.getMount('market'),
      mountScoreboard: appShell?.getMount('strategy'),
      mountReport: appShell?.getMount('strategy'),
      layoutShell: Boolean(appShell),
      document: resolvedDocument,
      window: resolvedWindow
    });
  }

  let socket = null;
  let reconnectTimer = null;
  let isDestroyed = false;
  let isConnecting = false;
  const wsConnectingState =
    typeof ResolvedWebSocket.CONNECTING === 'number'
      ? ResolvedWebSocket.CONNECTING
      : 0;

  function setConnectionStatus(label, modifier = '') {
    if (!statusBadge) {
      return;
    }

    const t = (key) => i18n ? i18n.t(key) : key;
    statusBadge.textContent =
      modifier === 'live' ? t('connection.live') :
      modifier === 'reconnecting' ? t('connection.reconnecting') :
      modifier === 'error' ? t('connection.error') :
      modifier === 'connecting' ? t('app.connecting') :
      label;
    statusBadge.dataset.state = modifier;
  }

  function notifyState(state) {
    if (agentDetailPanel?.handleStateUpdate) {
      agentDetailPanel.handleStateUpdate(state);
    }
    if (marketStrategyPanel?.handleStateUpdate) {
      marketStrategyPanel.handleStateUpdate(state);
    }
    if (workflowDashboard?.handleStateUpdate) {
      workflowDashboard.handleStateUpdate(state);
    }
    if (overviewPanel?.handleStateUpdate) {
      overviewPanel.handleStateUpdate(state);
    }
    try {
      resolvedWindow.dispatchEvent(new CustomEvent('world-state', { detail: state || null }));
    } catch (_) { /* ignore */ }
  }

  function applyMessage(rawMessage) {
    if (!rawMessage) return;
    try {
      resolvedWindow.dispatchEvent(new CustomEvent('ws-message', { detail: rawMessage }));
    } catch (_) { /* ignore */ }

    if (rawMessage.type === 'state') {
      stateStore.setWorldState(rawMessage.data || null);
      notifyState(rawMessage.data || null);
    } else if (rawMessage.type === 'patch' && rawMessage.patch) {
      stateStore.applyStatePatch?.(rawMessage.patch);
      notifyState(stateStore.state || null);
    }
  }

  function handleSessionHotkey(ev) {
    const tag = ev.target?.tagName || '';
    if (/^(INPUT|TEXTAREA|SELECT)$/.test(tag)) return;
    if (ev.metaKey || ev.ctrlKey || ev.altKey) return;
    if (!/^[0-9]$/.test(ev.key)) return;
    if (!agentDetailPanel) return;
    const agents = Object.values(stateStore?.state?.agents || {});
    agents.sort((a, b) => (a.name || '').localeCompare(b.name || ''));
    const idx = ev.key === '0' ? -1 : Number(ev.key) - 1;
    if (idx === -1) {
      agentDetailPanel._close?.();
    } else if (agents[idx]) {
      agentDetailPanel.focusSession(agents[idx].sessionId || agents[idx].id);
    }
  }
  if (typeof resolvedWindow.addEventListener === 'function') {
    resolvedWindow.addEventListener('keydown', handleSessionHotkey);
  }

  async function fetchInitialState() {
    try {
      const headers = authToken
        ? { authorization: `Bearer ${authToken}` }
        : undefined;
      const response = await resolvedFetch(`${apiBaseUrl}/state`, { headers });
      if (!response.ok) {
        throw new Error(`Failed to fetch /state (${response.status})`);
      }

      const payload = await response.json();
      if (payload?.data) {
        stateStore.setWorldState(payload.data);
        notifyState(payload.data);
      }
    } catch (error) {
      console.error(error);
    }
  }

  async function issueWsTicket() {
    const headers = authToken
      ? {
          authorization: `Bearer ${authToken}`,
          'content-type': 'application/json'
        }
      : { 'content-type': 'application/json' };
    const response = await resolvedFetch(`${apiBaseUrl}/auth/ws-ticket`, {
      method: 'POST',
      headers,
      body: '{}'
    });
    if (!response.ok) {
      throw new Error(`Failed to issue WS ticket (${response.status})`);
    }

    const payload = await response.json();
    const ticket =
      typeof payload?.ticket === 'string' ? payload.ticket.trim() : '';
    if (!ticket) {
      throw new Error('WS ticket payload is missing ticket value.');
    }

    const wsUrlObject = new URL(resolvedWsBaseUrl);
    wsUrlObject.searchParams.set('ticket', ticket);
    return wsUrlObject.toString();
  }

  function scheduleReconnect() {
    if (isDestroyed || reconnectTimer) {
      return;
    }

    reconnectTimer = resolvedWindow.setTimeout(() => {
      reconnectTimer = null;
      connectWebSocket();
    }, 1500);
  }

  function connectWebSocket() {
    if (
      isDestroyed ||
      isConnecting ||
      (socket &&
        (socket.readyState === ResolvedWebSocket.OPEN ||
          socket.readyState === wsConnectingState))
    ) {
      return;
    }

    isConnecting = true;
    setConnectionStatus('Connecting...', 'connecting');
    issueWsTicket()
      .then(wsUrl => {
        isConnecting = false;
        if (isDestroyed) {
          return;
        }

        socket = new ResolvedWebSocket(wsUrl);

        socket.addEventListener('open', () => {
          setConnectionStatus('Live', 'live');
        });

        socket.addEventListener('message', event => {
          try {
            const message = JSON.parse(event.data);
            applyMessage(message);
          } catch (error) {
            console.error('Failed to parse WS message', error);
          }
        });

        socket.addEventListener('close', () => {
          if (isDestroyed) {
            return;
          }

          setConnectionStatus('Reconnecting...', 'reconnecting');
          scheduleReconnect();
        });

        socket.addEventListener('error', () => {
          setConnectionStatus('Connection Error', 'error');
        });
      })
      .catch(error => {
        isConnecting = false;
        console.error('Failed to initialize WS connection', error);
        if (isDestroyed) {
          return;
        }
        setConnectionStatus('Connection Error', 'error');
        scheduleReconnect();
      });
  }

  function destroy() {
    if (isDestroyed) {
      return;
    }

    isDestroyed = true;

    if (reconnectTimer) {
      resolvedWindow.clearTimeout(reconnectTimer);
      reconnectTimer = null;
    }

    if (socket && typeof socket.close === 'function') {
      socket.close();
    }

    if (typeof stateStore.destroy === 'function') {
      stateStore.destroy();
    }

    if (agentDetailPanel && typeof agentDetailPanel.destroy === 'function') {
      agentDetailPanel.destroy();
    }

    if (agentRoster && typeof agentRoster.destroy === 'function') {
      agentRoster.destroy();
    }

    if (agentPromptPanel && typeof agentPromptPanel.destroy === 'function') {
      agentPromptPanel.destroy();
    }

    if (eventLog && typeof eventLog.destroy === 'function') eventLog.destroy();
    if (roundTimeline && typeof roundTimeline.destroy === 'function') roundTimeline.destroy();
    if (workflowDashboard && typeof workflowDashboard.destroy === 'function') workflowDashboard.destroy();
    if (overviewPanel && typeof overviewPanel.destroy === 'function') overviewPanel.destroy();
    if (appShell && typeof appShell.destroy === 'function') appShell.destroy();
    if (marketStrategyPanel && typeof marketStrategyPanel.destroy === 'function') marketStrategyPanel.destroy();
  }

  return {
    fetchInitialState,
    connectWebSocket,
    destroy,
    getWorldState() {
      return stateStore.state || null;
    },
    getStateStore() {
      return stateStore;
    }
  };
}

export function bootstrapFrontendApp(options = {}) {
  const resolvedWindow =
    options.windowLike || (typeof window !== 'undefined' ? window : null);
  const app = createFrontendApp(options);
  if (resolvedWindow && typeof resolvedWindow === 'object') {
    resolvedWindow.__futuresSimApp = app;
  }

  if (resolvedWindow && typeof resolvedWindow.addEventListener === 'function') {
    resolvedWindow.addEventListener('beforeunload', () => {
      app.destroy();
    });
  }

  app.fetchInitialState();
  app.connectWebSocket();
  return app;
}
