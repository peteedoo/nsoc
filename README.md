# NSOC - Network Security Operations Center

**Live App:** https://xlkd3tzcyhrtk.kimi.page

Hybrid security learning lab & production platform. Installable PWA with 5 agent personalities, 6 workflows, 17 defense guides, and dual-mode operation.

## Install on Your Phone

**Android (Chrome):** Open the link → tap "Install NSOC" banner

**iPhone (Safari):** Open the link → Share → "Add to Home Screen"

## What's New in v2.2

### Persistence
Your preferences are saved automatically: mode (SIM/LIVE), personality, active view, completed remediation steps, and visited guides. Everything survives browser restarts.

### Global Search (Ctrl+K)
Search across all workflows, remediation guides, and skills from anywhere in the app. Results are instant and categorized by type.

### Onboarding Flow
First-time users see a 5-slide walkthrough covering: welcome, dual-mode operation, personality-driven agents, defense mode, and mobile installation. Ends with a personality picker.

### Refined Mobile UX
- **Bottom navigation** with 5 primary tabs (Dash, Flows, Term, Defend, Findings)
- **Active indicators** — subtle top-line highlight on the active tab
- **Touch-optimized** — 44px+ tap targets, active state feedback
- **Responsive grids** — auto-collapse to single column on phones
- **Animations** — fadeIn, slideUp, stagger on all views

### Visual Polish
- Card hover effects with subtle lift
- Custom thin scrollbar
- Backdrop blur on overlays
- Focus-visible rings for accessibility
- Staggered entry animations on lists

## Architecture

| Layer | Components |
|---|---|
| **Core** | Python engine with async workflow execution |
| **CLI** | Full terminal interface (`nsoc.py`) |
| **Dashboard** | React + TypeScript + Tailwind + Recharts |
| **Agents** | 5 JSON personality files |
| **Skills** | pentest-ai-agents, pentest-ai, nmap-mcp, security-dashboard, web-security-audit, code-vuln-audit |
| **PWA** | Service worker, manifest, 8 icon sizes, offline support |

## License

MIT
