import { useState, useEffect, useMemo, useCallback, useRef } from 'react';
import {
  useReactTable,
  getCoreRowModel,
  flexRender,
  createColumnHelper,
  type CellContext,
} from '@tanstack/react-table';
import {
  Plus,
  Copy,
  Trash2,
  Send,
  CalendarClock,
  Keyboard,
  AlertTriangle,
  CheckCircle2,
  Users,
} from 'lucide-react';
import { format, subDays, parseISO, isValid } from 'date-fns';
import { useStore } from '@/store';
import { useKeyboardNavigation } from '@/hooks/useKeyboardNavigation';
import { cn } from '@/lib/utils';
import { toast } from 'sonner';
import type { Member } from '@/types';

// ------------------------------------------------------------------
// Types
// ------------------------------------------------------------------
interface StandupRow {
  member: Member;
  yesterday: string;
  completed: string;
  planned: string;
  blockers: string;
  hours: number | '';
}

interface StandupDraft {
  date: string;
  rows: StandupRow[];
  lastSaved: string;
}

// ------------------------------------------------------------------
// Helpers
// ------------------------------------------------------------------
const EDITABLE_COLS = ['completed', 'planned', 'blockers', 'hours'] as const;
type EditableCol = (typeof EDITABLE_COLS)[number];

function draftKey(date: string) {
  return `standup_draft_${date}`;
}

function getYesterdayStr(date: string): string {
  try {
    return format(subDays(parseISO(date), 1), 'yyyy-MM-dd');
  } catch {
    return format(subDays(new Date(), 1), 'yyyy-MM-dd');
  }
}

function loadDraft(date: string, members: Member[]): StandupRow[] | null {
  try {
    const raw = localStorage.getItem(draftKey(date));
    if (raw) {
      const draft = JSON.parse(raw) as StandupDraft;
      if (draft.rows && draft.rows.length === members.length) {
        return draft.rows;
      }
    }
  } catch {
    // ignore
  }
  return null;
}

function saveDraft(date: string, rows: StandupRow[]) {
  try {
    const draft: StandupDraft = {
      date,
      rows,
      lastSaved: new Date().toISOString(),
    };
    localStorage.setItem(draftKey(date), JSON.stringify(draft));
  } catch {
    // ignore storage errors
  }
}

function loadYesterdayLogs(date: string): Record<string, Partial<StandupRow>> {
  try {
    const yest = getYesterdayStr(date);
    const raw = localStorage.getItem(draftKey(yest));
    if (raw) {
      const draft = JSON.parse(raw) as StandupDraft;
      const map: Record<string, Partial<StandupRow>> = {};
      for (const row of draft.rows) {
        map[row.member.id] = {
          planned: row.planned, // yesterday's planned = today's yesterday
          completed: row.completed,
          hours: row.hours,
        };
      }
      return map;
    }
  } catch {
    // ignore
  }
  return {};
}

function createEmptyRows(members: Member[]): StandupRow[] {
  return members.map((m) => ({
    member: m,
    yesterday: '',
    completed: '',
    planned: '',
    blockers: '',
    hours: '',
  }));
}

function formatDateLabel(date: string): string {
  try {
    const d = parseISO(date);
    if (!isValid(d)) return date;
    return format(d, 'MMMM d, yyyy');
  } catch {
    return date;
  }
}

// ------------------------------------------------------------------
// Inline Input Cell Component
// ------------------------------------------------------------------
function InlineInputCell({
  value,
  onChange,
  onBlur,
  placeholder,
  type = 'text',
  rowId,
  colId,
  registerCell,
  onKeyDown,
  className,
}: {
  value: string | number;
  onChange: (v: string) => void;
  onBlur?: () => void;
  placeholder?: string;
  type?: 'text' | 'number';
  rowId: string;
  colId: string;
  registerCell: (rowId: string, colId: string, el: HTMLInputElement | null) => void;
  onKeyDown: (e: React.KeyboardEvent<HTMLInputElement>) => void;
  className?: string;
}) {
  const [localValue, setLocalValue] = useState(() => String(value ?? ''));
  const isBlocker = colId === 'blockers' && String(localValue).trim().length > 0;

  // Sync external value
  useEffect(() => {
    setLocalValue(String(value ?? ''));
  }, [value]);

  return (
    <input
      ref={(el) => registerCell(rowId, colId, el)}
      type={type}
      value={localValue}
      placeholder={placeholder}
      onChange={(e) => {
        setLocalValue(e.target.value);
        onChange(e.target.value);
      }}
      onBlur={() => {
        onBlur?.();
      }}
      onKeyDown={onKeyDown}
      className={cn(
        'w-full h-full px-3 py-2.5 text-sm bg-transparent border-none outline-none',
        'focus:bg-[var(--bg-elevated)] focus:ring-2 focus:ring-inset focus:ring-[#7C3AED]/20',
        'transition-colors duration-150',
        type === 'number' && 'text-right tabular-nums',
        isBlocker && 'text-[#EF4444] font-medium placeholder:text-[#EF4444]/40',
        className
      )}
      step={type === 'number' ? '0.5' : undefined}
      min={type === 'number' ? '0' : undefined}
      max={type === 'number' ? '24' : undefined}
    />
  );
}

// ------------------------------------------------------------------
// Main Standup Page
// ------------------------------------------------------------------
export default function Standup() {
  const members = useStore((s) => s.members);
  const sprint = useStore((s) => s.sprint);

  const todayStr = format(new Date(), 'yyyy-MM-dd');
  const [selectedDate, setSelectedDate] = useState(todayStr);
  const [rows, setRows] = useState<StandupRow[]>(() => createEmptyRows(members));
  const [submittedAt, setSubmittedAt] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [lastSaved, setLastSaved] = useState<string | null>(null);
  const [showShortcuts, setShowShortcuts] = useState(false);
  const [viewAll, setViewAll] = useState(true); // all members vs my tasks

  const autoSaveTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const tableContainerRef = useRef<HTMLDivElement>(null);

  // Row IDs for keyboard navigation
  const rowIds = useMemo(() => rows.map((r) => r.member.id), [rows]);
  const colIds = useMemo(() => [...EDITABLE_COLS], []);

  // ----------------------------------------------------------------
  // Init & Draft Loading
  // ----------------------------------------------------------------
  useEffect(() => {
    const draft = loadDraft(selectedDate, members);
    if (draft) {
      setRows(draft);
    } else {
      // Try to fill "yesterday" from previous day's draft
      const yestLogs = loadYesterdayLogs(selectedDate);
      const fresh = createEmptyRows(members).map((row) => {
        const yest = yestLogs[row.member.id];
        if (yest) {
          return {
            ...row,
            yesterday: yest.planned || '',
          };
        }
        return row;
      });
      setRows(fresh);
    }
  }, [selectedDate, members]);

  // ----------------------------------------------------------------
  // Auto-save
  // ----------------------------------------------------------------
  const triggerAutoSave = useCallback(() => {
    if (autoSaveTimer.current) clearTimeout(autoSaveTimer.current);
    autoSaveTimer.current = setTimeout(() => {
      saveDraft(selectedDate, rows);
      setLastSaved(format(new Date(), 'HH:mm:ss'));
    }, 800);
  }, [selectedDate, rows]);

  useEffect(() => {
    triggerAutoSave();
    return () => {
      if (autoSaveTimer.current) clearTimeout(autoSaveTimer.current);
    };
  }, [rows, triggerAutoSave]);

  // ----------------------------------------------------------------
  // Cell update helper
  // ----------------------------------------------------------------
  const updateCell = useCallback(
    (memberId: string, col: EditableCol, value: string) => {
      setRows((prev) =>
        prev.map((r) =>
          r.member.id === memberId ? { ...r, [col]: value } : r
        )
      );
    },
    []
  );

  // ----------------------------------------------------------------
  // Batch Operations
  // ----------------------------------------------------------------
  const handleFillFromYesterday = useCallback(() => {
    const yestLogs = loadYesterdayLogs(selectedDate);
    let filled = 0;
    setRows((prev) =>
      prev.map((r) => {
        const yest = yestLogs[r.member.id];
        if (yest && !r.completed && yest.planned) {
          filled++;
          return { ...r, completed: yest.planned };
        }
        return r;
      })
    );
    toast.success(`Filled ${filled} member${filled !== 1 ? 's' : ''} from yesterday`);
  }, [selectedDate]);

  const handleCopyYesterday = useCallback(() => {
    setRows((prev) =>
      prev.map((r) => ({
        ...r,
        completed: r.yesterday || r.completed,
      }))
    );
    toast.success('Copied Yesterday column to Completed for all members');
  }, []);

  const handleClearAll = useCallback(() => {
    if (
      window.confirm(
        'Clear all standup entries? This will reset all editable fields for this date.'
      )
    ) {
      setRows((prev) =>
        prev.map((r) => ({
          ...r,
          completed: '',
          planned: '',
          blockers: '',
          hours: '',
        }))
      );
      toast.info('All entries cleared');
    }
  }, []);

  const handleAddLog = useCallback(() => {
    // Create a temporary "new member" row
    const tempId = `temp-${Date.now()}`;
    const newMember: Member = {
      id: tempId,
      name: 'New Member',
      role: 'dev',
      capacity: 8,
    };
    const newRow: StandupRow = {
      member: newMember,
      yesterday: '',
      completed: '',
      planned: '',
      blockers: '',
      hours: '',
    };
    setRows((prev) => [...prev, newRow]);
    // Focus the new row after render
    setTimeout(() => {
      nav.focusCell(tempId, 'completed');
    }, 50);
  }, []);

  // ----------------------------------------------------------------
  // Submit
  // ----------------------------------------------------------------
  const handleSubmit = useCallback(async () => {
    // Validate
    let hasError = false;
    for (const r of rows) {
      const h = Number(r.hours);
      if (r.hours !== '' && (isNaN(h) || h < 0 || h > 24)) {
        hasError = true;
        toast.error(`${r.member.name}: Hours must be between 0 and 24`);
      }
    }
    if (hasError) return;

    setSubmitting(true);

    // Simulate API call
    await new Promise((res) => setTimeout(res, 600));

    const now = new Date().toISOString();
    setSubmittedAt(now);
    saveDraft(selectedDate, rows);

    toast.success(`Standup submitted for ${formatDateLabel(selectedDate)}`);
    setSubmitting(false);
  }, [rows, selectedDate]);

  // ----------------------------------------------------------------
  // Keyboard Navigation
  // ----------------------------------------------------------------
  const nav = useKeyboardNavigation({
    onSubmit: handleSubmit,
    onFillFromYesterday: handleFillFromYesterday,
  });

  // ----------------------------------------------------------------
  // Derived stats
  // ----------------------------------------------------------------
  const completedCount = rows.filter(
    (r) => r.completed.trim() || r.planned.trim() || r.hours !== ''
  ).length;
  const totalHours = rows.reduce((sum, r) => {
    const h = Number(r.hours);
    return sum + (isNaN(h) ? 0 : h);
  }, 0);
  const blockerCount = rows.filter((r) => r.blockers.trim()).length;
  const hasChanges = rows.some(
    (r) => r.completed.trim() || r.planned.trim() || r.blockers.trim() || r.hours !== ''
  );

  // ----------------------------------------------------------------
  // TanStack Table Columns
  // ----------------------------------------------------------------
  const columnHelper = createColumnHelper<StandupRow>();

  const columns = useMemo(
    () => [
      // ---- Member Column ----
      columnHelper.accessor('member', {
        header: 'Member',
        size: 140,
        cell: (info: CellContext<StandupRow, Member>) => {
          const member = info.getValue();
          return (
            <div className="flex items-center gap-2 px-3 py-2">
              <div className="w-7 h-7 rounded-full bg-gradient-to-br from-violet-500 to-pink-500 flex items-center justify-center text-white text-xs font-semibold shrink-0">
                {member.name.charAt(0)}
              </div>
              <div className="min-w-0">
                <div className="text-sm font-medium truncate">{member.name}</div>
                <div className="text-xs text-[var(--text-tertiary)] uppercase">{member.role}</div>
              </div>
            </div>
          );
        },
      }),

      // ---- Yesterday Column (read-only) ----
      columnHelper.accessor('yesterday', {
        header: 'Yesterday',
        size: 180,
        cell: (info: CellContext<StandupRow, string>) => (
          <div className="px-3 py-2 text-sm text-[var(--text-secondary)] truncate max-w-[180px]">
            {info.getValue() || (
              <span className="text-[var(--text-tertiary)] italic">—</span>
            )}
          </div>
        ),
      }),

      // ---- Completed Column ----
      columnHelper.accessor('completed', {
        header: 'Completed',
        size: 180,
        cell: (info: CellContext<StandupRow, string>) => {
          const row = info.row.original;
          return (
            <InlineInputCell
              value={info.getValue()}
              onChange={(v) => updateCell(row.member.id, 'completed', v)}
              placeholder="What was done..."
              rowId={row.member.id}
              colId="completed"
              registerCell={nav.registerCell}
              onKeyDown={(e) =>
                nav.handleKeyDown(e, rowIds, colIds, row.member.id, 'completed')
              }
            />
          );
        },
      }),

      // ---- Planned Column ----
      columnHelper.accessor('planned', {
        header: 'Planned',
        size: 180,
        cell: (info: CellContext<StandupRow, string>) => {
          const row = info.row.original;
          return (
            <InlineInputCell
              value={info.getValue()}
              onChange={(v) => updateCell(row.member.id, 'planned', v)}
              placeholder="What's planned..."
              rowId={row.member.id}
              colId="planned"
              registerCell={nav.registerCell}
              onKeyDown={(e) =>
                nav.handleKeyDown(e, rowIds, colIds, row.member.id, 'planned')
              }
            />
          );
        },
      }),

      // ---- Blockers Column ----
      columnHelper.accessor('blockers', {
        header: 'Blockers',
        size: 160,
        cell: (info: CellContext<StandupRow, string>) => {
          const row = info.row.original;
          const hasBlocker = !!info.getValue().trim();
          return (
            <div className="relative">
              <InlineInputCell
                value={info.getValue()}
                onChange={(v) => updateCell(row.member.id, 'blockers', v)}
                placeholder="Any blockers..."
                rowId={row.member.id}
                colId="blockers"
                registerCell={nav.registerCell}
                onKeyDown={(e) =>
                  nav.handleKeyDown(e, rowIds, colIds, row.member.id, 'blockers')
                }
                className={cn(hasBlocker && 'text-[#EF4444]')}
              />
              {hasBlocker && (
                <div className="absolute left-0 top-0 bottom-0 w-0.5 bg-[#EF4444]" />
              )}
            </div>
          );
        },
      }),

      // ---- Hours Column ----
      columnHelper.accessor('hours', {
        header: () => <span className="text-right block w-full">Hours</span>,
        size: 80,
        cell: (info: CellContext<StandupRow, number | ''>) => {
          const row = info.row.original;
          return (
            <InlineInputCell
              value={info.getValue()}
              onChange={(v) => {
                // Validate 0-24
                const num = parseFloat(v);
                if (v === '' || (!isNaN(num) && num >= 0 && num <= 24)) {
                  updateCell(row.member.id, 'hours', v);
                }
              }}
              placeholder="0"
              type="number"
              rowId={row.member.id}
              colId="hours"
              registerCell={nav.registerCell}
              onKeyDown={(e) =>
                nav.handleKeyDown(e, rowIds, colIds, row.member.id, 'hours')
              }
            />
          );
        },
      }),
    ],
    [updateCell, nav, rowIds, colIds]
  );

  const table = useReactTable({
    data: rows,
    columns,
    getCoreRowModel: getCoreRowModel(),
    enableRowSelection: false,
  });

  // ----------------------------------------------------------------
  // Render
  // ----------------------------------------------------------------
  return (
    <div className="flex flex-col h-[calc(100dvh-48px-32px)] overflow-hidden">
      {/* ========== HEADER ========== */}
      <div className="shrink-0 px-6 py-4 bg-[var(--bg-surface)] border-b border-[var(--border-default)] flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-bold text-[var(--text-primary)]">
              Standup
            </h1>
            <input
              type="date"
              value={selectedDate}
              onChange={(e) => setSelectedDate(e.target.value)}
              className="text-sm border border-[var(--border-default)] rounded-md px-2 py-1 bg-[var(--bg-surface)] text-[var(--text-primary)] outline-none focus:ring-2 focus:ring-[#7C3AED]/30"
            />
          </div>
          <p className="text-sm text-[var(--text-secondary)] mt-0.5">
            {formatDateLabel(selectedDate)}
            {sprint && (
              <span className="ml-2">
                ·{' '}
                <span className="font-medium text-[#7C3AED]">{sprint.name}</span>
              </span>
            )}
          </p>
        </div>

        <div className="flex items-center gap-2">
          {/* Progress badge */}
          <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-[var(--bg-elevated)] text-xs font-medium text-[var(--text-secondary)]">
            <CheckCircle2 className="w-3.5 h-3.5 text-[#22C55E]" />
            <span>
              {completedCount}/{rows.length} filled
            </span>
          </div>
          {blockerCount > 0 && (
            <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-red-50 dark:bg-red-900/20 text-xs font-medium text-[#EF4444]">
              <AlertTriangle className="w-3.5 h-3.5" />
              <span>{blockerCount} blocker</span>
            </div>
          )}
          <button
            onClick={handleSubmit}
            disabled={submitting || !hasChanges}
            className={cn(
              'flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-all',
              submitting || !hasChanges
                ? 'bg-[var(--bg-elevated)] text-[var(--text-tertiary)] cursor-not-allowed'
                : 'bg-[#7C3AED] text-white hover:bg-[#6D28D9] shadow-sm'
            )}
          >
            {submitting ? (
              <>
                <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                Submitting...
              </>
            ) : (
              <>
                <Send className="w-4 h-4" />
                Submit
              </>
            )}
          </button>
        </div>
      </div>

      {/* ========== TOOLBAR ========== */}
      <div className="shrink-0 px-6 py-2.5 bg-[var(--bg-surface)] border-b border-[var(--border-subtle)] flex flex-wrap items-center gap-2">
        <button
          onClick={handleAddLog}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-md text-sm font-medium text-[#7C3AED] bg-[#7C3AED]/10 hover:bg-[#7C3AED]/20 transition-colors"
        >
          <Plus className="w-3.5 h-3.5" />
          Log
        </button>

        <button
          onClick={handleFillFromYesterday}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-md text-sm font-medium text-[var(--text-secondary)] hover:bg-[var(--bg-elevated)] transition-colors"
          title="Fill empty Completed from yesterday's Planned (Y)"
        >
          <CalendarClock className="w-3.5 h-3.5" />
          Fill from Yesterday
        </button>

        <button
          onClick={handleCopyYesterday}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-md text-sm font-medium text-[var(--text-secondary)] hover:bg-[var(--bg-elevated)] transition-colors"
          title="Copy Yesterday column to Completed"
        >
          <Copy className="w-3.5 h-3.5" />
          Copy Yesterday
        </button>

        <button
          onClick={handleClearAll}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-md text-sm font-medium text-[var(--text-secondary)] hover:bg-red-50 dark:hover:bg-red-900/20 hover:text-[#EF4444] transition-colors"
        >
          <Trash2 className="w-3.5 h-3.5" />
          Clear All
        </button>

        <div className="flex-1" />

        {/* View toggle */}
        <div className="flex items-center gap-1 bg-[var(--bg-elevated)] rounded-md p-0.5">
          <button
            onClick={() => setViewAll(true)}
            className={cn(
              'flex items-center gap-1.5 px-3 py-1 rounded text-xs font-medium transition-colors',
              viewAll
                ? 'bg-[var(--bg-surface)] text-[var(--text-primary)] shadow-sm'
                : 'text-[var(--text-tertiary)] hover:text-[var(--text-secondary)]'
            )}
          >
            <Users className="w-3 h-3" />
            All
          </button>
          <button
            onClick={() => setViewAll(false)}
            className={cn(
              'flex items-center gap-1.5 px-3 py-1 rounded text-xs font-medium transition-colors',
              !viewAll
                ? 'bg-[var(--bg-surface)] text-[var(--text-primary)] shadow-sm'
                : 'text-[var(--text-tertiary)] hover:text-[var(--text-secondary)]'
            )}
          >
            Me
          </button>
        </div>

        {/* Keyboard shortcuts toggle */}
        <button
          onClick={() => setShowShortcuts(!showShortcuts)}
          className="flex items-center gap-1.5 px-2 py-1.5 rounded-md text-xs text-[var(--text-tertiary)] hover:text-[var(--text-secondary)] hover:bg-[var(--bg-elevated)] transition-colors"
          title="Keyboard shortcuts"
        >
          <Keyboard className="w-3.5 h-3.5" />
          Shortcuts
        </button>

        {lastSaved && (
          <span className="text-xs text-[var(--text-tertiary)] ml-1">
            Auto-saved {lastSaved}
          </span>
        )}
      </div>

      {/* ========== SHORTCUTS PANEL ========== */}
      {showShortcuts && (
        <div className="shrink-0 px-6 py-2 bg-[var(--bg-elevated)] border-b border-[var(--border-default)] flex flex-wrap gap-x-6 gap-y-1">
          <ShortcutItem keys={['Tab']} desc="Next cell" />
          <ShortcutItem keys={['Shift', 'Tab']} desc="Previous cell" />
          <ShortcutItem keys={['Enter']} desc="Next row" />
          <ShortcutItem keys={['Shift', 'Enter']} desc="Previous row" />
          <ShortcutItem keys={['Ctrl', 'Enter']} desc="Submit all" />
          <ShortcutItem keys={['Y']} desc="Fill from yesterday" />
          <ShortcutItem keys={['Esc']} desc="Cancel edit" />
        </div>
      )}

      {/* ========== TABLE ========== */}
      <div ref={tableContainerRef} className="flex-1 overflow-auto bg-[var(--bg-surface)]">
        <table className="w-full border-collapse">
          {/* Table Header */}
          <thead className="sticky top-0 z-10">
            {table.getHeaderGroups().map((headerGroup) => (
              <tr key={headerGroup.id} className="bg-[var(--bg-elevated)]">
                {headerGroup.headers.map((header) => (
                  <th
                    key={header.id}
                    className="text-left text-xs font-semibold text-[var(--text-secondary)] uppercase tracking-wider border-b border-[var(--border-default)] px-3 py-2.5 whitespace-nowrap"
                    style={{ width: header.getSize() }}
                  >
                    {flexRender(
                      header.column.columnDef.header,
                      header.getContext()
                    )}
                  </th>
                ))}
              </tr>
            ))}
          </thead>

          {/* Table Body */}
          <tbody>
            {table.getRowModel().rows.map((row) => {
              const hasData =
                row.original.completed.trim() ||
                row.original.planned.trim() ||
                row.original.hours !== '';
              const hasBlocker = !!row.original.blockers.trim();

              return (
                <tr
                  key={row.id}
                  className={cn(
                    'border-b border-[var(--border-subtle)] transition-colors duration-150 group',
                    'hover:bg-[var(--bg-elevated)]/50',
                    hasData && 'border-l-2 border-l-[#7C3AED]',
                    hasBlocker && 'bg-red-50/30 dark:bg-red-900/5'
                  )}
                >
                  {row.getVisibleCells().map((cell) => (
                    <td
                      key={cell.id}
                      className={cn(
                        'p-0 text-sm border-r border-[var(--border-subtle)] last:border-r-0',
                        'h-[52px]'
                      )}
                      style={{ width: cell.column.getSize() }}
                    >
                      {flexRender(
                        cell.column.columnDef.cell,
                        cell.getContext()
                      )}
                    </td>
                  ))}
                </tr>
              );
            })}

            {/* Empty state */}
            {rows.length === 0 && (
              <tr>
                <td
                  colSpan={columns.length}
                  className="text-center py-16 text-[var(--text-tertiary)]"
                >
                  <Users className="w-10 h-10 mx-auto mb-3 opacity-40" />
                  <p className="text-sm font-medium">No team members</p>
                  <p className="text-xs mt-1">
                    Add members in Settings to start standup
                  </p>
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {/* ========== FOOTER / SUMMARY BAR ========== */}
      <div className="shrink-0 bg-[var(--bg-elevated)] border-t border-[var(--border-default)] px-6 py-2.5 flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-4 text-sm">
          <div className="flex items-center gap-1.5">
            <span className="text-[var(--text-secondary)]">Total hours:</span>
            <span
              className={cn(
                'font-semibold tabular-nums',
                totalHours > 10
                  ? 'text-[#F59E0B]'
                  : 'text-[var(--text-primary)]'
              )}
            >
              {totalHours.toFixed(1)}h
            </span>
            {totalHours > 10 && (
              <span className="text-xs text-[#F59E0B] flex items-center gap-1 ml-1">
                <AlertTriangle className="w-3 h-3" />
                High workload
              </span>
            )}
          </div>

          <div className="w-px h-4 bg-[var(--border-default)]" />

          <div className="flex items-center gap-1.5 text-[var(--text-secondary)]">
            <span>Progress:</span>
            <span className="font-medium text-[var(--text-primary)]">
              {completedCount}/{rows.length}
            </span>
            <span>members</span>
          </div>

          {submittedAt && (
            <>
              <div className="w-px h-4 bg-[var(--border-default)]" />
              <div className="flex items-center gap-1.5 text-xs text-[var(--text-tertiary)]">
                <CheckCircle2 className="w-3 h-3 text-[#22C55E]" />
                Submitted {format(new Date(submittedAt), 'HH:mm')}
              </div>
            </>
          )}
        </div>

        <div className="flex items-center gap-2">
          <span className="text-xs text-[var(--text-tertiary)]">
            Ctrl+Enter to submit
          </span>
          <button
            onClick={handleSubmit}
            disabled={submitting || !hasChanges}
            className={cn(
              'flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium transition-all',
              submitting || !hasChanges
                ? 'text-[var(--text-tertiary)] cursor-not-allowed'
                : 'bg-[#7C3AED] text-white hover:bg-[#6D28D9]'
            )}
          >
            {submitting ? 'Submitting...' : 'Submit Standup'}
          </button>
        </div>
      </div>
    </div>
  );
}

// ------------------------------------------------------------------
// Shortcut Item Component
// ------------------------------------------------------------------
function ShortcutItem({ keys, desc }: { keys: string[]; desc: string }) {
  return (
    <div className="flex items-center gap-1.5 text-xs">
      <div className="flex items-center gap-0.5">
        {keys.map((k, i) => (
          <span key={i} className="flex items-center">
            {i > 0 && <span className="text-[var(--text-tertiary)] mx-0.5">+</span>}
            <kbd className="px-1.5 py-0.5 rounded border border-[var(--border-default)] bg-[var(--bg-surface)] text-[var(--text-secondary)] font-mono text-[10px] font-medium">
              {k}
            </kbd>
          </span>
        ))}
      </div>
      <span className="text-[var(--text-tertiary)]">{desc}</span>
    </div>
  );
}
