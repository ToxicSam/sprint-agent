# Frontend Agent Guide

React 19 + TypeScript + Vite 7 + Tailwind CSS v3 + shadcn/ui frontend for Sprint Agent.

## Structure

```
frontend/src/
  main.tsx              # Entry point: HashRouter, no StrictMode
  App.tsx               # Route definitions
  pages/                # Route-level pages: Dashboard, Planning, Standup, Retro, Settings, Login
  components/           # Reusable components + ~50 shadcn/ui primitives in ui/
  store/index.ts        # Single Zustand store with persist middleware
  api/                  # client.ts (smart fetch + offline localStorage fallback), sprint.ts, tasks.ts, members.ts, standup.ts, retro.ts, agent.ts, index.ts
  types/index.ts        # All TypeScript interfaces and enums
  hooks/                # use-mobile.ts, useKeyboardNavigation.ts
  lib/utils.ts          # cn() utility (clsx + tailwind-merge)
```

## Where to Look

| Task | File |
|------|------|
| Add a page | `src/App.tsx` + `src/pages/` |
| Add a component | `src/components/` (shadcn/ui in `ui/`) |
| Add an API endpoint | `src/api/` + re-export in `index.ts` |
| Add/modify types | `src/types/index.ts` |
| State changes | `src/store/index.ts` |
| Styling tokens | `tailwind.config.js` (custom colors, spacing, z-index) |
| Offline behavior | `src/api/client.ts` (localStorage fallback) |

## Conventions

- **TypeScript strict mode** with `noUnusedLocals` and `noUnusedParameters` — compiler errors on unused variables.
- **Path alias `@/`** maps to `src/`. Use it for all imports.
- **Zustand selectors** should be granular: `useStore(s => s.tasks)` to avoid re-renders.
- **Styling**: Use `cn()` from `@/lib/utils` for conditional class merging. Prefer Tailwind utilities over custom CSS.
- **shadcn/ui**: Components live in `components/ui/`. Add new ones via the CLI (`npx shadcn add <component>`).
- **API client**: `apiFetch()` in `client.ts` auto-detects backend health via `/api/health`. Falls back to `localStorage` if unreachable.
- **Keyboard navigation**: `useKeyboardNavigation.ts` provides Excel-like Tab/Enter/Ctrl+Enter behavior for tables.
- **Theme**: Dark mode toggled via `theme` state in Zustand. Tailwind `darkMode: ["class"]` with CSS variables.
- **Custom design tokens**: Status colors (`status-todo`, `status-progress`, `status-done`, `status-paused`, `status-blocked`), z-index scale (`sticky` through `drag`), spacing scale (`space-1` through `space-10`).

## Anti-Patterns

- Do NOT use `React.StrictMode` — explicitly disabled in `main.tsx`.
- Do NOT add mock data to frontend code. The backend seeds from `backend/data/init.json`. The frontend only has a minimal demo fallback in `client.ts` for offline mode.
- Do NOT use auto-increment integers for IDs. All entity IDs are UUID strings.
- Do NOT create multiple Zustand stores. Use the single store in `store/index.ts` with granular selectors.
- Do NOT import from relative paths (`../components/...`). Always use `@/` alias.
- Do NOT add custom CSS in component files. Use Tailwind utilities or extend `tailwind.config.js`.
