import { apiFetch } from './client';
import type { DailyLog } from '@/types';

export async function getDailyLogs(sprintId: string): Promise<DailyLog[]> {
  return apiFetch<DailyLog[]>(`/api/sprint/${sprintId}/daily-logs`, { method: 'GET' });
}

export async function createDailyLog(log: Omit<DailyLog, 'id'>): Promise<DailyLog> {
  return apiFetch<DailyLog>('/api/daily-logs', {
    method: 'POST',
    body: JSON.stringify(log),
  });
}

export async function updateDailyLog(id: string, patch: Partial<DailyLog>): Promise<DailyLog> {
  return apiFetch<DailyLog>(`/api/daily-logs/${id}`, {
    method: 'PATCH',
    body: JSON.stringify(patch),
  });
}
