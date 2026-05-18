import { useEffect } from 'react';
import { useStore } from '@/store';
import { cn } from '@/lib/utils';
import Navbar from './Navbar';
import Sidebar from './Sidebar';
import AgentPanel from './AgentPanel';
import BottomBar from './BottomBar';

interface LayoutProps {
  children: React.ReactNode;
}

export default function Layout({ children }: LayoutProps) {
  const theme = useStore(s => s.theme);
  const sidebarExpanded = useStore(s => s.sidebarExpanded);
  const agentPanelOpen = useStore(s => s.agentPanelOpen);

  useEffect(() => {
    const root = document.documentElement;
    if (theme === 'dark') {
      root.classList.add('dark');
    } else {
      root.classList.remove('dark');
    }
  }, [theme]);

  return (
    <div className="min-h-[100dvh] bg-[hsl(var(--background))] text-[hsl(var(--foreground))]">
      <Navbar />
      <Sidebar />
      <AgentPanel />

      <main
        className={cn(
          'pt-12 pb-8 transition-all duration-200',
          sidebarExpanded ? 'pl-[200px]' : 'pl-[52px]',
          agentPanelOpen ? 'pr-[320px]' : 'pr-[48px]'
        )}
      >
        {children}
      </main>

      <BottomBar />
    </div>
  );
}
