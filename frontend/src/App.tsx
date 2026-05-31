import { lazy, Suspense } from 'react'
import { Routes, Route, Outlet } from 'react-router-dom'
import Layout from './components/Layout'

// ─── Route-level code splitting ──────────────────────────
const Dashboard = lazy(() => import('./pages/Dashboard'))
const Planning  = lazy(() => import('./pages/Planning'))
const Standup   = lazy(() => import('./pages/Standup'))
const Retro     = lazy(() => import('./pages/Retro'))
const Settings  = lazy(() => import('./pages/Settings'))
const Login     = lazy(() => import('./pages/Login'))

// ─── Page preloading helpers ─────────────────────────────
const PAGE_LOADERS: Record<string, () => Promise<unknown>> = {
  '/planning': () => import('./pages/Planning'),
  '/standup':  () => import('./pages/Standup'),
  '/retro':    () => import('./pages/Retro'),
  '/settings': () => import('./pages/Settings'),
  '/':         () => import('./pages/Dashboard'),
}

/** Preload a page chunk on hover / focus */
export function preloadPage(page: string): void {
  PAGE_LOADERS[page]?.()
}

// ─── Fallback loader ─────────────────────────────────────
function PageLoader() {
  return (
    <div className="flex items-center justify-center min-h-[60vh]">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-[hsl(var(--primary))]" />
    </div>
  )
}

function LayoutWrapper() {
  return (
    <Layout>
      <Outlet />
    </Layout>
  )
}

export default function App() {
  return (
    <Suspense fallback={<PageLoader />}>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route element={<LayoutWrapper />}>
          <Route path="/" element={<Dashboard />} />
          <Route path="/planning" element={<Planning />} />
          <Route path="/standup" element={<Standup />} />
          <Route path="/retro" element={<Retro />} />
          <Route path="/settings" element={<Settings />} />
        </Route>
      </Routes>
    </Suspense>
  )
}
