import React from 'react'
import { Routes, Route, Link, Navigate } from 'react-router-dom'
import Login from './pages/Login'
import Register from './pages/Register'
import Dashboard from './pages/Dashboard'
import Accounts from './pages/Accounts'
import Transactions from './pages/Transactions'
import Budgets from './pages/Budgets'
import Reports from './pages/Reports'
import Categories from './pages/Categories'
import Investments from './pages/Investments'
import Settings from './pages/Settings'
import DebtPlanner from './pages/DebtPlanner'
import Goals from './pages/Goals'
import { AuthProvider, useAuth } from './components/AuthContext'
import Sidebar from './components/Sidebar'

function PrivateRoute({ children }) {
  const { token } = useAuth()
  return token ? children : <Navigate to="/login" replace />
}

export default function App() {
  return (
    <AuthProvider>
      <Routes>
        {/* Public routes without sidebar */}
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />

        {/* Authenticated layout with sidebar */}
        <Route
          path="*"
          element={
            <PrivateRoute>
              <AppShell />
            </PrivateRoute>
          }
        />
      </Routes>
    </AuthProvider>
  )
}

function AppShell() {
  const [mobileOpen, setMobileOpen] = React.useState(false)
  const hamburgerRef = React.useRef(null)

  // Close on Esc when open
  React.useEffect(() => {
    if (!mobileOpen) return
    const onKey = (e) => {
      if (e.key === 'Escape') setMobileOpen(false)
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [mobileOpen])

  // Restore focus to hamburger on close
  React.useEffect(() => {
    if (!mobileOpen && hamburgerRef.current) {
      hamburgerRef.current.focus({ preventScroll: true })
    }
  }, [mobileOpen])
  return (
    <div className="min-h-screen flex bg-gray-50">
      {/* Overlay for mobile */}
      <div
        className={
          'fixed inset-0 z-40 bg-black/40 md:hidden transition-opacity duration-200 ' +
          (mobileOpen ? 'opacity-100 pointer-events-auto' : 'opacity-0 pointer-events-none')
        }
        onClick={() => setMobileOpen(false)}
        aria-hidden
      />
      <Sidebar mobileOpen={mobileOpen} onMobileClose={() => setMobileOpen(false)} />
      <div className="flex-1 min-w-0">
        <header className="bg-white border-b border-gray-200 px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <button
              ref={hamburgerRef}
              className="md:hidden inline-flex text-gray-700 hover:text-gray-900 p-2 rounded hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-malkaBlue"
              aria-label="Open menu"
              onClick={() => setMobileOpen(true)}
            >
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-6 h-6">
                <path fillRule="evenodd" d="M3.75 6.75a.75.75 0 0 1 .75-.75h15a.75.75 0 0 1 0 1.5h-15a.75.75 0 0 1-.75-.75Zm0 5.25a.75.75 0 0 1 .75-.75h15a.75.75 0 0 1 0 1.5h-15a.75.75 0 0 1-.75-.75Zm0 5.25a.75.75 0 0 1 .75-.75h15a.75.75 0 0 1 0 1.5h-15a.75.75 0 0 1-.75-.75Z" clipRule="evenodd" />
              </svg>
            </button>
            <Link to="/" className="text-xl font-bold text-malkaBlue">Malka Money</Link>
          </div>
          <NavLinks minimal />
        </header>
        <main className="p-4">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/categories" element={<Categories />} />
            <Route path="/accounts" element={<Accounts />} />
            <Route path="/transactions" element={<Transactions />} />
            <Route path="/budgets" element={<Budgets />} />
            <Route path="/reports" element={<Reports />} />
            <Route path="/investments" element={<Investments />} />
            <Route path="/settings" element={<Settings />} />
            <Route path="/debt" element={<DebtPlanner />} />
            <Route path="/goals" element={<Goals />} />
          </Routes>
        </main>
      </div>
    </div>
  )
}

function NavLinks({ minimal = false }) {
  const { token, logout } = useAuth()
  if (!token) {
    return (
      <div className="space-x-4">
        <Link to="/login">Login</Link>
        <Link to="/register">Register</Link>
      </div>
    )
  }
  if (minimal) {
    return (
      <button onClick={logout} className="text-red-600">Logout</button>
    )
  }
  return null
}
