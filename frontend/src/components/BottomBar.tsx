import { useStore } from '@/store';
import { format, differenceInDays, parseISO } from 'date-fns';

export default function BottomBar() {
  const sprint = useStore(s => s.sprint);
  const tasks = useStore(s => s.tasks);

  const total = tasks.length;
  const done = tasks.filter(t => t.status === 'done').length;
  const inProgress = tasks.filter(t => t.status === 'progress').length;
  const paused = tasks.filter(t => t.status === 'paused').length;
  const blocked = tasks.filter(t => t.blocked_by.length > 0).length;

  let daysLeft = 0;
  if (sprint) {
    daysLeft = Math.max(0, differenceInDays(parseISO(sprint.end_date), new Date()));
  }

  return (
    <footer className="fixed bottom-0 left-0 right-0 z-[30] h-8 flex items-center justify-between px-4 text-xs bg-[hsl(var(--card))] border-t border-[hsl(var(--border))]">
      <div className="flex items-center gap-4">
        {sprint && (
          <>
            <span className="font-semibold text-[hsl(var(--foreground))]">{sprint.name}</span>
            <span className="text-[hsl(var(--muted-foreground))]">
              {format(parseISO(sprint.start_date), 'MMM d')} – {format(parseISO(sprint.end_date), 'MMM d')}
            </span>
          </>
        )}
      </div>
      <div className="flex items-center gap-4 text-[hsl(var(--muted-foreground))]">
        <span>{total} tasks</span>
        <span>{done} done</span>
        <span>{inProgress} in progress</span>
        <span>{paused} paused</span>
        <span className={blocked > 0 ? 'text-red-500 font-medium' : ''}>{blocked} blocked</span>
        <span>{daysLeft} days left</span>
      </div>
      <div className="hidden md:flex items-center gap-2 text-[hsl(var(--muted-foreground))]">
        <kbd className="px-1.5 py-0.5 rounded border border-[hsl(var(--border))] bg-[hsl(var(--accent))] text-[10px] font-mono">N</kbd>
        <span>new</span>
        <kbd className="px-1.5 py-0.5 rounded border border-[hsl(var(--border))] bg-[hsl(var(--accent))] text-[10px] font-mono">E</kbd>
        <span>edit</span>
        <kbd className="px-1.5 py-0.5 rounded border border-[hsl(var(--border))] bg-[hsl(var(--accent))] text-[10px] font-mono">?</kbd>
        <span>help</span>
      </div>
    </footer>
  );
}
