# NSOC - Network Security Operations Center

**NSOC** is a hybrid learning lab & production security platform with **Defense Mode** — it doesn't just find issues, it teaches you how to fix them. Integrates 5 security skills into a unified workflow engine with personality-driven AI agents.

[![Dashboard](https://img.shields.io/badge/Dashboard-Live-success)](https://xlkd3tzcyhrtk.kimi.page)
[![Version](https://img.shields.io/badge/version-2.1.0-blue)](https://github.com/peteedoo/nsoc)
[![Guides](https://img.shields.io/badge/remediation_guides-17-orange)](https://github.com/peteedoo/nsoc)

## What's New in v2.1 — Defense Mode

NSOC now includes a **Defense & Remediation** tab that transforms every finding into a learning opportunity:

- **17 Detailed Remediation Guides** covering network, web app, code, TLS, and monitoring issues
- **Side-by-side Code Comparisons** — see vulnerable code next to the fixed version
- **Step-by-step Fix Instructions** with completion tracking
- **Learning Paths** — Beginner → Intermediate → Advanced progressions
- **Active Findings** — auto-matches scan results to relevant remediation guides
- **Why It Matters** — real-world context for every vulnerability
- **Verification Commands** — test that your fix actually worked

## Features

### Dual-Mode Operation
- **SIMULATION** — Safe learning environment with realistic results
- **LIVE** — Real security tools on authorized targets

### 5 Agent Personalities
| Personality | Role | Focus |
|---|---|---|
| **Default** | Security Analyst | Balanced technical analysis |
| **CEO** | Executive | Business impact, dollars, ROI |
| **Coder** | Security Engineer | Raw CLI, code fixes, patches |
| **Red Team** | Offensive Operator | Exploit chaining, lateral movement |
| **Blue Team** | Defender | Detection, IR, hardening |

### 6 Security Workflows
- Network Discovery & Mapping
- Web Application Security Audit
- Traffic Analysis & Monitoring
- Full Penetration Test
- Code Security Assessment
- Blue Team Monitoring Setup

### Remediation Coverage (17 Guides)
| Category | Guides |
|---|---|
| **Network** | Exposed MySQL, SSH hardening, RDP filtering, Kernel updates |
| **Web App** | SQL injection, XSS, Exposed .env files |
| **Code Security** | Vulnerable deps, Exposed secrets, Weak hashing, Deserialization, Debug mode |
| **TLS** | Weak ciphers, Certificate expiry |
| **Monitoring** | Port scan response, Unencrypted auth |

## Quick Start

### Web Dashboard
**https://xlkd3tzcyhrtk.kimi.page**

Click the **Defense** (shield) icon in the sidebar to enter Defense Mode.

### CLI
```bash
python3 cli/nsoc.py

# Run a scan then see remediation
python3 cli/nsoc.py workflow run network-map --target 192.168.1.0/24
python3 cli/nsoc.py workflow run webapp-audit --target example.com
```

## Project Structure

```
nsoc/
├── core/engine.py              # Orchestration engine
├── cli/nsoc.py                 # Terminal CLI
├── agents/personalities/       # 5 personality JSON files
├── dashboard/
│   ├── src/
│   │   ├── App.tsx             # Main app with 7 views
│   │   ├── sections/
│   │   │   ├── DashboardView.tsx
│   │   │   ├── WorkflowsView.tsx
│   │   │   ├── TerminalView.tsx
│   │   │   ├── ResultsView.tsx
│   │   │   ├── SkillsView.tsx
│   │   │   ├── RemediationView.tsx   # NEW: Defense mode
│   │   │   └── SettingsView.tsx
│   │   ├── lib/
│   │   │   ├── data.ts         # Simulation data
│   │   │   └── remediation.ts  # NEW: 17 remediation guides
│   │   └── types/
│   │       └── index.ts
│   └── dist/                   # Built dashboard
└── README.md
```

## License

MIT
