import { Link, useLocation } from 'react-router-dom';
import { LayoutDashboard, CalendarDays, ClipboardList, BarChart3, Settings, ChevronLeft, ChevronRight } from 'lucide-react';
import { useStore } from '@/store';
import { cn } from '@/lib/utils';
import { preloadPage } from '@/App';

const NAV_ITEMS = [
  { path: '/', icon: LayoutDashboard, label: 'Dashboard' },
  { path: '/planning', icon: CalendarDays, label: 'Planning' },
  { path: '/standup', icon: ClipboardList, label: 'Standup' },
  { path: '/retro', icon: BarChart3, label: 'Retro' },
  { path: '/settings', icon: Settings, label: 'Settings' },
];

export default function Sidebar() {
  const location = useLocation();
  const sidebarExpanded = useStore(s => s.sidebarExpanded);
  const toggleSidebar = useStore(s => s.toggleSidebar);

  return (
    <aside
      className={cn(
        'fixed left-0 top-12 bottom-8 z-[30] bg-[hsl(var(--card))] border-r border-[hsl(var(--border))] transition-all duration-200 flex flex-col',
        sidebarExpanded ? 'w-[200px]' : 'w-[52px]'
      )}
    >
      <div className="flex-1 py-2 flex flex-col gap-0.5 px-1.5">
        {NAV_ITEMS.map(item => {
          const isActive = location.pathname === item.path;
          return (
            <Link
              key={item.path}
              to={item.path}
              onMouseEnter={() => preloadPage(item.path)}
              onFocus={() => preloadPage(item.path)}
              className={cn(
                'relative flex items-center gap-3 rounded-md px-2 py-2 text-sm transition-colors group',
                isActive
                  ? 'bg-violet-500/10 text-violet-600 dark:text-violet-400'
                  : 'text-[hsl(var(--muted-foreground))] hover:text-[hsl(var(--foreground))] hover:bg-[hsl(var(--accent))]'
              )}
              title={!sidebarExpanded ? item.label : undefined}
            >
              <item.icon className="w-[18px] h-[18px] shrink-0" />
              {sidebarExpanded && (
                <span className="truncate font-medium">{item.label}</span>
              )}
              {/* Tooltip on collapsed */}
              {!sidebarExpanded && (
                <div className="absolute left-full ml-2 px-2 py-1 bg-[hsl(var(--foreground))] text-[hsl(var(--background))] text-xs rounded opacity-0 group-hover:opacity-100 pointer-events-none whitespace-nowrap z-50 transition-opacity">
                  {item.label}
                </div>
              )}
            </Link>
          );
        })}
      </div>

      {/* Toggle button */}
      <div className="p-1.5 border-t border-[hsl(var(--border))]">
        <button
          onClick={toggleSidebar}
          className="flex items-center justify-center w-full h-8 rounded-md text-[hsl(var(--muted-foreground))] hover:text-[hsl(var(--foreground))] hover:bg-[hsl(var(--accent))] transition-colors"
          title={sidebarExpanded ? 'Collapse' : 'Expand'}
        >
          {sidebarExpanded ? <ChevronLeft className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
        </button>
      </div>
    </aside>
  );
}
