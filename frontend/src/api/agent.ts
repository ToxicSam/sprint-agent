import { apiFetch } from './client';
import type { AgentMessage } from '@/types';

interface AgentActionResult {
  success: boolean;
  message: string;
  data: Record<string, unknown>;
}

export async function sendMessage(content: string, context?: Record<string, unknown>): Promise<AgentMessage> {
  const result = await apiFetch<AgentActionResult>('/api/agent/chat', {
    method: 'POST',
    body: JSON.stringify({ role: 'user', content, context }),
  });
  return {
    id: `msg-agent-${Date.now()}`,
    role: 'agent',
    content: result.message,
    created_at: new Date().toISOString(),
  };
}

export async function getMessageHistory(): Promise<AgentMessage[]> {
  return apiFetch<AgentMessage[]>('/api/agent/history', { method: 'GET' });
}

export async function clearHistory(): Promise<void> {
  return apiFetch<void>('/api/agent/history', { method: 'DELETE' });
}
