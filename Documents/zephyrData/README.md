# Zephyr Scale — Automation Coverage Dashboard

An interactive Streamlit dashboard that connects to **Zephyr Scale Cloud** via REST API to visualize test case automation coverage across projects and folders.

## Features

- **Project & folder filters** — drill down into any combination
- **KPI cards** — total test cases, automated, not automated, and coverage %
- **Donut chart** — overall automated vs. manual distribution
- **Stacked bar chart** — coverage breakdown by folder
- **Summary table** — per-folder totals and coverage %
- **Detail table** — full test case list with status, priority, labels, and automation flag
- **5-minute cache** — avoids rate limiting on the Zephyr Scale API

## How it works

A test case is classified as **automated** when it has the label `Automation Status` in Zephyr Scale. The label name is configurable via the `AUTOMATION_LABEL` constant in `dashboard.py`.

## Project structure

```
zephyrDashboard/
├── .cursor/
│   └── mcp.json        # SmartBear MCP config for Cursor IDE
├── .env.example        # Environment variable template
├── .gitignore
├── requirements.txt
├── zephyr_client.py    # Zephyr Scale Cloud REST API client
└── dashboard.py        # Streamlit app
```

## Setup

### 1. Get a Zephyr Scale API token

In Jira Cloud → **Zephyr Scale** → your profile icon → **API Access Tokens** → **Create Token**. Copy the generated token.

### 2. Configure environment variables

```bash
cp .env.example .env
```

Open `.env` and set your token:

```
ZEPHYR_API_TOKEN=your_token_here
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the dashboard

```bash
streamlit run dashboard.py
```

The app will open at `http://localhost:8501`.

## Cursor MCP integration

The `.cursor/mcp.json` file configures the [SmartBear MCP server](https://github.com/SmartBear/smartbear-mcp) so Cursor's AI can query Zephyr Scale directly. Requires Node.js installed.

Set `ZEPHYR_API_TOKEN` as an environment variable before opening Cursor, or update the value directly in `.cursor/mcp.json`.

## Requirements

- Python 3.10+
- Node.js (optional, for Cursor MCP only)
- Zephyr Scale Cloud account with API access
