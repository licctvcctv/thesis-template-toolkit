class EventValidationError extends Error {
  constructor(message, details = []) {
    super(message);
    this.name = 'EventValidationError';
    this.statusCode = 400;
    this.details = details;
  }
}

function cloneState(state) {
  if (typeof globalThis.structuredClone === 'function') {
    return globalThis.structuredClone(state);
  }

  return JSON.parse(JSON.stringify(state));
}

function replaceState(targetState, nextState) {
  Object.keys(targetState).forEach(key => {
    delete targetState[key];
  });
  Object.assign(targetState, nextState);
}

function normalizeEventBatch(input) {
  if (Array.isArray(input)) {
    if (input.length === 0) {
      throw new EventValidationError('Event array must not be empty.', [
        { index: 0, error: 'At least one event is required.' }
      ]);
    }
    return input;
  }

  if (typeof input === 'object' && input !== null) {
    return [input];
  }

  throw new EventValidationError('Request body must be an event object or array.');
}

function normalizeTimestamp(value) {
  if (typeof value === 'number' && Number.isFinite(value)) {
    return value;
  }
  if (typeof value === 'string' && value.trim()) {
    const parsed = Date.parse(value);
    if (Number.isFinite(parsed)) return parsed;
  }
  return Date.now();
}

function normalizeEvent(rawEvent) {
  if (typeof rawEvent !== 'object' || rawEvent === null) {
    throw new Error('Event must be an object.');
  }

  const eventType = String(rawEvent.eventType || rawEvent.type || '').trim();
  if (!eventType) {
    throw new Error('Event must include eventType or type.');
  }

  const normalized = {
    ...rawEvent,
    eventType,
    timestamp: normalizeTimestamp(rawEvent.timestamp || rawEvent.ts)
  };

  if (rawEvent.agentId != null) normalized.agentId = String(rawEvent.agentId);
  if (rawEvent.taskId != null) normalized.taskId = String(rawEvent.taskId);
  if (rawEvent.runId != null) normalized.runId = String(rawEvent.runId);

  return normalized;
}

function ensureRecord(target, key) {
  if (typeof target[key] !== 'object' || target[key] === null || Array.isArray(target[key])) {
    target[key] = {};
  }
  return target[key];
}

function applyGenericEvent(event, worldState) {
  const agents = ensureRecord(worldState, 'agents');
  const runs = ensureRecord(worldState, 'runs');
  const meta = ensureRecord(worldState, 'meta');

  meta.lastEvent = {
    eventType: event.eventType,
    agentId: event.agentId || null,
    taskId: event.taskId || null,
    runId: event.runId || null,
    timestamp: event.timestamp
  };

  if (event.agentId) {
    const current = agents[event.agentId] || {};
    agents[event.agentId] = {
      ...current,
      id: current.id || event.agentId,
      name: event.name || current.name || event.agentId,
      status: event.status || current.status || 'working',
      lastEventType: event.eventType,
      lastEventAt: event.timestamp
    };
  }

  if (event.runId) {
    const current = runs[event.runId] || {};
    runs[event.runId] = {
      ...current,
      id: current.id || event.runId,
      agentId: event.agentId || current.agentId || null,
      status: event.status || current.status || 'running',
      updatedAt: event.timestamp
    };
  }
}

function processIncomingEvents(input, worldState, options = {}) {
  const applyEvent =
    typeof options.applyEvent === 'function'
      ? options.applyEvent
      : applyGenericEvent;
  const afterEachApply =
    typeof options.afterEachApply === 'function' ? options.afterEachApply : null;
  const rawEvents = normalizeEventBatch(input);
  const normalizedEvents = [];
  const errors = [];

  rawEvents.forEach((rawEvent, index) => {
    try {
      normalizedEvents.push(normalizeEvent(rawEvent));
    } catch (error) {
      errors.push({ index, error: error.message });
    }
  });

  if (errors.length > 0) {
    throw new EventValidationError('One or more events are invalid.', errors);
  }

  const snapshot = cloneState(worldState);

  try {
    normalizedEvents.forEach(event => {
      applyEvent(event, worldState);
      if (afterEachApply) {
        afterEachApply(worldState, event);
      }
    });
  } catch (error) {
    replaceState(worldState, snapshot);
    throw error;
  }

  return normalizedEvents;
}

module.exports = {
  EventValidationError,
  processIncomingEvents
};
