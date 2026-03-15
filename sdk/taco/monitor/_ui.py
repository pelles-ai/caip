"""Embedded HTML UI for the TACO Agent Monitor."""

HTML_UI = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>TACO Agent Monitor</title>
<style>
  :root {
    --bg: #fafafa; --bg-card: #fff; --bg-hover: #f5f5f5;
    --text: #1a1a2e; --text-muted: #6b7280; --text-dim: #9ca3af;
    --border: #e5e7eb; --border-light: #f3f4f6;
    --accent: #6366f1; --accent-light: #eef2ff;
    --in-bg: #eff6ff; --in-border: #bfdbfe; --in-text: #1d4ed8; --in-dot: #3b82f6;
    --out-bg: #ecfdf5; --out-border: #a7f3d0; --out-text: #047857; --out-dot: #10b981;
    --handler-bg: #f5f3ff; --handler-border: #ddd6fe; --handler-text: #6d28d9; --handler-dot: #8b5cf6;
    --disc-bg: #fff7ed; --disc-border: #fed7aa; --disc-text: #c2410c; --disc-dot: #f97316;
    --err-bg: #fef2f2; --err-border: #fecaca; --err-text: #dc2626; --err-dot: #ef4444;
    --radius: 8px; --font: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
    --mono: 'SF Mono', 'Cascadia Code', 'Fira Code', Consolas, monospace;
  }
  @media (prefers-color-scheme: dark) {
    :root {
      --bg: #0f0f17; --bg-card: #1a1a2e; --bg-hover: #22223a;
      --text: #e5e5ef; --text-muted: #9ca3b8; --text-dim: #6b7280;
      --border: #2a2a42; --border-light: #22223a;
      --accent: #818cf8; --accent-light: #1e1b4b;
      --in-bg: #172554; --in-border: #1e3a5f; --in-text: #60a5fa; --in-dot: #3b82f6;
      --out-bg: #052e16; --out-border: #14532d; --out-text: #34d399; --out-dot: #10b981;
      --handler-bg: #1e1b3a; --handler-border: #312e81; --handler-text: #a78bfa; --handler-dot: #8b5cf6;
      --disc-bg: #2a1708; --disc-border: #431407; --disc-text: #fb923c; --disc-dot: #f97316;
      --err-bg: #2a0808; --err-border: #450a0a; --err-text: #f87171; --err-dot: #ef4444;
    }
  }
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body { font-family: var(--font); background: var(--bg); color: var(--text); font-size: 13px; height: 100vh; display: flex; flex-direction: column; }

  /* Header */
  .header { display: flex; align-items: center; gap: 12px; padding: 12px 20px; border-bottom: 1px solid var(--border); background: var(--bg-card); flex-shrink: 0; }
  .header h1 { font-size: 15px; font-weight: 600; white-space: nowrap; }
  .header .agent-name { color: var(--accent); font-weight: 700; }
  .header .logo { font-size: 18px; }
  .status { display: flex; align-items: center; gap: 5px; font-size: 11px; color: var(--text-muted); margin-left: auto; }
  .status-dot { width: 7px; height: 7px; border-radius: 50%; }
  .status-dot.connected { background: #10b981; }
  .status-dot.disconnected { background: #ef4444; animation: pulse 1.5s infinite; }
  @keyframes pulse { 0%,100% { opacity: 1; } 50% { opacity: 0.4; } }
  .btn { padding: 5px 12px; border-radius: 6px; border: 1px solid var(--border); background: var(--bg-card); color: var(--text-muted); font-size: 11px; cursor: pointer; font-family: var(--font); transition: all 0.15s; }
  .btn:hover { background: var(--bg-hover); color: var(--text); }

  /* Filters */
  .filters { display: flex; gap: 6px; padding: 8px 20px; border-bottom: 1px solid var(--border); background: var(--bg-card); flex-shrink: 0; flex-wrap: wrap; align-items: center; }
  .filters label { font-size: 11px; color: var(--text-dim); font-weight: 500; margin-right: 4px; }
  .filter-chip { padding: 3px 10px; border-radius: 12px; border: 1px solid var(--border); background: var(--bg); color: var(--text-muted); font-size: 11px; cursor: pointer; transition: all 0.15s; user-select: none; }
  .filter-chip.active { border-color: var(--accent); background: var(--accent-light); color: var(--accent); font-weight: 500; }
  .filter-chip:hover { border-color: var(--accent); }
  .event-count { margin-left: auto; font-size: 11px; color: var(--text-dim); font-variant-numeric: tabular-nums; }

  /* Timeline */
  .timeline { flex: 1; overflow-y: auto; padding: 8px 20px 80px; }
  .event { display: flex; gap: 10px; padding: 8px 12px; border-radius: var(--radius); margin-bottom: 4px; transition: background 0.15s; cursor: pointer; border: 1px solid transparent; }
  .event:hover { background: var(--bg-hover); }
  .event.expanded { border-color: var(--border); }
  .event-dot { width: 8px; height: 8px; border-radius: 50%; margin-top: 4px; flex-shrink: 0; }
  .event-body { flex: 1; min-width: 0; }
  .event-header { display: flex; align-items: center; gap: 8px; }
  .event-time { font-size: 11px; color: var(--text-dim); font-variant-numeric: tabular-nums; font-family: var(--mono); flex-shrink: 0; }
  .event-kind { font-size: 9px; font-weight: 600; padding: 2px 6px; border-radius: 4px; flex-shrink: 0; text-transform: uppercase; letter-spacing: 0.3px; white-space: nowrap; }
  .event-method { font-size: 12px; font-weight: 600; color: var(--text); }
  .event-summary { font-size: 12px; color: var(--text-muted); margin-top: 2px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
  .event-duration { font-size: 11px; color: var(--text-dim); font-family: var(--mono); margin-left: auto; flex-shrink: 0; }
  .event-payload { margin-top: 8px; padding: 10px; border-radius: 6px; background: var(--bg); border: 1px solid var(--border-light); font-family: var(--mono); font-size: 11px; white-space: pre-wrap; word-break: break-all; max-height: 400px; overflow-y: auto; color: var(--text-muted); line-height: 1.5; }
  .event-error { color: var(--err-text); font-weight: 500; margin-top: 4px; font-size: 12px; }

  /* Kind-specific colors */
  .kind-in .event-dot { background: var(--in-dot); }
  .kind-in .event-kind { background: var(--in-bg); color: var(--in-text); border: 1px solid var(--in-border); }
  .kind-out .event-dot { background: var(--out-dot); }
  .kind-out .event-kind { background: var(--out-bg); color: var(--out-text); border: 1px solid var(--out-border); }
  .kind-handler .event-dot { background: var(--handler-dot); }
  .kind-handler .event-kind { background: var(--handler-bg); color: var(--handler-text); border: 1px solid var(--handler-border); }
  .kind-disc .event-dot { background: var(--disc-dot); }
  .kind-disc .event-kind { background: var(--disc-bg); color: var(--disc-text); border: 1px solid var(--disc-border); }
  .kind-err .event-dot { background: var(--err-dot); }
  .kind-err .event-kind { background: var(--err-bg); color: var(--err-text); border: 1px solid var(--err-border); }

  /* Scroll anchor */
  .scroll-btn { position: fixed; bottom: 20px; right: 20px; padding: 8px 16px; border-radius: 20px; background: var(--accent); color: #fff; border: none; font-size: 12px; cursor: pointer; box-shadow: 0 2px 8px rgba(0,0,0,0.2); display: none; z-index: 10; font-family: var(--font); }
  .scroll-btn.visible { display: block; }

  /* Empty state */
  .empty { text-align: center; padding: 60px 20px; color: var(--text-dim); }
  .empty-icon { font-size: 36px; margin-bottom: 12px; }
  .empty h2 { font-size: 16px; font-weight: 500; margin-bottom: 4px; color: var(--text-muted); }
</style>
</head>
<body>

<div class="header">
  <span class="logo">&#x1F32E;</span>
  <h1>TACO Agent Monitor &mdash; <span class="agent-name" id="agentName">Agent</span></h1>
  <div class="status">
    <span class="status-dot" id="statusDot"></span>
    <span id="statusText">Connecting...</span>
  </div>
  <button class="btn" onclick="clearEvents()">Clear</button>
</div>

<div class="filters">
  <label>Filter:</label>
  <span class="filter-chip active" data-filter="all" onclick="toggleFilter(this)">All</span>
  <span class="filter-chip active" data-filter="incoming" onclick="toggleFilter(this)">Incoming</span>
  <span class="filter-chip active" data-filter="outgoing" onclick="toggleFilter(this)">Outgoing</span>
  <span class="filter-chip active" data-filter="handler" onclick="toggleFilter(this)">Handler</span>
  <span class="filter-chip active" data-filter="discovery" onclick="toggleFilter(this)">Discovery</span>
  <span class="event-count" id="eventCount">0 events</span>
</div>

<div class="timeline" id="timeline"></div>
<button class="scroll-btn" id="scrollBtn" onclick="scrollToBottom()">&#x2193; New events</button>

<script>
const timeline = document.getElementById('timeline');
const scrollBtn = document.getElementById('scrollBtn');
const eventCountEl = document.getElementById('eventCount');
const agentNameEl = document.getElementById('agentName');
const statusDot = document.getElementById('statusDot');
const statusText = document.getElementById('statusText');

// Derive the base path so fetch/ws work when mounted under a prefix
const basePath = location.pathname.replace(/\/$/, '');

let events = [];
let autoScroll = true;
let expandedId = null;
let filters = { all: true, incoming: true, outgoing: true, handler: true, discovery: true };
let ws = null;
let reconnectDelay = 1000;

// --- Filters ---
function toggleFilter(chip) {
  const f = chip.dataset.filter;
  if (f === 'all') {
    const allActive = chip.classList.contains('active');
    document.querySelectorAll('.filter-chip').forEach(c => {
      c.classList.toggle('active', !allActive);
      filters[c.dataset.filter] = !allActive;
    });
  } else {
    filters[f] = !filters[f];
    chip.classList.toggle('active', filters[f]);
    const allChip = document.querySelector('[data-filter="all"]');
    const nonAll = ['incoming','outgoing','handler','discovery'];
    const allOn = nonAll.every(k => filters[k]);
    allChip.classList.toggle('active', allOn);
    filters.all = allOn;
  }
  renderAll();
}

function kindCategory(kind) {
  if (kind.startsWith('incoming')) return 'incoming';
  if (kind.startsWith('outgoing')) return 'outgoing';
  if (kind.startsWith('handler')) return 'handler';
  if (kind === 'discovery') return 'discovery';
  return 'incoming';
}

function isVisible(ev) {
  if (filters.all) return true;
  return filters[kindCategory(ev.kind)];
}

// --- Rendering ---
function kindClass(kind) {
  if (kind.includes('error') || kind === 'handler_error') return 'kind-err';
  if (kind.startsWith('incoming')) return 'kind-in';
  if (kind.startsWith('outgoing')) return 'kind-out';
  if (kind.startsWith('handler')) return 'kind-handler';
  if (kind === 'discovery') return 'kind-disc';
  return 'kind-in';
}

function kindLabel(kind) {
  const map = {
    'incoming_request': 'RECEIVED',
    'incoming_response': 'REPLIED',
    'outgoing_request': 'CALLING',
    'outgoing_response': 'GOT REPLY',
    'handler_start': 'PROCESSING',
    'handler_end': 'COMPLETED',
    'handler_error': 'FAILED',
    'discovery': 'DISCOVERY',
  };
  return map[kind] || kind.toUpperCase();
}

function formatTime(ts) {
  try {
    const d = new Date(ts);
    return d.toLocaleTimeString('en-US', { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' })
      + '.' + String(d.getMilliseconds()).padStart(3, '0');
  } catch { return ts; }
}

function truncatePayload(obj) {
  const s = JSON.stringify(obj, null, 2);
  return s.length > 8000 ? s.slice(0, 8000) + '\n... (truncated)' : s;
}

function renderEvent(ev) {
  if (!isVisible(ev)) return '';
  const kc = kindClass(ev.kind);
  const expanded = expandedId === ev.id;
  const dur = ev.duration_ms != null ? `${Math.round(ev.duration_ms)}ms` : '';
  const arrow = ev.direction === 'in' ? '&#x2B07;' : ev.direction === 'out' ? '&#x2B06;' : '&#x2699;';

  let html = `<div class="event ${kc} ${expanded ? 'expanded' : ''}" data-id="${ev.id}" onclick="toggleExpand('${ev.id}')">
    <div class="event-dot"></div>
    <div class="event-body">
      <div class="event-header">
        <span class="event-time">${formatTime(ev.ts)}</span>
        <span class="event-kind">${kindLabel(ev.kind)}</span>
        <span class="event-method">${arrow} ${ev.method || ''}</span>
        ${dur ? `<span class="event-duration">${dur}</span>` : ''}
      </div>
      <div class="event-summary">${escapeHtml(ev.summary || '')}</div>
      ${ev.error ? `<div class="event-error">${escapeHtml(ev.error)}</div>` : ''}
      ${expanded && ev.payload != null ? `<div class="event-payload">${escapeHtml(truncatePayload(ev.payload))}</div>` : ''}
    </div>
  </div>`;
  return html;
}

function escapeHtml(s) {
  const d = document.createElement('div');
  d.textContent = s;
  return d.innerHTML;
}

function renderAll() {
  const visible = events.filter(isVisible);
  timeline.innerHTML = visible.length === 0
    ? '<div class="empty"><div class="empty-icon">&#x1F50D;</div><h2>No events yet</h2><p>Events will appear here as the agent processes requests</p></div>'
    : visible.map(renderEvent).join('');
  eventCountEl.textContent = `${events.length} events`;
  if (autoScroll) scrollToBottom();
}

function toggleExpand(id) {
  expandedId = expandedId === id ? null : id;
  renderAll();
}

// --- Scroll ---
timeline.addEventListener('scroll', () => {
  const atBottom = timeline.scrollHeight - timeline.scrollTop - timeline.clientHeight < 60;
  autoScroll = atBottom;
  scrollBtn.classList.toggle('visible', !atBottom && events.length > 0);
});

function scrollToBottom() {
  timeline.scrollTop = timeline.scrollHeight;
  autoScroll = true;
  scrollBtn.classList.remove('visible');
}

// --- Append events efficiently ---
function appendEvent(ev) {
  events.push(ev);
  if (isVisible(ev)) {
    // Remove empty state if present
    const empty = timeline.querySelector('.empty');
    if (empty) empty.remove();
    timeline.insertAdjacentHTML('beforeend', renderEvent(ev));
  }
  eventCountEl.textContent = `${events.length} events`;
  if (autoScroll) scrollToBottom();
}

// --- Data ---
async function loadHistory() {
  try {
    const resp = await fetch(`${basePath}/api/events?limit=500`);
    const data = await resp.json();
    events = data;
    renderAll();
  } catch(e) {
    console.warn('Failed to load history:', e);
  }
}

async function loadInfo() {
  try {
    const resp = await fetch(`${basePath}/api/info`);
    const info = await resp.json();
    agentNameEl.textContent = info.agentName || 'Agent';
    document.title = `Monitor - ${info.agentName || 'Agent'}`;
  } catch(e) {
    console.warn('Failed to load info:', e);
  }
}

async function clearEvents() {
  try {
    await fetch(`${basePath}/api/clear`, { method: 'POST' });
    events = [];
    expandedId = null;
    renderAll();
  } catch(e) { console.warn('Clear failed:', e); }
}

// --- WebSocket ---
function connectWs() {
  const proto = location.protocol === 'https:' ? 'wss:' : 'ws:';
  ws = new WebSocket(`${proto}//${location.host}${basePath}/ws`);

  ws.onopen = () => {
    statusDot.className = 'status-dot connected';
    statusText.textContent = 'Live';
    reconnectDelay = 1000;
  };

  ws.onmessage = (e) => {
    try {
      const ev = JSON.parse(e.data);
      appendEvent(ev);
    } catch {}
  };

  ws.onclose = () => {
    statusDot.className = 'status-dot disconnected';
    statusText.textContent = 'Reconnecting...';
    setTimeout(connectWs, reconnectDelay);
    reconnectDelay = Math.min(reconnectDelay * 1.5, 10000);
  };

  ws.onerror = () => ws.close();
}

// --- Init ---
loadInfo();
loadHistory().then(connectWs);
</script>
</body>
</html>"""
