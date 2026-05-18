import { useState, useEffect } from 'react';
import { useStore } from '@/store';
import { X, Save, Trash2 } from 'lucide-react';
import type { Priority, TaskStatus } from '@/types';

interface SlideOverProps {
  onClose: () => void;
}

const STATUS_OPTIONS: { value: TaskStatus; label: string }[] = [
  { value: 'todo', label: 'Not Started' },
  { value: 'progress', label: 'In Progress' },
  { value: 'done', label: 'Completed' },
  { value: 'paused', label: 'Paused' },
];

const PRIORITY_OPTIONS: { value: Priority; label: string }[] = [
  { value: 10, label: 'Critical (10)' },
  { value: 9, label: 'Critical (9)' },
  { value: 8, label: 'High (8)' },
  { value: 7, label: 'High (7)' },
  { value: 6, label: 'Medium (6)' },
  { value: 5, label: 'Medium (5)' },
  { value: 4, label: 'Medium (4)' },
  { value: 3, label: 'Low (3)' },
  { value: 2, label: 'Low (2)' },
  { value: 1, label: 'Low (1)' },
];

export default function SlideOver({ onClose }: SlideOverProps) {
  const selectedTaskId = useStore(s => s.selectedTaskId);
  const tasks = useStore(s => s.tasks);
  const members = useStore(s => s.members);
  const updateTask = useStore(s => s.updateTask);
  const deleteTask = useStore(s => s.deleteTask);
  const selectTask = useStore(s => s.selectTask);

  const task = tasks.find(t => t.id === selectedTaskId);

  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [status, setStatus] = useState<TaskStatus>('todo');
  const [priority, setPriority] = useState<Priority>(5);
  const [assigneeId, setAssigneeId] = useState<string>('');
  const [storyPoints, setStoryPoints] = useState<string>('');

  useEffect(() => {
    if (task) {
      setTitle(task.title);
      setDescription(task.description);
      setStatus(task.status);
      setPriority(task.priority as Priority);
      setAssigneeId(task.assignee_id || '');
      setStoryPoints(task.story_points.toString());
    }
  }, [task]);

  useEffect(() => {
    const handleEsc = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    window.addEventListener('keydown', handleEsc);
    return () => window.removeEventListener('keydown', handleEsc);
  }, [onClose]);

  if (!task) return null;

  const handleSave = async () => {
    await updateTask(task.id, {
      title,
      description,
      status,
      priority,
      assignee_id: assigneeId || null,
      story_points: storyPoints ? parseInt(storyPoints) : 0,
    });
    onClose();
  };

  const handleDelete = async () => {
    if (window.confirm('Delete this task?')) {
      await deleteTask(task.id);
      selectTask(null);
      onClose();
    }
  };

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black/30 z-[40]"
        onClick={onClose}
      />

      {/* Panel */}
      <aside className="fixed right-0 top-0 bottom-0 z-[50] w-[480px] max-w-[100vw] bg-[hsl(var(--card))] shadow-xl flex flex-col animate-in slide-in-from-right duration-200">
        {/* Header */}
        <div className="flex items-center justify-between px-5 h-14 border-b border-[hsl(var(--border))] shrink-0">
          <h2 className="font-semibold text-base truncate pr-4">{task.title}</h2>
          <button
            onClick={onClose}
            className="p-2 rounded-md hover:bg-[hsl(var(--accent))] transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Body */}
        <div className="flex-1 overflow-y-auto p-5 space-y-4">
          {/* Title */}
          <div className="space-y-1.5">
            <label className="text-xs font-medium text-[hsl(var(--muted-foreground))]">Title</label>
            <input
              type="text"
              value={title}
              onChange={e => setTitle(e.target.value)}
              className="w-full h-9 px-3 rounded border border-[hsl(var(--border))] bg-[hsl(var(--background))] text-sm focus:outline-none focus:ring-2 focus:ring-violet-500/30"
            />
          </div>

          {/* Status + Priority */}
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1.5">
              <label className="text-xs font-medium text-[hsl(var(--muted-foreground))]">Status</label>
              <select
                value={status}
                onChange={e => setStatus(e.target.value as TaskStatus)}
                className="w-full h-9 px-3 rounded border border-[hsl(var(--border))] bg-[hsl(var(--background))] text-sm focus:outline-none focus:ring-2 focus:ring-violet-500/30"
              >
                {STATUS_OPTIONS.map(opt => (
                  <option key={opt.value} value={opt.value}>{opt.label}</option>
                ))}
              </select>
            </div>
            <div className="space-y-1.5">
              <label className="text-xs font-medium text-[hsl(var(--muted-foreground))]">Priority</label>
              <select
                value={priority}
                onChange={e => setPriority(parseInt(e.target.value) as Priority)}
                className="w-full h-9 px-3 rounded border border-[hsl(var(--border))] bg-[hsl(var(--background))] text-sm focus:outline-none focus:ring-2 focus:ring-violet-500/30"
              >
                {PRIORITY_OPTIONS.map(opt => (
                  <option key={opt.value} value={opt.value}>{opt.label}</option>
                ))}
              </select>
            </div>
          </div>

          {/* Assignee + Story Points */}
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1.5">
              <label className="text-xs font-medium text-[hsl(var(--muted-foreground))]">Assignee</label>
              <select
                value={assigneeId}
                onChange={e => setAssigneeId(e.target.value)}
                className="w-full h-9 px-3 rounded border border-[hsl(var(--border))] bg-[hsl(var(--background))] text-sm focus:outline-none focus:ring-2 focus:ring-violet-500/30"
              >
                <option value="">Unassigned</option>
                {members.map(m => (
                  <option key={m.id} value={m.id}>{m.name} ({m.role.toUpperCase()})</option>
                ))}
              </select>
            </div>
            <div className="space-y-1.5">
              <label className="text-xs font-medium text-[hsl(var(--muted-foreground))]">Story Points</label>
              <input
                type="number"
                value={storyPoints}
                onChange={e => setStoryPoints(e.target.value)}
                className="w-full h-9 px-3 rounded border border-[hsl(var(--border))] bg-[hsl(var(--background))] text-sm focus:outline-none focus:ring-2 focus:ring-violet-500/30"
              />
            </div>
          </div>

          {/* Description */}
          <div className="space-y-1.5">
            <label className="text-xs font-medium text-[hsl(var(--muted-foreground))]">Description</label>
            <textarea
              value={description}
              onChange={e => setDescription(e.target.value)}
              rows={4}
              className="w-full px-3 py-2 rounded border border-[hsl(var(--border))] bg-[hsl(var(--background))] text-sm focus:outline-none focus:ring-2 focus:ring-violet-500/30 resize-none"
            />
          </div>

          {/* Meta */}
          <div className="pt-3 border-t border-[hsl(var(--border))] text-xs text-[hsl(var(--muted-foreground))]">
            <p>ID: {task.id}</p>
            <p>Created: {new Date(task.created_at).toLocaleString()}</p>
            <p>Updated: {new Date(task.updated_at).toLocaleString()}</p>
            {task.blocked_by.length > 0 && (
              <p className="text-red-500">Blocked by: {task.blocked_by.join(', ')}</p>
            )}
          </div>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between px-5 h-14 border-t border-[hsl(var(--border))] shrink-0">
          <button
            onClick={handleDelete}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-md text-sm text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors"
          >
            <Trash2 className="w-4 h-4" />
            Delete
          </button>
          <div className="flex gap-2">
            <button
              onClick={onClose}
              className="px-3 py-1.5 rounded-md text-sm text-[hsl(var(--muted-foreground))] hover:bg-[hsl(var(--accent))] transition-colors"
            >
              Cancel
            </button>
            <button
              onClick={handleSave}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-md bg-violet-500 text-white text-sm font-medium hover:bg-violet-600 transition-colors"
            >
              <Save className="w-4 h-4" />
              Save
            </button>
          </div>
        </div>
      </aside>
    </>
  );
}
