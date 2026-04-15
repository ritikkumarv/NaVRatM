import { startTransition, useEffect, useState } from "react";
import AnalyticsBoard from "./AnalyticsBoard";
import ApplicationWorkbench from "./ApplicationWorkbench";
import ApplicantHistory from "./ApplicantHistory";
import LoanForm from "./LoanForm";
import "./styles.css";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "";

const navigationItems = [
  { id: "verify", label: "Verify" },
  { id: "apply", label: "Apply" },
  { id: "analytics", label: "Analytics" },
  { id: "history", label: "History" },
];

const seedHistory = [
  {
    id: "APP-301",
    applicantName: "Riya Sharma",
    pan: "ABCPR1234L",
    aadhaar: "452198761245",
    type: "verification",
    status: "verified",
    risk: "low",
    amount: 450000,
    updatedAt: "2m ago",
    summary: "Identity checks cleared and applicant is ready for underwriting.",
  },
  {
    id: "APP-274",
    applicantName: "Arjun Mehta",
    pan: "FGHTM6789Q",
    aadhaar: "764512309876",
    type: "application",
    status: "review",
    risk: "medium",
    amount: 780000,
    updatedAt: "18m ago",
    summary: "Application queued for manual review due to partial income mismatch.",
  },
  {
    id: "APP-198",
    applicantName: "Sana Iqbal",
    pan: "PLMNI4321B",
    aadhaar: "808012341234",
    type: "verification",
    status: "flagged",
    risk: "high",
    amount: 920000,
    updatedAt: "42m ago",
    summary: "Blacklisting or identity mismatch requires escalation before approval.",
  },
];

function App() {
  const [health, setHealth] = useState("checking");
  const [activeView, setActiveView] = useState("verify");
  const [history, setHistory] = useState(seedHistory);

  useEffect(() => {
    const controller = new AbortController();
    const timeoutId = window.setTimeout(() => controller.abort(), 3000);

    const checkHealth = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/health`, {
          signal: controller.signal,
        });

        if (!response.ok) {
          throw new Error("Backend unavailable");
        }

        setHealth("online");
      } catch (error) {
        setHealth("offline");
      } finally {
        window.clearTimeout(timeoutId);
      }
    };

    checkHealth();

    return () => {
      window.clearTimeout(timeoutId);
      controller.abort();
    };
  }, []);

  const registerVerification = (payload) => {
    const record = {
      id: `APP-${Date.now().toString().slice(-3)}`,
      applicantName: payload.applicantName || "Walk-in applicant",
      pan: payload.pan,
      aadhaar: payload.aadhaar,
      type: "verification",
      status: payload.isVerified ? "verified" : "review",
      risk: payload.isVerified ? "low" : "medium",
      amount: payload.amount || 600000,
      updatedAt: "Just now",
      summary: payload.isVerified
        ? "Verification passed and the profile can move to the next credit step."
        : "Verification completed but still needs manual review before approval.",
    };

    setHistory((current) => [record, ...current].slice(0, 8));
  };

  const registerApplication = (payload) => {
    const record = {
      id: `APP-${Date.now().toString().slice(-3)}`,
      applicantName: payload.applicantName,
      pan: payload.pan,
      aadhaar: payload.aadhaar,
      type: "application",
      status: "submitted",
      risk: payload.monthlyIncome >= 90000 ? "low" : "medium",
      amount: payload.loanAmount,
      updatedAt: "Just now",
      summary: `${payload.purpose} request submitted for screening and assignment.`,
    };

    setHistory((current) => [record, ...current].slice(0, 8));
    startTransition(() => {
      setActiveView("history");
    });
  };

  const renderActiveView = () => {
    if (activeView === "apply") {
      return <ApplicationWorkbench health={health} onSubmitApplication={registerApplication} />;
    }

    if (activeView === "analytics") {
      return <AnalyticsBoard health={health} history={history} />;
    }

    if (activeView === "history") {
      return <ApplicantHistory health={health} history={history} />;
    }

    return <LoanForm health={health} onRecordVerification={registerVerification} />;
  };

  return (
    <div className="app-shell">
      <div className="canvas-glow canvas-glow-one" />
      <div className="canvas-glow canvas-glow-two" />

      <main className="dashboard-shell">
        <header className="topbar">
          <div className="topbar-main">
            <span className="product-kicker">LoanOps Studio</span>
            <h1>Modern loan review workspace for verification, intake, and tracking.</h1>
            <p className="topbar-subtitle">
              Switch between identity checks, application entry, analytics, and live
              history without leaving the same fast frontend.
            </p>
          </div>

          <div className="topbar-meta">
            <div className={`status-chip status-${health}`}>
              <span className="status-dot" />
              Backend {health === "checking" ? "checking" : health}
            </div>
            <a className="docs-link" href={`${API_BASE_URL}/docs`} target="_blank" rel="noreferrer">
              Open API Docs
            </a>
          </div>
        </header>

        <section className="command-bar">
          <nav className="segmented-nav" aria-label="Workspace sections">
            {navigationItems.map((item) => (
              <button
                key={item.id}
                className={item.id === activeView ? "nav-chip active" : "nav-chip"}
                type="button"
                onClick={() => {
                  startTransition(() => {
                    setActiveView(item.id);
                  });
                }}
              >
                {item.label}
              </button>
            ))}
          </nav>

          <div className="command-summary">
            <article>
              <span className="summary-label">Open cases</span>
              <strong>{history.length}</strong>
            </article>
            <article>
              <span className="summary-label">Verified</span>
              <strong>{history.filter((item) => item.status === "verified").length}</strong>
            </article>
            <article>
              <span className="summary-label">Needs review</span>
              <strong>
                {
                  history.filter((item) =>
                    ["review", "flagged"].includes(item.status)
                  ).length
                }
              </strong>
            </article>
          </div>
        </section>

        {renderActiveView()}
      </main>
    </div>
  );
}

export default App;
