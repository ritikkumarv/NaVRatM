/* ══════════ Detail Panel, Explain, Decide ══════════ */

async function openDetail(id) {
  selectedId = id;
  applyFilters(); // re-render to highlight
  try {
    const app = await api('/applications/' + id);
    renderDetail(app);
    document.getElementById('detailOverlay').classList.add('active');
  } catch (e) { showToast('Failed to load detail: ' + e.message, 'error'); }
}

function closeDetail() {
  document.getElementById('detailOverlay').classList.remove('active');
  selectedId = null;
  applyFilters();
}

function renderDetail(app) {
  const p = app.risk_profile || {};
  const factors = p.factors || [];
  const anomalies = p.anomalies || [];
  const nflags = p.network_flags || [];
  const discs = app.discrepancies || [];

  document.getElementById('detailPanel').innerHTML = `
    <h2>
      <span>${app.id} \u2014 ${app.declared.full_name}</span>
      <button class="close-btn" onclick="closeDetail()">&times;</button>
    </h2>

    <div class="detail-section">
      <h3>Status & Risk</h3>
      <div style="display:flex;gap:1rem;align-items:center;margin-bottom:0.5rem;">
        <span class="status-badge status-${app.status}" style="font-size:0.85rem;">${app.status.replace('_',' ')}</span>
        <span class="badge badge-${app.risk_band || 'low'}" style="font-size:0.85rem;">${app.risk_band || '\u2014'}</span>
        <span style="font-size:1.4rem;font-weight:700;color:${scoreColor(app.risk_score)}">${app.risk_score ?? '\u2014'}<span style="font-size:0.7rem;color:var(--text-secondary)">/100</span></span>
      </div>
    </div>

    <div class="detail-section">
      <h3>Declared Values</h3>
      <div class="detail-grid">
        ${Object.entries(app.declared).map(([k,v]) => `<div class="field"><span class="lbl">${k.replace(/_/g,' ')}:</span> <span class="val">${v || '\u2014'}</span></div>`).join('')}
      </div>
    </div>

    ${factors.length ? `<div class="detail-section">
      <h3>Risk Factors (${factors.length})</h3>
      <ul class="detail-list">
        ${factors.map(f => `<li class="severity-${f.points > 10 ? 'high' : f.points > 5 ? 'medium' : 'low'}">
          <strong>${f.factor_name}</strong> \u2014 ${f.points}/${f.max_points} pts<br>
          <span style="color:var(--text-secondary);font-size:0.75rem;">${f.description}</span>
        </li>`).join('')}
      </ul>
    </div>` : ''}

    ${anomalies.length ? `<div class="detail-section">
      <h3>Anomalies (${anomalies.length})</h3>
      <ul class="detail-list">
        ${anomalies.map(a => `<li class="severity-${a.severity || 'medium'}">
          <strong>${a.anomaly_type}</strong> +${a.contributing_score || 0} pts<br>
          <span style="color:var(--text-secondary);font-size:0.75rem;">${a.description}</span>
        </li>`).join('')}
      </ul>
    </div>` : ''}

    ${nflags.length ? `<div class="detail-section">
      <h3>Network Flags (${nflags.length})</h3>
      <ul class="detail-list">
        ${nflags.map(n => `<li class="severity-high">
          <strong>${n.flag_type}</strong> (confidence: ${(n.confidence*100).toFixed(0)}%)<br>
          <span style="color:var(--text-secondary);font-size:0.75rem;">${n.description}</span>
          ${n.linked_entity_ids?.length ? `<br><span style="font-size:0.72rem;color:var(--info);">Linked: ${n.linked_entity_ids.join(', ')}</span>` : ''}
        </li>`).join('')}
      </ul>
    </div>` : ''}

    ${discs.length ? `<div class="detail-section">
      <h3>Discrepancies (${discs.length})</h3>
      <ul class="detail-list">
        ${discs.map(d => `<li class="severity-${d.severity}">
          <strong>${d.field}</strong> \u2014 ${d.source_document}<br>
          Declared: <em>${d.declared_value}</em> vs Extracted: <em>${d.extracted_value}</em>
          <span style="font-size:0.72rem;color:var(--text-secondary);"> (match: ${(d.match_score*100).toFixed(0)}%)</span>
        </li>`).join('')}
      </ul>
    </div>` : ''}

    <div class="detail-section">
      <h3>Explanation</h3>
      <div class="explain-box" id="explainBox">${app.explanation || '<span style="color:var(--text-secondary)">Click "Explain" to generate an AI explanation.</span>'}</div>
      <button class="btn btn-outline btn-sm" style="margin-top:0.5rem;" onclick="explainApp('${app.id}')">&#128172; Explain</button>
    </div>

    <div class="decision-bar">
      <button class="btn btn-success btn-sm" onclick="decide('${app.id}','approve')">&#10003; Approve</button>
      <button class="btn btn-outline btn-sm" style="border-color:var(--warning);color:var(--warning);" onclick="decide('${app.id}','flag')">&#9873; Flag</button>
      <button class="btn btn-danger btn-sm" onclick="decide('${app.id}','reject')">&#10007; Reject</button>
      <button class="btn btn-outline btn-sm" style="border-color:var(--info);color:var(--info);" onclick="decide('${app.id}','escalate')">&#8679; Escalate</button>
    </div>
  `;
}

// ── Actions ──
async function processAll() {
  const btn = document.getElementById('btnProcessAll');
  btn.disabled = true;
  showLoading('Processing all applications through the pipeline...');
  try {
    const result = await api('/applications/process-all', { method: 'POST' });
    hideLoading();
    showToast(`Processed ${result.total_processed} apps in ${result.processing_time_seconds}s (avg score: ${result.avg_score})`);
    await fetchAll();
  } catch (e) {
    hideLoading();
    showToast('Process-all failed: ' + e.message, 'error');
  } finally {
    btn.disabled = false;
  }
}

async function decide(id, action) {
  try {
    await api(`/applications/${id}/decide`, {
      method: 'POST',
      body: JSON.stringify({ action, reason: 'Officer decision via dashboard' }),
    });
    showToast(`${id}: ${action}d`);
    await openDetail(id);
    await fetchAll();
  } catch (e) { showToast('Decision failed: ' + e.message, 'error'); }
}

async function explainApp(id) {
  const box = document.getElementById('explainBox');
  box.innerHTML = '<span class="spinner"></span> Generating explanation...';
  try {
    const res = await api(`/applications/${id}/explain`, {
      method: 'POST',
      body: JSON.stringify({ language: 'en-IN' }),
    });
    box.textContent = res.explanation;
  } catch (e) {
    box.textContent = 'Failed to generate explanation: ' + e.message;
  }
}
