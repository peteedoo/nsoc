# NSOC - Network Security Operations Center

**Live:** https://xlkd3tzcyhrtk.kimi.page

Hybrid security learning lab & production platform. Installable PWA.

## Install on Your Phone

**Android:** Open link in Chrome → tap "Install NSOC"

**iPhone:** Open link in Safari → Share → "Add to Home Screen"

## v2.2 Refinements

### Responsive-First Layouts
All 7 views now use mobile-first responsive grids:
- **Dashboard**: 2-col stats → 4-col desktop, stacked charts, 2-3-6 col skills
- **Workflows**: Single column → 3-column split-pane on desktop
- **Results**: 2-col risk cards → 5-col desktop
- **Skills**: Single column → 2-column cards, grid architecture diagram
- **Settings**: Stacked → 2-column mode cards, centered max-width

### Persistence
- Mode, personality, active view saved to localStorage
- Remediation step completion persists across sessions
- Onboarding shown only once

### Global Search (Ctrl+K)
Search across all workflows, remediation guides, and skills.

### Onboarding
5-slide walkthrough for first-time users ending with personality picker.

### Animations
- fadeIn on view transitions
- stagger-children with progressive delays
- Card hover lift effect
- Backdrop blur on overlays

### Navigation Labels
Dash · Flows · Term · Defend · Findings (mobile bottom nav)

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

## Bootable Kali Linux (USB)

Build a **custom, USB-bootable Kali Linux** with NSOC and its security
toolchain pre-installed — boot it anywhere, no install required.

```bash
cd kali-build
sudo ./build.sh                                  # build the ISO (Debian/Kali host)
sudo ./flash-usb.sh images/<image>.iso /dev/sdX  # write it to a USB stick
```

Boot the stick (Live mode) and run `nsoc`. See
[`kali-build/README.md`](kali-build/README.md) for variants, persistence,
and customization.

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
├── kali-build/                 # Custom bootable Kali Linux build
│   ├── build.sh                # Build the ISO (wraps Kali live-build)
│   ├── flash-usb.sh            # Write the ISO to a USB stick
│   └── config/                 # Package lists, hooks, file overlays
└── README.md
```

## License
MIT
