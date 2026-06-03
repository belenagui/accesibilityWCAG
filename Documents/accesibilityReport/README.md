# WCAG Accessibility Reporter

An automated accessibility testing tool that audits any URL against **WCAG 2.1 A/AA** standards using **Cypress + axe-core**, and presents the results in an interactive dashboard with violation details and code-level fix guidance.

---

## How it works

The tool has three layers that work together: a browser-based dashboard, an Express server, and a headless Cypress test runner.

```
User enters URL
      │
      ▼
Dashboard (http://localhost:3000)
  POST /api/audit  ──────────────────────►  Express Server (server/index.js)
                                                    │
                                                    │  spawns
                                                    ▼
                                          Cypress (headless)
                                            └─ visits the URL
                                            └─ injects axe-core
                                            └─ runs checkA11y()
                                            └─ maps violations to WCAG criteria
                                            └─ attaches fix suggestions
                                            └─ saves results/axe-results.json
                                                    │
  GET /api/status  ◄──────────────────────  polling every 1.5s
  GET /api/results ◄──────────────────────  when run completes
      │
      ▼
Dashboard renders:
  - Summary cards by impact
  - Filterable violation list
  - Per-violation: HTML nodes, WCAG info, fix code
```

**Step by step:**

1. Open **http://localhost:3000** in your browser
2. Type or paste any publicly accessible URL into the input field
3. Click **Run Audit** — the server validates the URL and spawns a Cypress process
4. The dashboard polls `/api/status` every 1.5 seconds and shows live log output
5. When Cypress finishes, the results JSON is written to `results/axe-results.json`
6. The dashboard fetches `/api/results` and renders the full report:
   - Impact summary cards (Critical / Serious / Moderate / Minor)
   - A filterable list of every violation
   - Each violation expands to show affected HTML elements, WCAG criterion, and an annotated code fix
7. If zero violations are found, a green pass banner is shown instead

---

## Tech stack

| Layer | Tool | Purpose |
|---|---|---|
| Test runner | [Cypress 13](https://www.cypress.io/) | Headless browser automation |
| Accessibility engine | [axe-core](https://github.com/dequelabs/axe-core) via [cypress-axe](https://github.com/component-driven/cypress-axe) | WCAG rule evaluation |
| WCAG standard | WCAG 2.1 A / AA / Best Practice | Conformance target |
| Backend | Node.js + Express | Orchestrates Cypress, serves results |
| Frontend | Vanilla HTML / CSS / JS | Dashboard UI, no build step required |

---

## Prerequisites

| Requirement | Minimum version | Check |
|---|---|---|
| Node.js | v18.0.0 | `node --version` |
| npm | v9.0.0 | `npm --version` |
| OS | Windows 10, macOS 12, Ubuntu 20.04 | — |

> **Cypress also requires a supported browser.** On Linux, install the system dependencies listed in the [Cypress Linux prereqs](https://docs.cypress.io/guides/getting-started/installing-cypress#Linux-Prerequisites). On Windows and macOS, no extra steps are needed — Cypress bundles Electron.

The URL being audited must be reachable from your machine. Both public URLs and `localhost` addresses work, as long as the target server is running when the audit is triggered.

---

## Setup

```bash
# 1. Clone the repository
git clone https://github.com/belenagui/accesibilityWCAG.git
cd accesibilityWCAG

# 2. Install dependencies
# First run downloads the Cypress binary (~300 MB) — this takes a few minutes
npm install

# 3. Start the dashboard server
npm start
```

Then open **http://localhost:3000** in your browser.

**Troubleshooting:**

- `EADDRINUSE` — port 3000 is already in use. Kill the existing process or change `PORT` in `server/index.js`.
- `Cypress binary not found` — run `npx cypress install` to re-download the binary.
- SSL errors on Windows — the project uses `http.sslVerify=false` for git; the app itself does not bypass SSL for the audited URL.

---

## Project structure

```
accesibilityWCAG/
│
├── cypress/
│   ├── e2e/
│   │   └── accessibility.cy.js   # Main test: visits URL, injects axe-core,
│   │                             # maps violations to WCAG criteria,
│   │                             # attaches fix suggestions, saves JSON
│   └── support/
│       └── e2e.js                # Imports cypress-axe to make injectAxe()
│                                 # and checkA11y() available globally
│
├── public/
│   └── index.html                # Single-page dashboard — URL input, live
│                                 # status polling, summary cards, violation
│                                 # list with expandable fix tabs
│
├── server/
│   └── index.js                  # Express server
│                                 #   POST /api/audit  — starts Cypress run
│                                 #   GET  /api/status — returns run state + logs
│                                 #   GET  /api/results — serves axe-results.json
│
├── results/                      # Auto-generated at runtime (git-ignored)
│   └── axe-results.json          # Full violation report with WCAG mappings
│
├── cypress.config.js             # Cypress config: spec pattern, reporter,
│                                 # saveReport task (writes results JSON)
├── .gitignore
├── package.json
└── README.md
```

---

## What it checks

The test runs all axe-core rules tagged `wcag2a`, `wcag2aa`, `wcag21aa`, and `best-practice`. The table below lists the most common rules along with their WCAG 2.1 criterion, conformance level, and a short description of what the rule validates:

| Rule ID | WCAG Criterion | Level | Principle | Description |
|---|---|---|---|---|
| `color-contrast` | 1.4.3 | AA | Perceivable | Text must have a contrast ratio of at least 4.5:1 (3:1 for large text) against its background |
| `image-alt` | 1.1.1 | A | Perceivable | Every `<img>` must have an `alt` attribute describing its content or purpose |
| `label` | 1.3.1 | A | Perceivable | Each form input must be associated with a visible `<label>` or an `aria-label` / `aria-labelledby` |
| `link-name` | 2.4.4 | A | Operable | Links must have discernible text so users understand where they lead |
| `button-name` | 4.1.2 | A | Robust | Buttons must have an accessible name so screen readers can announce their purpose |
| `html-has-lang` | 3.1.1 | A | Understandable | The `<html>` element must have a `lang` attribute so assistive technology uses the correct language rules |
| `document-title` | 2.4.2 | A | Operable | Every page must have a unique, descriptive `<title>` element |
| `heading-order` | 1.3.1 | A | Perceivable | Heading levels must be sequential (h1 → h2 → h3) without skipping levels |
| `meta-viewport` | 1.4.4 | AA | Perceivable | The viewport meta tag must not use `user-scalable=no`, which blocks zoom for low-vision users |
| `skip-link` | 2.4.1 | A | Operable | Pages must offer a way to skip repetitive navigation (e.g. "Skip to main content") |
| `frame-title` | 2.4.1 | A | Operable | Every `<iframe>` must have a `title` attribute describing its content |
| `aria-allowed-attr` | 4.1.2 | A | Robust | ARIA attributes must be permitted for the element's role |
| `aria-required-attr` | 4.1.2 | A | Robust | Elements with a role must include all required ARIA attributes for that role |
| `aria-valid-attr` | 4.1.2 | A | Robust | All `aria-*` attribute names must be valid ARIA attributes |
| `aria-hidden-focus` | 4.1.2 | A | Robust | Focusable elements must not be hidden from assistive technology via `aria-hidden="true"` |
| `list` | 1.3.1 | A | Perceivable | `<ul>` and `<ol>` elements must contain only `<li>` items as direct children |
| `listitem` | 1.3.1 | A | Perceivable | `<li>` elements must be inside a `<ul>` or `<ol>` |
| `form-field-multiple-labels` | 1.3.1 | A | Perceivable | Form fields must not have more than one label |
| `tabindex` | 2.4.3 | A | Operable | Elements must not use a `tabindex` greater than 0, which disrupts natural focus order |

> For the full rule set see the [axe-core rule documentation](https://dequeuniversity.com/rules/axe/).

---

## Dashboard features

### URL input panel
- **Text field** — accepts any `http://` or `https://` URL; submits on Enter or button click
- **Run Audit button** — disabled while an audit is already running to prevent concurrent runs
- **Error banner** — shown inline if the URL is invalid or Cypress exits with an error

### Live status bar
Appears as soon as an audit starts. Shows:
- A spinning indicator while Cypress is running
- The last line of Cypress stdout output, updated every 1.5 seconds
- Automatically hides when results are ready

### Summary cards
Five cards displayed at the top of the results area:

| Card | Color | What it counts |
|---|---|---|
| Total Violations | Purple | All violations regardless of impact |
| Critical | Red | Violations that block access entirely |
| Serious | Orange | High-priority violations |
| Moderate | Yellow | Medium-priority violations |
| Minor | Green | Low-priority violations |

### Filter bar
One button per impact level. Clicking a filter hides all violations that don't match. The count in each button reflects the current number of violations at that level. Defaults to **All**.

### Violation cards
Each violation is a collapsible card showing:
- **Impact badge** — color-coded label (Critical / Serious / Moderate / Minor)
- **Rule title** — human-readable description of what failed
- **Element count** — how many HTML elements triggered the violation
- **WCAG badge** — criterion number and conformance level (e.g. `WCAG 1.4.3 (AA)`)
- **Expand/collapse chevron** — click anywhere on the header to open

When expanded, each card has three tabs:

**How to Fix**
- A plain-English explanation of why the violation matters
- An annotated code block showing the correct implementation (HTML, CSS, or JS depending on the rule)
- A direct link to the full rule documentation on Deque University

**Affected Elements**
- The CSS selector path targeting each failing element
- The raw HTML snippet of the element as it appears on the page
- The axe-core failure summary explaining exactly what is wrong

**WCAG Info**
- Rule ID, WCAG criterion number, conformance level, WCAG principle
- All axe-core tags associated with the rule (e.g. `wcag2aa`, `best-practice`)

### Pass state
If axe-core finds zero violations, the violation list is replaced with a green banner: *"No violations found — this page passes WCAG 2.1 AA checks!"*

---

## Running the audit from the command line

You can trigger the Cypress test directly without starting the dashboard server. Results are saved to `results/axe-results.json`.

```bash
# Audit a URL headlessly (no browser window)
npx cypress run \
  --spec cypress/e2e/accessibility.cy.js \
  --env url=https://example.com

# Audit a localhost app
npx cypress run \
  --spec cypress/e2e/accessibility.cy.js \
  --env url=http://localhost:8080

# Open the Cypress Test Runner (interactive, with browser UI)
npx cypress open

# Run with a specific browser
npx cypress run \
  --spec cypress/e2e/accessibility.cy.js \
  --env url=https://example.com \
  --browser chrome
```

> If no `--env url=` is provided, the test defaults to `https://example.com`.

---

## License

MIT
