const express = require('express')
const cors = require('cors')
const { spawn } = require('child_process')
const path = require('path')
const fs = require('fs')

const app = express()
const PORT = 3000
const RESULTS_FILE = path.join(__dirname, '..', 'results', 'axe-results.json')

app.use(cors())
app.use(express.json())
app.use(express.static(path.join(__dirname, '..', 'public')))

let runStatus = { running: false, log: [], error: null }

app.post('/api/audit', (req, res) => {
  const { url } = req.body
  if (!url || !url.startsWith('http')) {
    return res.status(400).json({ error: 'Please provide a valid URL starting with http:// or https://' })
  }

  if (runStatus.running) {
    return res.status(409).json({ error: 'An audit is already running. Please wait.' })
  }

  // Clear previous results
  if (fs.existsSync(RESULTS_FILE)) fs.unlinkSync(RESULTS_FILE)
  runStatus = { running: true, log: [], error: null, url }

  res.json({ message: 'Audit started', url })

  const isWindows = process.platform === 'win32'
  const cypressBin = path.join(__dirname, '..', 'node_modules', '.bin', isWindows ? 'cypress.cmd' : 'cypress')

  // Verify Cypress binary exists before spawning
  if (!fs.existsSync(cypressBin)) {
    runStatus.running = false
    runStatus.error = `Cypress binary not found at ${cypressBin}. Run: npm install`
    return
  }

  const child = spawn(
    cypressBin,
    ['run', '--spec', 'cypress/e2e/accessibility.cy.js', '--env', `url=${url}`],
    {
      cwd: path.join(__dirname, '..'),
      env: { ...process.env, FORCE_COLOR: '0' }
    }
  )

  // Kill Cypress if it hangs for more than 2 minutes
  const killTimer = setTimeout(() => {
    if (runStatus.running) {
      child.kill('SIGTERM')
      runStatus.running = false
      runStatus.error = 'Audit timed out after 2 minutes. The page may be unreachable or require authentication.'
    }
  }, 120000)

  child.stdout.on('data', d => {
    const line = d.toString().trim()
    if (line) runStatus.log.push(line)
  })
  child.stderr.on('data', d => {
    const line = d.toString().trim()
    if (line) runStatus.log.push(`[stderr] ${line}`)
  })

  child.on('error', (err) => {
    clearTimeout(killTimer)
    runStatus.running = false
    runStatus.error = `Failed to start Cypress: ${err.message}`
  })

  child.on('close', (code) => {
    clearTimeout(killTimer)
    runStatus.running = false
    if (code !== 0 && !fs.existsSync(RESULTS_FILE)) {
      const lastLogs = runStatus.log.slice(-5).join(' | ')
      runStatus.error = `Cypress exited with code ${code}. ${lastLogs}`
    }
  })
})

app.get('/api/status', (req, res) => {
  res.json(runStatus)
})

app.get('/api/results', (req, res) => {
  if (!fs.existsSync(RESULTS_FILE)) {
    return res.status(404).json({ error: 'No results yet. Run an audit first.' })
  }
  try {
    const data = JSON.parse(fs.readFileSync(RESULTS_FILE, 'utf8'))
    res.json(data)
  } catch {
    res.status(500).json({ error: 'Failed to parse results file.' })
  }
})

app.listen(PORT, () => {
  console.log(`\nAccessibility Reporter running at http://localhost:${PORT}\n`)
})
