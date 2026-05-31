import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import Login from './Login'

// ─── Mocks ───────────────────────────────────────────────

const mockNavigate = vi.fn()

vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom')
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  }
})

vi.mock('@/store', () => ({
  useStore: (selector: any) => {
    const state = {
      sprint: null,
      setBoardData: vi.fn(),
    }
    return selector ? selector(state) : state
  },
}))

// ─── Tests ───────────────────────────────────────────────

describe('Login Page', () => {
  beforeEach(() => {
    mockNavigate.mockClear()
    localStorage.clear()
  })

  it('renders role selection buttons (Scrum Master and Developer)', () => {
    render(
      <MemoryRouter>
        <Login />
      </MemoryRouter>
    )

    expect(screen.getByRole('radio', { name: /scrum master/i })).toBeInTheDocument()
    expect(screen.getByRole('radio', { name: /developer/i })).toBeInTheDocument()
    expect(screen.getByText('Sprint Agent')).toBeInTheDocument()
  })

  it('renders role descriptions', () => {
    render(
      <MemoryRouter>
        <Login />
      </MemoryRouter>
    )

    expect(screen.getByText('Manage sprints, tasks, and team')).toBeInTheDocument()
    expect(screen.getByText('View tasks, submit standup, collaborate')).toBeInTheDocument()
  })

  it('selects Scrum Master role on click', async () => {
    const user = userEvent.setup()
    render(
      <MemoryRouter>
        <Login />
      </MemoryRouter>
    )

    const smButton = screen.getByRole('radio', { name: /scrum master/i })
    await user.click(smButton)

    expect(smButton).toHaveAttribute('aria-checked', 'true')
  })

  it('selects Developer role on click', async () => {
    const user = userEvent.setup()
    render(
      <MemoryRouter>
        <Login />
      </MemoryRouter>
    )

    const devButton = screen.getByRole('radio', { name: /developer/i })
    await user.click(devButton)

    expect(devButton).toHaveAttribute('aria-checked', 'true')
  })

  it('disables "Get Started" button when no role is selected', () => {
    render(
      <MemoryRouter>
        <Login />
      </MemoryRouter>
    )

    const submitButton = screen.getByRole('button', { name: /get started/i })
    expect(submitButton).toBeDisabled()
  })

  it('enables "Get Started" button after selecting a role', async () => {
    const user = userEvent.setup()
    render(
      <MemoryRouter>
        <Login />
      </MemoryRouter>
    )

    const smButton = screen.getByRole('radio', { name: /scrum master/i })
    await user.click(smButton)

    const submitButton = screen.getByRole('button', { name: /get started/i })
    await waitFor(() => {
      expect(submitButton).not.toBeDisabled()
    })
  })

  it('renders file drop zone for JSON import', () => {
    render(
      <MemoryRouter>
        <Login />
      </MemoryRouter>
    )

    expect(screen.getByText(/drop json file or click to upload/i)).toBeInTheDocument()
    expect(screen.getByText(/or import data to get started:/i)).toBeInTheDocument()
  })

  it('selects Scrum Master role via keyboard shortcut "1"', async () => {
    render(
      <MemoryRouter>
        <Login />
      </MemoryRouter>
    )

    const container = screen.getByText('I am a:').parentElement?.parentElement
    if (container) {
      fireEvent.keyDown(container, { key: '1' })
    }

    // The keyDown handler is on the outer div
    const smButton = screen.getByRole('radio', { name: /scrum master/i })
    await waitFor(() => {
      expect(smButton).toHaveAttribute('aria-checked', 'true')
    })
  })

  it('selects Developer role via keyboard shortcut "2"', async () => {
    render(
      <MemoryRouter>
        <Login />
      </MemoryRouter>
    )

    const container = screen.getByText('I am a:').parentElement?.parentElement
    if (container) {
      fireEvent.keyDown(container, { key: '2' })
    }

    const devButton = screen.getByRole('radio', { name: /developer/i })
    await waitFor(() => {
      expect(devButton).toHaveAttribute('aria-checked', 'true')
    })
  })

  it('renders the "Skip for now" link', () => {
    render(
      <MemoryRouter>
        <Login />
      </MemoryRouter>
    )

    expect(screen.getByText(/skip for now/i)).toBeInTheDocument()
  })

  it('renders remember role checkbox checked by default', () => {
    render(
      <MemoryRouter>
        <Login />
      </MemoryRouter>
    )

    const checkbox = screen.getByRole('checkbox', { name: /remember my role/i })
    expect(checkbox).toBeChecked()
  })
})
