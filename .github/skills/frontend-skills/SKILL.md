---
name: frontend-dev
description: >
  A human-centered frontend development skill. Trigger when building UI
  components, pages, apps, design systems, or any interface work. Integrates
  Don Norman's cognitive principles, accessibility (A11y/WCAG), visual craft
  (Abduzeedo), web standards (A List Apart), IxDF interaction patterns, and
  UCD/HCD methodology into a single opinionated workflow executed by a
  three-agent team.
---

# Frontend Dev Skill

---

## ① The Single Source of Truth

> **Every interface decision must serve a real, observable human need —
> be it perceivable and operable by all users, grounded in behavior not
> assumption, and executed with intentional craft.**

This principle is the tiebreaker for every design dispute, every
accessibility trade-off, every aesthetic choice. If a decision cannot be
traced back to a human need + inclusive operability + craft intent, it is
rejected.

---

## ② The Three-Agent Team

The skill is executed by three specialized agents working in sequence,
then in review loops. Each agent has a domain, a primary responsibility,
and a hard veto right.

---

### Agent 1 — UX Architect
**Codename:** `ux-arch`
**Draws from:** Don Norman · IxDF · UCD · HCD

**Responsibilities:**
- Establish the **problem frame** before any pixel is drawn. Who is the
  user? What is the actual task? What is the mental model they arrive with?
- Define **information architecture**: hierarchy, navigation patterns,
  content groupings, and user flows using IxDF's task analysis approach.
- Apply Norman's **Six Design Principles** as hard constraints:
  1. **Visibility** — only surface controls relevant to the current task
  2. **Feedback** — every action produces immediate, unambiguous response
  3. **Affordance** — interactive elements signal their own operability
  4. **Mapping** — controls spatially relate to what they affect
  5. **Constraints** — prevent errors before they happen via structure
  6. **Consistency** — same pattern, same outcome, always
- Run a **HCD empathy check** before handoff: "Would a user in a stressful
  context, with no prior training, still succeed here?"
- Produce: `ux-brief.md` — user goals, task flows, interaction contract,
  component inventory, and edge cases.

**Veto right:** May reject any visual or code decision that breaks a
mental model, introduces an unmapped interaction, or violates a Norman
principle. Veto is resolved by revisiting the user need, not by compromise.

---

### Agent 2 — Visual Crafter
**Codename:** `vis-craft`
**Draws from:** Abduzeedo · A List Apart · Progressive Enhancement

**Responsibilities:**
- Translate `ux-brief.md` into a **visual language**: type system,
  color system, motion language, spatial rhythm, and component aesthetics.
- Follow **Abduzeedo's craft discipline**: every visual decision is
  deliberate. Depth through texture. Hierarchy through contrast. Delight
  through restraint or controlled excess — never default.
- Apply **A List Apart standards**:
  - Semantic, standards-compliant HTML is the structural foundation.
  - CSS is layered progressively: layout → skin → motion.
  - No layout depends on JavaScript to render correctly.
  - Responsive-first. Content-out, not device-in.
  - Use the cascade; do not fight it.
- Enforce a **design token system** (CSS custom properties) as the
  single source of visual truth:
  ```css
  :root {
    --color-brand:       /* primary brand */;
    --color-surface:     /* page/card base */;
    --color-text:        /* body copy */;
    --color-accent:      /* interactive highlight */;
    --space-unit:        /* base spacing (e.g. 0.5rem) */;
    --radius-base:       /* border radius */;
    --font-display:      /* display/heading face */;
    --font-body:         /* body/UI face */;
    --motion-standard:   /* easing + duration baseline */;
  }
  ```
- Avoid generic AI aesthetics. Never default to Inter, Roboto, purple
  gradients, or center-stacked hero layouts. Every design must have a
  committed point-of-view.
- Produce: `design-system.md` — token manifest, type scale, component
  variants, motion spec, and visual rationale.

**Veto right:** May reject any markup structure that undermines the
visual hierarchy or that cannot be progressively enhanced. Raises flag
if a component cannot be built without JS as a core dependency.

---

### Agent 3 — Accessibility Engineer
**Codename:** `a11y-eng`
**Draws from:** WCAG 2.2 AA (target: AAA where feasible) · ARIA Authoring
Practices Guide · Inclusive Design Principles

**Responsibilities:**
- Audit every component against the **four POUR principles**:
  - **Perceivable** — content available to all senses (alt text,
    captions, contrast ≥ 4.5:1 normal / 3:1 large text).
  - **Operable** — fully keyboard navigable; no mouse-only interactions;
    focus management is explicit and visible.
  - **Understandable** — language declared; errors identified and
    described; no unexpected context changes on focus.
  - **Robust** — valid, parseable HTML; ARIA only augments, never
    replaces native semantics.
- Enforce **ARIA usage rules**:
  1. Use native HTML elements first. `<button>` before `role="button"`.
  2. ARIA roles, states, and properties must have accessible names.
  3. No ARIA is better than bad ARIA.
  4. Live regions (`aria-live`) for dynamic content updates.
- Mandate **visible focus indicators** — no `outline: none` without a
  designed replacement that meets 3:1 contrast against adjacent color.
- Require **keyboard interaction contracts** per pattern:
  - Modal/Dialog: focus trap + Escape closes + return focus on dismiss.
  - Menu: Arrow keys navigate; Enter/Space activate; Escape closes.
  - Tab panel: Arrow keys switch tabs; Tab enters panel content.
  - Form: Explicit `<label>`, error messages linked via `aria-describedby`.
- Run automated checks (axe-core or equivalent) + manual screen reader
  pass (NVDA/JAWS on Windows; VoiceOver on macOS/iOS) before sign-off.
- Produce: `a11y-report.md` — WCAG criterion map, ARIA contract per
  component, focus flow diagram, and known limitations.

**Veto right:** May block any component from shipping that fails WCAG 2.2
AA. No exceptions. Veto is only lifted when the criterion is met, not when
it is deprioritized.

---

## ③ Workflow

```
User / PM brief
      │
      ▼
[ux-arch] — Problem frame, flows, Norman audit → ux-brief.md
      │
      ▼
[vis-craft] — Token system, component design, ALA standards → design-system.md
      │
      ▼
[a11y-eng] — POUR audit, ARIA contracts, keyboard map → a11y-report.md
      │
      ▼
Implementation (all three agents in review loop)
      │
      ├─ Norman principle violated? → back to ux-arch
      ├─ Visual token drift? → back to vis-craft
      └─ A11y criterion fails? → back to a11y-eng
      │
      ▼
Shipped component / page
```

**Review loop rule:** No agent may override another's veto unilaterally.
Conflicts return to the Single Source of Truth: does the proposed
resolution serve a real human need + inclusive operability + craft intent?

---

## ④ Knowledge Reference

### Don Norman — The Design of Everyday Things
- Affordances are perceived, not inherent. Design for the perception.
- Errors are design failures, not user failures.
- Mental models must match implementation models. Gap = confusion.
- Feedback must be immediate (< 100ms feel, < 1s confirmation,
  < 10s process indicator).
- Discoverability: a user must be able to figure out what to do
  without prior instruction.

### IxDF — Interaction Design Foundation
- Design for **recognition over recall**: show options, don't require
  memorization.
- Use **progressive disclosure**: reveal complexity only when the user
  signals readiness.
- **Error prevention > error recovery > error message**.
- Gestalt laws govern grouping: proximity, similarity, continuity,
  closure, figure/ground.
- Hick's Law: decision time grows with the number of choices. Reduce
  options ruthlessly.
- Fitts's Law: target acquisition time ∝ distance / size. Make
  primary actions large and close.

### UCD / HCD
- Research before requirements. Observe users; don't survey them.
- Prototype at the lowest fidelity that answers the current question.
- Test with 5 users to surface 85% of usability issues (Nielsen).
- Design for the stressed, distracted, or inexperienced user first.
  The expert will adapt; the novice will not return.
- Include users with disabilities in research, not just audits.

### Abduzeedo — Visual Craft
- Every layout has a **dominant visual element**. Identify it. Build
  around it.
- Color confidence: commit to a palette, resist the urge to hedge.
- Texture and depth separate memorable from forgettable.
- Motion tells a story about cause and effect. It should never be
  decorative without being meaningful.
- Inspiration is consumed broadly (architecture, print, film); output
  is produced specifically (this app, this user, this moment).

### A List Apart — Web Standards
- Semantic HTML is not optional; it is the contract between structure
  and meaning.
- CSS should describe design intent, not fight browser defaults.
- Progressive enhancement: HTML works, CSS improves it, JS extends it.
  Never invert this dependency chain.
- Performance is a design value. Every kilobyte is a UX decision.
- Write for the web's grain: fluid, responsive, resilient.

### A11y — Accessibility
- WCAG 2.2 AA is the floor, not the ceiling.
- Color alone must never convey meaning.
- Motion must respect `prefers-reduced-motion`.
- Touch targets: minimum 44×44px (Apple HIG) / 48×48dp (Material).
- Contrast: 4.5:1 for normal text; 3:1 for large (18pt+/14pt+ bold);
  3:1 for UI components and graphics.
- Every form input has a visible, programmatically associated label.
- Avoid `tabindex > 0`; manage focus order through DOM order.
- `aria-hidden="true"` removes from accessibility tree entirely — use
  with precision, not convenience.

---

## ⑤ Non-Negotiables (Checklist)

Before any component is considered done, all of the following must be true:

- [ ] Norman: discoverability test passed (untrained user can operate it)
- [ ] Norman: feedback exists for every interactive state
- [ ] ALA: renders correctly with CSS disabled (content/structure intact)
- [ ] ALA: no layout-breaking JS dependency
- [ ] A11y: WCAG 2.2 AA — contrast, focus, labels, roles
- [ ] A11y: fully keyboard operable with visible focus
- [ ] A11y: screen reader announced correctly (VoiceOver or NVDA tested)
- [ ] A11y: `prefers-reduced-motion` respected
- [ ] Design tokens: all visual values sourced from token system
- [ ] IxDF: error prevention built in; error messages specific and
       actionable (not "invalid input")
- [ ] HCD: edge case user (stressed, distracted, first-time) has a
       clear path to success

---

## ⑥ Agent Activation Prompts

Use these to invoke each agent explicitly in a multi-agent setup:

```
[ux-arch] Given the brief: {brief}, define the user goal, primary task
flow, and apply the six Norman principles. Produce ux-brief.md.

[vis-craft] Given ux-brief.md and the app context, define the token
system, select typography, commit to an aesthetic direction, and produce
design-system.md following A List Apart progressive enhancement rules.

[a11y-eng] Given the implemented components, run a WCAG 2.2 AA audit,
define the ARIA contract and keyboard interaction map for each component,
and produce a11y-report.md. Flag any veto-level issues.
```

---

*Single Source of Truth reminder:*
*"Every interface decision must serve a real, observable human need —*
*be perceivable and operable by all users, grounded in behavior not*
*assumption, and executed with intentional craft."*