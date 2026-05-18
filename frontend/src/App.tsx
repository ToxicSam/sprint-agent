import { Routes, Route, Outlet } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import Planning from './pages/Planning'
import Standup from './pages/Standup'
import Retro from './pages/Retro'
import Settings from './pages/Settings'
import Login from './pages/Login'

function LayoutWrapper() {
  return (
    <Layout>
      <Outlet />
    </Layout>
  )
}

export default function App() {
  return (
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
  )
}
