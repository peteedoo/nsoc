#!/usr/bin/env python3
"""
NSOC Core Engine - Agent Orchestration & Workflow Manager
Manages the lifecycle of security operations across all 5 integrated skills.
Supports both SIMULATION (learning lab) and LIVE (real-world) modes.
"""

import os
import json
import asyncio
import subprocess
from datetime import datetime
from typing import Dict, List, Optional, Any, Literal
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path


class OpMode(Enum):
    SIMULATION = "simulation"  # Learning lab - safe, educational
    LIVE = "live"              # Real-world - requires confirmation


class AgentState(Enum):
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    ERROR = "error"
    AWAITING_APPROVAL = "awaiting_approval"


@dataclass
class OperationResult:
    """Result of a security operation."""
    tool: str
    command: str
    stdout: str
    stderr: str
    returncode: int
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    findings: List[Dict] = field(default_factory=list)
    risk_level: str = "info"  # info, low, medium, high, critical
    persona_adapted_output: str = ""  # Output adapted by personality


@dataclass
class WorkflowStep:
    """A single step in a security workflow."""
    id: str
    name: str
    skill: str  # Which of the 5 skills this uses
    tool: str
    command: str
    description: str
    requires_approval_in_live: bool = True
    estimated_duration: int = 60  # seconds
    depends_on: List[str] = field(default_factory=list)


@dataclass
class Workflow:
    """A complete security workflow composed of steps."""
    id: str
    name: str
    description: str
    category: str  # recon, webapp, network, code, compliance
    steps: List[WorkflowStep] = field(default_factory=list)
    mode: OpMode = OpMode.SIMULATION
    target: str = ""
    state: AgentState = AgentState.IDLE
    results: List[OperationResult] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


class NSOCEngine:
    """
    Central orchestration engine for NSOC.
    Coordinates all 5 skills with personality-driven agents.
    """

    SKILL_MAP = {
        "pentest-ai-agents": {
            "name": "Pentest AI Agents",
            "category": "offensive",
            "tools": ["recon-advisor", "network-attacker", "traffic-analyzer",
                     "ad-attacker", "web-hunter", "api-security", "lateral-movement",
                     "persistence-planner", "evasion-specialist"],
        },
        "pentest-ai": {
            "name": "Pentest AI (ptai)",
            "category": "offensive",
            "tools": ["nmap", "masscan", "nuclei", "ffuf", "sqlmap",
                     "bloodhound-python", "netexec", "impacket"],
        },
        "nmap-mcp": {
            "name": "Nmap MCP Server",
            "category": "network",
            "tools": ["host-discovery", "port-scan-syn", "port-scan-tcp",
                     "port-scan-udp", "service-detection", "os-detection", "nse-scripts"],
        },
        "security-dashboard": {
            "name": "Security Dashboard",
            "category": "monitoring",
            "tools": ["gateway-monitor", "network-security", "exposed-surface",
                     "system-updates", "ssh-monitor", "tls-monitor", "resource-usage"],
        },
        "web-security-audit": {
            "name": "Web Security Audit",
            "category": "webapp",
            "tools": ["owasp-a01", "owasp-a02", "owasp-a03", "owasp-a04",
                     "owasp-a05", "owasp-a06", "owasp-a07", "owasp-a08",
                     "owasp-a09", "owasp-a10"],
        },
        "code-vuln-audit": {
            "name": "Code Vulnerability Audit",
            "category": "code",
            "tools": ["deps-scan", "secrets-scan", "owasp-pattern-scan"],
        },
    }

    WORKFLOW_TEMPLATES = {
        "network-map": {
            "name": "Network Discovery & Mapping",
            "description": "Discover and map network topology, hosts, services, and OS",
            "category": "network",
            "steps": [
                {"id": "nm-1", "name": "Host Discovery", "skill": "nmap-mcp",
                 "tool": "host-discovery", "command": "nmap -sn {target}",
                 "description": "Discover live hosts on the network", "requires_approval_in_live": False},
                {"id": "nm-2", "name": "Port Scan", "skill": "nmap-mcp",
                 "tool": "port-scan-syn", "command": "nmap -sS -p- {target}",
                 "description": "Scan all ports on discovered hosts", "depends_on": ["nm-1"]},
                {"id": "nm-3", "name": "Service Detection", "skill": "nmap-mcp",
                 "tool": "service-detection", "command": "nmap -sV -A {target}",
                 "description": "Detect services and versions", "depends_on": ["nm-2"]},
                {"id": "nm-4", "name": "OS Fingerprinting", "skill": "nmap-mcp",
                 "tool": "os-detection", "command": "nmap -O {target}",
                 "description": "Identify operating systems", "depends_on": ["nm-2"]},
            ]
        },
        "webapp-audit": {
            "name": "Web Application Security Audit",
            "description": "Full OWASP Top 10 web application security assessment",
            "category": "webapp",
            "steps": [
                {"id": "wa-1", "name": "Reconnaissance", "skill": "pentest-ai-agents",
                 "tool": "recon-advisor", "command": "ptai recon {target}",
                 "description": "Initial reconnaissance and discovery"},
                {"id": "wa-2", "name": "OWASP Top 10 Scan", "skill": "web-security-audit",
                 "tool": "owasp-a03", "command": "ptai scan --owasp {target}",
                 "description": "Check for injection vulnerabilities", "depends_on": ["wa-1"]},
                {"id": "wa-3", "name": "XSS Testing", "skill": "web-security-audit",
                 "tool": "owasp-a03", "command": "ptai xss --target {target}",
                 "description": "Test for cross-site scripting", "depends_on": ["wa-1"]},
                {"id": "wa-4", "name": "Auth Testing", "skill": "web-security-audit",
                 "tool": "owasp-a07", "command": "ptai auth --target {target}",
                 "description": "Test authentication mechanisms", "depends_on": ["wa-1"]},
                {"id": "wa-5", "name": "Code Scan", "skill": "code-vuln-audit",
                 "tool": "owasp-pattern-scan", "command": "nsoc-scan code --target {target}",
                 "description": "Scan source code for vulnerabilities", "depends_on": ["wa-1"]},
            ]
        },
        "traffic-analysis": {
            "name": "Traffic Analysis & Monitoring",
            "description": "Capture, analyze, and monitor network traffic for anomalies",
            "category": "network",
            "steps": [
                {"id": "ta-1", "name": "Traffic Capture", "skill": "pentest-ai-agents",
                 "tool": "traffic-analyzer", "command": "tcpdump -i any -w capture.pcap",
                 "description": "Capture network traffic to pcap file"},
                {"id": "ta-2", "name": "Protocol Analysis", "skill": "pentest-ai-agents",
                 "tool": "traffic-analyzer", "command": "ptai traffic --analyze capture.pcap",
                 "description": "Analyze protocols and extract metadata", "depends_on": ["ta-1"]},
                {"id": "ta-3", "name": "Anomaly Detection", "skill": "security-dashboard",
                 "tool": "network-security", "command": "nsoc-monitor anomalies --pcap capture.pcap",
                 "description": "Detect traffic anomalies and patterns", "depends_on": ["ta-2"]},
            ]
        },
        "full-pentest": {
            "name": "Full Penetration Test",
            "description": "Complete penetration test from recon to post-exploitation",
            "category": "offensive",
            "steps": [
                {"id": "pt-1", "name": "Network Recon", "skill": "pentest-ai-agents",
                 "tool": "recon-advisor", "command": "ptai recon --full {target}",
                 "description": "Comprehensive reconnaissance"},
                {"id": "pt-2", "name": "Port & Service Scan", "skill": "nmap-mcp",
                 "tool": "port-scan-syn", "command": "nmap -sS -sV -A -p- {target}",
                 "description": "Full port and service enumeration", "depends_on": ["pt-1"]},
                {"id": "pt-3", "name": "Vulnerability Scan", "skill": "pentest-ai",
                 "tool": "nuclei", "command": "nuclei -u {target} -severity critical,high",
                 "description": "Vulnerability assessment", "depends_on": ["pt-2"]},
                {"id": "pt-4", "name": "Web App Testing", "skill": "web-security-audit",
                 "tool": "owasp-a03", "command": "ptai web --full {target}",
                 "description": "Web application penetration testing", "depends_on": ["pt-2"]},
                {"id": "pt-5", "name": "Traffic Analysis", "skill": "pentest-ai-agents",
                 "tool": "traffic-analyzer", "command": "ptai traffic --capture {target}",
                 "description": "Capture and analyze traffic", "depends_on": ["pt-3", "pt-4"]},
            ]
        },
        "code-security": {
            "name": "Code Security Assessment",
            "description": "Scan codebase for vulnerabilities, secrets, and dependency issues",
            "category": "code",
            "steps": [
                {"id": "cs-1", "name": "Dependency Scan", "skill": "code-vuln-audit",
                 "tool": "deps-scan", "command": "nsoc-scan deps {target}",
                 "description": "Scan for vulnerable dependencies", "requires_approval_in_live": False},
                {"id": "cs-2", "name": "Secret Detection", "skill": "code-vuln-audit",
                 "tool": "secrets-scan", "command": "nsoc-scan secrets {target}",
                 "description": "Find leaked secrets and credentials", "requires_approval_in_live": False},
                {"id": "cs-3", "name": "OWASP Pattern Scan", "skill": "code-vuln-audit",
                 "tool": "owasp-pattern-scan", "command": "nsoc-scan owasp {target}",
                 "description": "Detect OWASP anti-patterns in code", "depends_on": ["cs-1", "cs-2"]},
            ]
        },
        "blue-team-monitor": {
            "name": "Blue Team Monitoring Setup",
            "description": "Deploy continuous security monitoring and detection",
            "category": "monitoring",
            "steps": [
                {"id": "bt-1", "name": "Gateway Monitor", "skill": "security-dashboard",
                 "tool": "gateway-monitor", "command": "nsoc-monitor gateway --enable",
                 "description": "Monitor gateway status and traffic", "requires_approval_in_live": False},
                {"id": "bt-2", "name": "Exposed Surface Scan", "skill": "security-dashboard",
                 "tool": "exposed-surface", "command": "nsoc-monitor surface --scan {target}",
                 "description": "Scan for exposed attack surfaces"},
                {"id": "bt-3", "name": "TLS Certificate Monitor", "skill": "security-dashboard",
                 "tool": "tls-monitor", "command": "nsoc-monitor tls --watch {target}",
                 "description": "Monitor TLS certificate health", "depends_on": ["bt-2"]},
                {"id": "bt-4", "name": "Resource Monitoring", "skill": "security-dashboard",
                 "tool": "resource-usage", "command": "nsoc-monitor resources --enable",
                 "description": "Monitor system resource usage", "requires_approval_in_live": False},
            ]
        },
    }

    def __init__(self, mode: OpMode = OpMode.SIMULATION, personality: str = "default"):
        self.mode = mode
        self.personality = personality
        self.active_workflows: Dict[str, Workflow] = {}
        self.history: List[Workflow] = []
        self.personality_config = self._load_personality(personality)

    def _load_personality(self, name: str) -> Dict:
        """Load a personality configuration file."""
        personality_path = Path(__file__).parent.parent / "agents" / "personalities" / f"{name}.json"
        if personality_path.exists():
            with open(personality_path) as f:
                return json.load(f)
        return {
            "name": "default", "role": "Security Analyst",
            "communication_style": "technical", "risk_threshold": "medium",
            "auto_approve": False, "verbosity": "detailed",
            "decision_weights": {"business_impact": 0.3, "technical_severity": 0.5, "exploitability": 0.2},
        }

    def set_personality(self, name: str) -> Dict:
        self.personality = name
        self.personality_config = self._load_personality(name)
        return self.personality_config

    def set_mode(self, mode: OpMode) -> None:
        self.mode = mode

    def list_workflows(self) -> List[Dict]:
        return [{"id": k, "name": w["name"], "description": w["description"],
                 "category": w["category"], "step_count": len(w["steps"])}
                for k, w in self.WORKFLOW_TEMPLATES.items()]

    def list_skills(self) -> List[Dict]:
        return [{"id": k, "name": s["name"], "category": s["category"], "tools": s["tools"]}
                for k, s in self.SKILL_MAP.items()]

    def create_workflow(self, template_id: str, target: str) -> Optional[Workflow]:
        if template_id not in self.WORKFLOW_TEMPLATES:
            return None
        tmpl = self.WORKFLOW_TEMPLATES[template_id]
        steps = [WorkflowStep(**{**step, "command": step["command"].format(target=target)})
                 for step in tmpl["steps"]]
        workflow = Workflow(
            id=f"{template_id}-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            name=tmpl["name"], description=tmpl["description"],
            category=tmpl["category"], steps=steps,
            mode=self.mode, target=target,
        )
        self.active_workflows[workflow.id] = workflow
        return workflow

    async def execute_step(self, workflow_id: str, step_id: str) -> OperationResult:
        workflow = self.active_workflows.get(workflow_id)
        if not workflow:
            raise ValueError(f"Workflow {workflow_id} not found")
        step = next((s for s in workflow.steps if s.id == step_id), None)
        if not step:
            raise ValueError(f"Step {step_id} not found")

        for dep_id in step.depends_on:
            dep_results = [r for r in workflow.results if r.tool == dep_id]
            if not dep_results:
                return OperationResult(tool=step.tool, command=step.command, stdout="",
                    stderr=f"Dependency {dep_id} not completed", returncode=-1, risk_level="error")

        if workflow.mode == OpMode.LIVE and step.requires_approval_in_live:
            if not self.personality_config.get("auto_approve", False):
                workflow.state = AgentState.AWAITING_APPROVAL
                return OperationResult(tool=step.tool, command=step.command, stdout="",
                    stderr="AWAITING_APPROVAL", returncode=-2, risk_level="info")

        workflow.state = AgentState.RUNNING

        if workflow.mode == OpMode.SIMULATION:
            result = await self._simulate_execution(step)
        else:
            result = await self._execute_live(step)

        result.persona_adapted_output = self._adapt_by_personality(result)
        workflow.results.append(result)

        if len(workflow.results) == len(workflow.steps):
            workflow.state = AgentState.COMPLETED
        return result

    async def _simulate_execution(self, step: WorkflowStep) -> OperationResult:
        simulations = {
            "host-discovery": self._sim_host_discovery,
            "port-scan-syn": self._sim_port_scan,
            "service-detection": self._sim_service_detection,
            "os-detection": self._sim_os_detection,
            "recon-advisor": self._sim_recon,
            "traffic-analyzer": self._sim_traffic,
            "nuclei": self._sim_nuclei,
            "deps-scan": self._sim_deps_scan,
            "secrets-scan": self._sim_secrets_scan,
            "owasp-pattern-scan": self._sim_owasp_scan,
            "gateway-monitor": self._sim_gateway,
            "exposed-surface": self._sim_surface,
            "tls-monitor": self._sim_tls,
            "resource-usage": self._sim_resources,
        }
        sim_func = simulations.get(step.tool, self._sim_generic)
        stdout, findings, risk = sim_func(step.command)
        await asyncio.sleep(1)
        return OperationResult(tool=step.tool, command=step.command, stdout=stdout,
            stderr="", returncode=0, findings=findings, risk_level=risk)

    async def _execute_live(self, step: WorkflowStep) -> OperationResult:
        try:
            proc = await asyncio.create_subprocess_shell(step.command,
                stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
            stdout, stderr = await proc.communicate()
            findings = self._parse_findings(stdout.decode())
            risk = self._assess_risk(findings)
            return OperationResult(tool=step.tool, command=step.command,
                stdout=stdout.decode(), stderr=stderr.decode(),
                returncode=proc.returncode or 0, findings=findings, risk_level=risk)
        except Exception as e:
            return OperationResult(tool=step.tool, command=step.command,
                stdout="", stderr=str(e), returncode=-1, risk_level="error")

    def _adapt_by_personality(self, result: OperationResult) -> str:
        style = self.personality_config.get("communication_style", "technical")
        if style == "executive": return self._to_executive_summary(result)
        elif style == "coder": return self._to_coder_output(result)
        elif style == "red_team": return self._to_red_team_output(result)
        elif style == "blue_team": return self._to_blue_team_output(result)
        else: return self._to_technical_output(result, self.personality_config.get("verbosity", "detailed"))

    def _sim_host_discovery(self, cmd: str) -> tuple:
        hosts = [
            {"ip": "192.168.1.1", "vendor": "Cisco Systems"},
            {"ip": "192.168.1.10", "vendor": "Dell Inc."},
            {"ip": "192.168.1.50", "vendor": "Raspberry Pi"},
            {"ip": "192.168.1.100", "vendor": "VMware"},
            {"ip": "192.168.1.254", "vendor": "Ubiquiti"},
        ]
        output = "Nmap scan report\n\nDiscovered hosts:\n"
        for h in hosts:
            output += f"  {h['ip']}  {h['vendor']}\n"
        return output, [{"type": "host", "host": h["ip"], "vendor": h["vendor"]} for h in hosts], "info"

    def _sim_port_scan(self, cmd: str) -> tuple:
        ports = [
            {"port": 22, "state": "open", "service": "ssh"},
            {"port": 80, "state": "open", "service": "http"},
            {"port": 443, "state": "open", "service": "https"},
            {"port": 3306, "state": "open", "service": "mysql"},
            {"port": 8080, "state": "open", "service": "http-proxy"},
        ]
        output = "PORT     STATE    SERVICE\n"
        for p in ports:
            output += f"{p['port']:<8} {p['state']:<8} {p['service']}\n"
        return output, [{"type": "port", "port": p["port"], "service": p["service"]} for p in ports], "medium"

    def _sim_service_detection(self, cmd: str) -> tuple:
        return "Service detection complete. 6 services identified.", [{"type": "service", "count": 6}], "info"

    def _sim_os_detection(self, cmd: str) -> tuple:
        return "OS: Linux 5.15.0 (95% confidence)", [{"type": "os", "name": "Linux 5.15.0"}], "low"

    def _sim_recon(self, cmd: str) -> tuple:
        return "Recon complete. 12 subdomains found.", [{"type": "subdomain", "count": 12}], "low"

    def _sim_traffic(self, cmd: str) -> tuple:
        return "Traffic analysis. 15K packets. 3 anomalies.", [{"type": "anomaly", "count": 3}], "medium"

    def _sim_nuclei(self, cmd: str) -> tuple:
        return "SQL Injection (critical), XSS (high)", [
            {"type": "vuln", "severity": "critical"}, {"type": "vuln", "severity": "high"}], "critical"

    def _sim_deps_scan(self, cmd: str) -> tuple:
        return "3 vulnerable deps found.", [{"type": "vuln_dep", "severity": "critical"}], "critical"

    def _sim_secrets_scan(self, cmd: str) -> tuple:
        return "2 secrets found.", [{"type": "secret", "count": 2}], "high"

    def _sim_owasp_scan(self, cmd: str) -> tuple:
        return "8 OWASP violations.", [{"type": "owasp", "count": 8}], "high"

    def _sim_gateway(self, cmd: str) -> tuple:
        return "Gateway healthy.", [{"type": "gateway", "status": "healthy"}], "low"

    def _sim_surface(self, cmd: str) -> tuple:
        return "Exposure score 7.2/10.", [{"type": "exposed"}], "high"

    def _sim_tls(self, cmd: str) -> tuple:
        return "TLS grade B. Weak ciphers enabled.", [{"type": "tls", "grade": "B"}], "medium"

    def _sim_resources(self, cmd: str) -> tuple:
        return "CPU 34%, Memory 62%.", [{"type": "resource"}], "low"

    def _sim_generic(self, cmd: str) -> tuple:
        return f"Simulated: {cmd}", [], "info"

    def _to_executive_summary(self, result: OperationResult) -> str:
        return f"[{result.risk_level.upper()}] {result.tool}: {len(result.findings)} findings. Action: {'Immediate' if result.risk_level in ['critical', 'high'] else 'Review'}."

    def _to_coder_output(self, result: OperationResult) -> str:
        return f"$ {result.command} | Exit: {result.returncode} | Risk: {result.risk_level}"

    def _to_red_team_output(self, result: OperationResult) -> str:
        return f"[EXPLOITABLE] {result.tool} => {len(result.findings)} vectors"

    def _to_blue_team_output(self, result: OperationResult) -> str:
        return f"[DETECTION] {result.tool} - Alert: {result.risk_level}"

    def _to_technical_output(self, result: OperationResult, verbosity: str) -> str:
        return result.stdout if verbosity != "minimal" else f"{result.tool}: {result.risk_level}"

    def _parse_findings(self, stdout: str) -> List[Dict]:
        return []

    def _assess_risk(self, findings: List[Dict]) -> str:
        if not findings: return "info"
        severities = [f.get("severity", "low") for f in findings]
        if "critical" in severities: return "critical"
        elif "high" in severities: return "high"
        elif "medium" in severities: return "medium"
        return "low"

    def get_status(self) -> Dict:
        return {"mode": self.mode.value, "personality": self.personality,
                "active_workflows": len(self.active_workflows),
                "completed_workflows": len(self.history),
                "personality_config": self.personality_config}

    def export_report(self, workflow_id: str, format: str = "json") -> str:
        workflow = self.active_workflows.get(workflow_id)
        if not workflow: return ""
        if format == "json":
            return json.dumps(asdict(workflow), indent=2, default=str)
        elif format == "markdown":
            md = f"# Security Report: {workflow.name}\n\n**Target:** {workflow.target}\n**Mode:** {workflow.mode.value}\n\n"
            for r in workflow.results:
                md += f"### {r.tool}\n- **Risk:** {r.risk_level}\n```\n{r.stdout[:2000]}\n```\n\n"
            return md
        return ""


_engine: Optional[NSOCEngine] = None

def get_engine(mode: OpMode = OpMode.SIMULATION, personality: str = "default") -> NSOCEngine:
    global _engine
    if _engine is None:
        _engine = NSOCEngine(mode, personality)
    return _engine
