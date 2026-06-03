import { apiFetch } from './client';
import type { RetroItem, RetroRating } from '@/types';

export async function getRetroItems(sprintId: string): Promise<RetroItem[]> {
  return apiFetch<RetroItem[]>(`/api/retro/${sprintId}`, { method: 'GET' });
}

export async function createRetroItem(item: Omit<RetroItem, 'id'>): Promise<RetroItem> {
  return apiFetch<RetroItem>('/api/retro', {
    method: 'POST',
    body: JSON.stringify(item),
  });
}

export async function voteRetroItem(id: string): Promise<RetroItem> {
  return apiFetch<RetroItem>(`/api/retro/vote`, {
    method: 'POST',
    body: JSON.stringify({ retro_id: id }),
  });
}

export async function deleteRetroItem(itemId: string): Promise<void> {
  return apiFetch<void>(`/api/retro/${itemId}`, { method: 'DELETE' });
}

export async function getRetroRatings(sprintId: string): Promise<RetroRating[]> {
  return apiFetch<RetroRating[]>(`/api/retro/${sprintId}/report`, { method: 'GET' });
}

export async function createRetroRating(rating: Omit<RetroRating, 'id'>): Promise<RetroRating> {
  return apiFetch<RetroRating>('/api/retro/rate', {
    method: 'POST',
    body: JSON.stringify(rating),
  });
}
