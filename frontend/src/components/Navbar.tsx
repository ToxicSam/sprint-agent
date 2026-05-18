import { Link, useLocation } from 'react-router-dom';
import { Sun, Moon, Bot, LayoutDashboard, ClipboardList, BarChart3, CalendarDays, Settings } from 'lucide-react';
import { useStore } from '@/store';
import { cn } from '@/lib/utils';

const NAV_TABS = [
  { path: '/', label: 'Dashboard', icon: LayoutDashboard },
  { path: '/planning', label: 'Planning', icon: CalendarDays },
  { path: '/standup', label: 'Standup', icon: ClipboardList },
  { path: '/retro', label: 'Retro', icon: BarChart3 },
  { path: '/settings', label: 'Settings', icon: Settings },
];

export default function Navbar() {
  const location = useLocation();
  const theme = useStore(s => s.theme);
  const setTheme = useStore(s => s.setTheme);
  const toggleAgentPanel = useStore(s => s.toggleAgentPanel);

  return (
    <header className="fixed top-0 left-0 right-0 z-[30] h-12 flex items-center px-4 gap-4 border-b border-[hsl(var(--border))] bg-[hsl(var(--card))]">
      {/* Logo */}
      <Link to="/" className="flex items-center gap-2 shrink-0 mr-4">
        <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-violet-500 to-pink-500 flex items-center justify-center">
          <span className="text-white text-xs font-bold">S</span>
        </div>
        <span className="font-semibold text-base hidden sm:inline text-[hsl(var(--foreground))]">Sprint Agent</span>
      </Link>

      {/* Nav Tabs */}
      <nav className="flex items-center gap-1 flex-1">
        {NAV_TABS.map(tab => {
          const isActive = location.pathname === tab.path;
          return (
            <Link
              key={tab.path}
              to={tab.path}
              className={cn(
                'flex items-center gap-1.5 px-3 py-1.5 rounded-md text-sm font-medium transition-colors',
                isActive
                  ? 'bg-violet-500/10 text-violet-600 dark:text-violet-400'
                  : 'text-[hsl(var(--muted-foreground))] hover:text-[hsl(var(--foreground))] hover:bg-[hsl(var(--accent))]'
              )}
            >
              <tab.icon className="w-4 h-4" />
              <span className="hidden md:inline">{tab.label}</span>
            </Link>
          );
        })}
      </nav>

      {/* Actions */}
      <div className="flex items-center gap-2">
        <button
          onClick={toggleAgentPanel}
          className="p-2 rounded-md text-[hsl(var(--muted-foreground))] hover:text-[hsl(var(--foreground))] hover:bg-[hsl(var(--accent))] transition-colors"
          title="Toggle Agent Panel (A)"
        >
          <Bot className="w-4 h-4" />
        </button>
        <button
          onClick={() => setTheme(theme === 'light' ? 'dark' : 'light')}
          className="p-2 rounded-md text-[hsl(var(--muted-foreground))] hover:text-[hsl(var(--foreground))] hover:bg-[hsl(var(--accent))] transition-colors"
          title="Toggle Theme (T)"
        >
          {theme === 'light' ? <Moon className="w-4 h-4" /> : <Sun className="w-4 h-4" />}
        </button>
        <div className="w-7 h-7 rounded-full bg-gradient-to-br from-violet-500 to-pink-500 flex items-center justify-center text-white text-xs font-semibold ml-1">
          U
        </div>
      </div>
    </header>
  );
}
