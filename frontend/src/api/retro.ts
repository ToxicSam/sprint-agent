import { apiFetch } from './client';
import type { RetroItem, RetroRating } from '@/types';

export async function getRetroItems(sprintId: string): Promise<RetroItem[]> {
  return apiFetch<RetroItem[]>(`/api/sprint/${sprintId}/retro/items`, { method: 'GET' });
}

export async function createRetroItem(item: Omit<RetroItem, 'id'>): Promise<RetroItem> {
  return apiFetch<RetroItem>('/api/retro/items', {
    method: 'POST',
    body: JSON.stringify(item),
  });
}

export async function voteRetroItem(id: string): Promise<RetroItem> {
  return apiFetch<RetroItem>(`/api/retro/items/${id}/vote`, { method: 'POST' });
}

export async function getRetroRatings(sprintId: string): Promise<RetroRating[]> {
  return apiFetch<RetroRating[]>(`/api/sprint/${sprintId}/retro/ratings`, { method: 'GET' });
}

export async function createRetroRating(rating: Omit<RetroRating, 'id'>): Promise<RetroRating> {
  return apiFetch<RetroRating>('/api/retro/ratings', {
    method: 'POST',
    body: JSON.stringify(rating),
  });
}
