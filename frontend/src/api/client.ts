import type { Sprint, Member, Task } from '@/types';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

let backendAvailable: boolean | null = null;

async function checkBackend(): Promise<boolean> {
  if (backendAvailable !== null) return backendAvailable;
  try {
    const res = await fetch(`${API_BASE}/api/health`, { method: 'GET', signal: AbortSignal.timeout(2000) });
    backendAvailable = res.ok;
  } catch {
    backendAvailable = false;
  }
  return backendAvailable;
}

export async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
  const useBackend = await checkBackend();

  if (useBackend) {
    const res = await fetch(`${API_BASE}${path}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
    });
    if (!res.ok) {
      const err = await res.text().catch(() => 'Unknown error');
      throw new Error(`API ${path} failed: ${res.status} ${err}`);
    }
    return res.json() as Promise<T>;
  }

  // Fallback to localStorage
  return localStorageApi<T>(path, options);
}

function localStorageKey(path: string): string {
  return `sprint_agent_${path.replace(/\//g, '_')}`;
}

function localStorageApi<T>(path: string, options?: RequestInit): Promise<T> {
  return new Promise((resolve, reject) => {
    const method = options?.method || 'GET';
    const key = localStorageKey(path);

    if (method === 'GET') {
      const raw = localStorage.getItem(key);
      if (raw) {
        resolve(JSON.parse(raw) as T);
        return;
      }
      // Return from default data if nothing stored
      const defaultData = getDefaultData(path);
      if (defaultData) {
        resolve(defaultData as T);
        return;
      }
      reject(new Error(`No data for ${path}`));
    } else if (method === 'POST' || method === 'PATCH' || method === 'PUT') {
      const body = options?.body ? JSON.parse(options.body as string) : {};
      localStorage.setItem(key, JSON.stringify(body));
      resolve(body as T);
    } else if (method === 'DELETE') {
      localStorage.removeItem(key);
      resolve(undefined as T);
    } else {
      reject(new Error(`Unsupported method: ${method}`));
    }
  });
}

function getDefaultData(path: string): unknown {
  if (path === '/api/board') {
    return { sprint: DEMO_SPRINT, members: DEMO_MEMBERS, tasks: DEMO_TASKS };
  }
  return null;
}

export async function fetchBoard(): Promise<{ sprint: Sprint; members: Member[]; tasks: Task[] }> {
  return apiFetch('/api/board', { method: 'GET' });
}

// ---- Demo Data ----
export const DEMO_SPRINT: Sprint = {
  id: 'sp-1',
  name: 'Sprint 26.05',
  goal: 'Complete mobile adaptation and API performance optimization',
  start_date: '2024-05-01',
  end_date: '2024-05-14',
  status: 'active',
  created_at: '2024-04-30T10:00:00Z',
};

export const DEMO_MEMBERS: Member[] = [
  { id: 'm-1', name: 'Alice', role: 'sm', capacity: 8, avatar: undefined },
  { id: 'm-2', name: 'Bob', role: 'dev', capacity: 8, avatar: undefined },
  { id: 'm-3', name: 'Carol', role: 'dev', capacity: 6, avatar: undefined },
  { id: 'm-4', name: 'David', role: 'qa', capacity: 8, avatar: undefined },
];

export const DEMO_TASKS: Task[] = [
  {
    id: 't-1', sprint_id: 'sp-1', title: 'Design database schema for user module',
    assignee_id: 'm-2', status: 'todo', priority: 8, story_points: 5,
    blocked_by: [], description: 'Design the core database tables for user management',
    created_at: '2024-05-01T08:00:00Z', updated_at: '2024-05-01T08:00:00Z',
  },
  {
    id: 't-2', sprint_id: 'sp-1', title: 'Set up CI/CD pipeline',
    assignee_id: 'm-3', status: 'todo', priority: 7, story_points: 3,
    blocked_by: [], description: 'Configure GitHub Actions for automated testing and deployment',
    created_at: '2024-05-01T09:00:00Z', updated_at: '2024-05-01T09:00:00Z',
  },
  {
    id: 't-3', sprint_id: 'sp-1', title: 'Write API documentation',
    assignee_id: null, status: 'todo', priority: 4, story_points: 2,
    blocked_by: [], description: 'Document all REST API endpoints with examples',
    created_at: '2024-05-01T10:00:00Z', updated_at: '2024-05-01T10:00:00Z',
  },
  {
    id: 't-4', sprint_id: 'sp-1', title: 'Implement user authentication',
    assignee_id: 'm-2', status: 'progress', priority: 10, story_points: 8,
    blocked_by: [], description: 'Implement JWT-based authentication flow',
    created_at: '2024-05-02T08:00:00Z', updated_at: '2024-05-03T10:00:00Z',
  },
  {
    id: 't-5', sprint_id: 'sp-1', title: 'Build dashboard UI components',
    assignee_id: 'm-3', status: 'progress', priority: 6, story_points: 5,
    blocked_by: [], description: 'Create reusable UI components for the dashboard',
    created_at: '2024-05-02T09:00:00Z', updated_at: '2024-05-03T11:00:00Z',
  },
  {
    id: 't-6', sprint_id: 'sp-1', title: 'Optimize API response time',
    assignee_id: 'm-2', status: 'progress', priority: 9, story_points: 5,
    blocked_by: ['t-4'], description: 'Reduce API latency below 200ms for all endpoints',
    created_at: '2024-05-02T10:00:00Z', updated_at: '2024-05-04T08:00:00Z',
  },
  {
    id: 't-7', sprint_id: 'sp-1', title: 'Implement dark mode toggle',
    assignee_id: 'm-3', status: 'progress', priority: 3, story_points: 2,
    blocked_by: [], description: 'Add theme switching between light and dark modes',
    created_at: '2024-05-03T08:00:00Z', updated_at: '2024-05-04T09:00:00Z',
  },
  {
    id: 't-8', sprint_id: 'sp-1', title: 'Create login page',
    assignee_id: 'm-2', status: 'done', priority: 8, story_points: 3,
    blocked_by: [], description: 'Build responsive login page with form validation',
    created_at: '2024-05-01T11:00:00Z', updated_at: '2024-05-05T16:00:00Z',
  },
  {
    id: 't-9', sprint_id: 'sp-1', title: 'Set up testing framework',
    assignee_id: 'm-4', status: 'done', priority: 7, story_points: 3,
    blocked_by: [], description: 'Configure Jest and React Testing Library',
    created_at: '2024-05-01T12:00:00Z', updated_at: '2024-05-04T14:00:00Z',
  },
  {
    id: 't-10', sprint_id: 'sp-1', title: 'Configure linting and formatting',
    assignee_id: 'm-3', status: 'done', priority: 5, story_points: 1,
    blocked_by: [], description: 'Set up ESLint and Prettier configs',
    created_at: '2024-05-01T13:00:00Z', updated_at: '2024-05-02T10:00:00Z',
  },
  {
    id: 't-11', sprint_id: 'sp-1', title: 'Mobile responsive fixes',
    assignee_id: 'm-3', status: 'paused', priority: 6, story_points: 5,
    blocked_by: ['t-5'], description: 'Fix layout issues on mobile screens',
    created_at: '2024-05-03T10:00:00Z', updated_at: '2024-05-05T12:00:00Z',
  },
  {
    id: 't-12', sprint_id: 'sp-1', title: 'Research third-party integrations',
    assignee_id: 'm-4', status: 'paused', priority: 2, story_points: 3,
    blocked_by: [], description: 'Evaluate third-party service integrations',
    created_at: '2024-05-04T08:00:00Z', updated_at: '2024-05-05T10:00:00Z',
  },
];
