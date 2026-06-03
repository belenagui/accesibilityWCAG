const { defineConfig } = require('cypress')

module.exports = defineConfig({
  e2e: {
    specPattern: 'cypress/e2e/**/*.cy.js',
    supportFile: 'cypress/support/e2e.js',
    reporter: 'json',
    reporterOptions: {
      output: 'results/axe-report.json'
    },
    video: false,
    screenshotOnRunFailure: false,
    setupNodeEvents(on, config) {
      on('task', {
        log(message) {
          console.log(message)
          return null
        },
        saveReport(report) {
          const fs = require('fs')
          const path = require('path')
          const dir = path.join(__dirname, 'results')
          if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true })
          fs.writeFileSync(
            path.join(dir, 'axe-results.json'),
            JSON.stringify(report, null, 2)
          )
          return null
        }
      })
    }
  }
})
