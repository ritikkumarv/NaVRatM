import { useState } from "react";

const initialForm = {
  applicantName: "",
  pan: "",
  aadhaar: "",
  loanAmount: "",
  monthlyIncome: "",
  purpose: "Home renovation",
  tenure: "36 months",
};

const purposeOptions = [
  "Home renovation",
  "Business expansion",
  "Education support",
  "Medical emergency",
];

const tenureOptions = ["12 months", "24 months", "36 months", "60 months"];

function ApplicationWorkbench({ health, onSubmitApplication }) {
  const [form, setForm] = useState(initialForm);
  const [status, setStatus] = useState("");

  const handleChange = (event) => {
    const { name, value } = event.target;
    const normalizedValue =
      name === "pan" ? value.toUpperCase().slice(0, 10) : value;

    setForm((current) => ({
      ...current,
      [name]: normalizedValue,
    }));
  };

  const applySample = () => {
    setForm({
      applicantName: "Karan Patel",
      pan: "AAECP4567M",
      aadhaar: "4512 7890 1234",
      loanAmount: "850000",
      monthlyIncome: "125000",
      purpose: "Business expansion",
      tenure: "36 months",
    });
    setStatus("");
  };

  const handleSubmit = (event) => {
    event.preventDefault();

    onSubmitApplication({
      ...form,
      loanAmount: Number(form.loanAmount),
      monthlyIncome: Number(form.monthlyIncome),
      aadhaar: form.aadhaar.replace(/\D/g, ""),
    });

    setStatus("Application saved and moved into the shared history queue.");
    setForm(initialForm);
  };

  return (
    <section className="studio-grid">
      <article className="studio-card input-card">
        <div className="card-topline">
          <div>
            <span className="panel-kicker">Application desk</span>
            <h3>Create a new loan request</h3>
          </div>
          <div className={`mini-status status-${health}`}>
            <span className="status-dot" />
            {health === "checking" ? "Checking API" : `API ${health}`}
          </div>
        </div>

        <form className="verification-form" onSubmit={handleSubmit}>
          <div className="dual-grid">
            <label className="input-block">
              <span>Applicant name</span>
              <input
                name="applicantName"
                value={form.applicantName}
                onChange={handleChange}
                placeholder="Full name"
                required
              />
            </label>

            <label className="input-block">
              <span>PAN</span>
              <input
                name="pan"
                value={form.pan}
                onChange={handleChange}
                placeholder="ABCDE1234F"
                required
              />
            </label>
          </div>

          <div className="dual-grid">
            <label className="input-block">
              <span>Aadhaar</span>
              <input
                name="aadhaar"
                value={form.aadhaar}
                onChange={handleChange}
                placeholder="1234 5678 9012"
                required
              />
            </label>

            <label className="input-block">
              <span>Loan amount</span>
              <input
                name="loanAmount"
                type="number"
                min="10000"
                step="1000"
                value={form.loanAmount}
                onChange={handleChange}
                placeholder="500000"
                required
              />
            </label>
          </div>

          <div className="dual-grid">
            <label className="input-block">
              <span>Monthly income</span>
              <input
                name="monthlyIncome"
                type="number"
                min="10000"
                step="1000"
                value={form.monthlyIncome}
                onChange={handleChange}
                placeholder="90000"
                required
              />
            </label>

            <label className="input-block">
              <span>Purpose</span>
              <select
                className="select-input"
                name="purpose"
                value={form.purpose}
                onChange={handleChange}
              >
                {purposeOptions.map((option) => (
                  <option key={option} value={option}>
                    {option}
                  </option>
                ))}
              </select>
            </label>
          </div>

          <label className="input-block">
            <span>Repayment tenure</span>
            <select
              className="select-input"
              name="tenure"
              value={form.tenure}
              onChange={handleChange}
            >
              {tenureOptions.map((option) => (
                <option key={option} value={option}>
                  {option}
                </option>
              ))}
            </select>
          </label>

          <div className="action-row">
            <button className="primary-button" type="submit">
              Save Application
            </button>
            <button className="secondary-button" type="button" onClick={applySample}>
              Use Sample
            </button>
          </div>
        </form>

        {status ? <div className="feedback-banner success-banner">{status}</div> : null}
      </article>

      <article className="studio-card results-card">
        <div className="card-topline">
          <div>
            <span className="panel-kicker">Intake guidance</span>
            <h3>Operator checklist</h3>
          </div>
          <div className="decision-pill decision-pass">Submission ready</div>
        </div>

        <div className="results-layout">
          <section className="decision-banner">
            <span className="note-label">Fast intake flow</span>
            <h4>Capture a complete application in one pass.</h4>
            <p>
              This screen is designed for data entry speed, with all key financial
              and identity fields available in one compact workspace.
            </p>
          </section>

          <div className="signal-grid">
            <article className="signal-card">
              <span className="signal-label">Focus</span>
              <strong>Single-screen intake</strong>
            </article>
            <article className="signal-card">
              <span className="signal-label">Outcome</span>
              <strong>Moves directly to history</strong>
            </article>
            <article className="signal-card">
              <span className="signal-label">Best for</span>
              <strong>Sales desk and ops teams</strong>
            </article>
            <article className="signal-card">
              <span className="signal-label">Next step</span>
              <strong>Verification or underwriting</strong>
            </article>
          </div>
        </div>
      </article>
    </section>
  );
}

export default ApplicationWorkbench;
