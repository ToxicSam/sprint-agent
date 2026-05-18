import { apiFetch } from './client';
import type { Sprint } from '@/types';

export async function getSprint(): Promise<Sprint> {
  return apiFetch<Sprint>('/api/sprint', { method: 'GET' });
}

export async function updateSprint(id: string, patch: Partial<Sprint>): Promise<Sprint> {
  return apiFetch<Sprint>(`/api/sprint/${id}`, {
    method: 'PATCH',
    body: JSON.stringify(patch),
  });
}

export async function createSprint(sprint: Omit<Sprint, 'id' | 'created_at'>): Promise<Sprint> {
  return apiFetch<Sprint>('/api/sprint', {
    method: 'POST',
    body: JSON.stringify(sprint),
  });
}
