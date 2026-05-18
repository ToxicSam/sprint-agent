import { useSortable } from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import type { Task } from '@/types';
import { useStore } from '@/store';
import { cn } from '@/lib/utils';
import { MoreHorizontal } from 'lucide-react';

interface TaskCardProps {
  task: Task;
}

const STATUS_BORDER: Record<string, string> = {
  todo: 'border-l-[#64748B]',
  progress: 'border-l-[#3B82F6]',
  done: 'border-l-[#22C55E]',
  paused: 'border-l-[#F59E0B]',
};

const STATUS_BORDER_DARK: Record<string, string> = {
  todo: 'dark:border-l-[#94A3B8]',
  progress: 'dark:border-l-[#60A5FA]',
  done: 'dark:border-l-[#4ADE80]',
  paused: 'dark:border-l-[#FBBF24]',
};

function getPriorityConfig(priority: number): { label: string; className: string } {
  if (priority >= 9) return { label: 'Critical', className: 'bg-[#EF4444] text-white' };
  if (priority >= 7) return { label: 'High', className: 'bg-[#F59E0B] text-[#1F2937]' };
  if (priority >= 4) return { label: 'Medium', className: 'bg-[#3B82F6] text-white' };
  return { label: 'Low', className: 'border border-[#64748B] text-[#64748B] dark:text-[#94A3B8] dark:border-[#94A3B8]' };
}

export default function TaskCard({ task }: TaskCardProps) {
  const selectTask = useStore(s => s.selectTask);
  const members = useStore(s => s.members);

  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging,
  } = useSortable({ id: task.id, data: { task } });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
  };

  const priorityConfig = getPriorityConfig(task.priority);
  const assignee = task.assignee || members.find(m => m.id === task.assignee_id);
  const isBlocked = task.blocked_by.length > 0;

  return (
    <div
      ref={setNodeRef}
      style={style}
      className={cn(
        'group relative bg-[hsl(var(--card))] rounded-lg border border-[hsl(var(--border))] cursor-grab active:cursor-grabbing',
        'border-l-[3px]',
        STATUS_BORDER[task.status] || STATUS_BORDER.todo,
        STATUS_BORDER_DARK[task.status] || STATUS_BORDER_DARK.todo,
        isDragging && 'opacity-40 rotate-[2deg] scale-[1.02] shadow-xl z-[90]',
        !isDragging && 'hover:shadow-md hover:-translate-y-[1px] transition-all duration-150'
      )}
      {...attributes}
      {...listeners}
      onClick={() => selectTask(task.id)}
    >
      <div className="p-3 space-y-2">
        {/* Top row: priority + menu */}
        <div className="flex items-center justify-between">
          {isBlocked ? (
            <span className="text-[10px] font-semibold px-1.5 py-0.5 rounded bg-[#EF4444] text-white uppercase tracking-wide">
              Blocked
            </span>
          ) : (
            <span className={cn('text-[10px] font-semibold px-1.5 py-0.5 rounded', priorityConfig.className)}>
              {priorityConfig.label}
            </span>
          )}
          <button
            className="opacity-0 group-hover:opacity-100 p-1 rounded hover:bg-[hsl(var(--accent))] transition-all"
            onPointerDown={e => e.stopPropagation()}
            onClick={e => {
              e.stopPropagation();
            }}
          >
            <MoreHorizontal className="w-3.5 h-3.5 text-[hsl(var(--muted-foreground))]" />
          </button>
        </div>

        {/* Title */}
        <p className="text-sm font-medium text-[hsl(var(--foreground))] line-clamp-2 leading-snug">
          {task.title}
        </p>

        {/* Bottom row: assignee + story points */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            {assignee ? (
              <div className="flex items-center gap-1">
                <div className="w-5 h-5 rounded-full bg-gradient-to-br from-violet-500 to-pink-500 flex items-center justify-center">
                  <span className="text-[9px] font-bold text-white">{assignee.name[0]}</span>
                </div>
                <span className="text-[11px] text-[hsl(var(--muted-foreground))]">{assignee.name}</span>
              </div>
            ) : (
              <span className="text-[11px] text-[hsl(var(--muted-foreground))]">Unassigned</span>
            )}
          </div>
          {task.story_points > 0 && (
            <span className="text-[11px] font-medium text-[hsl(var(--muted-foreground))]">
              {task.story_points}pt
            </span>
          )}
        </div>
      </div>
    </div>
  );
}
