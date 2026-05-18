import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { Sprint, Member, Task, TaskStatus, TaskFilter, TaskCreate, AgentMessage } from '@/types';
import { DEMO_SPRINT, DEMO_MEMBERS, DEMO_TASKS } from '@/api/client';

interface AppStore {
  // Sprint
  sprint: Sprint | null;
  members: Member[];
  tasks: Task[];

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
      // Initial state
      sprint: DEMO_SPRINT,
      members: DEMO_MEMBERS,
      tasks: DEMO_TASKS.map(t => ({
        ...t,
        assignee: DEMO_MEMBERS.find(m => m.id === t.assignee_id),
      })),
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

      createTask: async (taskCreate: TaskCreate) => {
        const state = get();
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
      },

      updateTask: async (id, patch) => {
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
        set(state => ({
          tasks: state.tasks.map(t =>
            t.id === id
              ? { ...t, status, updated_at: new Date().toISOString() }
              : t
          ),
        }));
      },

      deleteTask: async (id) => {
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
