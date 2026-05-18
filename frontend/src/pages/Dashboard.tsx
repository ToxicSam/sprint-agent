import { useState, useEffect, useMemo, useCallback } from 'react';
import { DndContext, type DragEndEvent, type DragOverEvent, type DragStartEvent, PointerSensor, useSensor, useSensors, closestCorners, DragOverlay } from '@dnd-kit/core';
import { SortableContext, verticalListSortingStrategy } from '@dnd-kit/sortable';
import type { Task, TaskStatus } from '@/types';
import { useStore } from '@/store';
import SprintHeader from '@/components/SprintHeader';
import TaskCard from '@/components/TaskCard';
import InlineTaskCreator from '@/components/InlineTaskCreator';
import SlideOver from '@/components/SlideOver';
import { cn } from '@/lib/utils';
import { Plus, Filter, Search, Kanban, List, X } from 'lucide-react';
import { useSortable } from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';

const COLUMNS: { id: TaskStatus; label: string; dotColor: string }[] = [
  { id: 'todo', label: 'NOT STARTED', dotColor: 'bg-[#64748B] dark:bg-[#94A3B8]' },
  { id: 'progress', label: 'IN PROGRESS', dotColor: 'bg-[#3B82F6] dark:bg-[#60A5FA]' },
  { id: 'done', label: 'COMPLETED', dotColor: 'bg-[#22C55E] dark:bg-[#4ADE80]' },
  { id: 'paused', label: 'PAUSED', dotColor: 'bg-[#F59E0B] dark:bg-[#FBBF24]' },
];

function SortableTaskCard({ task }: { task: Task }) {
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

  return (
    <div
      ref={setNodeRef}
      style={style}
      {...attributes}
      {...listeners}
      className={cn(isDragging && 'opacity-30')}
    >
      <TaskCard task={task} />
    </div>
  );
}

export default function Dashboard() {
  const tasks = useStore(s => s.tasks);
  const filter = useStore(s => s.filter);
  const setFilter = useStore(s => s.setFilter);
  const moveTask = useStore(s => s.moveTask);
  const selectedTaskId = useStore(s => s.selectedTaskId);
  const selectTask = useStore(s => s.selectTask);

  const [searchQuery, setSearchQuery] = useState('');
  const [activeId, setActiveId] = useState<string | null>(null);
  const [showFilters, setShowFilters] = useState(false);

  const sensors = useSensors(
    useSensor(PointerSensor, {
      activationConstraint: { distance: 8 },
    })
  );

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement || e.target instanceof HTMLSelectElement) {
        return;
      }
      if (e.key === 'n' || e.key === 'N') {
        e.preventDefault();
        const firstColumn = document.querySelector('[data-column="todo"] .inline-creator button');
        if (firstColumn instanceof HTMLElement) firstColumn.click();
      }
      if (e.key === 'f' || e.key === 'F') {
        e.preventDefault();
        const searchInput = document.querySelector('[data-search-input]') as HTMLElement;
        searchInput?.focus();
      }
      if (e.key === '1') document.querySelector<HTMLElement>('[data-column="todo"]')?.scrollIntoView({ behavior: 'smooth' });
      if (e.key === '2') document.querySelector<HTMLElement>('[data-column="progress"]')?.scrollIntoView({ behavior: 'smooth' });
      if (e.key === '3') document.querySelector<HTMLElement>('[data-column="done"]')?.scrollIntoView({ behavior: 'smooth' });
      if (e.key === '4') document.querySelector<HTMLElement>('[data-column="paused"]')?.scrollIntoView({ behavior: 'smooth' });
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  const filteredTasks = useMemo(() => {
    return tasks.filter(task => {
      if (filter.status && filter.status !== 'all' && filter.status !== 'blocked' && task.status !== filter.status) return false;
      if (filter.status === 'blocked' && task.blocked_by.length === 0) return false;
      if (filter.assignee && task.assignee_id !== filter.assignee) return false;
      if (filter.priority && task.priority !== filter.priority) return false;
      if (searchQuery) {
        const q = searchQuery.toLowerCase();
        const matchesTitle = task.title.toLowerCase().includes(q);
        const matchesDesc = task.description.toLowerCase().includes(q);
        const matchesAssignee = task.assignee?.name?.toLowerCase().includes(q) ?? false;
        if (!matchesTitle && !matchesDesc && !matchesAssignee) return false;
      }
      return true;
    });
  }, [tasks, filter, searchQuery]);

  const handleDragStart = useCallback((event: DragStartEvent) => {
    setActiveId(event.active.id as string);
  }, []);

  const handleDragOver = useCallback((event: DragOverEvent) => {
    const { active, over } = event;
    if (!over) return;

    const activeTask = tasks.find(t => t.id === active.id);
    if (!activeTask) return;

    const overId = over.id as string;
    const overColumn = COLUMNS.find(c => c.id === overId);

    if (overColumn && activeTask.status !== overColumn.id) {
      moveTask(activeTask.id, overColumn.id);
    }
  }, [tasks, moveTask]);

  const handleDragEnd = useCallback((event: DragEndEvent) => {
    const { active, over } = event;
    setActiveId(null);

    if (!over) return;

    const activeTask = tasks.find(t => t.id === active.id);
    if (!activeTask) return;

    const overId = over.id as string;
    const overColumn = COLUMNS.find(c => c.id === overId);
    const overTask = tasks.find(t => t.id === overId);

    if (overColumn) {
      moveTask(activeTask.id, overColumn.id);
    } else if (overTask) {
      const targetColumn = COLUMNS.find(c => c.id === overTask.status);
      if (targetColumn && activeTask.status !== targetColumn.id) {
        moveTask(activeTask.id, targetColumn.id);
      }
    }
  }, [tasks, moveTask]);

  const activeTask = activeId ? tasks.find(t => t.id === activeId) : null;

  return (
    <div className="h-full flex flex-col">
      <SprintHeader />

      {/* Toolbar */}
      <div className="flex items-center justify-between px-4 py-2 bg-[hsl(var(--card))] border-b border-[hsl(var(--border))] gap-3">
        <div className="flex items-center gap-2">
          <button
            onClick={() => {
              const firstCreator = document.querySelector('[data-column="todo"] .inline-creator button');
              if (firstCreator instanceof HTMLElement) firstCreator.click();
            }}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-md bg-violet-500 text-white text-sm font-medium hover:bg-violet-600 transition-colors"
          >
            <Plus className="w-3.5 h-3.5" />
            New Task
            <kbd className="ml-1 px-1 py-0.5 rounded bg-white/20 text-[10px] font-mono">N</kbd>
          </button>
          <button
            onClick={() => setShowFilters(!showFilters)}
            className={cn(
              'flex items-center gap-1.5 px-3 py-1.5 rounded-md text-sm transition-colors',
              showFilters
                ? 'bg-violet-500/10 text-violet-600'
                : 'text-[hsl(var(--muted-foreground))] hover:bg-[hsl(var(--accent))]'
            )}
          >
            <Filter className="w-3.5 h-3.5" />
            Filter
          </button>
        </div>

        <div className="flex items-center gap-2">
          <div className="relative">
            <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-[hsl(var(--muted-foreground))]" />
            <input
              data-search-input
              type="text"
              value={searchQuery}
              onChange={e => setSearchQuery(e.target.value)}
              placeholder="Search tasks..."
              className="w-48 h-8 pl-8 pr-7 rounded-md border border-[hsl(var(--border))] bg-[hsl(var(--background))] text-sm focus:outline-none focus:ring-2 focus:ring-violet-500/30 placeholder:text-[hsl(var(--muted-foreground))]"
            />
            {searchQuery && (
              <button
                onClick={() => setSearchQuery('')}
                className="absolute right-2 top-1/2 -translate-y-1/2 text-[hsl(var(--muted-foreground))] hover:text-[hsl(var(--foreground))]"
              >
                <X className="w-3.5 h-3.5" />
              </button>
            )}
          </div>
          <div className="flex items-center rounded-md border border-[hsl(var(--border))] overflow-hidden">
            <button className="p-1.5 bg-violet-500/10 text-violet-600">
              <Kanban className="w-3.5 h-3.5" />
            </button>
            <button className="p-1.5 text-[hsl(var(--muted-foreground))] hover:bg-[hsl(var(--accent))]">
              <List className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </div>

      {/* Active filter badges */}
      {showFilters && (
        <div className="flex items-center gap-2 px-4 py-1.5 bg-[hsl(var(--card))] border-b border-[hsl(var(--border))] text-xs">
          <span className="text-[hsl(var(--muted-foreground))]">Status:</span>
          {(['all', 'todo', 'progress', 'done', 'paused', 'blocked'] as const).map(s => (
            <button
              key={s}
              onClick={() => setFilter({ ...filter, status: s })}
              className={cn(
                'px-2 py-0.5 rounded-full border transition-colors capitalize',
                filter.status === s
                  ? 'bg-violet-500/10 text-violet-600 border-violet-500/20'
                  : 'border-[hsl(var(--border))] text-[hsl(var(--muted-foreground))] hover:bg-[hsl(var(--accent))]'
              )}
            >
              {s === 'all' ? 'All' : s}
            </button>
          ))}
          {filter.status && filter.status !== 'all' && (
            <button
              onClick={() => setFilter({ ...filter, status: 'all' })}
              className="text-[hsl(var(--muted-foreground))] hover:text-red-500 ml-1"
            >
              Clear
            </button>
          )}
        </div>
      )}

      {/* Kanban Board */}
      <div className="flex-1 overflow-x-auto overflow-y-hidden p-4">
        <DndContext
          sensors={sensors}
          collisionDetection={closestCorners}
          onDragStart={handleDragStart}
          onDragOver={handleDragOver}
          onDragEnd={handleDragEnd}
        >
          <div className="flex gap-4 h-full min-w-[1040px]">
            {COLUMNS.map(column => {
              const columnTasks = filteredTasks.filter(t => t.status === column.id);
              return (
                <div
                  key={column.id}
                  data-column={column.id}
                  className="flex-1 min-w-[260px] flex flex-col bg-[hsl(var(--accent))]/30 rounded-lg"
                >
                  {/* Column Header */}
                  <div className="flex items-center justify-between px-3 h-10 bg-[hsl(var(--accent))] rounded-t-lg shrink-0">
                    <div className="flex items-center gap-2">
                      <span className={cn('w-2 h-2 rounded-full', column.dotColor)} />
                      <span className="text-sm font-semibold text-[hsl(var(--foreground))]">{column.label}</span>
                    </div>
                    <span className="text-xs bg-[hsl(var(--card))] border border-[hsl(var(--border))] rounded-full px-2 py-0.5 font-medium">
                      {columnTasks.length}
                    </span>
                  </div>

                  {/* Column Body */}
                  <div className="flex-1 overflow-y-auto p-2 space-y-2 min-h-[120px]">
                    <SortableContext
                      items={columnTasks.map(t => t.id)}
                      strategy={verticalListSortingStrategy}
                    >
                      {columnTasks.map(task => (
                        <SortableTaskCard key={task.id} task={task} />
                      ))}
                    </SortableContext>

                    {/* Drop zone hint */}
                    {columnTasks.length === 0 && (
                      <div className="flex flex-col items-center justify-center py-8 text-[hsl(var(--muted-foreground))]">
                        <div className="w-10 h-10 rounded-lg border-2 border-dashed border-[hsl(var(--border))] flex items-center justify-center mb-2">
                          <Plus className="w-4 h-4" />
                        </div>
                        <p className="text-xs">Drop tasks here</p>
                      </div>
                    )}
                  </div>

                  {/* Inline Creator */}
                  <div className="p-2 shrink-0 inline-creator">
                    <InlineTaskCreator status={column.id} />
                  </div>
                </div>
              );
            })}
          </div>

          {/* Drag Overlay */}
          <DragOverlay dropAnimation={null}>
            {activeTask ? (
              <div className="opacity-90 rotate-2 shadow-xl">
                <TaskCard task={activeTask} />
              </div>
            ) : null}
          </DragOverlay>
        </DndContext>
      </div>

      {/* Slide Over */}
      {selectedTaskId && (
        <SlideOver onClose={() => selectTask(null)} />
      )}
    </div>
  );
}
