import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { Sprint, Member, Task, TaskStatus, TaskFilter, TaskCreate, AgentMessage } from '@/types';
import { fetchBoard } from '@/api/client';
import { createTask as apiCreateTask, updateTask as apiUpdateTask, moveTask as apiMoveTask, deleteTask as apiDeleteTask } from '@/api/tasks';

interface AppStore {
  // Sprint
  sprint: Sprint | null;
  members: Member[];
  tasks: Task[];
  boardLoaded: boolean;

  // UI State
  theme: 'light' | 'dark';
  agentPanelOpen: boolean;
  sidebarExpanded: boolean;
  selectedTaskId: string | null;
  filter: TaskFilter;

  // Agent
  agentMessages: AgentMessage[];
  agentTyping: boolean;

  // Actions
  setTheme: (t: 'light' | 'dark') => void;
  toggleAgentPanel: () => void;
  toggleSidebar: () => void;
  setFilter: (f: TaskFilter) => void;
  selectTask: (id: string | null) => void;
  loadBoardData: () => Promise<void>;
  createTask: (task: TaskCreate) => Promise<Task>;
  updateTask: (id: string, patch: Partial<Task>) => Promise<void>;
  moveTask: (id: string, status: TaskStatus) => Promise<void>;
  deleteTask: (id: string) => Promise<void>;
  addAgentMessage: (msg: AgentMessage) => void;
  setAgentTyping: (typing: boolean) => void;
  setBoardData: (sprint: Sprint, members: Member[], tasks: Task[]) => void;
}

export const useStore = create<AppStore>()(
  persist(
    (set, get) => ({
      // Initial state — empty until loaded from backend
      sprint: null,
      members: [],
      tasks: [],
      boardLoaded: false,

      theme: 'light',
      agentPanelOpen: false,
      sidebarExpanded: false,
      selectedTaskId: null,
      filter: { status: 'all' },
      agentMessages: [],
      agentTyping: false,

      // Actions
      setTheme: (theme) => set({ theme }),

      toggleAgentPanel: () => set(state => ({ agentPanelOpen: !state.agentPanelOpen })),

      toggleSidebar: () => set(state => ({ sidebarExpanded: !state.sidebarExpanded })),

      setFilter: (filter) => set({ filter }),

      selectTask: (selectedTaskId) => set({ selectedTaskId }),

      loadBoardData: async () => {
        try {
          const data = await fetchBoard();
          console.log('[Store] Board data loaded:', data);
          set({
            sprint: data.sprint,
            members: data.members,
            tasks: data.tasks.map((t: Task) => ({
              ...t,
              blocked_by: (() => {
                const val = t.blocked_by;
                if (val === null || val === undefined) return [];
                if (typeof val === 'string') {
                  try {
                    const parsed = JSON.parse(val);
                    return Array.isArray(parsed) ? parsed : [];
                  } catch {
                    return [];
                  }
                }
                if (Array.isArray(val)) return val;
                return [];
              })(),
              assignee: data.members.find((m: Member) => m.id === t.assignee_id),
            })),
            boardLoaded: true,
          });
        } catch (err) {
          console.error('Failed to load board data:', err);
          set({ boardLoaded: true });
        }
      },

      createTask: async (taskCreate: TaskCreate) => {
        const state = get();
        const payload = {
          ...taskCreate,
          sprint_id: state.sprint?.id || '',
          status: taskCreate.status || 'todo',
          priority: taskCreate.priority || 5,
          story_points: taskCreate.story_points || 0,
          blocked_by: null,
          description: taskCreate.description || '',
        };
        try {
          const created = await apiCreateTask(payload);
          const newTask: Task = {
            ...created,
            blocked_by: typeof created.blocked_by === 'string' && created.blocked_by
              ? JSON.parse(created.blocked_by)
              : [],
            assignee: state.members.find(m => m.id === created.assignee_id),
          };
          set(state => ({ tasks: [...state.tasks, newTask] }));
          return newTask;
        } catch (err) {
          console.error('Failed to create task:', err);
          // Fallback to optimistic local update if backend fails
          const newTask: Task = {
            id: `t-${Date.now()}`,
            sprint_id: state.sprint?.id || '',
            assignee_id: taskCreate.assignee_id || null,
            status: taskCreate.status || 'todo',
            priority: (taskCreate.priority as 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10) || 5,
            story_points: taskCreate.story_points || 0,
            blocked_by: [],
            description: taskCreate.description || '',
            title: taskCreate.title,
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
            assignee: state.members.find(m => m.id === taskCreate.assignee_id),
          };
          set(state => ({ tasks: [...state.tasks, newTask] }));
          return newTask;
        }
      },

      updateTask: async (id, patch) => {
        try {
          await apiUpdateTask(id, patch);
        } catch (err) {
          console.error('Failed to update task:', err);
        }
        set(state => ({
          tasks: state.tasks.map(t =>
            t.id === id
              ? {
                  ...t,
                  ...patch,
                  updated_at: new Date().toISOString(),
                  assignee: patch.assignee_id !== undefined
                    ? state.members.find(m => m.id === patch.assignee_id) || undefined
                    : t.assignee,
                }
              : t
          ),
        }));
      },

      moveTask: async (id, status) => {
        try {
          await apiMoveTask(id, status);
        } catch (err) {
          console.error('Failed to move task:', err);
        }
        set(state => ({
          tasks: state.tasks.map(t =>
            t.id === id
              ? { ...t, status, updated_at: new Date().toISOString() }
              : t
          ),
        }));
      },

      deleteTask: async (id) => {
        try {
          await apiDeleteTask(id);
        } catch (err) {
          console.error('Failed to delete task:', err);
        }
        set(state => ({
          tasks: state.tasks.filter(t => t.id !== id),
          selectedTaskId: state.selectedTaskId === id ? null : state.selectedTaskId,
        }));
      },

      addAgentMessage: (msg) => set(state => ({
        agentMessages: [...state.agentMessages, msg],
      })),

      setAgentTyping: (typing) => set({ agentTyping: typing }),

      setBoardData: (sprint, members, tasks) => set({
        sprint,
        members,
        tasks: tasks.map(t => ({
          ...t,
          assignee: members.find(m => m.id === t.assignee_id),
        })),
        boardLoaded: true,
      }),
    }),
    {
      name: 'sprint-agent-store',
      partialize: (state) => ({
        theme: state.theme,
        sidebarExpanded: state.sidebarExpanded,
      }),
    }
  )
);
