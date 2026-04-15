function formatCurrency(value) {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0,
  }).format(value);
}

function AnalyticsBoard({ health, history }) {
  const totalExposure = history.reduce((sum, item) => sum + (item.amount || 0), 0);
  const verifiedCount = history.filter((item) => item.status === "verified").length;
  const reviewCount = history.filter((item) =>
    ["review", "flagged"].includes(item.status)
  ).length;
  const applicationCount = history.filter((item) => item.type === "application").length;

  return (
    <section className="analytics-shell">
      <article className="studio-card analytics-hero">
        <div className="card-topline">
          <div>
            <span className="panel-kicker">Portfolio overview</span>
            <h3>Live activity analytics</h3>
          </div>
          <div className={`mini-status status-${health}`}>
            <span className="status-dot" />
            {health === "checking" ? "Checking API" : `API ${health}`}
          </div>
        </div>

        <div className="analytics-grid">
          <article className="metric-panel">
            <span className="summary-label">Tracked volume</span>
            <strong>{formatCurrency(totalExposure)}</strong>
            <p>Total value represented by the current case list.</p>
          </article>
          <article className="metric-panel">
            <span className="summary-label">Verified profiles</span>
            <strong>{verifiedCount}</strong>
            <p>Applicants that cleared identity checks and can move forward.</p>
          </article>
          <article className="metric-panel">
            <span className="summary-label">Needs review</span>
            <strong>{reviewCount}</strong>
            <p>Cases that still need manual intervention before approval.</p>
          </article>
          <article className="metric-panel">
            <span className="summary-label">Applications entered</span>
            <strong>{applicationCount}</strong>
            <p>Loan requests currently visible in the intake pipeline.</p>
          </article>
        </div>
      </article>

      <section className="studio-grid">
        <article className="studio-card">
          <div className="card-topline">
            <div>
              <span className="panel-kicker">Risk mix</span>
              <h3>Portfolio distribution</h3>
            </div>
          </div>

          <div className="distribution-list">
            {["low", "medium", "high"].map((level) => {
              const count = history.filter((item) => item.risk === level).length;
              const width = history.length ? Math.max((count / history.length) * 100, 10) : 10;
              return (
                <div className="distribution-row" key={level}>
                  <div className="distribution-head">
                    <span className="risk-name">{level} risk</span>
                    <strong>{count} cases</strong>
                  </div>
                  <div className="distribution-bar">
                    <div className={`distribution-fill ${level}`} style={{ width: `${width}%` }} />
                  </div>
                </div>
              );
            })}
          </div>
        </article>

        <article className="studio-card">
          <div className="card-topline">
            <div>
              <span className="panel-kicker">Ops notes</span>
              <h3>What this dashboard tells you</h3>
            </div>
          </div>

          <div className="insight-list">
            <article className="insight-card">
              <strong>Frontline teams can triage faster</strong>
              <p>Verification, intake, and queue tracking now live in one consistent interface.</p>
            </article>
            <article className="insight-card">
              <strong>Shared history feeds the analytics</strong>
              <p>Every new verification or application updates the portfolio counts immediately.</p>
            </article>
            <article className="insight-card">
              <strong>Good base for future backend metrics</strong>
              <p>This screen can later plug into real approval rates, fraud flags, and SLA data.</p>
            </article>
          </div>
        </article>
      </section>
    </section>
  );
}

export default AnalyticsBoard;
