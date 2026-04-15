# AI-Driven Beneficiary Intelligence and Fraud Detection Assistant

## Project Guiding Reference (Hackathon 2025)

## 1. Purpose of This Document

This document is the single guiding reference for the current hackathon build.

Primary objective:
- Build an officer-facing, measurable fraud and anomaly detection system for welfare applications.

Hackathon framing:
- This is not a full production rollout.
- Success is measured by impact signals: better triage quality, faster review time, and clearer fraud explanations.

## 2. Scope Decision (Locked)

In scope now:
- Officer interface only.
- End-to-end fraud and anomaly detection engine.
- Agentic pipeline that creates a risk/fraud profile from multi-source evidence.

Out of scope for current sprint:
- Citizen-facing interface.
- Full real-time integrations with every government system.

Planned expansion:
- Citizen self-check eligibility interface as a post-hackathon extension.

## 3. Problem Statement (Officer Workflow)

Current bottlenecks in welfare verification:
- Officers review too many applications manually with equal effort.
- Data is fragmented across documents, voice statements, and siloed records.
- Duplicate or synthetic identities are hard to spot at scale.
- Risk reasoning is often implicit, not auditable.

Target outcome:
- Every case gets a risk score and evidence-backed explanation.
- Officers review highest-risk cases first.
- System produces recommended action with confidence and rationale.

## 4. North-Star Impact Metrics (Hackathon)

We will evaluate impact, not feature count.

Primary metrics:
- Fraud catch lift: increase in high-risk true positives vs baseline rule-only checks.
- Review efficiency: reduction in average officer review time per application.
- Explainability quality: percentage of flagged cases with source-cited reasons.
- Priority precision: top-risk bucket precision at K (for example, precision@20).

Secondary metrics:
- False-positive rate for low-risk genuine beneficiaries.
- Identity collision detection rate (duplicate/synthetic profile detection).
- PII safety compliance: 0 unmasked sensitive fields in model prompts.

## 5. Officer-First Product Flow

1. Officer ingests case (voice, document, or digital form).
2. System extracts and normalizes fields to canonical schema.
3. Identity graph links person/entity across datasets.
4. Detection engine generates risk score + anomaly factors.
5. Explainer agent generates plain-language case summary.
6. Officer decides: Approve / Manual Review / Reject / Escalate.
7. Decision + outcome feeds learning loop.

## 6. Fraud/Anomaly Engine (Core)

## 6.1 Engine Design Principles

- Evidence-first: every risk point must map to verifiable source evidence.
- Hybrid scoring: combine rules, graph anomalies, and ML signals.
- Explainable by default: risk output must include contributing factors.
- Privacy-first: no raw PII in LLM prompts.
- Human-in-the-loop: high-impact actions always officer-confirmed.

## 6.2 Canonical Risk Profile (per beneficiary/case)

Each case outputs:
- `case_id`
- `beneficiary_entity_id`
- `risk_score` (0-100)
- `risk_band` (`low`, `medium`, `high`, `critical`)
- `factors[]`: weighted signals with source references
- `anomalies[]`: structured anomaly findings
- `network_flags[]`: ring/shared-attribute indicators
- `recommended_action`
- `confidence`
- `explanation_text`
- `explanation_audio_url` (optional)

## 6.3 Detection Layers

Layer A: Deterministic Rules
- ID mismatch across submitted records.
- DOB/name/address inconsistency beyond threshold.
- Income declaration vs banking/income signals mismatch.
- Duplicate application across schemes/time window.

Layer B: Entity Resolution and Graph Intelligence
- Beneficiary identity graph linking by masked keys and fuzzy features.
- Shared attributes graph: mobile, bank account, address, device, introducer.
- Ring detection: dense connected components with unusual claim patterns.

Layer C: Statistical/ML Anomaly Signals
- Outlier detection for income-benefit mismatch.
- Temporal anomalies (sudden surge in linked applications).
- Geo anomalies (application cluster behavior outside expected baseline).
- Similarity anomalies using embeddings over prior verified fraud cases.

Layer D: LLM-Assisted Reasoning
- Sarvam-105B synthesizes discrepancy evidence into officer-readable rationale.
- Must remain grounded to extracted facts and retrieved evidence only.

## 7. Agentic Architecture (Focused)

## 7.1 Core Agents

1. Intake and Normalization Agent
- Inputs: voice, form data, uploaded docs, text.
- Uses: Saaras v3, Sarvam Vision, Mayura.
- Output: canonical structured case payload with confidence.

2. Identity Resolution Agent
- Builds entity links across records using deterministic + fuzzy matching.
- Produces beneficiary graph node and linkage confidence.

3. Cross-Verification Agent
- Compares declared values vs extracted values vs external signals.
- Emits discrepancy ledger with severity.

4. Anomaly Detection Agent
- Runs rule engine + graph checks + ML detectors.
- Emits anomalies with per-signal score contribution.

5. Risk Scoring Agent
- Aggregates weighted signals into final score and band.
- Applies guardrails for false-positive control.

6. Fraud Prevention Agent
- Chooses intervention policy by risk level.
- Suggests: auto-approve, manual review, hard block, or escalate.

7. Explainer Agent
- Generates plain-language summary in officer language.
- Includes evidence pointers and action recommendation.

8. PII Guard Agent
- Masks/redacts PII before model calls.
- Enforces role-gated reveal policy and audit logging.

## 7.2 Agent Orchestration Strategy

Recommended orchestration:
- LangGraph DAG with explicit state schema.
- Hard gates between extraction, verification, and scoring.
- Retry policy per agent with bounded backoff.
- Dead-letter queue for failed external lookups.

Critical control points:
- If extraction confidence is low, force manual checkpoint.
- If source connectors are unavailable, score with uncertainty penalty.
- If high-risk and low-confidence conflict exists, escalate instead of auto-reject.

## 8. Data Sources and Enrichment Strategy

The following are candidate intelligence sources for stronger fraud profiling.

## 8.1 Core Sources Mentioned (to include)

- Aadhaar-linked service/application history (where legally and technically available).
- PAN / income tax indicators (AIS-like summaries), credit signals.
- Ration/PDS state records.
- Voter registry indicators (ECI-linked checks where permissible).
- Police/crime reference flags (policy- and role-limited usage).
- Central blacklist/watchlist repository.

## 8.2 Additional High-Value Sources (new ideas)

- Scheme-level historical decision trails (reason codes for prior rejection).
- Device and channel telemetry (repeated device-account patterns).
- Bank account velocity signals (many beneficiaries mapped to one account).
- Mobile number reuse patterns across unrelated identities.
- Household-level duplication (same household claiming mutually exclusive benefits).
- Geo-consistency checks (declared residence vs recurring transaction geography).
- Employer and occupation plausibility checks for income claims.
- Death registry and migration indicators for ghost-beneficiary detection.
- Grievance and appeal history signals (pattern of repeated fraudulent attempts).
- Agent/facilitator network indicators (single operator linked to abnormal rejection/fraud rates).

## 8.3 Source Reliability Weighting

Every source should have:
- `source_trust_score`
- `last_updated_at`
- `access_mode` (`live`, `batch`, `cached`, `synthetic`)
- `evidence_uri`

Risk scoring must discount stale or weak sources.

## 9. Fraud Pattern Library (Initial)

Seed fraud pattern categories:
- Identity duplication: one person, many variants.
- Synthetic household construction.
- Income suppression or mismatch.
- Shared bank account ring.
- Shared mobile/device ring.
- Forged or tampered document patterns.
- Scheme hopping after repeated rejection.
- Ghost beneficiaries (inactive/deceased/migrated signals).

Each pattern should define:
- Detection logic
- Required evidence fields
- Risk contribution range
- Recommended officer action

## 10. Fraud Prevention Strategy (Not Just Detection)

Risk band actions:
- Low (0-24): fast-track with spot checks.
- Medium (25-49): standard review + additional document request.
- High (50-74): mandatory manual verification and supervisor sign-off.
- Critical (75-100): hold disbursement, escalate to fraud cell, preserve evidence packet.

Preventive controls:
- Pre-disbursement hold for critical risk.
- Mandatory second-factor verification for high-risk identity collisions.
- Auto-generated evidence packet for legal/audit trail.
- Ring-level monitoring and periodic watchlist updates.

## 11. Privacy, Security, and Compliance Baseline

Mandatory controls:
- PII masking at ingestion.
- Vault-backed storage for sensitive fields.
- Role-based reveal (Operator, Supervisor, Admin, Auditor).
- Prompt redaction: no raw Aadhaar/PAN/account in LLM input.
- Immutable audit log for all reveal/decrypt events.

Hackathon compliance goal:
- Demonstrate architecture and controls, even if some connectors use synthetic/mock data.

## 12. Hackathon Build Plan (Impact-First)

## Sprint A: Detection MVP
- Canonical schema + ingestion pipeline.
- Rule engine + discrepancy ledger.
- Basic risk scoring with explainable factors.

## Sprint B: Anomaly Intelligence
- Identity graph and ring heuristics.
- Embedding similarity over prior cases.
- Risk band actions and escalation paths.

## Sprint C: Officer Decision Intelligence
- Explainer outputs in officer language.
- Risk dashboard with evidence drill-down.
- Outcome feedback capture for learning loop.

## Sprint D: Demo and Evaluation
- 50-100 synthetic cases with ground truth.
- Baseline comparison (manual/rule-only vs agentic engine).
- Impact report with the North-Star metrics.

## 13. Demo Scenarios (Must Show)

1. Clean beneficiary case auto-routed to low risk.
2. Duplicate identity ring detected through shared attributes.
3. Income mismatch flagged using multi-source verification.
4. High-risk case with evidence-backed explanation and supervisor escalation.

## 14. Post-Hackathon Expansion

- Citizen-facing interface for eligibility guidance and status support.
- Deeper real-time integrations (DigiLocker, department APIs, grievance systems).
- Advanced graph ML for organized fraud networks.
- Federated learning across departments without raw data sharing.

## 15. Definition of Done (Hackathon)

The project is considered successful when:
- Officer can process a case end-to-end in the interface.
- Every case receives risk score + evidence + recommended action.
- At least one network/ring anomaly type is demonstrated live.
- Explanations are multilingual and understandable by non-technical officials.
- Impact metrics are reported against a baseline.
