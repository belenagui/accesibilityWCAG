/// <reference types="cypress" />

const WCAG_CRITERIA = {
  'color-contrast': { criterion: '1.4.3', level: 'AA', principle: 'Perceivable' },
  'image-alt': { criterion: '1.1.1', level: 'A', principle: 'Perceivable' },
  'label': { criterion: '1.3.1', level: 'A', principle: 'Perceivable' },
  'link-name': { criterion: '2.4.4', level: 'A', principle: 'Operable' },
  'button-name': { criterion: '4.1.2', level: 'A', principle: 'Robust' },
  'html-has-lang': { criterion: '3.1.1', level: 'A', principle: 'Understandable' },
  'document-title': { criterion: '2.4.2', level: 'A', principle: 'Operable' },
  'heading-order': { criterion: '1.3.1', level: 'A', principle: 'Perceivable' },
  'landmark-one-main': { criterion: '1.3.6', level: 'AAA', principle: 'Perceivable' },
  'region': { criterion: '1.3.6', level: 'AAA', principle: 'Perceivable' },
  'focus-trap': { criterion: '2.1.2', level: 'A', principle: 'Operable' },
  'keyboard': { criterion: '2.1.1', level: 'A', principle: 'Operable' },
  'tabindex': { criterion: '2.4.3', level: 'A', principle: 'Operable' },
  'aria-allowed-attr': { criterion: '4.1.2', level: 'A', principle: 'Robust' },
  'aria-required-attr': { criterion: '4.1.2', level: 'A', principle: 'Robust' },
  'aria-valid-attr': { criterion: '4.1.2', level: 'A', principle: 'Robust' },
  'aria-hidden-focus': { criterion: '4.1.2', level: 'A', principle: 'Robust' },
  'frame-title': { criterion: '2.4.1', level: 'A', principle: 'Operable' },
  'list': { criterion: '1.3.1', level: 'A', principle: 'Perceivable' },
  'listitem': { criterion: '1.3.1', level: 'A', principle: 'Perceivable' },
  'meta-viewport': { criterion: '1.4.4', level: 'AA', principle: 'Perceivable' },
  'skip-link': { criterion: '2.4.1', level: 'A', principle: 'Operable' },
  'form-field-multiple-labels': { criterion: '1.3.1', level: 'A', principle: 'Perceivable' }
}

const FIX_SUGGESTIONS = {
  'color-contrast': {
    description: 'Text must have sufficient contrast ratio against its background.',
    fix: `/* Ensure contrast ratio of at least 4.5:1 for normal text, 3:1 for large text */
/* Example: replace low-contrast colors */
.text-element {
  color: #1a1a1a;         /* dark text */
  background-color: #ffffff; /* white background — ratio 18.1:1 */
}
/* Tool: use https://webaim.org/resources/contrastchecker/ */`
  },
  'image-alt': {
    description: 'Images must have alternative text describing their content or purpose.',
    fix: `<!-- Informative image -->
<img src="chart.png" alt="Bar chart showing Q1 sales grew 20% over Q4" />

<!-- Decorative image — empty alt, role="presentation" -->
<img src="divider.png" alt="" role="presentation" />

<!-- Icon button — describe the action -->
<button>
  <img src="search.svg" alt="Search" />
</button>`
  },
  'label': {
    description: 'Form inputs must have an associated label so screen readers can announce them.',
    fix: `<!-- Option 1: explicit <label for="..."> -->
<label for="email">Email address</label>
<input type="email" id="email" name="email" />

<!-- Option 2: aria-label when no visible label is needed -->
<input type="search" aria-label="Search the site" />

<!-- Option 3: aria-labelledby pointing to visible text -->
<h2 id="billing">Billing address</h2>
<input type="text" aria-labelledby="billing" />`
  },
  'link-name': {
    description: 'Links must have discernible text so users know where they lead.',
    fix: `<!-- Bad: "click here" is meaningless out of context -->
<!-- <a href="/report">Click here</a> -->

<!-- Good: descriptive text -->
<a href="/report">Download accessibility report</a>

<!-- Icon-only link — use aria-label -->
<a href="/home" aria-label="Go to homepage">
  <svg aria-hidden="true">...</svg>
</a>`
  },
  'button-name': {
    description: 'Buttons must have an accessible name so screen readers can announce their purpose.',
    fix: `<!-- Text button — already accessible -->
<button type="button">Save changes</button>

<!-- Icon-only button — add aria-label -->
<button type="button" aria-label="Close dialog">
  <svg aria-hidden="true" focusable="false">...</svg>
</button>

<!-- Image button -->
<button type="submit">
  <img src="send.png" alt="Send message" />
</button>`
  },
  'html-has-lang': {
    description: 'The <html> element must have a lang attribute so assistive technology uses the correct language rules.',
    fix: `<!-- Add lang to the root element -->
<html lang="en">
  ...
</html>

<!-- For multilingual pages, also set lang on subsections -->
<p lang="es">Hola mundo</p>`
  },
  'document-title': {
    description: 'Every page must have a unique, descriptive <title> so users know where they are.',
    fix: `<head>
  <!-- Format: "Page Name | Site Name" -->
  <title>Checkout — Acme Store</title>
</head>

/* In React with react-helmet */
import { Helmet } from 'react-helmet'
<Helmet><title>Checkout — Acme Store</title></Helmet>`
  },
  'heading-order': {
    description: 'Headings must follow a logical nesting order (h1 → h2 → h3) without skipping levels.',
    fix: `<!-- Bad: jumps from h1 to h3 -->
<!-- <h1>Page title</h1><h3>Section</h3> -->

<!-- Good: sequential levels -->
<h1>Page title</h1>
  <h2>Main section</h2>
    <h3>Subsection</h3>
  <h2>Another section</h2>

<!-- Use CSS to control visual size, not heading level -->
.visually-large { font-size: 2rem; font-weight: bold; }`
  },
  'aria-allowed-attr': {
    description: 'ARIA attributes must be valid for the element\'s role.',
    fix: `<!-- Bad: aria-checked on a <div> with no role -->
<!-- <div aria-checked="true">Option</div> -->

<!-- Good: use the correct role or native element -->
<input type="checkbox" id="opt" checked />
<label for="opt">Option</label>

<!-- Or with explicit role -->
<div role="checkbox" aria-checked="true" tabindex="0">Option</div>`
  },
  'frame-title': {
    description: 'iframes must have a title attribute describing their content.',
    fix: `<!-- Add a descriptive title -->
<iframe
  src="https://example.com/map"
  title="Interactive location map"
  width="600"
  height="400"
></iframe>

<!-- Hidden/empty iframes used for scripts -->
<iframe src="tracker.html" title="Analytics tracker" aria-hidden="true"></iframe>`
  },
  'meta-viewport': {
    description: 'The viewport meta tag must not disable user scaling, which is needed by low-vision users.',
    fix: `<!-- Bad: user-scalable=no prevents zoom -->
<!-- <meta name="viewport" content="width=device-width, user-scalable=no"> -->

<!-- Good: allow scaling -->
<meta name="viewport" content="width=device-width, initial-scale=1" />`
  },
  'skip-link': {
    description: 'Pages must provide a way to skip repetitive navigation content.',
    fix: `<!-- Add as the first element inside <body> -->
<a href="#main-content" class="skip-link">Skip to main content</a>

<main id="main-content">
  <!-- page content -->
</main>

/* CSS — visible on focus, hidden otherwise */
.skip-link {
  position: absolute;
  top: -40px;
  left: 0;
  background: #000;
  color: #fff;
  padding: 8px;
  z-index: 100;
}
.skip-link:focus {
  top: 0;
}`
  }
}

function getFixSuggestion(ruleId) {
  if (FIX_SUGGESTIONS[ruleId]) return FIX_SUGGESTIONS[ruleId]
  return {
    description: 'Review the axe-core documentation for this rule.',
    fix: `// Visit https://dequeuniversity.com/rules/axe/4.8/${ruleId} for detailed guidance`
  }
}

describe('WCAG Accessibility Audit', () => {
  const targetUrl = Cypress.env('url') || 'https://example.com'

  before(() => {
    cy.log(`Auditing: ${targetUrl}`)
  })

  it(`runs full axe audit on ${targetUrl}`, () => {
    cy.visit(targetUrl, { failOnStatusCode: false })
    cy.injectAxe()

    const violations = []
    const passes = []
    const incomplete = []

    cy.checkA11y(
      null,
      {
        runOnly: {
          type: 'tag',
          values: ['wcag2a', 'wcag2aa', 'wcag21aa', 'best-practice']
        }
      },
      (axeViolations) => {
        axeViolations.forEach(v => {
          const wcag = WCAG_CRITERIA[v.id] || { criterion: 'N/A', level: v.tags.includes('wcag2a') ? 'A' : 'AA', principle: 'Unknown' }
          const fix = getFixSuggestion(v.id)
          violations.push({
            id: v.id,
            impact: v.impact,
            description: v.description,
            help: v.help,
            helpUrl: v.helpUrl,
            wcagCriterion: wcag.criterion,
            wcagLevel: wcag.level,
            principle: wcag.principle,
            tags: v.tags,
            nodes: v.nodes.map(n => ({
              html: n.html,
              target: n.target,
              failureSummary: n.failureSummary
            })),
            fixDescription: fix.description,
            fixCode: fix.fix
          })
        })
      },
      false  // do not fail the test on violations — we collect and report them ourselves
    )

    cy.then(() => {
      const reportData = {
        url: targetUrl,
        timestamp: new Date().toISOString(),
        violations,
        summary: {
          total: violations.length,
          critical: violations.filter(v => v.impact === 'critical').length,
          serious: violations.filter(v => v.impact === 'serious').length,
          moderate: violations.filter(v => v.impact === 'moderate').length,
          minor: violations.filter(v => v.impact === 'minor').length
        }
      }
      cy.task('saveReport', reportData)
    })
  })
})
