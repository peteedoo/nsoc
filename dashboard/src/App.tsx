import { useState } from 'react';
import { Shield, Activity, Terminal, Settings, BarChart3, Workflow, BookOpen } from 'lucide-react';
import type { OpMode, Personality } from './types';
import { PERSONALITIES } from './lib/data';
import { DashboardView } from './sections/DashboardView';
import { WorkflowsView } from './sections/WorkflowsView';
import { TerminalView } from './sections/TerminalView';
import { ResultsView } from './sections/ResultsView';
import { SettingsView } from './sections/SettingsView';
import { SkillsView } from './sections/SkillsView';
import { ModeToggle } from './components/ModeToggle';
import { PersonalitySelector } from './components/PersonalitySelector';
import './index.css';

function App() {
  const [mode, setMode] = useState<OpMode>('simulation');
  const [personality, setPersonality] = useState<Personality>(PERSONALITIES[0]);
  const [activeView, setActiveView] = useState('dashboard');
  const [terminalHistory, setTerminalHistory] = useState<string[]>([
    'NSOC v2.0.0 - Network Security Operations Center',
    'Mode: SIMULATION | Agent: Security Analyst',
    'Type "help" for available commands.',
    '',
  ]);

  const addToTerminal = (lines: string[]) => {
    setTerminalHistory(prev => [...prev, ...lines, '']);
  };

  const views = [
    { id: 'dashboard', label: 'Dashboard', icon: BarChart3 },
    { id: 'workflows', label: 'Workflows', icon: Workflow },
    { id: 'terminal', label: 'Terminal', icon: Terminal },
    { id: 'results', label: 'Results', icon: Activity },
    { id: 'skills', label: 'Skills', icon: BookOpen },
    { id: 'settings', label: 'Settings', icon: Settings },
  ];

  return (
    <div className="h-screen w-screen flex flex-col bg-[#0a0e1a] text-gray-100 overflow-hidden">
      <header className="h-14 bg-[#111827] border-b border-gray-800 flex items-center justify-between px-4 shrink-0">
        <div className="flex items-center gap-3">
          <Shield className="w-6 h-6" style={{ color: personality.color_scheme }} />
          <span className="font-bold text-lg tracking-wide">NSOC</span>
          <span className="text-xs text-gray-500 ml-1">v2.0.0</span>
        </div>
        <div className="flex items-center gap-4">
          <ModeToggle mode={mode} onChange={setMode} addToTerminal={addToTerminal} />
          <PersonalitySelector personality={personality} onChange={setPersonality} />
        </div>
      </header>

      <div className="flex flex-1 overflow-hidden">
        <nav className="w-14 bg-[#111827] border-r border-gray-800 flex flex-col items-center py-2 gap-1 shrink-0">
          {views.map(v => {
            const Icon = v.icon;
            const isActive = activeView === v.id;
            return (
              <button
                key={v.id}
                onClick={() => setActiveView(v.id)}
                className={`w-10 h-10 rounded-lg flex items-center justify-center transition-all ${
                  isActive ? 'bg-gray-700 text-white' : 'text-gray-500 hover:text-gray-300 hover:bg-gray-800'
                }`}
                title={v.label}
              >
                <Icon className="w-5 h-5" />
              </button>
            );
          })}
        </nav>

        <main className="flex-1 overflow-auto bg-[#0a0e1a]">
          {activeView === 'dashboard' && (
            <DashboardView mode={mode} personality={personality} addToTerminal={addToTerminal} onNavigate={setActiveView} />
          )}
          {activeView === 'workflows' && (
            <WorkflowsView mode={mode} personality={personality} addToTerminal={addToTerminal} />
          )}
          {activeView === 'terminal' && (
            <TerminalView history={terminalHistory} setHistory={setTerminalHistory} mode={mode} personality={personality} />
          )}
          {activeView === 'results' && <ResultsView personality={personality} />}
          {activeView === 'skills' && <SkillsView personality={personality} />}
          {activeView === 'settings' && (
            <SettingsView mode={mode} setMode={setMode} personality={personality} setPersonality={setPersonality} addToTerminal={addToTerminal} />
          )}
        </main>
      </div>
    </div>
  );
}

export default App;
