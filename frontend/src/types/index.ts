export type TaskStatus = 'todo' | 'progress' | 'done' | 'paused';
export type Priority = 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10;
export type SprintStatus = 'active' | 'completed' | 'cancelled';
export type MemberRole = 'sm' | 'dev' | 'qa' | 'po';

export interface Member {
  id: string;
  name: string;
  role: MemberRole;
  capacity: number;
  avatar?: string;
}

export interface Sprint {
  id: string;
  name: string;
  goal: string;
  start_date: string;
  end_date: string;
  status: SprintStatus;
  created_at: string;
}

export interface Task {
  id: string;
  sprint_id: string;
  title: string;
  assignee_id: string | null;
  status: TaskStatus;
  priority: Priority;
  story_points: number;
  blocked_by: string[];
  description: string;
  created_at: string;
  updated_at: string;
  assignee?: Member;
}

export interface DailyLog {
  id: string;
  sprint_id: string;
  member_id: string;
  date: string;
  completed: string;
  planned: string;
  blockers: string;
  hours_spent: number;
  member?: Member;
}

export interface RetroItem {
  id: string;
  sprint_id: string;
  category: 'liked' | 'disliked' | 'action';
  item: string;
  votes: number;
}

export interface RetroRating {
  id: string;
  sprint_id: string;
  dimension: 'velocity' | 'quality' | 'teamwork' | 'process';
  score: number;
}

export interface AgentMessage {
  id: string;
  role: 'user' | 'agent' | 'system';
  content: string;
  context?: Record<string, unknown>;
  created_at: string;
}

export interface TaskFilter {
  status?: TaskStatus | 'all' | 'blocked';
  assignee?: string;
  priority?: Priority;
  search?: string;
}

export interface TaskCreate {
  title: string;
  assignee_id?: string;
  status?: TaskStatus;
  priority?: Priority;
  story_points?: number;
  description?: string;
}
