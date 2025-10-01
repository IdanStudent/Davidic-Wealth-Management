import React, { useEffect, useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from './AuthContext'

export default function Sidebar() {
  const [collapsed, setCollapsed] = useState(() => localStorage.getItem('sidebar_collapsed') === '1')
  const location = useLocation()
  const navigate = useNavigate()
  const { logout } = useAuth()

  useEffect(() => {
    localStorage.setItem('sidebar_collapsed', collapsed ? '1' : '0')
  }, [collapsed])

  const items = [
    { to: '/', label: 'Dashboard' },
    { to: '/categories', label: 'Categories' },
    { to: '/accounts', label: 'Accounts' },
    { to: '/investments', label: 'Investments' },
    { to: '/transactions', label: 'Transactions' },
    { to: '/budgets', label: 'Budgets' },
    { to: '/reports', label: 'Reports' },
    { to: '/settings', label: 'Settings' },
  ]

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <aside className={(collapsed ? 'w-16' : 'w-64') + ' bg-white border-r border-gray-200 min-h-screen flex flex-col transition-all duration-200'}>
      <div className="flex items-center justify-between gap-2 p-3 border-b border-gray-100">
        <Link to="/" className="text-jewishBlue font-bold truncate" title="Jewish Wealth">
          {collapsed ? 'JW' : 'Jewish Wealth'}
        </Link>
        <button
          aria-label={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
          className="text-gray-600 hover:text-gray-900 p-1 rounded hover:bg-gray-100"
          onClick={() => setCollapsed(c => !c)}
          title={collapsed ? 'Expand' : 'Collapse'}
        >
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-5 h-5">
            <path fillRule="evenodd" d="M3.75 6.75a.75.75 0 0 1 .75-.75h15a.75.75 0 0 1 0 1.5h-15a.75.75 0 0 1-.75-.75Zm0 5.25a.75.75 0 0 1 .75-.75h15a.75.75 0 0 1 0 1.5h-15a.75.75 0 0 1-.75-.75Zm0 5.25a.75.75 0 0 1 .75-.75h15a.75.75 0 0 1 0 1.5h-15a.75.75 0 0 1-.75-.75Z" clipRule="evenodd" />
          </svg>
        </button>
      </div>

      <nav className="flex-1 overflow-y-auto py-2">
        <ul className="space-y-1">
          {items.map(item => {
            const active = location.pathname === item.to || (item.to !== '/' && location.pathname.startsWith(item.to))
            return (
              <li key={item.to}>
                <Link
                  to={item.to}
                  className={
                    'flex items-center gap-3 px-3 py-2 rounded-md transition-colors ' +
                    (active ? 'bg-jewishBlue/10 text-jewishBlue font-medium' : 'text-gray-700 hover:bg-gray-100')
                  }
                  title={item.label}
                >
                  {/* Placeholder icon - small dot; you can swap with real icons later */}
                  <span className="w-2 h-2 rounded-full bg-current"></span>
                  {!collapsed && <span className="truncate">{item.label}</span>}
                </Link>
              </li>
            )
          })}
        </ul>
      </nav>

      <div className="p-3 border-t border-gray-100">
        <button
          onClick={handleLogout}
          className="w-full flex items-center gap-3 px-3 py-2 rounded-md text-red-600 hover:bg-red-50 transition-colors"
          title="Logout"
        >
          <span className="w-2 h-2 rounded-full bg-current"></span>
          {!collapsed && <span className="truncate">Logout</span>}
        </button>
      </div>
    </aside>
  )
}
