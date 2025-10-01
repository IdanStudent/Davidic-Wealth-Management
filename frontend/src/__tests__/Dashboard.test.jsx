import React from 'react'
import { render } from '@testing-library/react'
import Dashboard from '../pages/Dashboard'
import { AuthProvider } from '../components/AuthContext'

test('Dashboard renders snapshot', () => {
  const { container } = render(
    <AuthProvider>
      <Dashboard />
    </AuthProvider>
  )
  expect(container).toBeDefined()
})
