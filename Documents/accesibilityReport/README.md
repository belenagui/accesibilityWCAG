# WCAG Accessibility Reporter

Automated WCAG 2.1 AA accessibility testing with **Cypress + axe-core**, served through a visual report dashboard.

## Stack

| Layer | Tool |
|---|---|
| Test runner | Cypress 13 |
| Accessibility engine | axe-core (via cypress-axe) |
| WCAG standards | WCAG 2.1 A / AA / Best Practice |
| Dashboard | Express + vanilla HTML/CSS/JS |

## Setup

```bash
npm install
```

> First run installs Cypress (~300 MB binary). This takes a few minutes.

## Run

```bash
npm start
```

Then open **http://localhost:3000**, enter any URL and click **Run Audit**.

## What it checks

- Color contrast (1.4.3)
- Image alt text (1.1.1)
- Form labels (1.3.1)
- Link and button names (2.4.4 / 4.1.2)
- HTML lang attribute (3.1.1)
- Document title (2.4.2)
- Heading order (1.3.1)
- ARIA attribute validity (4.1.2)
- Viewport zoom (1.4.4)
- Skip links (2.4.1)
- iFrame titles (2.4.1)
- + all axe-core wcag2a / wcag2aa / wcag21aa rules

## Report features

- Summary cards by impact (critical / serious / moderate / minor)
- Filter by impact level
- Per-violation: affected HTML elements, WCAG criterion, fix code, Deque docs link
