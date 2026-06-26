# NSOC - Network Security Operations Center

**NSOC** is a hybrid learning lab & production security platform that integrates 5 security skills into a unified workflow engine with personality-driven AI agents. It operates in two modes: **SIMULATION** (safe learning environment) and **LIVE** (real-world security operations).

[![Dashboard](https://img.shields.io/badge/Dashboard-Live-success)](https://xlkd3tzcyhrtk.kimi.page)
[![Version](https://img.shields.io/badge/version-2.0.0-blue)](https://github.com/peteedoo/nsoc)
[![License](https://img.shields.io/badge/license-MIT-green)]()

## Features

- **Dual-Mode Operation**: SIMULATION for safe learning, LIVE for authorized real-world ops
- **5 Integrated Security Skills**: pentest-ai-agents, pentest-ai, nmap-mcp, security-dashboard, web-security-audit, code-vuln-audit
- **5 Agent Personalities**: Security Analyst, CEO, Security Engineer, Red Team, Blue Team
- **6 Pre-built Workflows**: Network Mapping, WebApp Audit, Traffic Analysis, Full Pentest, Code Security, Blue Team Monitoring
- **Web Dashboard**: React-based dark theme UI with real-time terminal
- **Python CLI**: Full terminal interface for scripting and automation

## Quick Start

### Dashboard (Web UI)

The web dashboard is deployed and accessible at:
**https://xlkd3tzcyhrtk.kimi.page**

### CLI

```bash
# Run the CLI
python3 cli/nsoc.py

# Or with commands
python3 cli/nsoc.py status
python3 cli/nsoc.py workflow list
python3 cli/nsoc.py workflow run network-map --target 192.168.1.0/24
python3 cli/nsoc.py agent set red-team
python3 cli/nsoc.py mode live
```

## Agent Personalities

| Personality | Role | Focus | Auto-Approve |
|---|---|---|---|
| **Default** | Security Analyst | Balanced technical analysis | No |
| **CEO** | Executive | Business impact, dollars, ROI | No |
| **Coder** | Security Engineer | Raw CLI, code fixes, patches | No |
| **Red Team** | Offensive Operator | Exploit chaining, lateral movement | Yes |
| **Blue Team** | Defender | Detection, IR, hardening | No |

## Workflows

| Workflow | Category | Steps | Description |
|---|---|---|---|
| `network-map` | Network | 4 | Host discovery, port scan, service detection, OS fingerprinting |
| `webapp-audit` | WebApp | 5 | OWASP Top 10 assessment with code scanning |
| `traffic-analysis` | Network | 3 | PCAP capture, protocol analysis, anomaly detection |
| `full-pentest` | Offensive | 5 | Complete pentest from recon to post-exploitation |
| `code-security` | Code | 3 | Dependency, secret, and OWASP pattern scanning |
| `blue-team-monitor` | Monitoring | 4 | Gateway, surface, TLS, and resource monitoring |

## Project Structure

```
nsoc/
├── core/
│   └── engine.py          # Central orchestration engine
├── agents/
│   └── personalities/
│       ├── default.json    # Security Analyst
│       ├── ceo.json        # Executive
│       ├── coder.json      # Security Engineer
│       ├── red-team.json   # Offensive Operator
│       └── blue-team.json  # Defender
├── cli/
│   └── nsoc.py            # Python CLI
├── dashboard/             # React web dashboard
│   ├── src/
│   │   ├── App.tsx
│   │   ├── sections/
│   │   │   ├── DashboardView.tsx
│   │   │   ├── WorkflowsView.tsx
│   │   │   ├── TerminalView.tsx
│   │   │   ├── ResultsView.tsx
│   │   │   ├── SkillsView.tsx
│   │   │   └── SettingsView.tsx
│   │   ├── components/
│   │   │   ├── ModeToggle.tsx
│   │   │   └── PersonalitySelector.tsx
│   │   ├── lib/
│   │   │   └── data.ts
│   │   └── types/
│   │       └── index.ts
│   └── dist/              # Built dashboard
└── README.md
```

## Safety & Ethics

- **SIMULATION mode** is safe for learning - all operations are simulated
- **LIVE mode** requires explicit authorization - real tools execute on real targets
- Only use LIVE mode on systems you own or have written authorization to test
- Scope guardrails are active in LIVE mode
- Red Team personality auto-approves steps - use with caution

## License

MIT
