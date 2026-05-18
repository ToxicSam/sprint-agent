import { useState, useRef, useEffect } from 'react';
import type { TaskStatus, Priority } from '@/types';
import { useStore } from '@/store';
import { Plus } from 'lucide-react';

interface InlineTaskCreatorProps {
  status: TaskStatus;
  onClose?: () => void;
}

export default function InlineTaskCreator({ status, onClose }: InlineTaskCreatorProps) {
  const [expanded, setExpanded] = useState(false);
  const [title, setTitle] = useState('');
  const [assigneeId, setAssigneeId] = useState('');
  const [priority, setPriority] = useState<Priority>(5);
  const [storyPoints, setStoryPoints] = useState('');
  const titleRef = useRef<HTMLInputElement>(null);
  const members = useStore(s => s.members);
  const createTask = useStore(s => s.createTask);

  useEffect(() => {
    if (expanded && titleRef.current) {
      titleRef.current.focus();
    }
  }, [expanded]);

  const handleCreate = async () => {
    if (!title.trim()) return;
    await createTask({
      title: title.trim(),
      assignee_id: assigneeId || undefined,
      status,
      priority,
      story_points: storyPoints ? parseInt(storyPoints) : undefined,
    });
    setTitle('');
    setAssigneeId('');
    setPriority(5);
    setStoryPoints('');
    setExpanded(false);
    onClose?.();
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      handleCreate();
    } else if (e.key === 'Escape') {
      setExpanded(false);
      onClose?.();
    }
  };

  if (!expanded) {
    return (
      <button
        onClick={() => setExpanded(true)}
        className="flex items-center gap-2 w-full px-3 py-2 rounded-lg border border-dashed border-[hsl(var(--border))] text-sm text-[hsl(var(--muted-foreground))] hover:text-[hsl(var(--foreground))] hover:border-[hsl(var(--muted-foreground))] hover:bg-[hsl(var(--accent))] transition-colors mt-2"
      >
        <Plus className="w-3.5 h-3.5" />
        Click or type to add a task
      </button>
    );
  }

  return (
    <div className="mt-2 p-3 rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--card))] shadow-sm space-y-2" onKeyDown={handleKeyDown}>
      <input
        ref={titleRef}
        type="text"
        value={title}
        onChange={e => setTitle(e.target.value)}
        placeholder="What needs to be done?"
        className="w-full h-8 px-2 rounded border border-[hsl(var(--border))] bg-[hsl(var(--background))] text-sm focus:outline-none focus:ring-2 focus:ring-violet-500/30 placeholder:text-[hsl(var(--muted-foreground))]"
      />
      <div className="flex gap-2">
        <select
          value={assigneeId}
          onChange={e => setAssigneeId(e.target.value)}
          className="h-8 px-2 rounded border border-[hsl(var(--border))] bg-[hsl(var(--background))] text-xs focus:outline-none focus:ring-2 focus:ring-violet-500/30"
        >
          <option value="">Assignee</option>
          {members.map(m => (
            <option key={m.id} value={m.id}>{m.name}</option>
          ))}
        </select>
        <select
          value={priority}
          onChange={e => setPriority(parseInt(e.target.value) as Priority)}
          className="h-8 px-2 rounded border border-[hsl(var(--border))] bg-[hsl(var(--background))] text-xs focus:outline-none focus:ring-2 focus:ring-violet-500/30"
        >
          <option value={10}>Critical</option>
          <option value={8}>High</option>
          <option value={5}>Medium</option>
          <option value={2}>Low</option>
        </select>
        <input
          type="number"
          value={storyPoints}
          onChange={e => setStoryPoints(e.target.value)}
          placeholder="Est"
          min={0}
          max={100}
          className="h-8 w-16 px-2 rounded border border-[hsl(var(--border))] bg-[hsl(var(--background))] text-xs focus:outline-none focus:ring-2 focus:ring-violet-500/30"
        />
      </div>
      <div className="flex gap-2">
        <button
          onClick={handleCreate}
          disabled={!title.trim()}
          className="px-3 py-1.5 rounded-md bg-violet-500 text-white text-xs font-medium hover:bg-violet-600 disabled:opacity-40 transition-colors"
        >
          Create
        </button>
        <button
          onClick={() => {
            setExpanded(false);
            onClose?.();
          }}
          className="px-3 py-1.5 rounded-md text-xs font-medium text-[hsl(var(--muted-foreground))] hover:bg-[hsl(var(--accent))] transition-colors"
        >
          Cancel
        </button>
      </div>
    </div>
  );
}
