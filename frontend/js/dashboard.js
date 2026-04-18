/* ══════════ Dashboard: Stats, Table, Filters, Heatmap ══════════ */
let allApps = [];
let currentSort = { key: 'risk_score', dir: 'desc' };
let selectedId = null;

// ── Stats ──
async function fetchStats() {
  try {
    const s = await api('/stats');
    document.getElementById('statTotal').textContent = s.total_applications;
    document.getElementById('statPending').textContent = s.pending;
    document.getElementById('statFlagged').textContent = s.flagged;
    document.getElementById('statApproved').textContent = s.approved;
    document.getElementById('statRejected').textContent = s.rejected;
    document.getElementById('statEscalated').textContent = s.escalated;
    document.getElementById('statAvgScore').textContent = s.avg_risk_score.toFixed(1);
    document.getElementById('statHighRisk').textContent = s.high_risk_count;
  } catch (e) { console.error('Stats fetch failed', e); }
}

// ── Application list ──
async function fetchApps() {
  try {
    const params = new URLSearchParams();
    params.set('sort_by', currentSort.key === 'name' ? 'name' : 'risk_score');
    params.set('sort_order', currentSort.dir);
    allApps = await api('/applications?' + params.toString());
    applyFilters();
  } catch (e) { console.error('Apps fetch failed', e); }
}

function applyFilters() {
  const status = document.getElementById('filterStatus').value;
  const band = document.getElementById('filterBand').value;
  const scheme = document.getElementById('filterScheme').value;
  const search = document.getElementById('filterSearch').value.toLowerCase();

  let filtered = allApps;
  if (status) filtered = filtered.filter(a => a.status === status);
  if (band) filtered = filtered.filter(a => a.risk_band === band);
  if (scheme) filtered = filtered.filter(a => a.scheme === scheme);
  if (search) filtered = filtered.filter(a =>
    a.applicant_name.toLowerCase().includes(search) || a.id.toLowerCase().includes(search)
  );

  // Sort
  filtered.sort((a, b) => {
    let va = a[currentSort.key] ?? '', vb = b[currentSort.key] ?? '';
    if (currentSort.key === 'name') { va = a.applicant_name; vb = b.applicant_name; }
    if (typeof va === 'number' && typeof vb === 'number') return currentSort.dir === 'asc' ? va - vb : vb - va;
    return currentSort.dir === 'asc' ? String(va).localeCompare(String(vb)) : String(vb).localeCompare(String(va));
  });

  document.getElementById('resultCount').textContent = `${filtered.length} of ${allApps.length} applications`;
  renderTable(filtered);
  renderHeatmap(filtered);
}

function sortBy(key) {
  if (currentSort.key === key) currentSort.dir = currentSort.dir === 'asc' ? 'desc' : 'asc';
  else { currentSort.key = key; currentSort.dir = 'desc'; }
  document.querySelectorAll('.sort-arrow').forEach(el => el.textContent = '');
  const arrow = document.getElementById('sort-' + key);
  if (arrow) arrow.textContent = currentSort.dir === 'asc' ? '\u25B2' : '\u25BC';
  applyFilters();
}

function renderTable(apps) {
  const tbody = document.getElementById('appTable');
  tbody.innerHTML = apps.map(a => `
    <tr class="${a.id === selectedId ? 'selected' : ''}" onclick="openDetail('${a.id}')">
      <td style="font-family:monospace; font-size:0.8rem;">${a.id}</td>
      <td>${a.applicant_name}</td>
      <td><span style="font-size:0.8rem;">${a.scheme}</span></td>
      <td><span class="status-badge status-${a.status}">${a.status.replace('_',' ')}</span></td>
      <td>
        <div class="score-bar">
          <span class="score-num" style="color:${scoreColor(a.risk_score)}">${a.risk_score ?? '\u2014'}</span>
          <div style="flex:1;background:var(--border);border-radius:3px;height:6px;">
            <div class="score-fill" style="width:${a.risk_score ?? 0}%;background:${scoreColor(a.risk_score)};"></div>
          </div>
        </div>
      </td>
      <td>${a.risk_band ? `<span class="badge badge-${a.risk_band}">${a.risk_band}</span>` : '\u2014'}</td>
    </tr>
  `).join('');
}

function renderHeatmap(apps) {
  const hm = document.getElementById('heatmap');
  hm.innerHTML = apps.map(a => {
    const s = a.risk_score ?? 0;
    return `<div class="heatmap-cell" style="background:${scoreColor(s)}; opacity:${0.4 + (s/100)*0.6}" data-tip="${a.id}: ${s}"></div>`;
  }).join('');
}
