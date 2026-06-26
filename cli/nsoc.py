#!/usr/bin/env python3
"""
NSOC CLI - Network Security Operations Center Command Line Interface
Usage: nsoc [workflow|scan|monitor|agent|report|config] [options]
"""

import sys
import json
import asyncio
import argparse
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))
from core.engine import NSOCEngine, OpMode, get_engine


class NSOCCLI:
    def __init__(self):
        self.engine = get_engine(OpMode.SIMULATION, "default")

    def print_banner(self):
        mode = self.engine.mode.value
        print(f"""
   _   _  ___   ___   ____
  | \\ | |/ _ \\ / _ \\ / ___|   Network Security Operations Center
  |  \\| | | | | | | | |      v2.0.0 - Hybrid Lab & Production
  | |\\  | |_| | |_| | |___    Mode: {mode.upper()}
  |_| \\_|\\___/ \\___/ \\____|   Agent: {self.engine.personality.upper()}

  Type 'nsoc --help' for commands.
        """)

    def workflow_list(self, args):
        print("\nAvailable Workflows:\n")
        for wf in self.engine.list_workflows():
            print(f"  {wf['id']:<20} {wf['name']} ({wf['step_count']} steps)")
            print(f"                       {wf['description']}\n")

    def workflow_run(self, args):
        if not args.target:
            print("Error: --target is required"); return 1
        workflow = self.engine.create_workflow(args.workflow, args.target)
        if not workflow:
            print(f"Error: Unknown workflow '{args.workflow}'"); return 1
        print(f"\nStarting: {workflow.name}\nTarget: {workflow.target}\n")

        async def run():
            for step in workflow.steps:
                print(f"\n[Step {step.id}] {step.name}")
                print(f"  Command: {step.command}")
                result = await self.engine.execute_step(workflow.id, step.id)
                print(f"  Status: {result.risk_level.upper()} | Findings: {len(result.findings)}")
                if result.persona_adapted_output:
                    print(f"  > {result.persona_adapted_output}")
            print("\nWorkflow complete.")

        asyncio.run(run())
        return 0

    def scan(self, args):
        wf_map = {"network": "network-map", "webapp": "webapp-audit",
                  "traffic": "traffic-analysis", "code": "code-security"}
        wf_id = wf_map.get(args.scan_type, args.scan_type)
        return self.workflow_run(argparse.Namespace(
            workflow=wf_id, target=args.target, dry_run=getattr(args, 'dry_run', False),
            yes=args.yes, verbose=args.verbose, export=getattr(args, 'export', None)))

    def agent_list(self, args):
        pd = Path(__file__).parent.parent / "agents" / "personalities"
        print("\nAgent Personalities:\n")
        for f in sorted(pd.glob("*.json")):
            p = json.load(f.open())
            print(f"  {p['name']:<15} {p['display_name']}")
            print(f"                 {p['description']}\n")

    def agent_set(self, args):
        self.engine.set_personality(args.personality)
        print(f"Switched to: {args.personality}")
        return 0

    def mode(self, args):
        if args.mode == "live":
            print("WARNING: LIVE mode executes real commands!")
            resp = input("Authorized? [yes/no]: ")
            if resp.lower() != "yes":
                print("Aborted."); return 1
            self.engine.set_mode(OpMode.LIVE)
            print(">>> LIVE MODE ACTIVATED <<<")
        else:
            self.engine.set_mode(OpMode.SIMULATION)
            print("[SIMULATION MODE]")
        return 0

    def status(self, args):
        s = self.engine.get_status()
        print(f"\nMode: {s['mode'].upper()}")
        print(f"Personality: {s['personality']}")
        print(f"Workflows: {s['active_workflows']} active")
        return 0

    def skills_list(self, args):
        print("\nIntegrated Skills:\n")
        for s in self.engine.list_skills():
            print(f"  {s['name']} [{s['category']}] - {len(s['tools'])} tools")


def main():
    parser = argparse.ArgumentParser(prog='nsoc', description='NSOC - Network Security Operations Center')
    parser.add_argument('--version', action='version', version='NSOC 2.0.0')
    parser.add_argument('--live', action='store_true')
    parser.add_argument('-y', '--yes', action='store_true')
    parser.add_argument('-v', '--verbose', action='store_true')

    sub = parser.add_subparsers(dest='command')
    sub.add_parser('status', help='Show status')

    mode_p = sub.add_parser('mode', help='Switch mode')
    mode_p.add_argument('mode', choices=['simulation', 'live'])

    agent_p = sub.add_parser('agent', help='Manage personalities')
    agent_s = agent_p.add_subparsers(dest='agent_cmd')
    agent_s.add_parser('list', help='List personalities')
    agent_set = agent_s.add_parser('set', help='Set personality')
    agent_set.add_argument('personality')

    wf_p = sub.add_parser('workflow', help='Manage workflows')
    wf_s = wf_p.add_subparsers(dest='wf_cmd')
    wf_s.add_parser('list', help='List workflows')
    wf_run = wf_s.add_parser('run', help='Run workflow')
    wf_run.add_argument('workflow')
    wf_run.add_argument('--target', '-t', required=True)
    wf_run.add_argument('--dry-run', action='store_true')
    wf_run.add_argument('--export', choices=['json', 'markdown'])

    scan_p = sub.add_parser('scan', help='Quick scan')
    scan_p.add_argument('scan_type', choices=['network', 'webapp', 'traffic', 'code'])
    scan_p.add_argument('--target', '-t', required=True)

    sub.add_parser('skills', help='List skills')

    args = parser.parse_args()
    cli = NSOCCLI()
    if args.live: cli.engine.set_mode(OpMode.LIVE)

    if not args.command:
        cli.print_banner(); parser.print_help(); return 0

    handlers = {
        'status': cli.status, 'mode': cli.mode,
        'agent': lambda a: cli.agent_list(a) if a.agent_cmd == 'list' else cli.agent_set(a),
        'workflow': lambda a: cli.workflow_list(a) if a.wf_cmd == 'list' else cli.workflow_run(a),
        'scan': cli.scan, 'skills': cli.skills_list,
    }
    h = handlers.get(args.command)
    return h(args) or 0 if h else (parser.print_help() or 1)


if __name__ == '__main__':
    sys.exit(main())
