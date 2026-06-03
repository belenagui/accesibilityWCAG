# WCAG Accessibility Reporter

An automated accessibility testing tool that audits any URL against **WCAG 2.1 A/AA** standards using **Cypress + axe-core**, and presents the results in an interactive dashboard with violation details and code-level fix guidance.

---

## How it works

1. Open the dashboard at `http://localhost:3000`
2. Enter any publicly accessible URL
3. Click **Run Audit** — the server spawns a headless Cypress run with axe-core
4. Results appear in real time: summary cards, filterable violation list, and per-violation fix examples

---

## Tech stack

| Layer | Tool |
|---|---|
| Test runner | [Cypress 13](https://www.cypress.io/) |
| Accessibility engine | [axe-core](https://github.com/dequelabs/axe-core) via [cypress-axe](https://github.com/component-driven/cypress-axe) |
| WCAG standards | WCAG 2.1 A / AA / Best Practice |
| Backend | Node.js + Express |
| Frontend | Vanilla HTML / CSS / JS |

---

## Prerequisites

- **Node.js** v18 or higher
- **npm** v9 or higher
- A publicly accessible URL to audit (localhost URLs work too if the server is running)

---

## Setup

```bash
# 1. Clone the repository
git clone https://github.com/belenagui/accesibilityWCAG.git
cd accesibilityWCAG

# 2. Install dependencies
# Note: first run downloads the Cypress binary (~300 MB) — this takes a few minutes
npm install

# 3. Start the dashboard
npm start
```

Then open **http://localhost:3000** in your browser.

---

## Project structure

```
accesibilityWCAG/
├── cypress/
│   ├── e2e/
│   │   └── accessibility.cy.js   # axe-core audit test + WCAG mappings + fix suggestions
│   └── support/
│       └── e2e.js                # imports cypress-axe
├── public/
│   └── index.html                # dashboard UI
├── server/
│   └── index.js                  # Express server — triggers Cypress, serves results
├── results/                      # auto-generated JSON report (git-ignored)
├── cypress.config.js
└── package.json
```

---

## What it checks

All **axe-core** `wcag2a`, `wcag2aa`, `wcag21aa`, and `best-practice` rule sets, including:

| Rule | WCAG Criterion | Level | Description |
|---|---|---|---|
| `color-contrast` | 1.4.3 | AA | Text must meet minimum contrast ratio |
| `image-alt` | 1.1.1 | A | Images must have descriptive alt text |
| `label` | 1.3.1 | A | Form inputs must have associated labels |
| `link-name` | 2.4.4 | A | Links must have discernible text |
| `button-name` | 4.1.2 | A | Buttons must have an accessible name |
| `html-has-lang` | 3.1.1 | A | `<html>` must declare a language |
| `document-title` | 2.4.2 | A | Every page must have a unique `<title>` |
| `heading-order` | 1.3.1 | A | Headings must not skip levels |
| `meta-viewport` | 1.4.4 | AA | Viewport must not disable user scaling |
| `skip-link` | 2.4.1 | A | Pages must provide a skip-navigation link |
| `frame-title` | 2.4.1 | A | `<iframe>` elements must have a title |
| `aria-*` validity | 4.1.2 | A | ARIA attributes must be valid for their role |

---

## Dashboard features

- **URL input** — enter any URL and trigger an audit on demand
- **Live status** — spinner with real-time Cypress log output while the audit runs
- **Summary cards** — total violations broken down by impact: Critical / Serious / Moderate / Minor
- **Filter bar** — narrow the list by impact level with one click
- **Violation cards** — each violation expands to show three tabs:
  - **How to Fix** — annotated code examples for the specific rule
  - **Affected Elements** — the actual HTML nodes that failed, with CSS selector and failure reason
  - **WCAG Info** — criterion number, conformance level, principle, and axe rule tags
- **Deque docs link** — direct link to the full rule documentation for each violation

---

## Running the audit from the command line

You can also run the Cypress test directly without the dashboard:

```bash
# Audit a specific URL headlessly
npx cypress run --spec cypress/e2e/accessibility.cy.js --env url=https://example.com

# Open Cypress Test Runner (interactive mode)
npx cypress open
```

Results are saved to `results/axe-results.json`.

---

## License

MIT
