function ApplicantHistory({ health, history }) {
  return (
    <section className="analytics-shell">
      <article className="studio-card analytics-hero">
        <div className="card-topline">
          <div>
            <span className="panel-kicker">Applicant queue</span>
            <h3>Recent cases and application movement</h3>
          </div>
          <div className={`mini-status status-${health}`}>
            <span className="status-dot" />
            {health === "checking" ? "Checking API" : `API ${health}`}
          </div>
        </div>

        <div className="history-list">
          {history.map((item) => (
            <article className="history-card" key={item.id}>
              <div className="history-main">
                <div className="history-id">{item.id}</div>
                <div>
                  <h4>{item.applicantName}</h4>
                  <p>{item.summary}</p>
                </div>
              </div>

              <div className="history-meta">
                <span className={`history-pill status-${item.risk}`}>{item.risk} risk</span>
                <span className={`history-pill history-status-${item.status}`}>{item.status}</span>
                <span className="history-text">{item.type}</span>
                <span className="history-text">{item.updatedAt}</span>
              </div>

              <div className="history-details">
                <span>PAN: {item.pan}</span>
                <span>Aadhaar: {item.aadhaar}</span>
                <span>Amount: INR {Number(item.amount || 0).toLocaleString("en-IN")}</span>
              </div>
            </article>
          ))}
        </div>
      </article>
    </section>
  );
}

export default ApplicantHistory;
