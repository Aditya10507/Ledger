# UI/UX Design Plan
## Ledger — AI Finance Controller Agent

**Version:** 1.0
**Principle:** Simple, modern, trustworthy. This is a finance tool — clarity beats decoration everywhere.

---

## 1. Design Principles

1. **Trust through clarity, not decoration.** Every flag must feel explainable and grounded, never mysterious. No dark patterns, no ambiguous icons for financial actions.
2. **Numbers first.** Amounts, deltas, and confidence scores are always visually prominent — never buried in prose.
3. **One primary action per screen.** Reviewing a flag should never require the analyst to guess what to do next.
4. **Calm, not alarming.** Anomalies are flagged with clear color coding, but the UI avoids aggressive red/alarm styling that would cause alert fatigue.
5. **Progressive disclosure.** Summary first, detail on demand — analysts shouldn't be forced to read every field to understand a flag's severity.

---

## 2. User Journey (Primary Flow)

```
Login
  → Dashboard (list of reconciliation runs)
    → Start New Run (upload ledger + settlement CSV)
      → Processing state
        → Run Summary (matched %, flagged %, value at risk)
          → Flag List (filterable, sortable)
            → Flag Detail (explanation, confidence, related transactions)
              → Decision (approve / reject / escalate + comment)
                → Audit Trail (view history for this flag)
```

---

## 3. Navigation Structure

**Top-level navigation (persistent sidebar or top bar):**
- Dashboard (all runs)
- New Run (upload)
- Audit Log (Admin only — global view)
- Account/Logout

**Within a run:** Summary tab → Flags tab → (Admin) Run-level audit tab

Navigation is intentionally shallow — no more than 3 levels deep from login to any flag detail, so analysts can move fast during review sessions.

---

## 4. Screens

| Screen | Purpose | Key Elements |
|---|---|---|
| **Login** | Authenticate | Email/password form, error state for invalid credentials |
| **Dashboard** | List all reconciliation runs | Table: run date, status, match %, flagged count; "New Run" button |
| **New Run / Upload** | Start a reconciliation | Two file drop zones (ledger, settlement), validation feedback, "Run Reconciliation" button |
| **Processing** | Show progress while matching runs | Simple progress indicator, non-blocking (can navigate away) |
| **Run Summary** | High-level results of one run | Stat cards: total records, matched %, flagged %, flagged value; breakdown chart by anomaly type |
| **Flag List** | Browse all flags in a run | Table/list: flag type, amount, confidence, status; filters (type, status, confidence range); sort by confidence/amount |
| **Flag Detail** | Investigate one flag | Related transaction(s) side-by-side, computed delta, AI explanation, confidence score, decision buttons, comment field |
| **Audit Trail (per flag)** | Full history of one flag | Chronological log: created → AI explanation generated → analyst decision(s) |
| **Global Audit Log (Admin)** | Cross-run oversight | Filterable table of all system events |

---

## 5. User Flows

### 5.1 Upload & Run Flow
1. Analyst clicks "New Run."
2. Drags/selects ledger CSV → inline validation (file type, size).
3. Drags/selects settlement CSV → inline validation.
4. Clicks "Run Reconciliation" — disabled until both files pass validation.
5. Sees processing state with a progress indicator.
6. Redirected automatically to Run Summary on completion.

### 5.2 Flag Review Flow
1. From Run Summary, analyst clicks "View Flags."
2. Sees flag list, sorted by confidence (highest risk first) by default.
3. Clicks a flag → detail view opens.
4. Reads explanation, reviews related transaction(s) side-by-side.
5. Selects Approve / Reject / Escalate, optionally adds a comment.
6. Confirms decision → returns to flag list with that flag now marked resolved (visually distinct, e.g., muted/checked state).

### 5.3 Error Recovery Flow
1. Analyst uploads a malformed file.
2. System shows an inline error naming the exact problem (e.g., "Row 42: 'amount' is not a valid number").
3. Analyst is not blocked from re-uploading a corrected file in place — no need to restart the whole flow.

---

## 6. Key Components (Reusable)

- **StatCard** — large number + label, used on Run Summary (e.g., "Matched: 94.2%").
- **FlagBadge** — colored pill showing flag type (duplicate / missing settlement / amount mismatch / timing anomaly).
- **ConfidenceMeter** — small horizontal bar or numeric badge (0–100), color-graded (low/medium/high risk).
- **TransactionCard** — compact display of a single transaction's key fields (ID, amount, timestamp, source).
- **DecisionBar** — the approve/reject/escalate action row with comment field, used on Flag Detail.
- **AuditRow** — single timeline entry (actor, action, timestamp) used in audit trail views.
- **FileDropZone** — upload component with drag-and-drop, validation state, and error messaging.

---

## 7. Forms & Validation UX

- File upload: validation happens immediately on file selection, not after a page-level "submit" — analysts get feedback before committing to a run.
- Decision form (approve/reject/escalate): the comment field is optional except when escalating, where a brief reason is required (so escalations are never ambiguous for whoever picks them up next).
- All form errors are shown inline, next to the relevant field — never only as a top-of-page banner disconnected from the input.

---

## 8. Loading / Error / Empty States

| State | Treatment |
|---|---|
| **Loading (run processing)** | Progress indicator with a short status line ("Matching transactions…", "Generating explanations…") — never a bare spinner with no context |
| **Loading (explanation pending)** | Flag is still visible with its computed data; explanation area shows a lightweight "Generating explanation…" placeholder, not a blocked screen |
| **Error (upload)** | Inline, specific, actionable message tied to the exact row/column/reason |
| **Error (explanation unavailable)** | Flag shows "AI explanation unavailable — reviewed using computed data" rather than hiding the flag or showing a broken state |
| **Empty (no runs yet)** | Friendly empty state with a clear "Start your first reconciliation" call to action |
| **Empty (no flags in a run)** | Positive framing: "No anomalies found — all transactions reconciled cleanly," not a blank table |

---

## 9. Responsive Behavior

- Primary use case is desktop (finance/ops work happens at a desk), so desktop is the design priority.
- Tablet: dashboard and flag list remain usable via responsive table-to-card collapse for narrower widths.
- Mobile: out of scope for MVP interaction design, but layouts should not visually break (basic responsive stacking is sufficient — full mobile optimization is a post-MVP concern).

---

## 10. Accessibility

- Color is never the only signal for status (e.g., flag severity pairs color with a text label, not color alone).
- All interactive elements (buttons, form fields) are reachable and operable via keyboard.
- Sufficient contrast ratios (WCAG AA minimum) between text and background, particularly important given the data-density of this UI.
- Form inputs have associated labels (not placeholder-only labeling) so screen readers can identify fields correctly.

---

## 11. Typography

- **Primary typeface:** A clean, modern sans-serif (e.g., Inter or similar) — highly legible at small sizes for dense tabular data.
- **Numeric data:** Use a tabular-figure/monospaced-number variant where available, so amounts align cleanly in columns — this matters a lot for a finance tool.
- **Hierarchy:** 3 weight levels are enough — Regular (body/table data), Medium (labels, section headers), Semibold (page titles, key stat numbers). Avoid introducing more than this to keep the UI calm.

---

## 12. Color Palette

| Purpose | Direction |
|---|---|
| Base/background | Neutral off-white/light gray — keeps focus on data, not chrome |
| Primary/brand | A single confident accent color (e.g., deep blue or indigo) for primary actions and active states |
| Success/Matched | Muted green |
| Flagged/Warning | Amber — not red, to avoid alarm fatigue for moderate-confidence flags |
| High-risk/Critical | Reserved red, used sparingly — only for high-confidence, high-value flags |
| Text | Dark neutral gray (not pure black) for body text, full contrast reserved for headers/numbers |

Avoid over-saturating the UI with color — in a finance tool, color should carry meaning (status), not decoration.

---

## 13. Spacing & Layout System

- Use a consistent spacing scale (e.g., 4px base unit: 4/8/12/16/24/32/48) throughout — no arbitrary one-off spacing values.
- Tables and cards use generous vertical padding to reduce visual density fatigue during long review sessions.
- Maintain a consistent max content width on wide screens (avoid full-bleed tables stretching edge-to-edge on large monitors) to keep line-scanning comfortable.

---

## 14. Design Tone Summary

Think "modern fintech ops tool" — closer to a Stripe/Ramp/Brex internal dashboard than a flashy consumer app. Confident, quiet, data-forward, and immediately legible to someone who has to make a real financial decision based on what they see.
