/* ══════════ API Client & UI Helpers ══════════ */
const API = 'http://127.0.0.1:8000/api';

async function api(path, opts = {}) {
  const res = await fetch(API + path, {
    headers: { 'Content-Type': 'application/json' },
    ...opts,
  });
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
  return res.json();
}

function showToast(msg, type = 'success') {
  const t = document.getElementById('toast');
  t.textContent = msg;
  t.className = 'toast show ' + type;
  setTimeout(() => t.className = 'toast', 3000);
}

function showLoading(msg) {
  document.getElementById('loadingMsg').textContent = msg;
  document.getElementById('loadingOverlay').style.display = 'flex';
}

function hideLoading() {
  document.getElementById('loadingOverlay').style.display = 'none';
}

function scoreColor(s) {
  if (s == null) return 'var(--text-secondary)';
  if (s < 25) return 'var(--risk-low)';
  if (s < 50) return 'var(--risk-medium)';
  if (s < 75) return 'var(--risk-high)';
  return 'var(--risk-critical)';
}
