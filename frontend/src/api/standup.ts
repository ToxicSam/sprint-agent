import { apiFetch } from './client';
import type { DailyLog } from '@/types';

export async function getDailyLogs(sprintId: string): Promise<DailyLog[]> {
  return apiFetch<DailyLog[]>(`/api/standup?sprint_id=${sprintId}`, { method: 'GET' });
}

export async function getTodayLogs(sprintId: string): Promise<DailyLog[]> {
  return apiFetch<DailyLog[]>(`/api/standup/today?sprint_id=${sprintId}`, { method: 'GET' });
}

export async function createDailyLog(log: Omit<DailyLog, 'id'>): Promise<DailyLog> {
  return apiFetch<DailyLog>('/api/standup', {
    method: 'POST',
    body: JSON.stringify(log),
  });
}

export async function updateDailyLog(id: string, patch: Partial<DailyLog>): Promise<DailyLog> {
  return apiFetch<DailyLog>(`/api/standup/${id}`, {
    method: 'PATCH',
    body: JSON.stringify(patch),
  });
}
