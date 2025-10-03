import React, { useEffect, useRef, useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from './AuthContext'

export default function Sidebar({ mobileOpen = false, onMobileClose = () => {} }) {
  const [collapsed, setCollapsed] = useState(() => localStorage.getItem('sidebar_collapsed') === '1')
  const location = useLocation()
  const navigate = useNavigate()
  const { logout } = useAuth()
  const firstLinkRef = useRef(null)

  useEffect(() => {
    localStorage.setItem('sidebar_collapsed', collapsed ? '1' : '0')
  }, [collapsed])

  // Focus the first link when opening on mobile
  useEffect(() => {
    if (mobileOpen && firstLinkRef.current) {
      firstLinkRef.current.focus({ preventScroll: true })
    }
  }, [mobileOpen])

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
    <aside
      className={
        // Mobile: off-canvas drawer
        'fixed inset-y-0 left-0 z-50 w-64 transform transition-transform duration-200 ease-in-out md:static md:z-auto ' +
        // Translate for mobile open/closed
        (mobileOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0') + ' ' +
        // Base styling
        ' bg-white border-r border-gray-200 min-h-screen flex flex-col shadow-lg md:shadow-none ' +
        // Desktop width collapse behavior
        (collapsed ? ' md:w-16' : ' md:w-64')
      }
      aria-hidden={!mobileOpen && typeof window !== 'undefined' && window.innerWidth < 768}
    >
      <div className="flex items-center justify-between gap-2 p-3 border-b border-gray-100">
        <Link to="/" className="text-malkaBlue font-bold truncate" title="Malka Money">
          <span className="hidden md:inline">{collapsed ? 'MM' : 'Malka Money'}</span>
          <span className="md:hidden">Malka Money</span>
        </Link>
        <div className="flex items-center gap-1">
          {/* Desktop collapse toggle */}
          <button
            aria-label={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
            className="hidden md:inline-flex text-gray-600 hover:text-gray-900 p-1 rounded hover:bg-gray-100"
            onClick={() => setCollapsed(c => !c)}
            title={collapsed ? 'Expand' : 'Collapse'}
          >
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-5 h-5">
              <path fillRule="evenodd" d="M3.75 6.75a.75.75 0 0 1 .75-.75h15a.75.75 0 0 1 0 1.5h-15a.75.75 0 0 1-.75-.75Zm0 5.25a.75.75 0 0 1 .75-.75h15a.75.75 0 0 1 0 1.5h-15a.75.75 0 0 1-.75-.75Zm0 5.25a.75.75 0 0 1 .75-.75h15a.75.75 0 0 1 0 1.5h-15a.75.75 0 0 1-.75-.75Z" clipRule="evenodd" />
            </svg>
          </button>
          {/* Mobile close */}
          <button
            aria-label="Close sidebar"
            className="md:hidden inline-flex text-gray-600 hover:text-gray-900 p-1 rounded hover:bg-gray-100"
            onClick={onMobileClose}
            title="Close"
          >
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-5 h-5">
              <path fillRule="evenodd" d="M6.225 4.811a.75.75 0 0 1 1.06 0L12 9.525l4.715-4.714a.75.75 0 1 1 1.06 1.06L13.06 10.586l4.715 4.714a.75.75 0 1 1-1.06 1.06L12 11.646l-4.715 4.714a.75.75 0 1 1-1.06-1.06l4.714-4.714-4.714-4.715a.75.75 0 0 1 0-1.06Z" clipRule="evenodd" />
            </svg>
          </button>
        </div>
      </div>

      <nav className="flex-1 overflow-y-auto py-2">
        <ul className="space-y-1">
          {items.map((item, idx) => {
            const active = location.pathname === item.to || (item.to !== '/' && location.pathname.startsWith(item.to))
            return (
              <li key={item.to}>
                <Link
                  to={item.to}
                  ref={idx === 0 ? firstLinkRef : undefined}
                  className={
                    'flex items-center gap-3 px-3 py-2 rounded-md transition-colors ' +
                    (active ? 'bg-malkaBlue/10 text-malkaBlue font-medium' : 'text-gray-700 hover:bg-gray-100')
                  }
                  title={item.label}
                >
                  {/* Placeholder icon - small dot; you can swap with real icons later */
                  /* On desktop collapsed, still show the dot; on mobile, always show labels */}
                  <span className="w-2 h-2 rounded-full bg-current"></span>
                  <span className={'truncate ' + (collapsed ? 'hidden md:inline' : '')}>{item.label}</span>
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
          <span className={'truncate ' + (collapsed ? 'hidden md:inline' : '')}>Logout</span>
        </button>
      </div>
    </aside>
  )
}
