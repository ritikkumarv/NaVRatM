/* ══════════ App Init & Auto-refresh ══════════ */
let refreshTimer = null;

async function fetchAll() {
  await Promise.all([fetchStats(), fetchApps()]);
}

// ── Init ──
fetchAll();

// Auto-refresh every 30 seconds
refreshTimer = setInterval(fetchAll, 30000);

// Keyboard: Escape closes detail
document.addEventListener('keydown', e => { if (e.key === 'Escape') closeDetail(); });

// Set initial sort arrow
document.getElementById('sort-risk_score').textContent = '\u25BC';
