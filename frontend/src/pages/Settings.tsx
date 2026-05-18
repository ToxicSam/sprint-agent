import { useState, useCallback, useEffect, useRef, useMemo } from 'react';
import { useStore } from '@/store';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Switch } from '@/components/ui/switch';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from '@/components/ui/alert-dialog';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import type { Member, MemberRole } from '@/types';
import { cn } from '@/lib/utils';
import {
  Settings2,
  Users,
  Database,
  Bot,
  Palette,
  Sun,
  Moon,
  Monitor,
  Upload,
  Download,
  FileJson,
  FileSpreadsheet,
  FileText,
  AlertTriangle,
  RotateCcw,
  Plus,
  Trash2,
  Pencil,
  Check,
  X,
  Globe,
  Clock,
  Briefcase,
  Sparkles,
  MessageSquare,
  Zap,
  Type,
  Layout,
  Eye,
  CheckCircle2,
  Loader2,
} from 'lucide-react';

/* ================================================================== */
/*  TYPES                                                              */
/* ================================================================== */

interface SettingsState {
  theme: 'light' | 'dark' | 'system';
  language: string;
  dateFormat: 'iso' | 'us' | 'eu';
  timeZone: string;
  workingHoursStart: number;
  workingHoursEnd: number;
  weekendSat: boolean;
  weekendSun: boolean;
  sprintDuration: number;
  accentColor: string;
  fontSize: 'sm' | 'md' | 'lg';
  animations: boolean;
  denseMode: boolean;
  agentPersonality: 'professional' | 'friendly' | 'direct';
  agentPrompt: string;
  autoSuggestions: boolean;
  contextMemory: boolean;
  keyboardHints: boolean;
}

const DEFAULT_SETTINGS: SettingsState = {
  theme: 'system',
  language: 'en',
  dateFormat: 'iso',
  timeZone: Intl.DateTimeFormat().resolvedOptions().timeZone,
  workingHoursStart: 9,
  workingHoursEnd: 18,
  weekendSat: true,
  weekendSun: true,
  sprintDuration: 14,
  accentColor: '#7C3AED',
  fontSize: 'md',
  animations: true,
  denseMode: false,
  agentPersonality: 'professional',
  agentPrompt: '',
  autoSuggestions: false,
  contextMemory: true,
  keyboardHints: true,
};

const ACCENT_COLORS = [
  { value: '#7C3AED', label: 'Purple' },
  { value: '#3B82F6', label: 'Blue' },
  { value: '#22C55E', label: 'Green' },
  { value: '#F59E0B', label: 'Orange' },
  { value: '#EC4899', label: 'Pink' },
  { value: '#14B8A6', label: 'Teal' },
];

const ROLES: { value: MemberRole; label: string }[] = [
  { value: 'sm', label: 'Scrum Master' },
  { value: 'dev', label: 'Developer' },
  { value: 'qa', label: 'QA Engineer' },
  { value: 'po', label: 'Product Owner' },
];

/* ================================================================== */
/*  MAIN COMPONENT                                                     */
/* ================================================================== */

export default function SettingsPage() {
  const members = useStore((s) => s.members);
  const [activeTab, setActiveTab] = useState('general');
  const [settings, setSettings] = useState<SettingsState>(() => {
    try {
      const saved = localStorage.getItem('app-settings');
      return saved ? { ...DEFAULT_SETTINGS, ...JSON.parse(saved) } : DEFAULT_SETTINGS;
    } catch {
      return DEFAULT_SETTINGS;
    }
  });
  const [hasChanges, setHasChanges] = useState(false);

  const updateSetting = useCallback(<K extends keyof SettingsState>(key: K, value: SettingsState[K]) => {
    setSettings((prev) => ({ ...prev, [key]: value }));
    setHasChanges(true);
  }, []);

  const saveSettings = useCallback(() => {
    localStorage.setItem('app-settings', JSON.stringify(settings));
    setHasChanges(false);
  }, [settings]);

  const resetSettings = useCallback(() => {
    setSettings(DEFAULT_SETTINGS);
    localStorage.removeItem('app-settings');
    setHasChanges(true);
  }, []);

  // Apply theme to document
  useEffect(() => {
    const root = document.documentElement;
    const isDark =
      settings.theme === 'dark' ||
      (settings.theme === 'system' && window.matchMedia('(prefers-color-scheme: dark)').matches);
    root.classList.toggle('dark', isDark);
  }, [settings.theme]);

  const tabItems = [
    { value: 'general', label: 'General', icon: Settings2 },
    { value: 'team', label: 'Team', icon: Users },
    { value: 'data', label: 'Data', icon: Database },
    { value: 'agent', label: 'Agent', icon: Bot },
    { value: 'appearance', label: 'Appearance', icon: Palette },
  ];

  return (
    <div className="p-6 max-w-[720px] mx-auto space-y-6">
      {/* Page header */}
      <div className="space-y-1">
        <h1 className="text-2xl font-bold text-[hsl(var(--foreground))]">Settings</h1>
        <p className="text-sm text-[hsl(var(--muted-foreground))]">Configure your workspace</p>
      </div>

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="mb-4 w-full justify-start">
          {tabItems.map((tab) => (
            <TabsTrigger key={tab.value} value={tab.value} className="gap-1.5">
              <tab.icon className="w-3.5 h-3.5" />
              <span className="hidden sm:inline">{tab.label}</span>
            </TabsTrigger>
          ))}
        </TabsList>

        {/* ---------- Tab: General ---------- */}
        <TabsContent value="general">
          <GeneralTab settings={settings} updateSetting={updateSetting} />
        </TabsContent>

        {/* ---------- Tab: Team ---------- */}
        <TabsContent value="team">
          <TeamTab members={members} />
        </TabsContent>

        {/* ---------- Tab: Data ---------- */}
        <TabsContent value="data">
          <DataTab />
        </TabsContent>

        {/* ---------- Tab: Agent ---------- */}
        <TabsContent value="agent">
          <AgentTab settings={settings} updateSetting={updateSetting} />
        </TabsContent>

        {/* ---------- Tab: Appearance ---------- */}
        <TabsContent value="appearance">
          <AppearanceTab settings={settings} updateSetting={updateSetting} />
        </TabsContent>
      </Tabs>

      {/* Bottom action bar */}
      <div className="sticky bottom-0 bg-[hsl(var(--background))] border-t border-[hsl(var(--border))] px-0 py-3 flex items-center justify-between -mx-6 px-6 -mb-6 mt-6 z-10">
        <AlertDialog>
          <AlertDialogTrigger asChild>
            <Button variant="ghost" size="sm" className="gap-2 text-[hsl(var(--muted-foreground))]">
              <RotateCcw className="w-4 h-4" />
              Reset to Defaults
            </Button>
          </AlertDialogTrigger>
          <AlertDialogContent>
            <AlertDialogHeader>
              <AlertDialogTitle>Reset All Settings?</AlertDialogTitle>
              <AlertDialogDescription>
                This will restore all settings to their default values. This action cannot be undone.
              </AlertDialogDescription>
            </AlertDialogHeader>
            <AlertDialogFooter>
              <AlertDialogCancel>Cancel</AlertDialogCancel>
              <AlertDialogAction onClick={resetSettings} className="bg-destructive text-white hover:bg-destructive/90">
                Reset
              </AlertDialogAction>
            </AlertDialogFooter>
          </AlertDialogContent>
        </AlertDialog>

        <Button onClick={saveSettings} disabled={!hasChanges} className="gap-2">
          <Check className="w-4 h-4" />
          Save Changes
        </Button>
      </div>
    </div>
  );
}

/* ================================================================== */
/*  GENERAL TAB                                                        */
/* ================================================================== */

function GeneralTab({
  settings,
  updateSetting,
}: {
  settings: SettingsState;
  updateSetting: <K extends keyof SettingsState>(key: K, value: SettingsState[K]) => void;
}) {
  const today = new Date();
  const datePreview = useMemo(() => {
    const d = today;
    switch (settings.dateFormat) {
      case 'us':
        return `${d.getMonth() + 1}/${d.getDate()}/${d.getFullYear()}`;
      case 'eu':
        return `${d.getDate()}/${d.getMonth() + 1}/${d.getFullYear()}`;
      default:
        return d.toISOString().slice(0, 10);
    }
  }, [settings.dateFormat]);

  return (
    <Card className="p-6 space-y-5">
      {/* Theme */}
      <div className="space-y-2">
        <label className="text-sm font-medium flex items-center gap-2">
          <Palette className="w-4 h-4 text-[hsl(var(--muted-foreground))]" />
          Theme
        </label>
        <div className="flex gap-2">
          {[
            { value: 'light' as const, icon: Sun, label: 'Light' },
            { value: 'dark' as const, icon: Moon, label: 'Dark' },
            { value: 'system' as const, icon: Monitor, label: 'System' },
          ].map((opt) => (
            <Button
              key={opt.value}
              variant={settings.theme === opt.value ? 'default' : 'outline'}
              size="sm"
              onClick={() => updateSetting('theme', opt.value)}
              className="gap-2 flex-1"
            >
              <opt.icon className="w-4 h-4" />
              {opt.label}
            </Button>
          ))}
        </div>
      </div>

      {/* Language */}
      <div className="space-y-2">
        <label className="text-sm font-medium flex items-center gap-2">
          <Globe className="w-4 h-4 text-[hsl(var(--muted-foreground))]" />
          Language
        </label>
        <Select value={settings.language} onValueChange={(v) => updateSetting('language', v)}>
          <SelectTrigger className="w-full">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="en">English</SelectItem>
            <SelectItem value="zh">中文 (Simplified Chinese)</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Date Format */}
      <div className="space-y-2">
        <label className="text-sm font-medium flex items-center gap-2">
          <CalendarIcon />
          Date Format
        </label>
        <div className="flex gap-2">
          {[
            { value: 'iso' as const, label: 'YYYY-MM-DD' },
            { value: 'us' as const, label: 'MM/DD/YYYY' },
            { value: 'eu' as const, label: 'DD/MM/YYYY' },
          ].map((opt) => (
            <Button
              key={opt.value}
              variant={settings.dateFormat === opt.value ? 'default' : 'outline'}
              size="sm"
              onClick={() => updateSetting('dateFormat', opt.value)}
              className="flex-1 text-xs"
            >
              {opt.label}
            </Button>
          ))}
        </div>
        <p className="text-xs text-[hsl(var(--muted-foreground))]">Today: {datePreview}</p>
      </div>

      {/* Working Hours */}
      <div className="space-y-2">
        <label className="text-sm font-medium flex items-center gap-2">
          <Clock className="w-4 h-4 text-[hsl(var(--muted-foreground))]" />
          Working Hours
        </label>
        <div className="flex items-center gap-3">
          <Input
            type="number"
            min={0}
            max={23}
            value={settings.workingHoursStart}
            onChange={(e) => updateSetting('workingHoursStart', parseInt(e.target.value) || 0)}
            className="w-20 text-center"
          />
          <span className="text-sm text-[hsl(var(--muted-foreground))]">to</span>
          <Input
            type="number"
            min={0}
            max={23}
            value={settings.workingHoursEnd}
            onChange={(e) => updateSetting('workingHoursEnd', parseInt(e.target.value) || 0)}
            className="w-20 text-center"
          />
        </div>
      </div>

      {/* Sprint Duration */}
      <div className="space-y-2">
        <label className="text-sm font-medium flex items-center gap-2">
          <Briefcase className="w-4 h-4 text-[hsl(var(--muted-foreground))]" />
          Default Sprint Duration
        </label>
        <div className="flex gap-2">
          {[
            { value: 10, label: '10 days' },
            { value: 14, label: '14 days' },
          ].map((opt) => (
            <Button
              key={opt.value}
              variant={settings.sprintDuration === opt.value ? 'default' : 'outline'}
              size="sm"
              onClick={() => updateSetting('sprintDuration', opt.value)}
              className="flex-1"
            >
              {opt.label}
            </Button>
          ))}
        </div>
        <div className="flex items-center gap-2">
          <span className="text-sm text-[hsl(var(--muted-foreground))]">Custom:</span>
          <Input
            type="number"
            min={1}
            max={30}
            value={settings.sprintDuration}
            onChange={(e) => updateSetting('sprintDuration', parseInt(e.target.value) || 14)}
            className="w-20 text-center"
          />
          <span className="text-sm text-[hsl(var(--muted-foreground))]">days</span>
        </div>
      </div>
    </Card>
  );
}

/* ================================================================== */
/*  TEAM TAB                                                           */
/* ================================================================== */

function TeamTab({ members: initialMembers }: { members: Member[] }) {
  const [members, setMembers] = useState<Member[]>(initialMembers);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editForm, setEditForm] = useState<Partial<Member>>({});

  // New member form
  const [showAddForm, setShowAddForm] = useState(false);
  const [newMember, setNewMember] = useState<{ name: string; role: MemberRole; capacity: string }>({
    name: '',
    role: 'dev',
    capacity: '8',
  });

  const handleStartEdit = useCallback((m: Member) => {
    setEditingId(m.id);
    setEditForm({ name: m.name, role: m.role, capacity: m.capacity });
  }, []);

  const handleSaveEdit = useCallback(() => {
    if (!editingId) return;
    setMembers((prev) =>
      prev.map((m) =>
        m.id === editingId
          ? { ...m, ...editForm, capacity: Number(editForm.capacity) || m.capacity }
          : m
      )
    );
    setEditingId(null);
  }, [editingId, editForm]);

  const handleCancelEdit = useCallback(() => {
    setEditingId(null);
    setEditForm({});
  }, []);

  const handleDeleteMember = useCallback((id: string) => {
    setMembers((prev) => prev.filter((m) => m.id !== id));
  }, []);

  const handleAddMember = useCallback(() => {
    if (!newMember.name.trim()) return;
    const member: Member = {
      id: `m-${Date.now()}`,
      name: newMember.name.trim(),
      role: newMember.role,
      capacity: parseInt(newMember.capacity) || 8,
    };
    setMembers((prev) => [...prev, member]);
    setNewMember({ name: '', role: 'dev', capacity: '8' });
    setShowAddForm(false);
  }, [newMember]);

  return (
    <div className="space-y-4">
      <Card className="p-6 gap-4">
        <div className="flex items-center justify-between">
          <h3 className="text-base font-semibold flex items-center gap-2">
            <Users className="w-4 h-4 text-[hsl(var(--muted-foreground))]" />
            Team Members
            <Badge variant="secondary" className="text-xs">{members.length}</Badge>
          </h3>
          <Button size="sm" onClick={() => setShowAddForm(true)} className="gap-2">
            <Plus className="w-4 h-4" />
            Add Member
          </Button>
        </div>

        <div className="border rounded-lg overflow-hidden">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Name</TableHead>
                <TableHead>Role</TableHead>
                <TableHead className="text-right">Capacity (h/day)</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {members.map((m) =>
                editingId === m.id ? (
                  <TableRow key={m.id}>
                    <TableCell>
                      <Input
                        value={editForm.name || ''}
                        onChange={(e) => setEditForm((f) => ({ ...f, name: e.target.value }))}
                        className="h-8 text-sm"
                      />
                    </TableCell>
                    <TableCell>
                      <Select
                        value={editForm.role as MemberRole}
                        onValueChange={(v) => setEditForm((f) => ({ ...f, role: v as MemberRole }))}
                      >
                        <SelectTrigger className="h-8 text-sm w-[140px]">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          {ROLES.map((r) => (
                            <SelectItem key={r.value} value={r.value}>
                              {r.label}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </TableCell>
                    <TableCell className="text-right">
                      <Input
                        type="number"
                        value={editForm.capacity || ''}
                        onChange={(e) => setEditForm((f) => ({ ...f, capacity: parseInt(e.target.value) || 0 }))}
                        className="h-8 text-sm w-20 inline-block text-right"
                      />
                    </TableCell>
                    <TableCell className="text-right">
                      <div className="flex items-center justify-end gap-1">
                        <Button variant="ghost" size="icon" onClick={handleSaveEdit} className="h-7 w-7">
                          <Check className="w-3.5 h-3.5 text-emerald-500" />
                        </Button>
                        <Button variant="ghost" size="icon" onClick={handleCancelEdit} className="h-7 w-7">
                          <X className="w-3.5 h-3.5" />
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ) : (
                  <TableRow key={m.id} className="group">
                    <TableCell className="font-medium">{m.name}</TableCell>
                    <TableCell>
                      <Badge variant="outline" className="text-xs">
                        {ROLES.find((r) => r.value === m.role)?.label || m.role}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-right tabular-nums">{m.capacity}h</TableCell>
                    <TableCell className="text-right">
                      <div className="flex items-center justify-end gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                        <Button variant="ghost" size="icon" onClick={() => handleStartEdit(m)} className="h-7 w-7">
                          <Pencil className="w-3.5 h-3.5" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => handleDeleteMember(m.id)}
                          className="h-7 w-7 text-red-500 hover:text-red-600 hover:bg-red-50"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                )
              )}
            </TableBody>
          </Table>
        </div>

        {/* Capacity summary */}
        <div className="flex items-center gap-4 text-sm text-[hsl(var(--muted-foreground))]">
          <span>
            Total capacity:{' '}
            <strong className="text-[hsl(var(--foreground))]">
              {members.reduce((s, m) => s + m.capacity, 0)}h/day
            </strong>
          </span>
          <span>
            Team:{' '}
            <strong className="text-[hsl(var(--foreground))]">
              {members.filter((m) => m.role === 'dev').length} dev
            </strong>
          </span>
          <span>
            QA:{' '}
            <strong className="text-[hsl(var(--foreground))]">
              {members.filter((m) => m.role === 'qa').length}
            </strong>
          </span>
        </div>
      </Card>

      {/* Add member dialog */}
      {showAddForm && (
        <Card className="p-4 gap-3 border-dashed border-2">
          <h4 className="text-sm font-medium">Add New Member</h4>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <Input
              placeholder="Name"
              value={newMember.name}
              onChange={(e) => setNewMember((p) => ({ ...p, name: e.target.value }))}
              onKeyDown={(e) => {
                if (e.key === 'Enter') handleAddMember();
              }}
              className="text-sm"
            />
            <Select
              value={newMember.role}
              onValueChange={(v) => setNewMember((p) => ({ ...p, role: v as MemberRole }))}
            >
              <SelectTrigger className="text-sm">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {ROLES.map((r) => (
                  <SelectItem key={r.value} value={r.value}>
                    {r.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Input
              type="number"
              placeholder="Capacity (h/day)"
              value={newMember.capacity}
              onChange={(e) => setNewMember((p) => ({ ...p, capacity: e.target.value }))}
              className="text-sm"
            />
          </div>
          <div className="flex justify-end gap-2">
            <Button variant="ghost" size="sm" onClick={() => setShowAddForm(false)}>
              Cancel
            </Button>
            <Button size="sm" onClick={handleAddMember} disabled={!newMember.name.trim()}>
              Add Member
            </Button>
          </div>
        </Card>
      )}
    </div>
  );
}

/* ================================================================== */
/*  DATA TAB                                                           */
/* ================================================================== */

function DataTab() {
  const [importData, setImportData] = useState<string>('');
  const [importFile, setImportFile] = useState<string>('');
  const [validationResult, setValidationResult] = useState<{
    valid: boolean;
    errors: string[];
    preview: { sprintName?: string; memberCount?: number; taskCount?: number } | null;
  } | null>(null);
  const [importing, setImporting] = useState(false);
  const [resetDialogOpen, setResetDialogOpen] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const dragRef = useRef<HTMLDivElement>(null);
  const [dragOver, setDragOver] = useState(false);

  const validateJson = useCallback((text: string): typeof validationResult => {
    try {
      const data = JSON.parse(text);
      const errors: string[] = [];
      if (!data || typeof data !== 'object') {
        return { valid: false, errors: ['Root must be an object'], preview: null };
      }
      if (!data.sprint && !data.members && !data.tasks) {
        errors.push('Missing required fields: sprint, members, or tasks');
      }
      const preview = {
        sprintName: data.sprint?.name,
        memberCount: Array.isArray(data.members) ? data.members.length : undefined,
        taskCount: Array.isArray(data.tasks) ? data.tasks.length : undefined,
      };
      return { valid: errors.length === 0, errors, preview: preview.sprintName || preview.memberCount !== undefined ? preview : null };
    } catch {
      return { valid: false, errors: ['Invalid JSON'], preview: null };
    }
  }, []);

  const handleFileDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setDragOver(false);
      const file = e.dataTransfer.files[0];
      if (!file || !file.name.endsWith('.json')) return;
      const reader = new FileReader();
      reader.onload = (ev) => {
        const text = String(ev.target?.result || '');
        setImportFile(file.name);
        setImportData(text);
        setValidationResult(validateJson(text));
      };
      reader.readAsText(file);
    },
    [validateJson]
  );

  const handleFileSelect = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0];
      if (!file) return;
      const reader = new FileReader();
      reader.onload = (ev) => {
        const text = String(ev.target?.result || '');
        setImportFile(file.name);
        setImportData(text);
        setValidationResult(validateJson(text));
      };
      reader.readAsText(file);
    },
    [validateJson]
  );

  const handleValidateText = useCallback(() => {
    if (!importData.trim()) return;
    setValidationResult(validateJson(importData));
  }, [importData, validateJson]);

  const handleImportReplace = useCallback(() => {
    if (!validationResult?.valid) return;
    setImporting(true);
    setTimeout(() => {
      try {
        localStorage.setItem('sprint_agent__api_board', importData);
        setImporting(false);
        setValidationResult(null);
        setImportData('');
        setImportFile('');
        window.location.reload();
      } catch {
        setImporting(false);
      }
    }, 600);
  }, [validationResult, importData]);

  const handleExportJson = useCallback(() => {
    const sprint = JSON.parse(localStorage.getItem('sprint_agent__api_board') || '{}');
    const payload = {
      sprint: sprint.sprint || { name: 'Sprint Export', goal: '', start_date: '', end_date: '', status: 'active', created_at: new Date().toISOString() },
      members: sprint.members || [],
      tasks: sprint.tasks || [],
      exportedAt: new Date().toISOString(),
    };
    const blob = new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `sprint-agent-data-${new Date().toISOString().slice(0, 10)}.json`;
    a.click();
    URL.revokeObjectURL(url);
  }, []);

  const handleExportCsv = useCallback(() => {
    const sprint = JSON.parse(localStorage.getItem('sprint_agent__api_board') || '{}');
    const tasks = sprint.tasks || [];
    const headers = ['id', 'title', 'status', 'priority', 'story_points', 'assignee_id', 'blocked_by', 'description'];
    const rows = tasks.map((t: Record<string, unknown>) =>
      headers.map((h) => {
        const val = t[h];
        if (Array.isArray(val)) return `"${val.join(',')}"`;
        return `"${String(val || '').replace(/"/g, '\\"')}"`;
      })
    );
    const csv = [headers.join(','), ...rows.map((r: string[]) => r.join(','))].join('\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `sprint-agent-tasks-${new Date().toISOString().slice(0, 10)}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  }, []);

  const handleExportMarkdown = useCallback(() => {
    const sprint = JSON.parse(localStorage.getItem('sprint_agent__api_board') || '{}');
    const tasks = sprint.tasks || [];
    let md = `# Sprint Report\n\n`;
    md += `| ID | Title | Status | Priority | Points | Assignee |\n`;
    md += `|---|---|---|---|---|---|\n`;
    tasks.forEach((t: Record<string, unknown>) => {
      md += `| ${t.id} | ${t.title} | ${t.status} | ${t.priority} | ${t.story_points || 0} | ${t.assignee_id || 'Unassigned'} |\n`;
    });
    const blob = new Blob([md], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `sprint-agent-report-${new Date().toISOString().slice(0, 10)}.md`;
    a.click();
    URL.revokeObjectURL(url);
  }, []);

  const handleResetDefault = useCallback(() => {
    localStorage.removeItem('sprint_agent__api_board');
    setResetDialogOpen(false);
    window.location.reload();
  }, []);

  return (
    <div className="space-y-4">
      {/* Import Section */}
      <Card className="p-6 gap-4">
        <h3 className="text-base font-semibold flex items-center gap-2">
          <Upload className="w-4 h-4 text-[hsl(var(--muted-foreground))]" />
          Import Data
        </h3>

        {/* Drag & drop zone */}
        <div
          ref={dragRef}
          onDragOver={(e) => {
            e.preventDefault();
            setDragOver(true);
          }}
          onDragLeave={() => setDragOver(false)}
          onDrop={handleFileDrop}
          onClick={() => fileInputRef.current?.click()}
          className={cn(
            'border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors',
            dragOver
              ? 'border-violet-500 bg-violet-50 dark:bg-violet-950/20'
              : 'border-[hsl(var(--border))] hover:border-[hsl(var(--muted-foreground))]/50 hover:bg-[hsl(var(--accent))]'
          )}
        >
          <Upload className="w-8 h-8 mx-auto mb-2 text-[hsl(var(--muted-foreground))]" />
          <p className="text-sm font-medium">
            {importFile ? `Selected: ${importFile}` : 'Drop a JSON data file here, or click to browse'}
          </p>
          <p className="text-xs text-[hsl(var(--muted-foreground))] mt-1">
            Format: {'{ sprint, members, tasks }'}
          </p>
          <input
            ref={fileInputRef}
            type="file"
            accept=".json"
            className="hidden"
            onChange={handleFileSelect}
          />
        </div>

        {/* Paste JSON */}
        <div className="space-y-2">
          <label className="text-xs font-medium text-[hsl(var(--muted-foreground))]">Or paste JSON:</label>
          <Textarea
            placeholder='{"sprint": {...}, "members": [...], "tasks": [...]}'
            value={importData}
            onChange={(e) => setImportData(e.target.value)}
            className="min-h-[80px] text-xs font-mono"
          />
          <div className="flex justify-end">
            <Button variant="outline" size="sm" onClick={handleValidateText} className="gap-1">
              <CheckCircle2 className="w-3.5 h-3.5" />
              Validate
            </Button>
          </div>
        </div>

        {/* Validation result */}
        {validationResult && (
          <div
            className={cn(
              'rounded-lg border p-3 text-sm',
              validationResult.valid
                ? 'border-emerald-200 bg-emerald-50 dark:border-emerald-800 dark:bg-emerald-950/30'
                : 'border-red-200 bg-red-50 dark:border-red-800 dark:bg-red-950/30'
            )}
          >
            {validationResult.valid ? (
              <div className="flex items-center gap-2 text-emerald-700 dark:text-emerald-300">
                <CheckCircle2 className="w-4 h-4 shrink-0" />
                <span>Valid JSON</span>
                {validationResult.preview && (
                  <span className="text-[hsl(var(--muted-foreground))] ml-2">
                    {validationResult.preview.sprintName && `${validationResult.preview.sprintName} · `}
                    {validationResult.preview.memberCount !== undefined && `${validationResult.preview.memberCount} members · `}
                    {validationResult.preview.taskCount !== undefined && `${validationResult.preview.taskCount} tasks`}
                  </span>
                )}
              </div>
            ) : (
              <div className="space-y-1">
                <div className="flex items-center gap-2 text-red-700 dark:text-red-300 font-medium">
                  <AlertTriangle className="w-4 h-4 shrink-0" />
                  <span>Validation failed</span>
                </div>
                <ul className="text-xs text-red-600 dark:text-red-400 ml-6 list-disc">
                  {validationResult.errors.map((err, i) => (
                    <li key={i}>{err}</li>
                  ))}
                </ul>
              </div>
            )}

            {validationResult.valid && (
              <div className="flex gap-2 mt-3">
                <Button size="sm" onClick={handleImportReplace} disabled={importing} className="gap-1">
                  {importing ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Download className="w-3.5 h-3.5" />}
                  Import & Replace
                </Button>
                <Button size="sm" variant="outline" onClick={handleImportReplace} disabled={importing} className="gap-1">
                  Import & Merge
                </Button>
              </div>
            )}
          </div>
        )}

        {/* Load from init.json */}
        <div className="pt-2 border-t border-[hsl(var(--border))]">
          <Button variant="ghost" size="sm" onClick={() => window.location.reload()} className="gap-2 text-[hsl(var(--muted-foreground))]">
            <RotateCcw className="w-4 h-4" />
            Reset to Default Data
          </Button>
        </div>
      </Card>

      {/* Export Section */}
      <Card className="p-6 gap-4">
        <h3 className="text-base font-semibold flex items-center gap-2">
          <Download className="w-4 h-4 text-[hsl(var(--muted-foreground))]" />
          Export Data
        </h3>
        <div className="flex flex-wrap gap-2">
          <Button variant="outline" onClick={handleExportJson} className="gap-2">
            <FileJson className="w-4 h-4" />
            Export as JSON
          </Button>
          <Button variant="outline" onClick={handleExportCsv} className="gap-2">
            <FileSpreadsheet className="w-4 h-4" />
            Export as CSV
          </Button>
          <Button variant="outline" onClick={handleExportMarkdown} className="gap-2">
            <FileText className="w-4 h-4" />
            Export as Markdown
          </Button>
        </div>
      </Card>

      {/* Reset Section */}
      <Card className="p-6 gap-4 border-red-200 dark:border-red-800/50">
        <h3 className="text-base font-semibold flex items-center gap-2 text-red-600 dark:text-red-400">
          <AlertTriangle className="w-4 h-4" />
          Reset
        </h3>
        <p className="text-sm text-[hsl(var(--muted-foreground))]">
          This will clear all sprint data, members, and tasks. This action cannot be undone.
        </p>
        <AlertDialog open={resetDialogOpen} onOpenChange={setResetDialogOpen}>
          <AlertDialogTrigger asChild>
            <Button variant="destructive" size="sm" className="gap-2 w-fit">
              <Trash2 className="w-4 h-4" />
              Reset to Default Data
            </Button>
          </AlertDialogTrigger>
          <AlertDialogContent>
            <AlertDialogHeader>
              <AlertDialogTitle>Reset All Data?</AlertDialogTitle>
              <AlertDialogDescription>
                This will delete all sprint data, members, tasks, and settings. This action is irreversible.
              </AlertDialogDescription>
            </AlertDialogHeader>
            <AlertDialogFooter>
              <AlertDialogCancel>Cancel</AlertDialogCancel>
              <AlertDialogAction onClick={handleResetDefault} className="bg-destructive text-white hover:bg-destructive/90">
                Reset
              </AlertDialogAction>
            </AlertDialogFooter>
          </AlertDialogContent>
        </AlertDialog>
      </Card>
    </div>
  );
}

/* ================================================================== */
/*  AGENT TAB                                                          */
/* ================================================================== */

function AgentTab({
  settings,
  updateSetting,
}: {
  settings: SettingsState;
  updateSetting: <K extends keyof SettingsState>(key: K, value: SettingsState[K]) => void;
}) {
  const personalities: { value: SettingsState['agentPersonality']; label: string; desc: string }[] = [
    { value: 'professional', label: 'Professional', desc: 'Formal, structured responses' },
    { value: 'friendly', label: 'Friendly', desc: 'Casual, conversational tone' },
    { value: 'direct', label: 'Direct', desc: 'Brief, to-the-point answers' },
  ];

  return (
    <Card className="p-6 space-y-5">
      {/* Personality */}
      <div className="space-y-2">
        <label className="text-sm font-medium flex items-center gap-2">
          <Sparkles className="w-4 h-4 text-[hsl(var(--muted-foreground))]" />
          Agent Personality
        </label>
        <div className="grid grid-cols-3 gap-2">
          {personalities.map((p) => (
            <button
              key={p.value}
              onClick={() => updateSetting('agentPersonality', p.value)}
              className={cn(
                'rounded-lg border p-3 text-left transition-colors',
                settings.agentPersonality === p.value
                  ? 'border-violet-500 bg-violet-50 dark:bg-violet-950/30'
                  : 'border-[hsl(var(--border))] hover:bg-[hsl(var(--accent))]'
              )}
            >
              <div className="text-sm font-medium">{p.label}</div>
              <div className="text-xs text-[hsl(var(--muted-foreground))]">{p.desc}</div>
            </button>
          ))}
        </div>
      </div>

      {/* Custom prompt */}
      <div className="space-y-2">
        <label className="text-sm font-medium flex items-center gap-2">
          <MessageSquare className="w-4 h-4 text-[hsl(var(--muted-foreground))]" />
          Custom System Prompt
        </label>
        <Textarea
          placeholder="Enter custom instructions for the AI agent..."
          value={settings.agentPrompt}
          onChange={(e) => updateSetting('agentPrompt', e.target.value)}
          className="min-h-[80px] text-sm"
        />
        <p className="text-xs text-[hsl(var(--muted-foreground))]">
          These instructions are prepended to every agent conversation.
        </p>
      </div>

      {/* Toggles */}
      <div className="space-y-3 pt-2">
        <ToggleRow
          icon={Zap}
          label="Auto-suggestions"
          description="Show completion suggestions while typing"
          checked={settings.autoSuggestions}
          onChange={(v) => updateSetting('autoSuggestions', v)}
        />
        <ToggleRow
          icon={Eye}
          label="Context Memory"
          description="Agent remembers context from previous conversations"
          checked={settings.contextMemory}
          onChange={(v) => updateSetting('contextMemory', v)}
        />
      </div>
    </Card>
  );
}

/* ================================================================== */
/*  APPEARANCE TAB                                                     */
/* ================================================================== */

function AppearanceTab({
  settings,
  updateSetting,
}: {
  settings: SettingsState;
  updateSetting: <K extends keyof SettingsState>(key: K, value: SettingsState[K]) => void;
}) {
  return (
    <Card className="p-6 space-y-5">
      {/* Theme */}
      <div className="space-y-2">
        <label className="text-sm font-medium">Theme</label>
        <div className="flex gap-2">
          {[
            { value: 'light' as const, icon: Sun, label: 'Light' },
            { value: 'dark' as const, icon: Moon, label: 'Dark' },
            { value: 'system' as const, icon: Monitor, label: 'System' },
          ].map((opt) => (
            <Button
              key={opt.value}
              variant={settings.theme === opt.value ? 'default' : 'outline'}
              size="sm"
              onClick={() => updateSetting('theme', opt.value)}
              className="gap-2 flex-1"
            >
              <opt.icon className="w-4 h-4" />
              {opt.label}
            </Button>
          ))}
        </div>
      </div>

      {/* Accent Color */}
      <div className="space-y-2">
        <label className="text-sm font-medium flex items-center gap-2">
          <Palette className="w-4 h-4 text-[hsl(var(--muted-foreground))]" />
          Accent Color
        </label>
        <div className="flex gap-2">
          {ACCENT_COLORS.map((c) => (
            <button
              key={c.value}
              onClick={() => updateSetting('accentColor', c.value)}
              className={cn(
                'w-8 h-8 rounded-full border-2 transition-all',
                settings.accentColor === c.value
                  ? 'border-[hsl(var(--foreground))] scale-110 shadow-md'
                  : 'border-transparent hover:scale-105'
              )}
              style={{ backgroundColor: c.value }}
              title={c.label}
            />
          ))}
        </div>
      </div>

      {/* Font Size */}
      <div className="space-y-2">
        <label className="text-sm font-medium flex items-center gap-2">
          <Type className="w-4 h-4 text-[hsl(var(--muted-foreground))]" />
          Font Size
        </label>
        <div className="flex gap-2">
          {[
            { value: 'sm' as const, label: 'Compact' },
            { value: 'md' as const, label: 'Default' },
            { value: 'lg' as const, label: 'Comfortable' },
          ].map((opt) => (
            <Button
              key={opt.value}
              variant={settings.fontSize === opt.value ? 'default' : 'outline'}
              size="sm"
              onClick={() => updateSetting('fontSize', opt.value)}
              className="flex-1"
            >
              {opt.label}
            </Button>
          ))}
        </div>
      </div>

      {/* Toggles */}
      <div className="space-y-3 pt-2">
        <ToggleRow
          icon={Sparkles}
          label="Animations"
          description="Enable UI animations and transitions"
          checked={settings.animations}
          onChange={(v) => updateSetting('animations', v)}
        />
        <ToggleRow
          icon={Layout}
          label="Dense Mode"
          description="Compact layout with tighter spacing"
          checked={settings.denseMode}
          onChange={(v) => updateSetting('denseMode', v)}
        />
        <ToggleRow
          icon={Eye}
          label="Keyboard Hints"
          description="Show shortcut hints in bottom bar and tooltips"
          checked={settings.keyboardHints}
          onChange={(v) => updateSetting('keyboardHints', v)}
        />
      </div>
    </Card>
  );
}

/* ================================================================== */
/*  SHARED COMPONENTS                                                  */
/* ================================================================== */

function ToggleRow({
  icon: Icon,
  label,
  description,
  checked,
  onChange,
}: {
  icon: typeof Zap;
  label: string;
  description: string;
  checked: boolean;
  onChange: (val: boolean) => void;
}) {
  return (
    <div className="flex items-center justify-between py-2">
      <div className="flex items-center gap-3">
        <Icon className="w-4 h-4 text-[hsl(var(--muted-foreground))] shrink-0" />
        <div>
          <div className="text-sm font-medium">{label}</div>
          <div className="text-xs text-[hsl(var(--muted-foreground))]">{description}</div>
        </div>
      </div>
      <Switch checked={checked} onCheckedChange={onChange} />
    </div>
  );
}

function CalendarIcon() {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width="16"
      height="16"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      className="text-[hsl(var(--muted-foreground))]"
    >
      <rect width="18" height="18" x="3" y="4" rx="2" ry="2" />
      <line x1="16" x2="16" y1="2" y2="6" />
      <line x1="8" x2="8" y1="2" y2="6" />
      <line x1="3" x2="21" y1="10" y2="10" />
    </svg>
  );
}


