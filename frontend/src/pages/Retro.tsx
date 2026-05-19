import { useState, useCallback, useMemo, useEffect, useRef } from 'react';
import { useStore } from '@/store';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Star,
  ThumbsUp,
  Plus,
  ClipboardPaste,
  Trash2,
  FileText,
  Download,
  Sparkles,
  CheckCircle2,
  GripVertical,
  TrendingUp,
  Users,
  Clock,
  BarChart3,
  CheckSquare,
  AlertTriangle,
  Loader2,
} from 'lucide-react';
import { cn } from '@/lib/utils';

/* ------------------------------------------------------------------ */
/*  Types                                                              */
/* ------------------------------------------------------------------ */

type RetroCategory = 'liked' | 'disliked' | 'action';
type RetroTemplate = 'mad-sad-glad' | '4ls' | 'starfish' | 'start-stop-continue';

interface RetroItemData {
  id: string;
  category: RetroCategory;
  text: string;
  votes: number;
  votedByMe: boolean;
}

interface RetroRatingData {
  dimension: string;
  label: string;
  score: number;
}

/* ------------------------------------------------------------------ */
/*  Constants                                                          */
/* ------------------------------------------------------------------ */

const RATING_DIMENSIONS: RetroRatingData[] = [
  { dimension: 'velocity', label: 'Velocity', score: 0 },
  { dimension: 'quality', label: 'Quality', score: 0 },
  { dimension: 'teamwork', label: 'Teamwork', score: 0 },
  { dimension: 'process', label: 'Process', score: 0 },
];

const TEMPLATE_MAP: Record<RetroTemplate, { name: string; categories: string[] }> = {
  'mad-sad-glad': {
    name: 'Mad / Sad / Glad',
    categories: ['Mad', 'Sad', 'Glad'],
  },
  '4ls': {
    name: '4Ls',
    categories: ['Liked', 'Learned', 'Lacked', 'Longed For'],
  },
  starfish: {
    name: 'Starfish',
    categories: ['Keep Doing', 'Less Of', 'More Of', 'Stop Doing', 'Start Doing'],
  },
  'start-stop-continue': {
    name: 'Start / Stop / Continue',
    categories: ['Start', 'Stop', 'Continue'],
  },
};

const TAB_CONFIG: { key: RetroCategory; label: string; icon: typeof CheckCircle2; color: string }[] = [
  { key: 'liked', label: 'What Went Well', icon: CheckCircle2, color: 'text-emerald-500' },
  { key: 'disliked', label: 'What to Improve', icon: AlertTriangle, color: 'text-amber-500' },
  { key: 'action', label: 'Action Items', icon: Star, color: 'text-violet-500' },
];

/* ------------------------------------------------------------------ */
/*  Helpers                                                            */
/* ------------------------------------------------------------------ */

function scoreColor(score: number): string {
  if (score <= 2) return 'text-red-500';
  if (score === 3) return 'text-amber-500';
  if (score >= 4) return 'text-emerald-500';
  return 'text-[hsl(var(--muted-foreground))]';
}

function scoreBg(score: number): string {
  if (score <= 2) return 'bg-red-50 dark:bg-red-950/30 border-red-200 dark:border-red-800';
  if (score === 3) return 'bg-amber-50 dark:bg-amber-950/30 border-amber-200 dark:border-amber-800';
  if (score >= 4) return 'bg-emerald-50 dark:bg-emerald-950/30 border-emerald-200 dark:border-emerald-800';
  return 'bg-[hsl(var(--card))] border-[hsl(var(--border))]';
}

/* ------------------------------------------------------------------ */
/*  Sub-Components                                                     */
/* ------------------------------------------------------------------ */

function StarRating({
  score,
  onRate,
  dimension,
}: {
  score: number;
  onRate: (dim: string, value: number) => void;
  dimension: string;
}) {
  const [hover, setHover] = useState(0);

  return (
    <div className="flex items-center gap-0.5">
      {[1, 2, 3, 4, 5].map((n) => (
        <button
          key={n}
          type="button"
          onClick={() => onRate(dimension, n)}
          onMouseEnter={() => setHover(n)}
          onMouseLeave={() => setHover(0)}
          className="p-0.5 transition-transform hover:scale-110 focus:outline-none focus-visible:ring-2 focus-visible:ring-violet-500/40 rounded"
          aria-label={`Rate ${n} stars`}
        >
          <Star
            className={cn(
              'w-5 h-5 transition-colors',
              n <= (hover || score) ? 'fill-amber-400 text-amber-400' : 'text-[hsl(var(--muted-foreground))]/30'
            )}
          />
        </button>
      ))}
    </div>
  );
}

function RatingCard({
  label,
  score,
  onRate,
  dimension,
}: {
  label: string;
  score: number;
  onRate: (dim: string, value: number) => void;
  dimension: string;
}) {
  const avg = score;

  return (
    <div
      className={cn(
        'flex flex-col items-center gap-2 rounded-lg border p-4 transition-colors min-w-[80px]',
        scoreBg(score)
      )}
    >
      <span className="text-xs font-medium text-[hsl(var(--muted-foreground))]">{label}</span>
      <span className={cn('text-3xl font-bold tabular-nums', scoreColor(score))}>
        {score || '-'}
      </span>
      <StarRating score={score} onRate={onRate} dimension={dimension} />
      {avg > 0 && <span className="text-xs text-[hsl(var(--muted-foreground))]">Avg: {avg.toFixed(1)}</span>}
    </div>
  );
}

/* ------------------------------------------------------------------ */
/*  Main Component                                                     */
/* ------------------------------------------------------------------ */

export default function Retro() {
  const sprint = useStore((s) => s.sprint);
  const members = useStore((s) => s.members);
  const tasks = useStore((s) => s.tasks);

  /* Ratings */
  const [ratings, setRatings] = useState<RetroRatingData[]>(RATING_DIMENSIONS.map((d) => ({ ...d, score: 0 })));
  const focusedDimension = useRef<string | null>(null);

  /* Feedback items */
  const [items, setItems] = useState<RetroItemData[]>([]);
  const [activeCategory, setActiveCategory] = useState<RetroCategory>('liked');
  const [inputValue, setInputValue] = useState('');

  /* Template */
  const [template, setTemplate] = useState<RetroTemplate>('mad-sad-glad');

  /* Summary */
  const [summary, setSummary] = useState('');
  const [generating, setGenerating] = useState(false);

  /* Computed */
  const averageScore = useMemo(() => {
    const scored = ratings.filter((r) => r.score > 0);
    if (scored.length === 0) return 0;
    return scored.reduce((sum, r) => sum + r.score, 0) / scored.length;
  }, [ratings]);

  const taskStats = useMemo(() => {
    const total = tasks.length;
    const done = tasks.filter((t) => t.status === 'done').length;
    const blocked = tasks.filter((t) => t.blocked_by.length > 0).length;
    const progress = tasks.filter((t) => t.status === 'progress').length;
    const paused = tasks.filter((t) => t.status === 'paused').length;
    const completionRate = total > 0 ? Math.round((done / total) * 100) : 0;
    const totalPoints = tasks.reduce((sum, t) => sum + (t.story_points || 0), 0);
    return { total, done, blocked, progress, paused, completionRate, totalPoints, memberCount: members.length };
  }, [tasks, members]);

  const filteredItems = useMemo(
    () => [...items.filter((i) => i.category === activeCategory)].sort((a, b) => b.votes - a.votes),
    [items, activeCategory]
  );

  /* Rating handlers */
  const handleRate = useCallback((dimension: string, value: number) => {
    setRatings((prev) => prev.map((r) => (r.dimension === dimension ? { ...r, score: value } : r)));
    focusedDimension.current = dimension;
  }, []);

  const handleKeyRate = useCallback(
    (e: React.KeyboardEvent) => {
      if (!focusedDimension.current) return;
      const num = parseInt(e.key, 10);
      if (num >= 1 && num <= 5) {
        handleRate(focusedDimension.current, num);
      }
    },
    [handleRate]
  );

  /* Feedback handlers */
  const addItem = useCallback(
    (text: string) => {
      const trimmed = text.trim();
      if (!trimmed) return;
      const newItem: RetroItemData = {
        id: `rf-${Date.now()}`,
        category: activeCategory,
        text: trimmed,
        votes: 0,
        votedByMe: false,
      };
      setItems((prev) => [...prev, newItem]);
      setInputValue('');
    },
    [activeCategory]
  );

  const handleVote = useCallback((id: string) => {
    setItems((prev) =>
      prev.map((item) =>
        item.id === id
          ? { ...item, votes: item.votedByMe ? item.votes - 1 : item.votes + 1, votedByMe: !item.votedByMe }
          : item
      )
    );
  }, []);

  const handleDelete = useCallback((id: string) => {
    setItems((prev) => prev.filter((i) => i.id !== id));
  }, []);

  const handleInputKeyDown = useCallback(
    (e: React.KeyboardEvent<HTMLInputElement>) => {
      if (e.key === 'Enter') {
        e.preventDefault();
        addItem(inputValue);
      }
    },
    [inputValue, addItem]
  );

  const handlePasteFromClipboard = useCallback(async () => {
    try {
      const text = await navigator.clipboard.readText();
      const lines = text
        .split('\n')
        .map((l) => l.trim())
        .filter((l) => l.length > 0);
      lines.forEach((line) => {
        const newItem: RetroItemData = {
          id: `rf-${Date.now()}-${Math.random().toString(36).slice(2, 6)}`,
          category: activeCategory,
          text: line,
          votes: 0,
          votedByMe: false,
        };
        setItems((prev) => [...prev, newItem]);
      });
    } catch {
      // silently fail
    }
  }, [activeCategory]);

  /* Template application */
  const handleApplyTemplate = useCallback(
    (tpl: RetroTemplate) => {
      setTemplate(tpl);
      const config = TEMPLATE_MAP[tpl];
      const mapped: RetroCategory[] = ['liked', 'disliked', 'action'];
      const newItems: RetroItemData[] = config.categories.slice(0, 3).map((cat, idx) => ({
        id: `rf-tpl-${Date.now()}-${idx}`,
        category: mapped[idx] || 'liked',
        text: `${cat}: ...`,
        votes: 0,
        votedByMe: false,
      }));
      setItems((prev) => [...prev.filter((i) => !i.id.startsWith('rf-tpl')), ...newItems]);
    },
    []
  );

  /* Generate summary */
  const handleGenerateSummary = useCallback(() => {
    setGenerating(true);
    setTimeout(() => {
      const rated = ratings.filter((r) => r.score > 0);
      const likedItems = items.filter((i) => i.category === 'liked');
      const dislikedItems = items.filter((i) => i.category === 'disliked');
      const actionItems = items.filter((i) => i.category === 'action');

      let text = `## Sprint Retrospective Summary\n\n`;
      text += `**Sprint**: ${sprint?.name || 'Current Sprint'}\n`;
      text += `**Date**: ${new Date().toLocaleDateString()}\n\n`;

      if (rated.length > 0) {
        text += `### Ratings\n`;
        rated.forEach((r) => {
          const stars = '★'.repeat(r.score) + '☆'.repeat(5 - r.score);
          text += `- ${r.label}: ${r.score}/5 ${stars}\n`;
        });
        text += `- **Average**: ${averageScore.toFixed(1)}/5\n\n`;
      }

      if (likedItems.length > 0) {
        text += `### What Went Well\n`;
        likedItems
          .sort((a, b) => b.votes - a.votes)
          .forEach((i) => {
            text += `- ${i.text}${i.votes > 0 ? ` (+${i.votes})` : ''}\n`;
          });
        text += `\n`;
      }

      if (dislikedItems.length > 0) {
        text += `### What to Improve\n`;
        dislikedItems
          .sort((a, b) => b.votes - a.votes)
          .forEach((i) => {
            text += `- ${i.text}${i.votes > 0 ? ` (+${i.votes})` : ''}\n`;
          });
        text += `\n`;
      }

      if (actionItems.length > 0) {
        text += `### Action Items\n`;
        actionItems
          .sort((a, b) => b.votes - a.votes)
          .forEach((i) => {
            text += `- [ ] ${i.text}\n`;
          });
        text += `\n`;
      }

      text += `### Sprint Stats\n`;
      text += `- Total tasks: ${taskStats.total}\n`;
      text += `- Completed: ${taskStats.done} (${taskStats.completionRate}%)\n`;
      text += `- In progress: ${taskStats.progress}\n`;
      text += `- Blocked: ${taskStats.blocked}\n`;
      text += `- Team size: ${taskStats.memberCount}\n`;
      text += `- Story points: ${taskStats.totalPoints}\n`;

      setSummary(text);
      setGenerating(false);
    }, 800);
  }, [ratings, items, sprint, averageScore, taskStats]);

  /* Export markdown */
  const handleExportMarkdown = useCallback(() => {
    const content = summary || handleGenerateSummary();
    const blob = new Blob([typeof content === 'string' ? content : ''], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `retro-${sprint?.name || 'sprint'}-${new Date().toISOString().slice(0, 10)}.md`;
    a.click();
    URL.revokeObjectURL(url);
  }, [summary, sprint]);

  /* Load saved retro from localStorage */
  useEffect(() => {
    const saved = localStorage.getItem('retro-draft');
    if (saved) {
      try {
        const parsed = JSON.parse(saved);
        if (parsed.ratings) setRatings(parsed.ratings);
        if (parsed.items) setItems(parsed.items);
        if (parsed.summary) setSummary(parsed.summary);
      } catch {
        // ignore
      }
    }
  }, []);

  /* Auto-save draft */
  useEffect(() => {
    const draft = { ratings, items, summary };
    localStorage.setItem('retro-draft', JSON.stringify(draft));
  }, [ratings, items, summary]);

  return (
    <div className="p-6 space-y-6 max-w-[960px] mx-auto" onKeyDown={handleKeyRate}>
      {/* ========== Page Header ========== */}
      <div className="space-y-1">
        <div className="flex items-center gap-3">
          <h1 className="text-2xl font-bold text-[hsl(var(--foreground))]">Sprint Retrospective</h1>
          <Badge variant="secondary" className="text-xs">
            {averageScore > 0 ? `${averageScore.toFixed(1)} avg` : 'In Progress'}
          </Badge>
        </div>
        <p className="text-sm text-[hsl(var(--muted-foreground))]">
          {sprint ? `${sprint.name} (${sprint.start_date} – ${sprint.end_date})` : 'Review the sprint and capture insights for next iteration'}
        </p>
      </div>

      {/* ========== Template & Stats ========== */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Template selector */}
        <Card className="p-4 gap-3">
          <h3 className="text-sm font-semibold text-[hsl(var(--muted-foreground))]">Retro Template</h3>
          <Select
            value={template}
            onValueChange={(v) => handleApplyTemplate(v as RetroTemplate)}
          >
            <SelectTrigger className="w-full">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="mad-sad-glad">Mad / Sad / Glad</SelectItem>
              <SelectItem value="4ls">4Ls (Liked, Learned, Lacked, Longed For)</SelectItem>
              <SelectItem value="starfish">Starfish</SelectItem>
              <SelectItem value="start-stop-continue">Start / Stop / Continue</SelectItem>
            </SelectContent>
          </Select>
          <p className="text-xs text-[hsl(var(--muted-foreground))]">
            Template: {TEMPLATE_MAP[template].name}
          </p>
        </Card>

        {/* Sprint stats */}
        <Card className="md:col-span-2 p-4 gap-3">
          <h3 className="text-sm font-semibold text-[hsl(var(--muted-foreground))]">Sprint Stats</h3>
          <div className="grid grid-cols-3 sm:grid-cols-4 gap-3">
            <StatBadge icon={BarChart3} label="Tasks" value={taskStats.total} />
            <StatBadge icon={CheckSquare} label="Done" value={`${taskStats.completionRate}%`} />
            <StatBadge icon={AlertTriangle} label="Blocked" value={taskStats.blocked} />
            <StatBadge icon={Users} label="Members" value={taskStats.memberCount} />
            <StatBadge icon={TrendingUp} label="In Progress" value={taskStats.progress} />
            <StatBadge icon={Clock} label="Paused" value={taskStats.paused} />
            <StatBadge icon={Star} label="Points" value={taskStats.totalPoints} />
          </div>
        </Card>
      </div>

      {/* ========== Ratings Section ========== */}
      <section>
        <h2 className="text-lg font-semibold mb-3 text-[hsl(var(--foreground))]">Team Ratings</h2>
        <div className="flex flex-wrap gap-3">
          {ratings.map((r) => (
            <div
              key={r.dimension}
              className="flex-1 min-w-[100px]"
              onFocus={() => { focusedDimension.current = r.dimension; }}
              tabIndex={0}
            >
              <RatingCard
                label={r.label}
                score={r.score}
                onRate={handleRate}
                dimension={r.dimension}
              />
            </div>
          ))}
        </div>
        {averageScore > 0 && (
          <div className="mt-2 text-sm text-[hsl(var(--muted-foreground))]">
            Average rating:{' '}
            <span className={cn('font-semibold', scoreColor(Math.round(averageScore)))}>
              {averageScore.toFixed(1)} / 5
            </span>
          </div>
        )}
        <p className="text-xs text-[hsl(var(--muted-foreground))] mt-1">
          Tip: Click a dimension to focus, then press 1–5 to rate.
        </p>
      </section>

      {/* ========== Feedback Items Section ========== */}
      <section>
        <h2 className="text-lg font-semibold mb-3 text-[hsl(var(--foreground))]">Feedback Items</h2>

        <Tabs value={activeCategory} onValueChange={(v) => setActiveCategory(v as RetroCategory)}>
          <TabsList className="mb-3">
            {TAB_CONFIG.map((tab) => {
              const count = items.filter((i) => i.category === tab.key).length;
              const Icon = tab.icon;
              return (
                <TabsTrigger key={tab.key} value={tab.key} className="gap-1.5">
                  <Icon className={cn('w-3.5 h-3.5', tab.color)} />
                  <span>{tab.label}</span>
                  {count > 0 && (
                    <Badge variant="secondary" className="text-[10px] h-5 px-1.5 ml-1">
                      {count}
                    </Badge>
                  )}
                </TabsTrigger>
              );
            })}
          </TabsList>

          {TAB_CONFIG.map((tab) => (
            <TabsContent key={tab.key} value={tab.key}>
              <Card className="p-0 overflow-hidden">
                {/* Card header */}
                <div className="px-4 py-3 border-b border-[hsl(var(--border))] flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <tab.icon className={cn('w-4 h-4', tab.color)} />
                    <span className="font-medium text-sm">{tab.label}</span>
                    <Badge variant="secondary" className="text-xs">
                      {filteredItems.length}
                    </Badge>
                  </div>
                  <div className="flex items-center gap-1">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={handlePasteFromClipboard}
                      className="h-7 px-2 text-xs"
                    >
                      <ClipboardPaste className="w-3.5 h-3.5 mr-1" />
                      Paste
                    </Button>
                  </div>
                </div>

                {/* Items list */}
                <div className="p-2 space-y-1 min-h-[100px]">
                  {filteredItems.length === 0 ? (
                    <div className="text-center py-8 text-sm text-[hsl(var(--muted-foreground))]">
                      Nothing here yet. Type below or paste from clipboard.
                    </div>
                  ) : (
                    filteredItems.map((item) => (
                      <FeedbackItemRow
                        key={item.id}
                        item={item}
                        onVote={handleVote}
                        onDelete={handleDelete}
                      />
                    ))
                  )}
                </div>

                {/* Add input */}
                <div className="px-3 py-2 border-t border-[hsl(var(--border))]">
                  <div className="flex items-center gap-2">
                    <Plus className="w-4 h-4 text-[hsl(var(--muted-foreground))] shrink-0" />
                    <Input
                      placeholder="Type and press Enter to add..."
                      value={inputValue}
                      onChange={(e) => setInputValue(e.target.value)}
                      onKeyDown={handleInputKeyDown}
                      className="h-8 text-sm border-0 shadow-none focus-visible:ring-0 px-0"
                    />
                  </div>
                </div>
              </Card>
            </TabsContent>
          ))}
        </Tabs>
      </section>

      {/* ========== Quick Actions ========== */}
      <section>
        <h2 className="text-lg font-semibold mb-3 text-[hsl(var(--foreground))]">Quick Actions</h2>
        <div className="flex flex-wrap gap-3">
          <Button
            onClick={handleGenerateSummary}
            disabled={generating}
            className="gap-2"
          >
            {generating ? <Loader2 className="w-4 h-4 animate-spin" /> : <Sparkles className="w-4 h-4" />}
            Generate Report
          </Button>
          <Button variant="outline" onClick={handleExportMarkdown} className="gap-2">
            <Download className="w-4 h-4" />
            Export to Markdown
          </Button>
          <Button
            variant="outline"
            onClick={() => {
              setRatings(RATING_DIMENSIONS.map((d) => ({ ...d, score: 0 })));
              setItems([]);
              setSummary('');
              localStorage.removeItem('retro-draft');
            }}
            className="gap-2"
          >
            <Trash2 className="w-4 h-4" />
            Reset
          </Button>
        </div>
      </section>

      {/* ========== Summary Section ========== */}
      {summary && (
        <section>
          <h2 className="text-lg font-semibold mb-3 text-[hsl(var(--foreground))]">Summary</h2>
          <Card className="p-4 gap-3">
            <div className="flex items-center gap-2 mb-2">
              <FileText className="w-4 h-4 text-[hsl(var(--muted-foreground))]" />
              <span className="text-sm font-medium">Retro Report</span>
            </div>
            <Textarea
              value={summary}
              onChange={(e) => setSummary(e.target.value)}
              className="min-h-[200px] text-sm font-mono"
            />
          </Card>
        </section>
      )}
    </div>
  );
}

/* ------------------------------------------------------------------ */
/*  Feedback Item Row                                                   */
/* ------------------------------------------------------------------ */

function FeedbackItemRow({
  item,
  onVote,
  onDelete,
}: {
  item: RetroItemData;
  onVote: (id: string) => void;
  onDelete: (id: string) => void;
}) {
  return (
    <div
      className={cn(
        'group flex items-center gap-2 rounded-md px-2 py-1.5 text-sm',
        'hover:bg-[hsl(var(--accent))] transition-colors'
      )}
    >
      <GripVertical className="w-3.5 h-3.5 text-[hsl(var(--muted-foreground))] shrink-0 opacity-0 group-hover:opacity-50 cursor-grab" />
      <span className="flex-1 min-w-0 truncate">{item.text}</span>

      <button
        onClick={() => onVote(item.id)}
        className={cn(
          'flex items-center gap-1 px-2 py-0.5 rounded-md text-xs transition-colors shrink-0',
          item.votedByMe
            ? 'bg-violet-100 text-violet-700 dark:bg-violet-900/40 dark:text-violet-300'
            : 'text-[hsl(var(--muted-foreground))] hover:bg-[hsl(var(--accent))]'
        )}
      >
        <ThumbsUp className={cn('w-3 h-3', item.votedByMe && 'fill-current')} />
        {item.votes > 0 && <span>{item.votes}</span>}
      </button>

      <button
        onClick={() => onDelete(item.id)}
        className="p-1 rounded text-[hsl(var(--muted-foreground))] opacity-0 group-hover:opacity-100 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-950/30 transition-all shrink-0"
      >
        <Trash2 className="w-3 h-3" />
      </button>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/*  Stat Badge                                                         */
/* ------------------------------------------------------------------ */

function StatBadge({
  icon: Icon,
  label,
  value,
}: {
  icon: typeof BarChart3;
  label: string;
  value: string | number;
}) {
  return (
    <div className="flex items-center gap-2 rounded-md bg-[hsl(var(--muted))] px-3 py-2">
      <Icon className="w-3.5 h-3.5 text-[hsl(var(--muted-foreground))] shrink-0" />
      <div className="min-w-0">
        <div className="text-xs text-[hsl(var(--muted-foreground))]">{label}</div>
        <div className="text-sm font-semibold">{value}</div>
      </div>
    </div>
  );
}
