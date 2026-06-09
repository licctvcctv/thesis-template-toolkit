// Minimal world state for the futures trading simulation (no pixel map).

const TRADING_LOCATIONS = Object.freeze([
  { id: 'store', name: '资讯采集台', type: 'station', x: 0, y: 0, w: 1, h: 1 },
  { id: 'library', name: '记忆档案馆', type: 'station', x: 0, y: 0, w: 1, h: 1 },
  { id: 'home_ne', name: '价格趋势墙', type: 'station', x: 0, y: 0, w: 1, h: 1 },
  { id: 'home_sw', name: '风险控制室', type: 'station', x: 0, y: 0, w: 1, h: 1 },
  { id: 'office', name: '交易执行门', type: 'station', x: 0, y: 0, w: 1, h: 1 },
  { id: 'cafe', name: '策略休息区', type: 'station', x: 0, y: 0, w: 1, h: 1 },
  { id: 'home_nw', name: '研究工作室', type: 'station', x: 0, y: 0, w: 1, h: 1 }
]);

function isRecord(value) {
  return value && typeof value === 'object' && !Array.isArray(value);
}

function createTradingWorldState() {
  return {
    world: {
      mode: 'trading',
      locations: TRADING_LOCATIONS.map(loc => ({ ...loc }))
    },
    agents: {},
    avatars: {},
    zones: {},
    runs: {},
    meta: {}
  };
}

function ensureWorldState(worldState) {
  if (!isRecord(worldState)) {
    throw new TypeError('worldState must be an object');
  }
  worldState.agents = isRecord(worldState.agents) ? worldState.agents : {};
  worldState.zones = isRecord(worldState.zones) ? worldState.zones : {};
  worldState.runs = isRecord(worldState.runs) ? worldState.runs : {};
  worldState.avatars = isRecord(worldState.avatars) ? worldState.avatars : {};
  if (!isRecord(worldState.world)) {
    worldState.world = createTradingWorldState().world;
  } else if (!Array.isArray(worldState.world.locations)) {
    worldState.world.locations = TRADING_LOCATIONS.map(loc => ({ ...loc }));
  }
  return worldState;
}

module.exports = {
  TRADING_LOCATIONS,
  createTradingWorldState,
  ensureWorldState
};
