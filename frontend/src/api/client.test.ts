import { describe, it, expect, vi, beforeEach, type Mock } from 'vitest'
import { apiFetch, fetchBoard } from './client'

// ─── Mock global fetch ───────────────────────────────────

global.fetch = vi.fn()

describe('apiFetch', () => {
  beforeEach(() => {
    ;(fetch as Mock).mockClear()
  })

  it('returns parsed JSON on successful request', async () => {
    const mockData = { id: '1', name: 'Test Sprint' }
    ;(fetch as Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => mockData,
    } as Response)

    const result = await apiFetch<{ id: string; name: string }>('/api/test')
    expect(result).toEqual(mockData)
  })

  it('sends correct headers including Content-Type', async () => {
    ;(fetch as Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => ({}),
    } as Response)

    await apiFetch('/api/test', { method: 'POST', body: '{}' })

    expect(fetch).toHaveBeenCalledWith(
      expect.stringContaining('/api/test'),
      expect.objectContaining({
        headers: expect.objectContaining({
          'Content-Type': 'application/json',
        }),
      })
    )
  }
  )

  it('throws error with status on failed response', async () => {
    ;(fetch as Mock).mockResolvedValueOnce({
      ok: false,
      status: 404,
      text: async () => 'Not Found',
    } as Response)

    await expect(apiFetch('/api/missing')).rejects.toThrow('404')
  })

  it('throws error with message on failed response', async () => {
    ;(fetch as Mock).mockResolvedValueOnce({
      ok: false,
      status: 500,
      text: async () => 'Internal Server Error',
    } as Response)

    await expect(apiFetch('/api/error')).rejects.toThrow('Internal Server Error')
  })

  it('throws error with "Unknown error" when text() fails', async () => {
    ;(fetch as Mock).mockResolvedValueOnce({
      ok: false,
      status: 503,
      text: async () => { throw new Error('Network error') },
    } as Response)

    await expect(apiFetch('/api/fail')).rejects.toThrow('Unknown error')
  })

  it('passes custom headers alongside defaults', async () => {
    ;(fetch as Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => ({}),
    } as Response)

    await apiFetch('/api/test', {
      headers: { Authorization: 'Bearer token123' },
    })

    expect(fetch).toHaveBeenCalledWith(
      expect.any(String),
      expect.objectContaining({
        headers: expect.objectContaining({
          'Content-Type': 'application/json',
          Authorization: 'Bearer token123',
        }),
      })
    )
  })

  it('constructs URL with API base from env', async () => {
    ;(fetch as Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => ({}),
    } as Response)

    await apiFetch('/api/board')

    expect(fetch).toHaveBeenCalledWith(
      expect.stringMatching(/^http.*\/api\/board$/),
      expect.any(Object)
    )
  })
})

describe('fetchBoard', () => {
  beforeEach(() => {
    ;(fetch as Mock).mockClear()
  })

  it('fetches board data with correct endpoint', async () => {
    const mockBoard = {
      sprint: { id: 's1', name: 'Sprint 1', goal: '', start_date: '', end_date: '', status: 'active' as const, created_at: '' },
      members: [{ id: 'm1', name: 'Alice', role: 'sm' as const, capacity: 80 }],
      tasks: [{ id: 't1', sprint_id: 's1', title: 'Task 1', assignee_id: null, status: 'todo' as const, priority: 5 as const, story_points: 3, blocked_by: [], description: '', created_at: '', updated_at: '' }],
    }

    ;(fetch as Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => mockBoard,
    } as Response)

    const result = await fetchBoard()
    expect(result).toEqual(mockBoard)
  })

  it('uses GET method for fetchBoard', async () => {
    ;(fetch as Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => ({}),
    } as Response)

    await fetchBoard()

    expect(fetch).toHaveBeenCalledWith(
      expect.any(String),
      expect.objectContaining({ method: 'GET' })
    )
  })
})
