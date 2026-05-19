import type { Sprint, Member, Task } from '@/types';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
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

export async function fetchBoard(): Promise<{ sprint: Sprint; members: Member[]; tasks: Task[] }> {
  return apiFetch('/api/board', { method: 'GET' });
}
