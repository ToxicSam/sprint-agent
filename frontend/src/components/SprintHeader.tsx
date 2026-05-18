import { useStore } from '@/store';
import { cn } from '@/lib/utils';
import { format, differenceInDays, parseISO } from 'date-fns';
import { Settings } from 'lucide-react';

const STATUS_CONFIG: Record<string, { label: string; className: string }> = {
  active: { label: 'Active', className: 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400' },
  planning: { label: 'Planning', className: 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400' },
  completed: { label: 'Completed', className: 'bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-400' },
  cancelled: { label: 'Cancelled', className: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400' },
};

export default function SprintHeader() {
  const sprint = useStore(s => s.sprint);
  const tasks = useStore(s => s.tasks);
  const setFilter = useStore(s => s.setFilter);
  const filter = useStore(s => s.filter);

  if (!sprint) return null;

  const total = tasks.length;
  const done = tasks.filter(t => t.status === 'done').length;
  const inProgress = tasks.filter(t => t.status === 'progress').length;
  const paused = tasks.filter(t => t.status === 'paused').length;
  const blocked = tasks.filter(t => t.blocked_by.length > 0).length;
  const daysLeft = Math.max(0, differenceInDays(parseISO(sprint.end_date), new Date()));

  const statusConfig = STATUS_CONFIG[sprint.status] || STATUS_CONFIG.active;

  const stats = [
    { label: 'Tasks', value: total, filter: {} as const },
    { label: 'Done', value: done, filter: { status: 'done' as const } },
    { label: 'In Progress', value: inProgress, filter: { status: 'progress' as const } },
    { label: 'Paused', value: paused, filter: { status: 'paused' as const } },
    { label: 'Blocked', value: blocked, filterKey: 'blocked' as const },
    { label: 'Days Left', value: daysLeft, filter: {} as const },
  ];

  return (
    <div className="px-6 py-4 bg-[hsl(var(--card))] border-b border-[hsl(var(--border))]">
      {/* Top row */}
      <div className="flex items-start justify-between">
        <div className="min-w-0">
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-bold text-[hsl(var(--foreground))] truncate">{sprint.name}</h1>
            <span className={cn('text-xs font-medium px-2 py-0.5 rounded-full', statusConfig.className)}>
              {statusConfig.label}
            </span>
          </div>
          <div className="flex items-center gap-2 mt-1 text-sm text-[hsl(var(--muted-foreground))]">
            <span>
              {format(parseISO(sprint.start_date), 'MMM d')} – {format(parseISO(sprint.end_date), 'MMM d')}
            </span>
            <span>·</span>
            <span className="truncate max-w-xl" title={sprint.goal}>{sprint.goal}</span>
          </div>
        </div>
        <div className="flex items-center gap-3 shrink-0 ml-4">
          <div className="text-right">
            <span className="text-lg font-bold">{daysLeft}</span>
            <span className="text-xs text-[hsl(var(--muted-foreground))] ml-1">days left</span>
          </div>
          <button className="p-2 rounded-md text-[hsl(var(--muted-foreground))] hover:text-[hsl(var(--foreground))] hover:bg-[hsl(var(--accent))] transition-colors">
            <Settings className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Metrics bar */}
      <div className="flex items-center gap-3 mt-3">
        {stats.map(stat => {
          const statStatus = (stat as Record<string, unknown>).status as string | undefined;
          const statFilterKey = (stat as Record<string, unknown>).filterKey as string | undefined;
          const filterStatus = filter.status as string | undefined;
          const isActive = statFilterKey === 'blocked'
            ? filterStatus === 'blocked'
            : statStatus ? filterStatus === statStatus : filterStatus === 'all' || !filterStatus;
          return (
            <button
              key={stat.label}
              onClick={() => {
                if (statFilterKey === 'blocked') {
                  setFilter({ ...filter, status: filterStatus === 'blocked' ? 'all' : 'blocked' });
                } else if (statStatus) {
                  setFilter({ ...filter, status: filterStatus === statStatus ? 'all' : statStatus as 'todo' | 'progress' | 'done' | 'paused' });
                } else {
                  setFilter({ ...filter, status: 'all' });
                }
              }}
              className={cn(
                'flex items-center gap-1.5 px-3 py-1.5 rounded-lg transition-colors',
                isActive
                  ? 'bg-violet-500/10 text-violet-600 dark:text-violet-400'
                  : 'hover:bg-[hsl(var(--accent))] text-[hsl(var(--foreground))]'
              )}
            >
              <span className="text-xl font-bold">{stat.value}</span>
              <span className="text-xs text-[hsl(var(--muted-foreground))]">{stat.label}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
}
