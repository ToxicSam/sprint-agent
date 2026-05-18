import { useState, useCallback, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { format, addDays, differenceInBusinessDays } from 'date-fns';
import {
  Users, Plus, Trash2, Upload, Calendar, Target,
  Zap, Clock, Save, ChevronDown, X, Check, Edit2,
  FileJson, Table2, AlertTriangle, Sparkles
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { Label } from '@/components/ui/label';
import { Checkbox } from '@/components/ui/checkbox';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover';
import { Calendar as CalendarComponent } from '@/components/ui/calendar';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { cn } from '@/lib/utils';
import { useStore } from '@/store';
import type { Member, MemberRole } from '@/types';
import type { DateRange } from 'react-day-picker';

// ─── Types ───────────────────────────────────────────────

interface DraftMember {
  id: string;
  name: string;
  role: MemberRole;
  capacity: number;
  coe: number;
  isEditing: boolean;
}

interface SprintForm {
  name: string;
  goal: string;
  startDate: Date;
  endDate: Date;
  workdays: number;
  status: 'planning' | 'active';
}

// ─── Constants ───────────────────────────────────────────

const ROLE_OPTIONS: { value: MemberRole; label: string }[] = [
  { value: 'sm', label: 'SM' },
  { value: 'dev', label: 'Dev' },
  { value: 'qa', label: 'QA' },
  { value: 'po', label: 'PO' },
];

const ROLE_COLORS: Record<MemberRole, string> = {
  sm: 'bg-[#7C3AED] text-white',
  dev: 'bg-[#3B82F6] text-white',
  qa: 'bg-[#F59E0B] text-white',
  po: 'bg-[#22C55E] text-white',
};

const DEFAULT_COE = 1.0;
const HOURS_PER_DAY = 8;

const TEMPLATES = [
  { label: 'Quick 1-week', days: 5 },
  { label: 'Standard 2-week', days: 10 },
  { label: 'Extended 3-week', days: 15 },
];

// ─── Helpers ─────────────────────────────────────────────

function generateSprintName(date: Date = new Date()): string {
  return `Sprint ${format(date, 'dd.MM')}`;
}

function calcWorkdays(start: Date, end: Date): number {
  const diff = differenceInBusinessDays(end, start);
  return Math.max(1, diff);
}

function calcCapacity(workdays: number, coe: number): number {
  return Math.round(workdays * HOURS_PER_DAY * coe);
}

function createDraftMember(overrides?: Partial<DraftMember>): DraftMember {
  return {
    id: `dm-${Date.now()}-${Math.random().toString(36).slice(2, 5)}`,
    name: '',
    role: 'dev',
    capacity: 0,
    coe: DEFAULT_COE,
    isEditing: true,
    ...overrides,
  };
}

// ─── Member Row Component ────────────────────────────────

interface MemberRowProps {
  member: DraftMember;
  index: number;
  onUpdate: (id: string, patch: Partial<DraftMember>) => void;
  onRemove: (id: string) => void;
  onStartEdit: (id: string) => void;
  onFinishEdit: (id: string) => void;
  onTabFromCoe: () => void;
  workdays: number;
}

function MemberRow({
  member,
  onUpdate,
  onRemove,
  onStartEdit,
  onFinishEdit,
  onTabFromCoe,
  workdays,
}: MemberRowProps) {
  const capacity = calcCapacity(workdays, member.coe);
  const isEditing = member.isEditing;

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      onFinishEdit(member.id);
    } else if (e.key === 'Tab' && e.currentTarget.dataset.field === 'coe') {
      e.preventDefault();
      onTabFromCoe();
    }
  };

  const handleBlur = () => {
    if (member.name.trim()) {
      onFinishEdit(member.id);
    }
  };

  const handleDoubleClick = () => {
    onStartEdit(member.id);
  };

  return (
    <TableRow
      className={cn(
        'group transition-all duration-150',
        isEditing && 'bg-accent/30'
      )}
    >
      {/* Name */}
      <TableCell onDoubleClick={handleDoubleClick}>
        {isEditing ? (
          <Input
            autoFocus
            data-field="name"
            value={member.name}
            onChange={(e) => onUpdate(member.id, { name: e.target.value })}
            onKeyDown={handleKeyDown}
            onBlur={handleBlur}
            placeholder="Name"
            className="h-8 text-sm"
          />
        ) : (
          <span className="text-sm font-medium">{member.name || '—'}</span>
        )}
      </TableCell>

      {/* Role */}
      <TableCell onDoubleClick={handleDoubleClick}>
        {isEditing ? (
          <Select
            value={member.role}
            onValueChange={(v) => onUpdate(member.id, { role: v as MemberRole })}
          >
            <SelectTrigger className="h-8 text-sm w-24">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {ROLE_OPTIONS.map((opt) => (
                <SelectItem key={opt.value} value={opt.value}>
                  {opt.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        ) : (
          <Badge
            className={cn(
              'text-[10px] font-bold uppercase px-1.5 py-0.5',
              ROLE_COLORS[member.role]
            )}
            variant="default"
          >
            {ROLE_OPTIONS.find((r) => r.value === member.role)?.label || member.role}
          </Badge>
        )}
      </TableCell>

      {/* CoE */}
      <TableCell onDoubleClick={handleDoubleClick}>
        {isEditing ? (
          <Input
            data-field="coe"
            type="number"
            step={0.1}
            min={0.1}
            max={2.0}
            value={member.coe}
            onChange={(e) =>
              onUpdate(member.id, { coe: parseFloat(e.target.value) || DEFAULT_COE })
            }
            onKeyDown={handleKeyDown}
            onBlur={handleBlur}
            className="h-8 text-sm w-20"
          />
        ) : (
          <span className="text-sm tabular-nums">{member.coe.toFixed(1)}</span>
        )}
      </TableCell>

      {/* Capacity */}
      <TableCell>
        <span
          className="text-sm font-semibold tabular-nums"
          title={`${workdays} workdays × ${HOURS_PER_DAY}h × ${member.coe} CoE = ${capacity}h`}
        >
          {capacity}h
        </span>
      </TableCell>

      {/* Actions */}
      <TableCell>
        <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
          <button
            onClick={() => onStartEdit(member.id)}
            className="p-1 rounded hover:bg-muted transition-colors"
            title="Edit"
          >
            <Edit2 className="w-3.5 h-3.5 text-muted-foreground" />
          </button>
          <button
            onClick={() => onRemove(member.id)}
            className="p-1 rounded hover:bg-destructive/10 transition-colors"
            title="Delete"
          >
            <Trash2 className="w-3.5 h-3.5 text-destructive" />
          </button>
        </div>
      </TableCell>
    </TableRow>
  );
}

// ─── Main Planning Page ──────────────────────────────────

export default function Planning() {
  const navigate = useNavigate();
  const setBoardData = useStore((s) => s.setBoardData);
  const existingMembers = useStore((s) => s.members);
  const existingSprint = useStore((s) => s.sprint);

  // ── Form State ────────────────────────────
  const today = new Date();
  const defaultEnd = addDays(today, 13);
  const [form, setForm] = useState<SprintForm>({
    name: generateSprintName(today),
    goal: '',
    startDate: today,
    endDate: defaultEnd,
    workdays: calcWorkdays(today, defaultEnd),
    status: 'planning',
  });

  // ── Members State ─────────────────────────
  const [members, setMembers] = useState<DraftMember[]>(() => {
    if (existingMembers.length > 0) {
      return existingMembers.map((m) =>
        createDraftMember({
          id: m.id,
          name: m.name,
          role: m.role,
          capacity: m.capacity,
          coe: DEFAULT_COE,
          isEditing: false,
        })
      );
    }
    return [];
  });

  // ── Import / Dialog State ─────────────────
  const [importTab, setImportTab] = useState('json');
  const [importText, setImportText] = useState('');
  const [showConfirmDialog, setShowConfirmDialog] = useState(false);
  const [confirmAction, setConfirmAction] = useState<(() => void) | null>(null);
  const [confirmTitle, setConfirmTitle] = useState('');
  const [confirmDesc, setConfirmDesc] = useState('');
  const fileInputRef = useRef<HTMLInputElement>(null);
  const jsonFileRef = useRef<HTMLInputElement>(null);

  // ── Update workdays when dates change ─────
  useEffect(() => {
    setForm((prev) => ({
      ...prev,
      workdays: calcWorkdays(prev.startDate, prev.endDate),
    }));
  }, [form.startDate, form.endDate]);

  // ── Handlers ──────────────────────────────

  const handleUpdateMember = useCallback(
    (id: string, patch: Partial<DraftMember>) => {
      setMembers((prev) =>
        prev.map((m) => (m.id === id ? { ...m, ...patch } : m))
      );
    },
    []
  );

  const handleAddMember = useCallback(() => {
    const newMember = createDraftMember();
    setMembers((prev) => [...prev, newMember]);
  }, []);

  const handleRemoveMember = useCallback((id: string) => {
    const member = members.find((m) => m.id === id);
    if (member && member.name.trim()) {
      setConfirmTitle('Delete Member');
      setConfirmDesc(`Remove "${member.name}" from the team?`);
      setConfirmAction(() => () => {
        setMembers((prev) => prev.filter((m) => m.id !== id));
        setShowConfirmDialog(false);
      });
      setShowConfirmDialog(true);
    } else {
      setMembers((prev) => prev.filter((m) => m.id !== id));
    }
  }, [members]);

  const handleStartEdit = useCallback((id: string) => {
    setMembers((prev) =>
      prev.map((m) => (m.id === id ? { ...m, isEditing: true } : m))
    );
  }, []);

  const handleFinishEdit = useCallback((id: string) => {
    setMembers((prev) =>
      prev.map((m) => (m.id === id ? { ...m, isEditing: false } : m))
    );
  }, []);

  const handleTabFromCoe = useCallback(() => {
    handleAddMember();
  }, [handleAddMember]);

  const handleTemplateSelect = useCallback(
    (days: number) => {
      const start = new Date();
      const end = addDays(start, days - 1);
      setForm((prev) => ({
        ...prev,
        startDate: start,
        endDate: end,
        workdays: days,
      }));
    },
    []
  );

  const handleImportJson = useCallback(
    (event: React.ChangeEvent<HTMLInputElement>) => {
      const file = event.target.files?.[0];
      if (!file) return;

      const reader = new FileReader();
      reader.onload = (e) => {
        try {
          const data = JSON.parse(e.target?.result as string);
          const imported: DraftMember[] = [];

          if (Array.isArray(data.members)) {
            data.members.forEach((m: Record<string, unknown>) => {
              const role = (m.role as MemberRole) || 'dev';
              if (
                typeof m.name === 'string' &&
                ROLE_OPTIONS.some((r) => r.value === role)
              ) {
                imported.push(
                  createDraftMember({
                    name: m.name,
                    role: role,
                    coe: typeof m.coe === 'number' ? m.coe : DEFAULT_COE,
                    isEditing: false,
                  })
                );
              }
            });
          }

          if (imported.length > 0) {
            setMembers(imported);
          }
        } catch {
          setConfirmTitle('Import Error');
          setConfirmDesc('Could not parse the JSON file. Please check the format.');
          setConfirmAction(() => () => setShowConfirmDialog(false));
          setShowConfirmDialog(true);
        }
      };
      reader.readAsText(file);

      event.target.value = '';
    },
    []
  );

  const handleImportCsv = useCallback(() => {
    if (!importText.trim()) return;

    const lines = importText
      .split('\n')
      .map((l) => l.trim())
      .filter(Boolean);
    if (lines.length === 0) return;

    const imported: DraftMember[] = [];
    const startIdx = lines[0].toLowerCase().includes('name') ? 1 : 0;

    for (let i = startIdx; i < lines.length; i++) {
      const parts = lines[i].split(/[,\t]/).map((p) => p.trim());
      if (parts.length >= 2 && parts[0]) {
        const rawRole = parts[1].toLowerCase();
        const role =
          ROLE_OPTIONS.find(
            (r) =>
              r.value === rawRole ||
              r.label.toLowerCase() === rawRole ||
              r.value === rawRole.replace(/[^a-z]/g, '')
          )?.value || 'dev';

        imported.push(
          createDraftMember({
            name: parts[0],
            role: role,
            coe: parseFloat(parts[2]) || DEFAULT_COE,
            isEditing: false,
          })
        );
      }
    }

    if (imported.length > 0) {
      setMembers(imported);
      setImportText('');
    }
  }, [importText]);

  const handleCreateSprint = useCallback(() => {
    if (!form.name.trim()) return;
    if (members.length === 0) return;

    const sprintMembers: Member[] = members.map((m) => ({
      id: m.id,
      name: m.name,
      role: m.role,
      capacity: calcCapacity(form.workdays, m.coe),
    }));

    const sprint = {
      id: `s-${Date.now()}`,
      name: form.name.trim(),
      goal: form.goal.trim(),
      start_date: form.startDate.toISOString().split('T')[0],
      end_date: form.endDate.toISOString().split('T')[0],
      status: (form.status === 'active' ? 'active' : 'active') as 'active',
      created_at: new Date().toISOString(),
    };

    setBoardData(sprint, sprintMembers, []);
    navigate('/');
  }, [form, members, navigate, setBoardData]);

  const handleSaveTemplate = useCallback(() => {
    const template = {
      name: form.name,
      goal: form.goal,
      workdays: form.workdays,
      members: members.map((m) => ({
        name: m.name,
        role: m.role,
        coe: m.coe,
      })),
    };

    const blob = new Blob([JSON.stringify(template, null, 2)], {
      type: 'application/json',
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `sprint-template-${format(new Date(), 'yyyyMMdd')}.json`;
    a.click();
    URL.revokeObjectURL(url);
  }, [form, members]);

  // ── Derived Values ────────────────────────

  const totalCapacity = members.reduce(
    (sum, m) => sum + calcCapacity(form.workdays, m.coe),
    0
  );

  const canCreate = form.name.trim().length > 0 && members.length > 0 && members.every((m) => m.name.trim());

  const dateRange: DateRange = {
    from: form.startDate,
    to: form.endDate,
  };

  // ── Render ────────────────────────────────

  return (
    <div className="p-6 lg:p-8 max-w-[1200px] mx-auto space-y-6">
      {/* Page Header */}
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-violet-500 to-pink-500 flex items-center justify-center">
          <Calendar className="w-5 h-5 text-white" />
        </div>
        <div>
          <h1 className="text-2xl font-bold text-[hsl(var(--foreground))]">
            Sprint Planning
          </h1>
          <p className="text-sm text-[hsl(var(--muted-foreground))]">
            Configure your sprint, team, and capacity
          </p>
        </div>
      </div>

      {/* Two Column Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">
        {/* ── Left Column: Sprint Setup (60%) ── */}
        <div className="lg:col-span-3 space-y-6">
          {/* Sprint Setup Card */}
          <div className="rounded-xl border border-[hsl(var(--border))] bg-[hsl(var(--card))] p-6 space-y-5">
            <div className="flex items-center gap-2">
              <Target className="w-4 h-4 text-[hsl(var(--primary))]" />
              <h2 className="text-lg font-semibold">Sprint Setup</h2>
            </div>

            {/* Sprint Name + Status Row */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label className="text-sm font-medium">Sprint Name</Label>
                <Input
                  value={form.name}
                  onChange={(e) =>
                    setForm((prev) => ({ ...prev, name: e.target.value }))
                  }
                  placeholder="Sprint 26.06"
                  className="h-9"
                />
              </div>

              <div className="space-y-2">
                <Label className="text-sm font-medium">Status</Label>
                <div className="flex items-center gap-3 h-9">
                  <button
                    onClick={() =>
                      setForm((prev) => ({ ...prev, status: 'planning' }))
                    }
                    className={cn(
                      'flex-1 h-9 rounded-md text-sm font-medium border transition-all',
                      form.status === 'planning'
                        ? 'border-[#7C3AED] bg-[#7C3AED]/10 text-[#7C3AED]'
                        : 'border-[hsl(var(--border))] text-[hsl(var(--muted-foreground))] hover:bg-[hsl(var(--accent))]'
                    )}
                  >
                    <span className="flex items-center justify-center gap-1.5">
                      <Clock className="w-3.5 h-3.5" />
                      Planning
                    </span>
                  </button>
                  <button
                    onClick={() =>
                      setForm((prev) => ({ ...prev, status: 'active' }))
                    }
                    className={cn(
                      'flex-1 h-9 rounded-md text-sm font-medium border transition-all',
                      form.status === 'active'
                        ? 'border-[#22C55E] bg-[#22C55E]/10 text-[#22C55E]'
                        : 'border-[hsl(var(--border))] text-[hsl(var(--muted-foreground))] hover:bg-[hsl(var(--accent))]'
                    )}
                  >
                    <span className="flex items-center justify-center gap-1.5">
                      <Zap className="w-3.5 h-3.5" />
                      Active
                    </span>
                  </button>
                </div>
              </div>
            </div>

            {/* Date Range */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div className="space-y-2">
                <Label className="text-sm font-medium">Start Date</Label>
                <Popover>
                  <PopoverTrigger asChild>
                    <Button
                      variant="outline"
                      className="w-full justify-start text-left font-normal h-9"
                    >
                      <Calendar className="mr-2 h-4 w-4" />
                      {format(form.startDate, 'MMM d, yyyy')}
                    </Button>
                  </PopoverTrigger>
                  <PopoverContent className="w-auto p-0" align="start">
                    <CalendarComponent
                      mode="single"
                      selected={form.startDate}
                      onSelect={(date) =>
                        date &&
                        setForm((prev) => ({ ...prev, startDate: date }))
                      }
                      initialFocus
                    />
                  </PopoverContent>
                </Popover>
              </div>

              <div className="space-y-2">
                <Label className="text-sm font-medium">End Date</Label>
                <Popover>
                  <PopoverTrigger asChild>
                    <Button
                      variant="outline"
                      className="w-full justify-start text-left font-normal h-9"
                    >
                      <Calendar className="mr-2 h-4 w-4" />
                      {format(form.endDate, 'MMM d, yyyy')}
                    </Button>
                  </PopoverTrigger>
                  <PopoverContent className="w-auto p-0" align="start">
                    <CalendarComponent
                      mode="single"
                      selected={form.endDate}
                      onSelect={(date) =>
                        date && setForm((prev) => ({ ...prev, endDate: date }))
                      }
                      disabled={(date) => date < form.startDate}
                      initialFocus
                    />
                  </PopoverContent>
                </Popover>
              </div>

              <div className="space-y-2">
                <Label className="text-sm font-medium">Workdays</Label>
                <Input
                  type="number"
                  min={1}
                  max={30}
                  value={form.workdays}
                  onChange={(e) =>
                    setForm((prev) => ({
                      ...prev,
                      workdays: parseInt(e.target.value) || 1,
                    }))
                  }
                  className="h-9"
                />
              </div>
            </div>

            {/* Sprint Goal */}
            <div className="space-y-2">
              <Label className="text-sm font-medium">Sprint Goal</Label>
              <Textarea
                value={form.goal}
                onChange={(e) =>
                  setForm((prev) => ({ ...prev, goal: e.target.value }))
                }
                placeholder="What do we want to achieve in this sprint?"
                rows={2}
                className="resize-none"
              />
            </div>

            {/* Template Presets */}
            <div className="space-y-2">
              <Label className="text-sm font-medium">Quick Templates</Label>
              <div className="flex gap-2">
                {TEMPLATES.map((t) => (
                  <Button
                    key={t.days}
                    variant="outline"
                    size="sm"
                    onClick={() => handleTemplateSelect(t.days)}
                    className="text-xs"
                  >
                    <Sparkles className="w-3 h-3 mr-1" />
                    {t.label}
                  </Button>
                ))}
              </div>
            </div>
          </div>

          {/* Import Section */}
          <div className="rounded-xl border border-[hsl(var(--border))] bg-[hsl(var(--card))] p-6 space-y-4">
            <div className="flex items-center gap-2">
              <Upload className="w-4 h-4 text-[hsl(var(--primary))]" />
              <h2 className="text-lg font-semibold">Import Members</h2>
            </div>

            <Tabs value={importTab} onValueChange={setImportTab}>
              <TabsList className="grid w-full grid-cols-2">
                <TabsTrigger value="json">
                  <FileJson className="w-3.5 h-3.5 mr-1.5" />
                  JSON Upload
                </TabsTrigger>
                <TabsTrigger value="csv">
                  <Table2 className="w-3.5 h-3.5 mr-1.5" />
                  CSV / Paste
                </TabsTrigger>
              </TabsList>

              <TabsContent value="json" className="space-y-3 mt-3">
                <input
                  ref={jsonFileRef}
                  type="file"
                  accept=".json"
                  onChange={handleImportJson}
                  className="hidden"
                />
                <div
                  onClick={() => jsonFileRef.current?.click()}
                  className={cn(
                    'border-2 border-dashed border-[hsl(var(--border))] rounded-lg',
                    'p-6 flex flex-col items-center justify-center gap-2',
                    'cursor-pointer hover:border-[hsl(var(--primary))]/50 hover:bg-[hsl(var(--accent))]/50 transition-all'
                  )}
                >
                  <Upload className="w-8 h-8 text-[hsl(var(--muted-foreground))]" />
                  <p className="text-sm text-[hsl(var(--muted-foreground))]">
                    Click to upload JSON file
                  </p>
                  <p className="text-xs text-[hsl(var(--muted-foreground))]/60">
                    Supports members array with name, role, coe fields
                  </p>
                </div>
              </TabsContent>

              <TabsContent value="csv" className="space-y-3 mt-3">
                <Textarea
                  value={importText}
                  onChange={(e) => setImportText(e.target.value)}
                  placeholder={`Paste tab or comma-separated data:\nName, Role, CoE\nAlice, Dev, 1.0\nBob, QA, 0.9`}
                  rows={4}
                  className="resize-none font-mono text-xs"
                />
                <Button
                  variant="secondary"
                  size="sm"
                  onClick={handleImportCsv}
                  disabled={!importText.trim()}
                >
                  <Upload className="w-3.5 h-3.5 mr-1.5" />
                  Import from Text
                </Button>
              </TabsContent>
            </Tabs>
          </div>
        </div>

        {/* ── Right Column: Team Members (40%) ── */}
        <div className="lg:col-span-2 space-y-6">
          <div className="rounded-xl border border-[hsl(var(--border))] bg-[hsl(var(--card))] p-6 space-y-4">
            {/* Member Header */}
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Users className="w-4 h-4 text-[hsl(var(--primary))]" />
                <h2 className="text-lg font-semibold">Team Members</h2>
                <Badge
                  variant="secondary"
                  className="text-xs"
                >
                  {members.length}
                </Badge>
              </div>
              <Button
                size="sm"
                onClick={handleAddMember}
                className="h-8 text-xs"
              >
                <Plus className="w-3.5 h-3.5 mr-1" />
                Add Member
              </Button>
            </div>

            {/* Members Table */}
            <div className="rounded-lg border border-[hsl(var(--border))] overflow-hidden">
              <Table>
                <TableHeader>
                  <TableRow className="hover:bg-transparent">
                    <TableHead className="text-xs font-medium w-[40%]">
                      Name
                    </TableHead>
                    <TableHead className="text-xs font-medium">
                      Role
                    </TableHead>
                    <TableHead className="text-xs font-medium">
                      CoE
                    </TableHead>
                    <TableHead className="text-xs font-medium">
                      Cap.
                    </TableHead>
                    <TableHead className="text-xs font-medium w-10" />
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {members.length === 0 ? (
                    <TableRow>
                      <TableCell
                        colSpan={5}
                        className="text-center py-8 text-sm text-[hsl(var(--muted-foreground))]"
                      >
                        No team members yet.
                        <br />
                        Click &quot;Add Member&quot; to get started.
                      </TableCell>
                    </TableRow>
                  ) : (
                    members.map((member, idx) => (
                      <MemberRow
                        key={member.id}
                        member={member}
                        index={idx}
                        onUpdate={handleUpdateMember}
                        onRemove={handleRemoveMember}
                        onStartEdit={handleStartEdit}
                        onFinishEdit={handleFinishEdit}
                        onTabFromCoe={handleTabFromCoe}
                        workdays={form.workdays}
                      />
                    ))
                  )}
                </TableBody>
              </Table>
            </div>

            {/* Capacity Summary */}
            {members.length > 0 && (
              <div className="rounded-lg bg-[hsl(var(--accent))] p-4 flex items-center justify-between">
                <div>
                  <p className="text-xs text-[hsl(var(--muted-foreground))]">
                    Total Capacity
                  </p>
                  <p className="text-2xl font-bold tabular-nums">
                    {totalCapacity}h
                  </p>
                </div>
                <div className="text-right">
                  <p className="text-xs text-[hsl(var(--muted-foreground))]">
                    Members
                  </p>
                  <p className="text-lg font-semibold">
                    {members.length}
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* ── Sticky Action Bar ── */}
      <div className="fixed bottom-0 left-0 right-0 bg-[hsl(var(--card))] border-t border-[hsl(var(--border))] p-4 z-20">
        <div className="max-w-[1200px] mx-auto flex items-center justify-between">
          <div className="flex items-center gap-4 text-sm text-[hsl(var(--muted-foreground))]">
            <span className="flex items-center gap-1.5">
              <Users className="w-4 h-4" />
              {members.length} members
            </span>
            <span className="flex items-center gap-1.5">
              <Clock className="w-4 h-4" />
              {form.workdays} workdays
            </span>
            <span className="flex items-center gap-1.5 font-semibold text-[hsl(var(--foreground))]">
              <Zap className="w-4 h-4" />
              {totalCapacity}h total
            </span>
          </div>

          <div className="flex items-center gap-3">
            <Button
              variant="outline"
              size="sm"
              onClick={handleSaveTemplate}
              disabled={members.length === 0}
            >
              <Save className="w-4 h-4 mr-1.5" />
              Save as Template
            </Button>
            <Button
              size="sm"
              onClick={handleCreateSprint}
              disabled={!canCreate}
              className="bg-[hsl(var(--primary))] text-[hsl(var(--primary-foreground))] hover:bg-[hsl(var(--primary))]/90"
            >
              <Zap className="w-4 h-4 mr-1.5" />
              Create Sprint
            </Button>
          </div>
        </div>
      </div>

      {/* Bottom padding to account for sticky bar */}
      <div className="h-16" />

      {/* ── Confirm Dialog ── */}
      <Dialog open={showConfirmDialog} onOpenChange={setShowConfirmDialog}>
        <DialogContent className="sm:max-w-[400px]">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <AlertTriangle className="w-5 h-5 text-[hsl(var(--destructive))]" />
              {confirmTitle}
            </DialogTitle>
            <DialogDescription>{confirmDesc}</DialogDescription>
          </DialogHeader>
          <DialogFooter className="gap-2">
            <Button
              variant="outline"
              onClick={() => setShowConfirmDialog(false)}
            >
              Cancel
            </Button>
            <Button
              variant="destructive"
              onClick={() => confirmAction?.()}
            >
              Confirm
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
