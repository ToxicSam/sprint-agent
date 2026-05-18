import { apiFetch } from './client';
import type { Member } from '@/types';

export async function getMembers(): Promise<Member[]> {
  return apiFetch<Member[]>('/api/members', { method: 'GET' });
}

export async function createMember(member: Omit<Member, 'id'>): Promise<Member> {
  return apiFetch<Member>('/api/members', {
    method: 'POST',
    body: JSON.stringify(member),
  });
}

export async function updateMember(id: string, patch: Partial<Member>): Promise<Member> {
  return apiFetch<Member>(`/api/members/${id}`, {
    method: 'PATCH',
    body: JSON.stringify(patch),
  });
}

export async function deleteMember(id: string): Promise<void> {
  return apiFetch<void>(`/api/members/${id}`, { method: 'DELETE' });
}
