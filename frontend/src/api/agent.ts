import { apiFetch } from './client';
import type { AgentMessage } from '@/types';

export async function sendMessage(content: string, context?: Record<string, unknown>): Promise<AgentMessage> {
  return apiFetch<AgentMessage>('/api/agent/chat', {
    method: 'POST',
    body: JSON.stringify({ content, context }),
  });
}

export async function getMessageHistory(): Promise<AgentMessage[]> {
  return apiFetch<AgentMessage[]>('/api/agent/history', { method: 'GET' });
}

export async function clearHistory(): Promise<void> {
  return apiFetch<void>('/api/agent/history', { method: 'DELETE' });
}
