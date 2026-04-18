const pptxgen = require("pptxgenjs");
const React = require("react");
const ReactDOMServer = require("react-dom/server");
const sharp = require("sharp");

// ── Icon helper ──
const {
  FaShieldAlt, FaExclamationTriangle, FaBrain, FaMicrophone,
  FaSearch, FaFileAlt, FaDatabase, FaNetworkWired, FaChartBar,
  FaUserShield, FaCheckCircle, FaCogs, FaLanguage, FaArrowRight,
  FaLock, FaEye, FaUsers, FaProjectDiagram, FaChartLine,
  FaBalanceScale, FaRobot, FaClipboardCheck, FaBullseye
} = require("react-icons/fa");

function renderIconSvg(IconComponent, color = "#000000", size = 256) {
  return ReactDOMServer.renderToStaticMarkup(
    React.createElement(IconComponent, { color, size: String(size) })
  );
}

async function iconToBase64Png(IconComponent, color, size = 256) {
  const svg = renderIconSvg(IconComponent, color, size);
  const pngBuffer = await sharp(Buffer.from(svg)).png().toBuffer();
  return "image/png;base64," + pngBuffer.toString("base64");
}

// ── Color palette: "Saffron Authority" — India gov feel ──
const C = {
  saffron:    "FF9933",
  saffronDim: "CC7A29",
  navy:       "0D1B2A",
  navyMid:    "1B2838",
  navyLight:  "243447",
  white:      "FFFFFF",
  offWhite:   "F0F4F8",
  lightGray:  "E2E8F0",
  midGray:    "94A3B8",
  darkGray:   "334155",
  green:      "22C55E",
  red:        "EF4444",
  amber:      "F59E0B",
  teal:       "0D9488",
  blue:       "3B82F6",
  accent:     "FF9933",
};

const FONT_TITLE = "Trebuchet MS";
const FONT_BODY = "Calibri";

// Shadow factory (fresh object each time)
const mkShadow = () => ({ type: "outer", color: "000000", blur: 4, offset: 2, angle: 135, opacity: 0.18 });

async function main() {
  const pres = new pptxgen();
  pres.layout = "LAYOUT_16x9";
  pres.author = "Team NaVRatM";
  pres.title = "NaVRatM — AI-Driven Beneficiary Intelligence & Fraud Detection";

  // Pre-render icons
  const icons = {
    shield:     await iconToBase64Png(FaShieldAlt, `#${C.saffron}`),
    warning:    await iconToBase64Png(FaExclamationTriangle, `#${C.amber}`),
    brain:      await iconToBase64Png(FaBrain, `#${C.saffron}`),
    mic:        await iconToBase64Png(FaMicrophone, `#${C.teal}`),
    search:     await iconToBase64Png(FaSearch, `#${C.blue}`),
    file:       await iconToBase64Png(FaFileAlt, `#${C.saffron}`),
    db:         await iconToBase64Png(FaDatabase, `#${C.teal}`),
    network:    await iconToBase64Png(FaNetworkWired, `#${C.red}`),
    chart:      await iconToBase64Png(FaChartBar, `#${C.saffron}`),
    userShield: await iconToBase64Png(FaUserShield, `#${C.green}`),
    check:      await iconToBase64Png(FaCheckCircle, `#${C.green}`),
    cogs:       await iconToBase64Png(FaCogs, `#${C.midGray}`),
    lang:       await iconToBase64Png(FaLanguage, `#${C.teal}`),
    arrow:      await iconToBase64Png(FaArrowRight, `#${C.saffron}`),
    lock:       await iconToBase64Png(FaLock, `#${C.red}`),
    eye:        await iconToBase64Png(FaEye, `#${C.blue}`),
    users:      await iconToBase64Png(FaUsers, `#${C.amber}`),
    project:    await iconToBase64Png(FaProjectDiagram, `#${C.saffron}`),
    line:       await iconToBase64Png(FaChartLine, `#${C.green}`),
    balance:    await iconToBase64Png(FaBalanceScale, `#${C.saffron}`),
    robot:      await iconToBase64Png(FaRobot, `#${C.teal}`),
    clipboard:  await iconToBase64Png(FaClipboardCheck, `#${C.green}`),
    target:     await iconToBase64Png(FaBullseye, `#${C.red}`),
  };

  // ════════════════════════════════════════════════════════════════
  // SLIDE 1 — TITLE
  // ════════════════════════════════════════════════════════════════
  {
    const s = pres.addSlide();
    s.background = { color: C.navy };
    // Top saffron accent bar
    s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.06, fill: { color: C.saffron } });
    // Shield icon
    s.addImage({ data: icons.shield, x: 4.4, y: 0.9, w: 1.2, h: 1.2 });
    // Title
    s.addText("NaVRatM", {
      x: 0.5, y: 2.2, w: 9, h: 0.9,
      fontSize: 48, fontFace: FONT_TITLE, color: C.saffron,
      bold: true, align: "center", margin: 0,
    });
    // Subtitle
    s.addText("AI-Driven Beneficiary Intelligence & Fraud Detection", {
      x: 1, y: 3.1, w: 8, h: 0.55,
      fontSize: 20, fontFace: FONT_BODY, color: C.lightGray,
      align: "center", margin: 0,
    });
    // Tagline
    s.addText("Protecting India's welfare ecosystem with evidence-based intelligence", {
      x: 1.5, y: 3.75, w: 7, h: 0.4,
      fontSize: 13, fontFace: FONT_BODY, color: C.midGray,
      italic: true, align: "center", margin: 0,
    });
    // Bottom bar
    s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 5.3, w: 10, h: 0.325, fill: { color: C.navyMid } });
    s.addText("Hackathon 2026  |  Powered by Sarvam AI", {
      x: 0.5, y: 5.3, w: 9, h: 0.325,
      fontSize: 11, fontFace: FONT_BODY, color: C.midGray,
      align: "center", margin: 0,
    });
  }

  // ════════════════════════════════════════════════════════════════
  // SLIDE 2 — THE PROBLEM
  // ════════════════════════════════════════════════════════════════
  {
    const s = pres.addSlide();
    s.background = { color: C.offWhite };
    s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.06, fill: { color: C.saffron } });

    s.addText("The Problem", {
      x: 0.6, y: 0.3, w: 8, h: 0.6,
      fontSize: 32, fontFace: FONT_TITLE, color: C.navy, bold: true, margin: 0,
    });
    s.addText("India's welfare disbursement leaks ₹1+ lakh crore annually to fraud, duplication, and ghost beneficiaries.", {
      x: 0.6, y: 0.9, w: 8.5, h: 0.45,
      fontSize: 13, fontFace: FONT_BODY, color: C.darkGray, margin: 0,
    });

    // 4 pain-point cards in a 2x2 grid
    const problems = [
      { icon: icons.users,   title: "Manual Overload",     desc: "Officers review every application with equal effort — no triage, no prioritisation." },
      { icon: icons.file,    title: "Fragmented Data",     desc: "Documents, voice statements, and siloed records are never cross-verified automatically." },
      { icon: icons.network, title: "Invisible Fraud Rings", desc: "Duplicate/synthetic identities and shared-account networks go undetected at scale." },
      { icon: icons.eye,     title: "No Audit Trail",      desc: "Risk reasoning is implicit — decisions can't be justified or reviewed objectively." },
    ];

    const cardW = 4.1, cardH = 1.6, gapX = 0.5, gapY = 0.35;
    const startX = 0.6, startY = 1.55;

    problems.forEach((p, i) => {
      const col = i % 2, row = Math.floor(i / 2);
      const cx = startX + col * (cardW + gapX);
      const cy = startY + row * (cardH + gapY);

      s.addShape(pres.shapes.RECTANGLE, {
        x: cx, y: cy, w: cardW, h: cardH,
        fill: { color: C.white }, shadow: mkShadow(),
      });
      // Left accent bar
      s.addShape(pres.shapes.RECTANGLE, {
        x: cx, y: cy, w: 0.06, h: cardH,
        fill: { color: C.red },
      });
      s.addImage({ data: p.icon, x: cx + 0.25, y: cy + 0.3, w: 0.42, h: 0.42 });
      s.addText(p.title, {
        x: cx + 0.8, y: cy + 0.2, w: cardW - 1, h: 0.35,
        fontSize: 14, fontFace: FONT_TITLE, color: C.navy, bold: true, margin: 0,
      });
      s.addText(p.desc, {
        x: cx + 0.8, y: cy + 0.6, w: cardW - 1.1, h: 0.85,
        fontSize: 11, fontFace: FONT_BODY, color: C.darkGray, margin: 0,
      });
    });
  }

  // ════════════════════════════════════════════════════════════════
  // SLIDE 3 — OUR SOLUTION
  // ════════════════════════════════════════════════════════════════
  {
    const s = pres.addSlide();
    s.background = { color: C.navy };
    s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.06, fill: { color: C.saffron } });

    s.addText("Our Solution", {
      x: 0.6, y: 0.3, w: 8, h: 0.6,
      fontSize: 32, fontFace: FONT_TITLE, color: C.saffron, bold: true, margin: 0,
    });
    s.addText("An AI-powered officer assistant that ingests, verifies, scores, and explains every welfare application.", {
      x: 0.6, y: 0.85, w: 8.5, h: 0.45,
      fontSize: 13, fontFace: FONT_BODY, color: C.lightGray, margin: 0,
    });

    // 3 Key pillars
    const pillars = [
      { icon: icons.brain,      title: "Intelligent Detection",  desc: "Multi-layer fraud engine: deterministic rules, graph analysis, anomaly patterns, and LLM-assisted reasoning." },
      { icon: icons.lang,       title: "Voice-First, Multilingual", desc: "Sarvam AI powers STT, TTS, translation across 12+ Indian languages — officers speak, system understands." },
      { icon: icons.userShield, title: "Explainable & Auditable", desc: "Every risk score comes with evidence-backed explanation, source citations, and recommended action." },
    ];

    const pillarW = 2.8, pillarH = 2.7, pillarGap = 0.35;
    const pStartX = 0.6;
    const pStartY = 1.55;

    pillars.forEach((p, i) => {
      const px = pStartX + i * (pillarW + pillarGap);
      s.addShape(pres.shapes.RECTANGLE, {
        x: px, y: pStartY, w: pillarW, h: pillarH,
        fill: { color: C.navyMid }, shadow: mkShadow(),
      });
      // Top accent
      s.addShape(pres.shapes.RECTANGLE, {
        x: px, y: pStartY, w: pillarW, h: 0.06,
        fill: { color: C.saffron },
      });
      s.addImage({ data: p.icon, x: px + (pillarW - 0.55) / 2, y: pStartY + 0.3, w: 0.55, h: 0.55 });
      s.addText(p.title, {
        x: px + 0.2, y: pStartY + 1.0, w: pillarW - 0.4, h: 0.4,
        fontSize: 14, fontFace: FONT_TITLE, color: C.saffron, bold: true, align: "center", margin: 0,
      });
      s.addText(p.desc, {
        x: px + 0.2, y: pStartY + 1.45, w: pillarW - 0.4, h: 1.2,
        fontSize: 11, fontFace: FONT_BODY, color: C.lightGray, align: "center", margin: 0,
      });
    });
  }

  // ════════════════════════════════════════════════════════════════
  // SLIDE 4 — SYSTEM ARCHITECTURE (Pipeline)
  // ════════════════════════════════════════════════════════════════
  {
    const s = pres.addSlide();
    s.background = { color: C.offWhite };
    s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.06, fill: { color: C.saffron } });

    s.addText("System Architecture", {
      x: 0.6, y: 0.25, w: 8, h: 0.55,
      fontSize: 30, fontFace: FONT_TITLE, color: C.navy, bold: true, margin: 0,
    });
    s.addText("End-to-end pipeline: Ingest → Extract → Verify → Detect → Score → Explain → Decide", {
      x: 0.6, y: 0.75, w: 9, h: 0.35,
      fontSize: 12, fontFace: FONT_BODY, color: C.darkGray, italic: true, margin: 0,
    });

    const stages = [
      { icon: icons.mic,    label: "Intake",      desc: "Voice / Doc / Form" },
      { icon: icons.file,   label: "Extract",     desc: "OCR + Sarvam Vision" },
      { icon: icons.search, label: "Verify",      desc: "Cross-verification" },
      { icon: icons.db,     label: "Enrich",      desc: "9 data connectors" },
      { icon: icons.target, label: "Detect",      desc: "6 fraud patterns" },
      { icon: icons.chart,  label: "Score",       desc: "Weighted risk (0-100)" },
      { icon: icons.brain,  label: "Explain",     desc: "Sarvam-105B LLM" },
      { icon: icons.clipboard, label: "Decide",   desc: "Officer action" },
    ];

    const stageW = 1.0, stageH = 1.85, stageGap = 0.14;
    const sStartX = 0.45, sStartY = 1.35;

    stages.forEach((st, i) => {
      const sx = sStartX + i * (stageW + stageGap);
      // Card
      s.addShape(pres.shapes.RECTANGLE, {
        x: sx, y: sStartY, w: stageW, h: stageH,
        fill: { color: C.white }, shadow: mkShadow(),
      });
      // Top accent
      s.addShape(pres.shapes.RECTANGLE, {
        x: sx, y: sStartY, w: stageW, h: 0.05,
        fill: { color: C.saffron },
      });
      // Icon
      s.addImage({ data: st.icon, x: sx + (stageW - 0.4) / 2, y: sStartY + 0.2, w: 0.4, h: 0.4 });
      // Step number
      s.addText(String(i + 1), {
        x: sx + 0.04, y: sStartY + 0.08, w: 0.25, h: 0.25,
        fontSize: 9, fontFace: FONT_BODY, color: C.white, bold: true,
        align: "center", valign: "middle", margin: 0,
      });
      s.addShape(pres.shapes.OVAL, {
        x: sx + 0.04, y: sStartY + 0.08, w: 0.22, h: 0.22,
        fill: { color: C.saffron },
      });
      s.addText(String(i + 1), {
        x: sx + 0.04, y: sStartY + 0.08, w: 0.22, h: 0.22,
        fontSize: 8, fontFace: FONT_BODY, color: C.white, bold: true,
        align: "center", valign: "middle", margin: 0,
      });
      // Label
      s.addText(st.label, {
        x: sx, y: sStartY + 0.72, w: stageW, h: 0.3,
        fontSize: 11, fontFace: FONT_TITLE, color: C.navy, bold: true, align: "center", margin: 0,
      });
      // Desc
      s.addText(st.desc, {
        x: sx + 0.05, y: sStartY + 1.05, w: stageW - 0.1, h: 0.7,
        fontSize: 9, fontFace: FONT_BODY, color: C.darkGray, align: "center", margin: 0,
      });

      // Arrow between stages
      if (i < stages.length - 1) {
        s.addImage({ data: icons.arrow, x: sx + stageW + 0.01, y: sStartY + 0.7, w: 0.14, h: 0.14 });
      }
    });

    // Tech stack bar at bottom
    s.addShape(pres.shapes.RECTANGLE, {
      x: 0.45, y: 3.55, w: 9.1, h: 1.7, fill: { color: C.navy },
      shadow: mkShadow(),
    });
    s.addText("Tech Stack", {
      x: 0.7, y: 3.65, w: 3, h: 0.35,
      fontSize: 13, fontFace: FONT_TITLE, color: C.saffron, bold: true, margin: 0,
    });
    const techItems = [
      ["Backend", "FastAPI + Uvicorn (async)"],
      ["AI Engine", "Sarvam-30B / 105B LLM, Saarika STT, Bulbul TTS, Mayura Translate"],
      ["Database", "SQLAlchemy + SQLite (async)"],
      ["Matching", "RapidFuzz (fuzzy string matching)"],
      ["Frontend", "Vanilla JS SPA — Dark-themed officer dashboard"],
      ["Privacy", "Regex-based PII masking at extraction time"],
    ];
    techItems.forEach((item, i) => {
      const col = i < 3 ? 0 : 1;
      const row = i % 3;
      const tx = 0.7 + col * 4.5;
      const ty = 4.05 + row * 0.38;
      s.addText([
        { text: `${item[0]}:  `, options: { bold: true, color: C.saffron, fontSize: 10, fontFace: FONT_BODY } },
        { text: item[1], options: { color: C.lightGray, fontSize: 10, fontFace: FONT_BODY } },
      ], { x: tx, y: ty, w: 4.3, h: 0.3, margin: 0 });
    });
  }

  // ════════════════════════════════════════════════════════════════
  // SLIDE 5 — DETECTION ENGINE DEEP DIVE
  // ════════════════════════════════════════════════════════════════
  {
    const s = pres.addSlide();
    s.background = { color: C.navy };
    s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.06, fill: { color: C.saffron } });

    s.addText("Detection Engine — 4 Layers", {
      x: 0.6, y: 0.25, w: 8, h: 0.55,
      fontSize: 28, fontFace: FONT_TITLE, color: C.saffron, bold: true, margin: 0,
    });

    const layers = [
      {
        letter: "A", title: "Deterministic Rules", color: C.blue,
        items: [
          "12 weighted rules (dob_mismatch: 25, blacklisted: 35, deceased: 40 …)",
          "Fuzzy name match via RapidFuzz (token_sort_ratio, threshold 85%)",
          "Income deviation check at 30% tolerance",
          "Severity multipliers: HIGH=1.0, MEDIUM=0.6, LOW=0.3",
        ]
      },
      {
        letter: "B", title: "Cross-Verification", color: C.teal,
        items: [
          "Declared vs extracted vs connector signals",
          "6 field verifiers: name, DOB, income, address, gender, phone",
          "Indian-name normalisation (Shri/Smt prefix stripping, whitespace)",
          "Discrepancy ledger with severity + match_score + evidence_uri",
        ]
      },
      {
        letter: "C", title: "Fraud Pattern Library", color: C.amber,
        items: [
          "Ghost beneficiary (no docs / empty extraction / no Aadhaar record)",
          "Duplicate identity (shared phone / bank / Aadhaar across apps)",
          "Deceased claims (death registry match + post-mortem filing)",
          "Income inflation, scheme hopping, address clustering",
        ]
      },
      {
        letter: "D", title: "LLM-Assisted Reasoning", color: C.red,
        items: [
          "Sarvam-105B synthesises evidence into officer-readable explanation",
          "Strictly grounded to extracted facts — no hallucination risk",
          "Multilingual output via Mayura translate (11 languages)",
          "PII-free prompts enforced by masking guard",
        ]
      },
    ];

    const layH = 1.05, layGap = 0.12, layStartY = 0.9;
    layers.forEach((l, i) => {
      const ly = layStartY + i * (layH + layGap);
      // Background card
      s.addShape(pres.shapes.RECTANGLE, {
        x: 0.5, y: ly, w: 9, h: layH,
        fill: { color: C.navyMid }, shadow: mkShadow(),
      });
      // Left color bar
      s.addShape(pres.shapes.RECTANGLE, {
        x: 0.5, y: ly, w: 0.06, h: layH,
        fill: { color: l.color },
      });
      // Letter badge
      s.addShape(pres.shapes.OVAL, {
        x: 0.7, y: ly + (layH - 0.4) / 2, w: 0.4, h: 0.4,
        fill: { color: l.color },
      });
      s.addText(l.letter, {
        x: 0.7, y: ly + (layH - 0.4) / 2, w: 0.4, h: 0.4,
        fontSize: 14, fontFace: FONT_TITLE, color: C.white, bold: true,
        align: "center", valign: "middle", margin: 0,
      });
      // Title
      s.addText(l.title, {
        x: 1.25, y: ly + 0.08, w: 3, h: 0.3,
        fontSize: 13, fontFace: FONT_TITLE, color: l.color, bold: true, margin: 0,
      });
      // Bullet items (2 columns)
      l.items.forEach((item, j) => {
        const col = j < 2 ? 0 : 1;
        const row = j % 2;
        s.addText([
          { text: "●  ", options: { color: l.color, fontSize: 9 } },
          { text: item, options: { color: C.lightGray, fontSize: 9, fontFace: FONT_BODY } },
        ], {
          x: 1.25 + col * 4.1, y: ly + 0.38 + row * 0.28, w: 4.0, h: 0.28, margin: 0,
        });
      });
    });
  }

  // ════════════════════════════════════════════════════════════════
  // SLIDE 6 — DATA CONNECTORS (9 enrichment sources)
  // ════════════════════════════════════════════════════════════════
  {
    const s = pres.addSlide();
    s.background = { color: C.offWhite };
    s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.06, fill: { color: C.saffron } });

    s.addText("9 Enrichment Connectors", {
      x: 0.6, y: 0.25, w: 8, h: 0.55,
      fontSize: 28, fontFace: FONT_TITLE, color: C.navy, bold: true, margin: 0,
    });
    s.addText("Parallel async fetch per application — each with trust scoring and evidence URI", {
      x: 0.6, y: 0.75, w: 9, h: 0.3,
      fontSize: 12, fontFace: FONT_BODY, color: C.darkGray, italic: true, margin: 0,
    });

    const connectors = [
      { name: "Aadhaar History", trust: "0.85", desc: "Linked schemes, application history, rejection reasons" },
      { name: "PAN / Income Tax", trust: "0.80", desc: "Income indicators, ITR status, credit signals" },
      { name: "Ration / PDS", trust: "0.75", desc: "State PDS records, ration card status" },
      { name: "Voter Registry", trust: "0.70", desc: "Electoral roll verification, constituency match" },
      { name: "Bank Velocity", trust: "0.80", desc: "Beneficiary-to-account mapping, anomaly count" },
      { name: "Death Registry", trust: "0.90", desc: "Deceased match with confidence + registry date" },
      { name: "Central Blacklist", trust: "0.95", desc: "Watchlist status, entries with severity + source agency" },
      { name: "Police Reference", trust: "0.60", desc: "Crime reference flags (policy-limited)" },
      { name: "Scheme History", trust: "0.85", desc: "Cross-scheme duplicates, hopping patterns" },
    ];

    const cW = 2.85, cH = 1.15, cGap = 0.22;
    const cStartX = 0.5, cStartY = 1.2;

    connectors.forEach((c, i) => {
      const col = i % 3, row = Math.floor(i / 3);
      const cx = cStartX + col * (cW + cGap);
      const cy = cStartY + row * (cH + cGap);

      s.addShape(pres.shapes.RECTANGLE, {
        x: cx, y: cy, w: cW, h: cH,
        fill: { color: C.white }, shadow: mkShadow(),
      });
      s.addShape(pres.shapes.RECTANGLE, {
        x: cx, y: cy, w: cW, h: 0.04,
        fill: { color: C.teal },
      });
      s.addText(c.name, {
        x: cx + 0.15, y: cy + 0.12, w: cW - 0.3, h: 0.28,
        fontSize: 11, fontFace: FONT_TITLE, color: C.navy, bold: true, margin: 0,
      });
      s.addText(`Trust: ${c.trust}`, {
        x: cx + cW - 0.85, y: cy + 0.12, w: 0.7, h: 0.25,
        fontSize: 8, fontFace: FONT_BODY, color: C.teal, bold: true, align: "right", margin: 0,
      });
      s.addText(c.desc, {
        x: cx + 0.15, y: cy + 0.45, w: cW - 0.3, h: 0.6,
        fontSize: 9, fontFace: FONT_BODY, color: C.darkGray, margin: 0,
      });
    });
  }

  // ════════════════════════════════════════════════════════════════
  // SLIDE 7 — RISK SCORING MODEL
  // ════════════════════════════════════════════════════════════════
  {
    const s = pres.addSlide();
    s.background = { color: C.navy };
    s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.06, fill: { color: C.saffron } });

    s.addText("Risk Scoring Model", {
      x: 0.6, y: 0.25, w: 8, h: 0.55,
      fontSize: 28, fontFace: FONT_TITLE, color: C.saffron, bold: true, margin: 0,
    });

    // Left side — rule weights table
    s.addText("Weighted Rule Engine", {
      x: 0.6, y: 0.9, w: 4.5, h: 0.3,
      fontSize: 14, fontFace: FONT_TITLE, color: C.lightGray, bold: true, margin: 0,
    });

    const rules = [
      ["Deceased match", "40"],
      ["Blacklisted", "35"],
      ["Duplicate detected", "30"],
      ["DOB mismatch", "25"],
      ["Bank velocity anomaly", "25"],
      ["Income deviation", "20"],
      ["Name mismatch", "20"],
      ["Scheme hopping", "20"],
      ["Missing documents", "15"],
      ["Address mismatch", "10"],
      ["Gender mismatch", "10"],
      ["Phone mismatch", "5"],
    ];

    const tableRows = [
      [
        { text: "RULE", options: { bold: true, color: C.navy, fontSize: 9, fontFace: FONT_BODY, fill: { color: C.saffron } } },
        { text: "WEIGHT", options: { bold: true, color: C.navy, fontSize: 9, fontFace: FONT_BODY, fill: { color: C.saffron }, align: "center" } },
      ],
      ...rules.map((r, i) => [
        { text: r[0], options: { fontSize: 9, fontFace: FONT_BODY, color: C.lightGray, fill: { color: i % 2 === 0 ? C.navyLight : C.navyMid } } },
        { text: r[1], options: { fontSize: 9, fontFace: FONT_BODY, color: C.saffron, bold: true, align: "center", fill: { color: i % 2 === 0 ? C.navyLight : C.navyMid } } },
      ]),
    ];

    s.addTable(tableRows, {
      x: 0.6, y: 1.25, w: 4.3, colW: [3.2, 1.1],
      border: { pt: 0.5, color: C.navyLight },
      rowH: 0.28,
    });

    // Right side — risk bands
    s.addText("Risk Bands & Actions", {
      x: 5.3, y: 0.9, w: 4.5, h: 0.3,
      fontSize: 14, fontFace: FONT_TITLE, color: C.lightGray, bold: true, margin: 0,
    });

    const bands = [
      { band: "LOW (0-24)", color: C.green, action: "Fast-track + spot checks" },
      { band: "MEDIUM (25-49)", color: C.amber, action: "Standard review + additional docs" },
      { band: "HIGH (50-74)", color: "F97316", action: "Mandatory manual verification" },
      { band: "CRITICAL (75-100)", color: C.red, action: "Hold disbursement → fraud cell" },
    ];

    bands.forEach((b, i) => {
      const by = 1.35 + i * 0.9;
      s.addShape(pres.shapes.RECTANGLE, {
        x: 5.3, y: by, w: 4.2, h: 0.75,
        fill: { color: C.navyMid }, shadow: mkShadow(),
      });
      s.addShape(pres.shapes.RECTANGLE, {
        x: 5.3, y: by, w: 0.06, h: 0.75,
        fill: { color: b.color },
      });
      s.addText(b.band, {
        x: 5.55, y: by + 0.08, w: 3.8, h: 0.3,
        fontSize: 12, fontFace: FONT_TITLE, color: b.color, bold: true, margin: 0,
      });
      s.addText(b.action, {
        x: 5.55, y: by + 0.38, w: 3.8, h: 0.3,
        fontSize: 10, fontFace: FONT_BODY, color: C.lightGray, margin: 0,
      });
    });
  }

  // ════════════════════════════════════════════════════════════════
  // SLIDE 8 — SARVAM AI INTEGRATION
  // ════════════════════════════════════════════════════════════════
  {
    const s = pres.addSlide();
    s.background = { color: C.offWhite };
    s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.06, fill: { color: C.saffron } });

    s.addText("Sarvam AI — Full-Stack Indian Language AI", {
      x: 0.6, y: 0.25, w: 9, h: 0.55,
      fontSize: 28, fontFace: FONT_TITLE, color: C.navy, bold: true, margin: 0,
    });

    const apis = [
      {
        title: "Chat Completions", model: "sarvam-30b / sarvam-105b",
        desc: "Field extraction from docs, risk explanation generation, officer query answering",
        detail: "64K–128K context, wiki grounding, tool calling capable",
        color: C.saffron,
      },
      {
        title: "Speech-to-Text", model: "saarika:v2.5 / saaras:v3",
        desc: "Officer voice input in 12+ Indian languages, auto language detection",
        detail: "Modes: transcribe, verbatim, transliterate, code-mix",
        color: C.teal,
      },
      {
        title: "STT-Translate", model: "saaras:v2.5",
        desc: "Direct speech-to-English pipeline for LLM processing",
        detail: "Auto-detects spoken language, outputs English",
        color: C.blue,
      },
      {
        title: "Text-to-Speech", model: "bulbul:v3",
        desc: "Audio response generation for voice-first officer UX",
        detail: "37 voices, pace/pitch control, streaming capable",
        color: C.green,
      },
      {
        title: "Translation", model: "mayura:v1",
        desc: "Explanation & interface text in officer's preferred language",
        detail: "11 languages, formal/colloquial modes, numeral options",
        color: C.amber,
      },
    ];

    const apiW = 8.8, apiH = 0.78, apiGap = 0.15;
    const apiStartY = 0.95;

    apis.forEach((a, i) => {
      const ay = apiStartY + i * (apiH + apiGap);
      s.addShape(pres.shapes.RECTANGLE, {
        x: 0.6, y: ay, w: apiW, h: apiH,
        fill: { color: C.white }, shadow: mkShadow(),
      });
      s.addShape(pres.shapes.RECTANGLE, {
        x: 0.6, y: ay, w: 0.06, h: apiH,
        fill: { color: a.color },
      });
      s.addText(a.title, {
        x: 0.85, y: ay + 0.05, w: 2.5, h: 0.28,
        fontSize: 12, fontFace: FONT_TITLE, color: C.navy, bold: true, margin: 0,
      });
      s.addText(a.model, {
        x: 3.4, y: ay + 0.08, w: 2.5, h: 0.22,
        fontSize: 9, fontFace: FONT_BODY, color: a.color, bold: true, margin: 0,
      });
      s.addText(a.desc, {
        x: 0.85, y: ay + 0.35, w: 5, h: 0.22,
        fontSize: 9.5, fontFace: FONT_BODY, color: C.darkGray, margin: 0,
      });
      s.addText(a.detail, {
        x: 6, y: ay + 0.35, w: 3.2, h: 0.22,
        fontSize: 8.5, fontFace: FONT_BODY, color: C.midGray, italic: true, margin: 0,
      });
    });
  }

  // ════════════════════════════════════════════════════════════════
  // SLIDE 9 — PRIVACY & SECURITY
  // ════════════════════════════════════════════════════════════════
  {
    const s = pres.addSlide();
    s.background = { color: C.navy };
    s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.06, fill: { color: C.saffron } });

    s.addText("Privacy & Security by Design", {
      x: 0.6, y: 0.3, w: 8, h: 0.55,
      fontSize: 28, fontFace: FONT_TITLE, color: C.saffron, bold: true, margin: 0,
    });

    const secItems = [
      { icon: icons.lock,      title: "PII Masking at Ingestion",     desc: "Aadhaar → XXXX-XXXX-1098, PAN → XXXXX1234X, Phone → XXXXXX3210. Regex-based masking applied before any LLM call — zero raw PII in prompts." },
      { icon: icons.userShield, title: "Role-Based Access Control",   desc: "Operator / Supervisor / Admin / Auditor roles. Sensitive field reveal is gated by role. Immutable audit log for every reveal event." },
      { icon: icons.eye,       title: "Source Trust Weighting",       desc: "Every connector carries trust_score (0-1), last_updated_at, and access_mode. Stale or low-trust sources are discounted in scoring." },
      { icon: icons.check,     title: "Human-in-the-Loop",           desc: "High-impact actions (reject, escalate) always need officer confirmation. System recommends, human decides. Full decision audit trail." },
    ];

    const secW = 4.15, secH = 1.55, secGap = 0.35;
    const secStartX = 0.6, secStartY = 1.05;

    secItems.forEach((item, i) => {
      const col = i % 2, row = Math.floor(i / 2);
      const sx = secStartX + col * (secW + secGap);
      const sy = secStartY + row * (secH + secGap);

      s.addShape(pres.shapes.RECTANGLE, {
        x: sx, y: sy, w: secW, h: secH,
        fill: { color: C.navyMid }, shadow: mkShadow(),
      });
      s.addShape(pres.shapes.RECTANGLE, {
        x: sx, y: sy, w: secW, h: 0.05,
        fill: { color: C.saffron },
      });
      s.addImage({ data: item.icon, x: sx + 0.2, y: sy + 0.25, w: 0.4, h: 0.4 });
      s.addText(item.title, {
        x: sx + 0.75, y: sy + 0.2, w: secW - 1, h: 0.3,
        fontSize: 13, fontFace: FONT_TITLE, color: C.saffron, bold: true, margin: 0,
      });
      s.addText(item.desc, {
        x: sx + 0.2, y: sy + 0.65, w: secW - 0.4, h: 0.85,
        fontSize: 10, fontFace: FONT_BODY, color: C.lightGray, margin: 0,
      });
    });
  }

  // ════════════════════════════════════════════════════════════════
  // SLIDE 10 — DEMO RESULTS & METRICS
  // ════════════════════════════════════════════════════════════════
  {
    const s = pres.addSlide();
    s.background = { color: C.offWhite };
    s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.06, fill: { color: C.saffron } });

    s.addText("Demo & Impact Metrics", {
      x: 0.6, y: 0.25, w: 8, h: 0.55,
      fontSize: 28, fontFace: FONT_TITLE, color: C.navy, bold: true, margin: 0,
    });

    // Big stat callouts
    const stats = [
      { value: "52", label: "Seed Applications", sub: "Ground truth labelled" },
      { value: "6", label: "Fraud Patterns", sub: "Ghost, duplicate, deceased…" },
      { value: "12", label: "Risk Rules", sub: "Weighted scoring engine" },
      { value: "9", label: "Data Connectors", sub: "Parallel async enrichment" },
    ];

    stats.forEach((st, i) => {
      const sx = 0.6 + i * 2.3;
      s.addShape(pres.shapes.RECTANGLE, {
        x: sx, y: 0.95, w: 2.0, h: 1.35,
        fill: { color: C.white }, shadow: mkShadow(),
      });
      s.addText(st.value, {
        x: sx, y: 1.0, w: 2.0, h: 0.55,
        fontSize: 36, fontFace: FONT_TITLE, color: C.saffron, bold: true, align: "center", margin: 0,
      });
      s.addText(st.label, {
        x: sx, y: 1.55, w: 2.0, h: 0.3,
        fontSize: 11, fontFace: FONT_BODY, color: C.navy, bold: true, align: "center", margin: 0,
      });
      s.addText(st.sub, {
        x: sx, y: 1.82, w: 2.0, h: 0.3,
        fontSize: 8.5, fontFace: FONT_BODY, color: C.midGray, align: "center", margin: 0,
      });
    });

    // Demo scenarios
    s.addText("Live Demo Scenarios", {
      x: 0.6, y: 2.55, w: 8, h: 0.35,
      fontSize: 16, fontFace: FONT_TITLE, color: C.navy, bold: true, margin: 0,
    });

    const demos = [
      { num: "1", title: "Clean Beneficiary", desc: "Auto-routed to LOW risk (score 5-10). Documents consistent, no flags.", color: C.green },
      { num: "2", title: "Duplicate Ring Detection", desc: "Shared bank+phone+Aadhaar across apps triggers HIGH/CRITICAL. Network flags surface linked entities.", color: C.red },
      { num: "3", title: "Income Mismatch", desc: "Declared ₹8K vs extracted ₹45K — 82% deviation. MEDIUM flag with evidence citations.", color: C.amber },
      { num: "4", title: "Deceased Claim", desc: "Death registry match (92% confidence). Post-mortem filing detected. CRITICAL + auto-escalation.", color: C.red },
    ];

    demos.forEach((d, i) => {
      const dy = 3.0 + i * 0.6;
      s.addShape(pres.shapes.RECTANGLE, {
        x: 0.6, y: dy, w: 8.8, h: 0.5,
        fill: { color: C.white }, shadow: mkShadow(),
      });
      s.addShape(pres.shapes.OVAL, {
        x: 0.75, y: dy + 0.08, w: 0.33, h: 0.33,
        fill: { color: d.color },
      });
      s.addText(d.num, {
        x: 0.75, y: dy + 0.08, w: 0.33, h: 0.33,
        fontSize: 11, fontFace: FONT_TITLE, color: C.white, bold: true,
        align: "center", valign: "middle", margin: 0,
      });
      s.addText(d.title, {
        x: 1.25, y: dy + 0.05, w: 2.5, h: 0.22,
        fontSize: 11, fontFace: FONT_TITLE, color: C.navy, bold: true, margin: 0,
      });
      s.addText(d.desc, {
        x: 1.25, y: dy + 0.27, w: 7.8, h: 0.2,
        fontSize: 9, fontFace: FONT_BODY, color: C.darkGray, margin: 0,
      });
    });
  }

  // ════════════════════════════════════════════════════════════════
  // SLIDE 11 — WHAT MAKES US DIFFERENT
  // ════════════════════════════════════════════════════════════════
  {
    const s = pres.addSlide();
    s.background = { color: C.navy };
    s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.06, fill: { color: C.saffron } });

    s.addText("What Sets NaVRatM Apart", {
      x: 0.6, y: 0.25, w: 8, h: 0.55,
      fontSize: 28, fontFace: FONT_TITLE, color: C.saffron, bold: true, margin: 0,
    });

    const diffs = [
      { icon: icons.balance,   title: "Evidence-First, Not Score-Only",  desc: "Every risk point maps to verifiable source evidence with URI — not a black-box number." },
      { icon: icons.robot,     title: "Fully Agentic Pipeline",         desc: "8-stage orchestrated DAG: intake → extract → verify → enrich → detect → score → explain → decide." },
      { icon: icons.lang,      title: "Built for Bharat",               desc: "Native Indic AI (Sarvam): Hindi, Tamil, Telugu, Bengali… Officers use their own language, not English." },
      { icon: icons.network,   title: "Network Intelligence",           desc: "Cross-application pattern matching: shared bank accounts, phone rings, address clustering, Aadhaar collisions." },
      { icon: icons.lock,      title: "Zero-PII LLM Prompts",          desc: "Aadhaar, PAN, phone, bank — all masked before any AI model call. Demonstrated, not just claimed." },
      { icon: icons.line,      title: "Measurable Impact",              desc: "52 ground-truth cases, precision/recall/F1 computed, per-pattern detection rates tracked." },
    ];

    const dW = 4.2, dH = 1.2, dGapX = 0.35, dGapY = 0.22;
    const dStartX = 0.55, dStartY = 0.95;

    diffs.forEach((d, i) => {
      const col = i % 2, row = Math.floor(i / 2);
      const dx = dStartX + col * (dW + dGapX);
      const dy = dStartY + row * (dH + dGapY);

      s.addShape(pres.shapes.RECTANGLE, {
        x: dx, y: dy, w: dW, h: dH,
        fill: { color: C.navyMid }, shadow: mkShadow(),
      });
      s.addShape(pres.shapes.RECTANGLE, {
        x: dx, y: dy, w: 0.05, h: dH,
        fill: { color: C.saffron },
      });
      s.addImage({ data: d.icon, x: dx + 0.2, y: dy + 0.15, w: 0.38, h: 0.38 });
      s.addText(d.title, {
        x: dx + 0.7, y: dy + 0.12, w: dW - 0.9, h: 0.3,
        fontSize: 12, fontFace: FONT_TITLE, color: C.saffron, bold: true, margin: 0,
      });
      s.addText(d.desc, {
        x: dx + 0.7, y: dy + 0.48, w: dW - 0.9, h: 0.65,
        fontSize: 10, fontFace: FONT_BODY, color: C.lightGray, margin: 0,
      });
    });
  }

  // ════════════════════════════════════════════════════════════════
  // SLIDE 12 — CLOSING / THANK YOU
  // ════════════════════════════════════════════════════════════════
  {
    const s = pres.addSlide();
    s.background = { color: C.navy };
    s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.06, fill: { color: C.saffron } });

    s.addImage({ data: icons.shield, x: 4.4, y: 0.8, w: 1.2, h: 1.2 });

    s.addText("NaVRatM", {
      x: 0.5, y: 2.1, w: 9, h: 0.8,
      fontSize: 44, fontFace: FONT_TITLE, color: C.saffron, bold: true, align: "center", margin: 0,
    });
    s.addText("Protecting genuine beneficiaries. Catching fraud before it costs.", {
      x: 1, y: 2.9, w: 8, h: 0.45,
      fontSize: 16, fontFace: FONT_BODY, color: C.lightGray, align: "center", margin: 0,
    });

    // Summary stats
    const closing = [
      "8-stage agentic pipeline",
      "9 enrichment connectors",
      "6 fraud pattern detectors",
      "12 weighted risk rules",
      "5 Sarvam AI APIs",
      "52 demo cases with ground truth",
    ];
    s.addText(closing.map((c, i) => ({
      text: `${c}${i < closing.length - 1 ? "   ·   " : ""}`,
      options: { fontSize: 11, fontFace: FONT_BODY, color: C.midGray },
    })), {
      x: 0.5, y: 3.6, w: 9, h: 0.35, align: "center", margin: 0,
    });

    // Call to action
    s.addShape(pres.shapes.RECTANGLE, {
      x: 3, y: 4.2, w: 4, h: 0.55,
      fill: { color: C.saffron },
      shadow: mkShadow(),
    });
    s.addText("LIVE DEMO →", {
      x: 3, y: 4.2, w: 4, h: 0.55,
      fontSize: 16, fontFace: FONT_TITLE, color: C.navy, bold: true,
      align: "center", valign: "middle", margin: 0,
    });

    // Bottom
    s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 5.3, w: 10, h: 0.325, fill: { color: C.navyMid } });
    s.addText("Team NaVRatM  |  Hackathon 2026  |  Powered by Sarvam AI  |  Built with FastAPI + PptxGenJS", {
      x: 0.5, y: 5.3, w: 9, h: 0.325,
      fontSize: 10, fontFace: FONT_BODY, color: C.midGray, align: "center", margin: 0,
    });
  }

  // ── Write file ──
  await pres.writeFile({ fileName: "NaVRatM_Hackathon_Deck.pptx" });
  console.log("✅ Deck generated: NaVRatM_Hackathon_Deck.pptx");
}

main().catch(err => {
  console.error("PPTX generation failed:", err);
  process.exit(1);
});
