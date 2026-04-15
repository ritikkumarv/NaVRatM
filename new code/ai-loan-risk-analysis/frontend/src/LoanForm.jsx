import { useEffect, useRef, useState } from "react";

const initialForm = {
  pan: "",
  aadhaar: "",
};

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "";
const REQUEST_TIMEOUT_MS = 8000;

function formatAadhaar(value) {
  const digits = value.replace(/\D/g, "").slice(0, 12);
  return digits.replace(/(\d{4})(?=\d)/g, "$1 ").trim();
}

function LoanForm({ health, onRecordVerification }) {
  const [form, setForm] = useState(initialForm);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const controllerRef = useRef(null);

  useEffect(() => {
    return () => {
      controllerRef.current?.abort();
    };
  }, []);

  const readResponse = async (response) => {
    const contentType = response.headers.get("content-type") || "";
    if (contentType.includes("application/json")) {
      return response.json();
    }
    return response.text();
  };

  const handleChange = (event) => {
    const { name, value } = event.target;

    if (name === "pan") {
      setForm((current) => ({
        ...current,
        pan: value.toUpperCase().slice(0, 10),
      }));
      return;
    }

    setForm((current) => ({
      ...current,
      aadhaar: formatAadhaar(value),
    }));
  };

  const applyDemoData = () => {
    setError("");
    setForm({
      pan: "ABCDE1234F",
      aadhaar: "1234 1234 1234",
    });
  };

  const clearForm = () => {
    controllerRef.current?.abort();
    setForm(initialForm);
    setError("");
    setResult(null);
    setIsSubmitting(false);
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    controllerRef.current?.abort();
    setIsSubmitting(true);
    setError("");

    const controller = new AbortController();
    controllerRef.current = controller;
    const timeoutId = window.setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);

    try {
      const response = await fetch(`${API_BASE_URL}/verify-user`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        signal: controller.signal,
        body: JSON.stringify({
          pan: form.pan,
          aadhaar: form.aadhaar,
        }),
      });

      const data = await readResponse(response);

      if (!response.ok) {
        const message =
          data?.detail?.[0]?.msg ||
          data?.detail ||
          "Verification failed. Please review the entered details.";
        throw new Error(message);
      }

      setResult(data);
      setError("");
      onRecordVerification?.({
        applicantName: "Verified applicant",
        pan: data.pan,
        aadhaar: data.aadhaar,
        isVerified: Boolean(data.pan_verified && data.aadhaar_verified),
      });
    } catch (submitError) {
      if (submitError.name === "AbortError") {
        setError("Request timed out. Make sure the backend is running, then try again.");
      } else {
        setError(
          submitError.message ||
            "Unable to reach the backend. Make sure the FastAPI server is running."
        );
      }
    } finally {
      window.clearTimeout(timeoutId);
      controllerRef.current = null;
      setIsSubmitting(false);
    }
  };

  const isVerified = Boolean(result?.pan_verified && result?.aadhaar_verified);

  return (
    <section className="studio-grid">
      <article className="studio-card input-card">
        <div className="card-topline">
          <div>
            <span className="panel-kicker">Input console</span>
            <h3>Applicant credentials</h3>
          </div>
          <div className={`mini-status status-${health}`}>
            <span className="status-dot" />
            {health === "checking" ? "Checking API" : `API ${health}`}
          </div>
        </div>

        <form className="verification-form" onSubmit={handleSubmit}>
          <label className="input-block">
            <span>PAN</span>
            <input
              name="pan"
              value={form.pan}
              onChange={handleChange}
              placeholder="ABCDE1234F"
              autoComplete="off"
              required
            />
            <small>Uppercase PAN format is auto-maintained while typing.</small>
          </label>

          <label className="input-block">
            <span>Aadhaar</span>
            <input
              name="aadhaar"
              value={form.aadhaar}
              onChange={handleChange}
              placeholder="1234 1234 1234"
              autoComplete="off"
              required
            />
            <small>Spaces are allowed here. The backend normalizes digits.</small>
          </label>

          <div className="action-row">
            <button className="primary-button" type="submit" disabled={isSubmitting}>
              {isSubmitting ? "Verifying..." : "Run Verification"}
            </button>
            <button className="secondary-button" type="button" onClick={applyDemoData}>
              Use Demo Data
            </button>
            <button className="ghost-button" type="button" onClick={clearForm}>
              Reset
            </button>
          </div>
        </form>

        {error ? <div className="feedback-banner error-banner">{error}</div> : null}

        <div className="quick-notes">
          <article>
            <span className="note-label">Checks included</span>
            <strong>PAN, Aadhaar, ITR, blacklist</strong>
          </article>
          <article>
            <span className="note-label">Response pattern</span>
            <strong>Structured decision summary</strong>
          </article>
        </div>
      </article>

      <article className="studio-card results-card">
        <div className="card-topline">
          <div>
            <span className="panel-kicker">Output desk</span>
            <h3>Verification snapshot</h3>
          </div>
          <div className={`decision-pill ${isVerified ? "decision-pass" : "decision-pending"}`}>
            {result ? (isVerified ? "Matched" : "Review") : "Awaiting input"}
          </div>
        </div>

        {result ? (
          <div className="results-layout">
            <section className="decision-banner">
              <div>
                <span className="note-label">Applicant PAN</span>
                <h4>{result.pan}</h4>
              </div>
              <p>
                {isVerified
                  ? "Identity checks passed cleanly and the applicant can move to the next review stage."
                  : "One or more checks need attention before moving this profile forward."}
              </p>
            </section>

            <div className="signal-grid">
              <article className="signal-card">
                <span className="signal-label">PAN match</span>
                <strong>{result.pan_verified ? "Verified" : "Invalid"}</strong>
              </article>
              <article className="signal-card">
                <span className="signal-label">Aadhaar match</span>
                <strong>{result.aadhaar_verified ? "Verified" : "Invalid"}</strong>
              </article>
              <article className="signal-card">
                <span className="signal-label">ITR status</span>
                <strong>{result.itr_status}</strong>
              </article>
              <article className="signal-card">
                <span className="signal-label">Blacklist flag</span>
                <strong>{result.is_blacklisted ? "Flagged" : "Clear"}</strong>
              </article>
            </div>

            <div className="detail-sheet">
              <div className="detail-row">
                <span>Normalized Aadhaar</span>
                <strong>{result.aadhaar}</strong>
              </div>
              <div className="detail-row">
                <span>ITR linked PAN</span>
                <strong>{result.itr_pan}</strong>
              </div>
              <div className="detail-row">
                <span>Blacklist PAN</span>
                <strong>{result.blacklist_pan}</strong>
              </div>
            </div>
          </div>
        ) : (
          <div className="empty-panel">
            <div className="empty-marker">01</div>
            <h4>Ready for a verification run</h4>
            <p>
              Enter the applicant details or use the demo button to preview the updated
              review experience.
            </p>
          </div>
        )}
      </article>
    </section>
  );
}

export default LoanForm;
