import { useState, useRef, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { Users, Code, Zap, Upload, AlertTriangle, Loader2, Check } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Checkbox } from '@/components/ui/checkbox';
import { Label } from '@/components/ui/label';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { cn } from '@/lib/utils';
import { useStore } from '@/store';

// ─── Types ───────────────────────────────────────────────

type UserRole = 'sm' | 'dev' | null;

interface ImportError {
  field: string;
  message: string;
}

// ─── Constants ───────────────────────────────────────────

const ROLES = [
  {
    id: 'sm' as const,
    label: 'Scrum Master',
    description: 'Manage sprints, tasks, and team',
    icon: Users,
    iconColor: 'text-[#7C3AED]',
    borderColor: 'border-[#7C3AED]',
    bgColor: 'bg-[#7C3AED]/10',
    hoverBorder: 'hover:border-[#7C3AED]/50',
    hoverBg: 'hover:bg-[#7C3AED]/5',
  },
  {
    id: 'dev' as const,
    label: 'Developer',
    description: 'View tasks, submit standup, collaborate',
    icon: Code,
    iconColor: 'text-[#EC4899]',
    borderColor: 'border-[#EC4899]',
    bgColor: 'bg-[#EC4899]/10',
    hoverBorder: 'hover:border-[#EC4899]/50',
    hoverBg: 'hover:bg-[#EC4899]/5',
  },
] as const;

// ─── Component ───────────────────────────────────────────

export default function Login() {
  const navigate = useNavigate();
  const sprint = useStore((s) => s.sprint);
  const setBoardData = useStore((s) => s.setBoardData);

  // ── State ──────────────────────────────
  const [selectedRole, setSelectedRole] = useState<UserRole>(null);
  const [rememberRole, setRememberRole] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [backendError, setBackendError] = useState(false);
  const [importErrors, setImportErrors] = useState<ImportError[]>([]);
  const [showImportErrors, setShowImportErrors] = useState(false);
  const [isDragOver, setIsDragOver] = useState(false);
  const [logoAnimating, setLogoAnimating] = useState(true);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // ── Logo animation ─────────────────────
  useEffect(() => {
    const timer = setTimeout(() => setLogoAnimating(false), 3000);
    return () => clearTimeout(timer);
  }, []);

  // ── Check for saved role ───────────────
  useEffect(() => {
    const saved = localStorage.getItem('sprint-agent-role');
    if (saved === 'sm' || saved === 'dev') {
      setSelectedRole(saved);
      setRememberRole(true);
    }
  }, []);

  // ── Handlers ───────────────────────────

  const handleRoleSelect = useCallback((role: UserRole) => {
    setSelectedRole(role);
  }, []);

  const handleSubmit = useCallback(() => {
    if (!selectedRole) return;

    setIsSubmitting(true);

    // Save role
    if (rememberRole) {
      localStorage.setItem('sprint-agent-role', selectedRole);
    } else {
      localStorage.removeItem('sprint-agent-role');
    }

    // Simulate brief loading for UX
    setTimeout(() => {
      setIsSubmitting(false);

      // Redirect based on sprint existence
      if (sprint && sprint.id) {
        navigate('/');
      } else {
        navigate('/planning');
      }
    }, 400);
  }, [selectedRole, rememberRole, sprint, navigate]);

  const handleImportFile = useCallback(
    (file: File) => {
      setImportErrors([]);

      const reader = new FileReader();
      reader.onload = (e) => {
        try {
          const data = JSON.parse(e.target?.result as string);
          const errors: ImportError[] = [];

          // Validate structure
          if (!data.sprint || typeof data.sprint !== 'object') {
            errors.push({ field: 'sprint', message: 'Missing sprint object' });
          } else {
            if (!data.sprint.name) {
              errors.push({ field: 'sprint.name', message: 'Missing sprint name' });
            }
            if (!data.sprint.start_date) {
              errors.push({
                field: 'sprint.start_date',
                message: 'Missing start_date',
              });
            }
          }

          if (errors.length > 0) {
            setImportErrors(errors);
            setShowImportErrors(true);
            return;
          }

          // Import data as Scrum Master
          setSelectedRole('sm');
          if (rememberRole) {
            localStorage.setItem('sprint-agent-role', 'sm');
          }

          // Build sprint and members
          const sprintData = {
            id: data.sprint.id || `s-${Date.now()}`,
            name: data.sprint.name || 'Imported Sprint',
            goal: data.sprint.goal || '',
            start_date: data.sprint.start_date,
            end_date: data.sprint.end_date,
            status: data.sprint.status || 'active',
            created_at: data.sprint.created_at || new Date().toISOString(),
          };

          const members = Array.isArray(data.members)
            ? data.members.map((m: Record<string, unknown>, idx: number) => ({
                id:
                  typeof m.id === 'string'
                    ? m.id
                    : `m-${Date.now()}-${idx}`,
                name: typeof m.name === 'string' ? m.name : 'Unknown',
                role: (m.role as 'sm' | 'dev' | 'qa' | 'po') || 'dev',
                capacity: typeof m.capacity === 'number' ? m.capacity : 80,
              }))
            : [];

          const tasks = Array.isArray(data.tasks)
            ? data.tasks.map((t: Record<string, unknown>, idx: number) => ({
                id:
                  typeof t.id === 'string'
                    ? t.id
                    : `t-${Date.now()}-${idx}`,
                sprint_id: sprintData.id,
                title: typeof t.title === 'string' ? t.title : 'Untitled',
                assignee_id:
                  typeof t.assignee_id === 'string' ? t.assignee_id : null,
                status: (t.status as 'todo' | 'progress' | 'done' | 'paused') || 'todo',
                priority: (t.priority as 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10) || 5,
                story_points: typeof t.story_points === 'number' ? t.story_points : 0,
                blocked_by: Array.isArray(t.blocked_by) ? t.blocked_by : [],
                description: typeof t.description === 'string' ? t.description : '',
                created_at: t.created_at || new Date().toISOString(),
                updated_at: t.updated_at || new Date().toISOString(),
              }))
            : [];

          setBoardData(sprintData, members, tasks);
          navigate('/');
        } catch {
          setImportErrors([{ field: 'file', message: 'Invalid JSON format' }]);
          setShowImportErrors(true);
        }
      };
      reader.readAsText(file);
    },
    [rememberRole, navigate, setBoardData]
  );

  const handleFileChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0];
      if (file) handleImportFile(file);
      e.target.value = '';
    },
    [handleImportFile]
  );

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setIsDragOver(false);
      const file = e.dataTransfer.files?.[0];
      if (file && file.name.endsWith('.json')) {
        handleImportFile(file);
      }
    },
    [handleImportFile]
  );

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
  }, []);

  const handleSkip = useCallback(() => {
    navigate('/planning');
  }, [navigate]);

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      if (e.key === '1') {
        setSelectedRole('sm');
      } else if (e.key === '2') {
        setSelectedRole('dev');
      }
    },
    []
  );

  // ── Render ─────────────────────────────

  return (
    <div
      className={cn(
        'min-h-[100dvh] flex items-center justify-center p-4',
        'bg-gradient-to-br from-[#7C3AED]/5 via-transparent to-[#EC4899]/5'
      )}
      onKeyDown={handleKeyDown}
    >
      {/* Background subtle pattern */}
      <div
        className="fixed inset-0 opacity-[0.02] pointer-events-none"
        style={{
          backgroundImage:
            'radial-gradient(circle at 1px 1px, currentColor 1px, transparent 0)',
          backgroundSize: '24px 24px',
        }}
      />

      {/* Main Card */}
      <div
        className={cn(
          'w-full max-w-[420px] relative z-10',
          'bg-[hsl(var(--card))] border border-[hsl(var(--border))]',
          'rounded-xl shadow-lg p-8',
          'transition-all duration-300'
        )}
      >
        {/* ── Logo & Brand ── */}
        <div className="text-center mb-8">
          <div
            className={cn(
              'w-12 h-12 rounded-xl bg-gradient-to-br from-[#7C3AED] to-[#EC4899]',
              'flex items-center justify-center mx-auto mb-3',
              'transition-transform duration-500',
              logoAnimating && 'animate-pulse'
            )}
            style={
              logoAnimating
                ? {
                    animation: 'pulse-scale 3s ease-in-out infinite',
                  }
                : undefined
            }
          >
            <Zap className="w-6 h-6 text-white" />
          </div>
          <h1
            className={cn(
              'text-2xl font-bold text-[hsl(var(--foreground))]',
              'transition-all duration-300'
            )}
          >
            Sprint Agent
          </h1>
          <p className="text-sm text-[hsl(var(--muted-foreground))] mt-1">
            Agile iteration management
          </p>
        </div>

        {/* ── Role Selection ── */}
        <div className="space-y-4">
          <p className="text-sm font-semibold text-[hsl(var(--muted-foreground))]">
            I am a:
          </p>

          <div className="grid grid-cols-2 gap-4">
            {ROLES.map((role) => {
              const isSelected = selectedRole === role.id;
              const Icon = role.icon;

              return (
                <button
                  key={role.id}
                  onClick={() => handleRoleSelect(role.id)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') handleRoleSelect(role.id);
                  }}
                  className={cn(
                    'relative flex flex-col items-center gap-2.5 p-4 rounded-lg border-2',
                    'text-center transition-all duration-150 cursor-pointer',
                    'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[hsl(var(--ring))] focus-visible:ring-offset-2',
                    isSelected
                      ? cn(role.borderColor, role.bgColor)
                      : cn(
                          'border-[hsl(var(--border))]',
                          role.hoverBorder,
                          role.hoverBg
                        )
                  )}
                  tabIndex={0}
                  role="radio"
                  aria-checked={isSelected}
                >
                  {isSelected && (
                    <div className="absolute top-2 right-2">
                      <div
                        className={cn(
                          'w-5 h-5 rounded-full flex items-center justify-center',
                          role.bgColor
                        )}
                      >
                        <Check
                          className={cn(
                            'w-3 h-3',
                            role.iconColor
                          )}
                        />
                      </div>
                    </div>
                  )}

                  <Icon
                    className={cn(
                      'w-8 h-8 transition-colors',
                      isSelected ? role.iconColor : 'text-[hsl(var(--muted-foreground))]'
                    )}
                  />
                  <div>
                    <p
                      className={cn(
                        'text-sm font-semibold',
                        isSelected
                          ? 'text-[hsl(var(--foreground))]'
                          : 'text-[hsl(var(--foreground))]'
                      )}
                    >
                      {role.label}
                    </p>
                    <p className="text-[11px] text-[hsl(var(--muted-foreground))] mt-0.5 leading-tight">
                      {role.description}
                    </p>
                  </div>
                </button>
              );
            })}
          </div>
        </div>

        {/* ── Remember & Submit ── */}
        <div className="mt-6 space-y-4">
          <div className="flex items-center gap-2.5">
            <Checkbox
              id="remember"
              checked={rememberRole}
              onCheckedChange={(checked) =>
                setRememberRole(checked === true)
              }
            />
            <Label
              htmlFor="remember"
              className="text-sm text-[hsl(var(--muted-foreground))] cursor-pointer"
            >
              Remember my role on this device
            </Label>
          </div>

          <Button
            className="w-full h-10 text-sm font-semibold bg-[hsl(var(--primary))] text-[hsl(var(--primary-foreground))] hover:bg-[hsl(var(--primary))]/90 transition-all active:scale-[0.98]"
            disabled={!selectedRole || isSubmitting}
            onClick={handleSubmit}
          >
            {isSubmitting ? (
              <Loader2 className="w-4 h-4 mr-2 animate-spin" />
            ) : null}
            {isSubmitting ? 'Getting started...' : 'Get Started'}
          </Button>
        </div>

        {/* ── Data Import Shortcut ── */}
        <div className="mt-6 pt-6 border-t border-[hsl(var(--border))]">
          <p className="text-sm text-[hsl(var(--muted-foreground))] mb-3">
            Or import data to get started:
          </p>

          <input
            ref={fileInputRef}
            type="file"
            accept=".json"
            onChange={handleFileChange}
            className="hidden"
          />

          <div
            onClick={() => fileInputRef.current?.click()}
            onDrop={handleDrop}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            className={cn(
              'h-20 rounded-lg border-2 border-dashed',
              'flex flex-col items-center justify-center gap-1.5',
              'cursor-pointer transition-all duration-150',
              isDragOver
                ? 'border-[hsl(var(--primary))] bg-[hsl(var(--primary))]/5'
                : 'border-[hsl(var(--border))] hover:border-[hsl(var(--primary))]/50 hover:bg-[hsl(var(--accent))]/50'
            )}
          >
            <Upload
              className={cn(
                'w-5 h-5 transition-colors',
                isDragOver
                  ? 'text-[hsl(var(--primary))]'
                  : 'text-[hsl(var(--muted-foreground))]'
              )}
            />
            <span className="text-xs text-[hsl(var(--muted-foreground))]">
              Drop JSON file or click to upload
            </span>
          </div>

          {/* Skip option */}
          <div className="text-center mt-3">
            <button
              onClick={handleSkip}
              className="text-xs text-[hsl(var(--muted-foreground))] hover:text-[hsl(var(--primary))] transition-colors underline underline-offset-2"
            >
              Skip for now →
            </button>
          </div>
        </div>

        {/* ── Backend Error Banner ── */}
        {backendError && (
          <div className="mt-4 rounded-lg border border-destructive/30 bg-destructive/10 p-3 flex items-start gap-2.5">
            <AlertTriangle className="w-4 h-4 text-destructive shrink-0 mt-0.5" />
            <div>
              <p className="text-xs font-medium text-destructive">
                Cannot connect to Sprint Agent backend.
              </p>
              <p className="text-[11px] text-destructive/70 mt-0.5">
                Check that the server is running. Some features will be
                unavailable.
              </p>
              <Button
                variant="ghost"
                size="sm"
                className="h-6 text-[11px] mt-1 text-destructive hover:text-destructive"
                onClick={() => setBackendError(false)}
              >
                Retry
              </Button>
            </div>
          </div>
        )}
      </div>

      {/* ── Import Errors Dialog ── */}
      <Dialog open={showImportErrors} onOpenChange={setShowImportErrors}>
        <DialogContent className="sm:max-w-[420px]">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2 text-destructive">
              <AlertTriangle className="w-5 h-5" />
              Import Error
            </DialogTitle>
            <DialogDescription>
              The uploaded file could not be imported. Please fix the following
              issues:
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-2 mt-2">
            {importErrors.map((err, idx) => (
              <div
                key={idx}
                className="rounded-md bg-destructive/10 border border-destructive/20 p-2.5 text-xs"
              >
                <span className="font-mono font-semibold text-destructive">
                  {err.field}:
                </span>{' '}
                <span className="text-destructive/80">{err.message}</span>
              </div>
            ))}
          </div>
          <Button
            className="w-full mt-4"
            variant="outline"
            onClick={() => setShowImportErrors(false)}
          >
            Close
          </Button>
        </DialogContent>
      </Dialog>

      {/* ── CSS Animations ── */}
      <style>{`
        @keyframes pulse-scale {
          0%, 100% { transform: scale(1); }
          50% { transform: scale(1.05); }
        }
      `}</style>
    </div>
  );
}
