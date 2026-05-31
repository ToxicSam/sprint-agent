import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import TaskCard from './TaskCard'
import type { Task } from '@/types'

// ─── Mocks ───────────────────────────────────────────────

const mockSelectTask = vi.fn()

vi.mock('@/store', () => ({
  useStore: (selector: any) => {
    const state = {
      members: [
        { id: 'm1', name: 'Alice Johnson', role: 'sm' as const, capacity: 80 },
        { id: 'm2', name: 'Bob Smith', role: 'dev' as const, capacity: 90 },
      ],
      selectTask: mockSelectTask,
    }
    return selector ? selector(state) : state
  },
}))

vi.mock('@dnd-kit/sortable', () => ({
  useSortable: () => ({
    attributes: { 'data-testid': 'sortable-item' },
    listeners: { onPointerDown: vi.fn() },
    setNodeRef: vi.fn(),
    transform: null,
    transition: undefined,
    isDragging: false,
  }),
}))

vi.mock('@dnd-kit/utilities', () => ({
  CSS: {
    Transform: {
      toString: () => '',
    },
  },
}))

// ─── Test Data ───────────────────────────────────────────

const mockTask: Task = {
  id: 't1',
  sprint_id: 's1',
  title: 'Implement user authentication',
  assignee_id: 'm1',
  status: 'progress',
  priority: 8,
  story_points: 5,
  blocked_by: [],
  description: 'Add OAuth2 login flow',
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-02T00:00:00Z',
}

const blockedTask: Task = {
  ...mockTask,
  id: 't2',
  title: 'Deploy to production',
  blocked_by: ['t1'],
  priority: 9,
  story_points: 3,
}

const unassignedTask: Task = {
  ...mockTask,
  id: 't3',
  title: 'Write documentation',
  assignee_id: null,
  status: 'todo',
  priority: 3,
  story_points: 2,
}

// ─── Tests ───────────────────────────────────────────────

describe('TaskCard', () => {
  beforeEach(() => {
    mockSelectTask.mockClear()
  })

  it('renders task title correctly', () => {
    render(<TaskCard task={mockTask} />)
    expect(screen.getByText('Implement user authentication')).toBeInTheDocument()
  })

  it('renders priority badge with correct label', () => {
    render(<TaskCard task={mockTask} />)
    expect(screen.getByText('High')).toBeInTheDocument()
  })

  it('renders story points', () => {
    render(<TaskCard task={mockTask} />)
    expect(screen.getByText('5pt')).toBeInTheDocument()
  })

  it('renders assignee name when task is assigned', () => {
    render(<TaskCard task={mockTask} />)
    expect(screen.getByText('Alice Johnson')).toBeInTheDocument()
  })

  it('renders "Unassigned" when task has no assignee', () => {
    render(<TaskCard task={unassignedTask} />)
    expect(screen.getByText('Unassigned')).toBeInTheDocument()
  })

  it('renders "Blocked" badge for blocked tasks', () => {
    render(<TaskCard task={blockedTask} />)
    expect(screen.getByText('Blocked')).toBeInTheDocument()
  })

  it('renders priority badge for non-blocked critical priority task', () => {
    render(<TaskCard task={{ ...mockTask, priority: 10 }} />)
    expect(screen.getByText('Critical')).toBeInTheDocument()
  })

  it('renders Medium priority badge correctly', () => {
    render(<TaskCard task={{ ...mockTask, priority: 5 }} />)
    expect(screen.getByText('Medium')).toBeInTheDocument()
  })

  it('renders Low priority badge correctly', () => {
    render(<TaskCard task={{ ...mockTask, priority: 2 }} />)
    expect(screen.getByText('Low')).toBeInTheDocument()
  })

  it('calls selectTask when card is clicked', () => {
    render(<TaskCard task={mockTask} />)
    const card = screen.getByText('Implement user authentication').closest('.group')
    if (card) {
      fireEvent.click(card)
    }
    expect(mockSelectTask).toHaveBeenCalledWith('t1')
  })

  it('has draggable attributes', () => {
    render(<TaskCard task={mockTask} />)
    expect(screen.getByTestId('sortable-item')).toBeInTheDocument()
  })

  it('does not show story points when zero', () => {
    render(<TaskCard task={{ ...mockTask, story_points: 0 }} />)
    expect(screen.queryByText(/pt$/)).not.toBeInTheDocument()
  })

  it('renders assignee initial avatar', () => {
    render(<TaskCard task={mockTask} />)
    expect(screen.getByText('A')).toBeInTheDocument()
  })
})
