// Central application state — replaces WorldMap for the trading UI.

function isObject(value) {
  return value && typeof value === 'object' && !Array.isArray(value);
}

function mergePatch(target, patch) {
  if (!isObject(patch)) return patch;
  if (!isObject(target)) target = {};
  for (const key of Object.keys(patch)) {
    const part = patch[key];
    if (part === null) delete target[key];
    else if (isObject(part)) target[key] = mergePatch(target[key], part);
    else target[key] = part;
  }
  return target;
}

export default class StateStore {
  constructor() {
    this.state = null;
    this.selectedAgent = null;
  }

  setWorldState(nextState) {
    this.state = nextState || null;
  }

  applyStatePatch(patch) {
    if (!patch || !isObject(patch)) return;
    if (!this.state) {
      this.state = mergePatch({}, patch);
      return;
    }
    mergePatch(this.state, patch);
  }

  destroy() {
    this.state = null;
    this.selectedAgent = null;
  }
}
