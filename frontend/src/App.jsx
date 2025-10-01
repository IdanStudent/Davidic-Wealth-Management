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
  return (
    <div className="min-h-screen flex bg-gray-50">
      <Sidebar />
      <div className="flex-1 min-w-0">
        <header className="bg-white border-b border-gray-200 px-4 py-3 flex items-center justify-between">
          <Link to="/" className="text-xl font-bold text-jewishBlue">Jewish Wealth</Link>
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
