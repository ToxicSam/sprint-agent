import { apiFetch } from './client';
import type { Task, TaskCreate } from '@/types';

export async function getTasks(): Promise<Task[]> {
  return apiFetch<Task[]>('/api/tasks', { method: 'GET' });
}

export async function getTask(id: string): Promise<Task> {
  return apiFetch<Task>(`/api/tasks/${id}`, { method: 'GET' });
}

export async function createTask(task: TaskCreate): Promise<Task> {
  return apiFetch<Task>('/api/tasks', {
    method: 'POST',
    body: JSON.stringify(task),
  });
}

export async function updateTask(id: string, patch: Partial<Task>): Promise<Task> {
  return apiFetch<Task>(`/api/tasks/${id}`, {
    method: 'PATCH',
    body: JSON.stringify(patch),
  });
}

export async function moveTask(id: string, status: string): Promise<Task> {
  return apiFetch<Task>(`/api/tasks/${id}/status`, {
    method: 'PATCH',
    body: JSON.stringify({ status }),
  });
}

export async function deleteTask(id: string): Promise<void> {
  return apiFetch<void>(`/api/tasks/${id}`, { method: 'DELETE' });
}
