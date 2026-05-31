import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import KanbanColumn from './KanbanColumn'
import type { Task } from '@/types'

// ─── Mocks ───────────────────────────────────────────────

vi.mock('@dnd-kit/core', () => ({
  useDroppable: () => ({
    setNodeRef: vi.fn(),
    isOver: false,
  }),
}))

// ─── Test Data ───────────────────────────────────────────

const mockTasks: Task[] = [
  {
    id: 't1',
    sprint_id: 's1',
    title: 'Task One',
    assignee_id: 'm1',
    status: 'todo',
    priority: 5,
    story_points: 3,
    blocked_by: [],
    description: '',
    created_at: '',
    updated_at: '',
  },
  {
    id: 't2',
    sprint_id: 's1',
    title: 'Task Two',
    assignee_id: null,
    status: 'todo',
    priority: 3,
    story_points: 2,
    blocked_by: [],
    description: '',
    created_at: '',
    updated_at: '',
  },
]

// ─── Tests ───────────────────────────────────────────────

describe('KanbanColumn', () => {
  it('renders column title correctly', () => {
    render(
      <KanbanColumn id="todo" label="TO DO" dotColor="bg-gray-400" tasks={[]} />
    )
    expect(screen.getByText('TO DO')).toBeInTheDocument()
  })

  it('displays correct task count', () => {
    render(
      <KanbanColumn id="todo" label="TO DO" dotColor="bg-gray-400" tasks={mockTasks} />
    )
    expect(screen.getByText('2')).toBeInTheDocument()
  })

  it('shows zero count for empty column', () => {
    render(
      <KanbanColumn id="todo" label="TO DO" dotColor="bg-gray-400" tasks={[]} />
    )
    expect(screen.getByText('0')).toBeInTheDocument()
  })

  it('renders empty state when no tasks', () => {
    render(
      <KanbanColumn id="todo" label="TO DO" dotColor="bg-gray-400" tasks={[]} />
    )
    expect(screen.getByText('No tasks')).toBeInTheDocument()
    expect(screen.getByText('Drop tasks here')).toBeInTheDocument()
  })

  it('does not show empty state when tasks exist', () => {
    render(
      <KanbanColumn id="todo" label="TO DO" dotColor="bg-gray-400" tasks={mockTasks}>
        <div data-testid="task-item">Task 1</div>
      </KanbanColumn>
    )
    expect(screen.queryByText('No tasks')).not.toBeInTheDocument()
    expect(screen.getByText('Task 1')).toBeInTheDocument()
  })

  it('renders children when tasks are present', () => {
    render(
      <KanbanColumn id="todo" label="TO DO" dotColor="bg-gray-400" tasks={mockTasks}>
        <div data-testid="child-content">Child Tasks</div>
      </KanbanColumn>
    )
    expect(screen.getByTestId('child-content')).toBeInTheDocument()
  })

  it('has droppable data attribute', () => {
    render(
      <KanbanColumn id="in-progress" label="IN PROGRESS" dotColor="bg-blue-400" tasks={[]} />
    )
    expect(screen.getByTestId('column-in-progress')).toBeInTheDocument()
  })

  it('renders colored dot indicator', () => {
    render(
      <KanbanColumn id="done" label="DONE" dotColor="bg-green-400" tasks={[]} />
    )
    expect(screen.getByTestId('column-dot')).toBeInTheDocument()
  })

  it('displays correct task count for single task', () => {
    render(
      <KanbanColumn id="paused" label="PAUSED" dotColor="bg-yellow-400" tasks={[mockTasks[0]]} />
    )
    expect(screen.getByText('1')).toBeInTheDocument()
  })
})
