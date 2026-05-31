import { useDroppable } from '@dnd-kit/core'
import type { Task } from '@/types'
import { cn } from '@/lib/utils'

interface KanbanColumnProps {
  id: string
  label: string
  dotColor: string
  tasks: Task[]
  children?: React.ReactNode
}

export default function KanbanColumn({ id, label, dotColor, tasks, children }: KanbanColumnProps) {
  const { setNodeRef, isOver } = useDroppable({ id })

  return (
    <div
      ref={setNodeRef}
      className={cn(
        'flex-1 min-w-[260px] rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--card))] flex flex-col',
        isOver && 'ring-2 ring-[hsl(var(--primary))] ring-offset-2'
      )}
      data-testid={`column-${id}`}
    >
      {/* Column header */}
      <div className="flex items-center justify-between px-3 py-2.5 border-b border-[hsl(var(--border))]">
        <div className="flex items-center gap-2">
          <div className={cn('w-2 h-2 rounded-full', dotColor)} data-testid="column-dot" />
          <span className="text-xs font-semibold text-[hsl(var(--foreground))] uppercase tracking-wide">
            {label}
          </span>
        </div>
        <span
          className="text-xs font-medium text-[hsl(var(--muted-foreground))] bg-[hsl(var(--muted))] px-1.5 py-0.5 rounded-full"
          data-testid="task-count"
        >
          {tasks.length}
        </span>
      </div>

      {/* Tasks area */}
      <div className="flex-1 p-2 space-y-2 min-h-[120px]">
        {tasks.length === 0 ? (
          <div
            className="flex flex-col items-center justify-center h-full text-[hsl(var(--muted-foreground))] py-8"
            data-testid="empty-state"
          >
            <p className="text-xs">No tasks</p>
            <p className="text-[10px] mt-0.5 opacity-60">Drop tasks here</p>
          </div>
        ) : (
          children
        )}
      </div>
    </div>
  )
}
