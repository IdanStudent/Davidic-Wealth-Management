import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../components/AuthContext'

export default function Login() {
  const { login, register } = useAuth()
  const [email, setEmail] = useState('test@example.com')
  const [password, setPassword] = useState('test1234')
  const [mode, setMode] = useState('login')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const navigate = useNavigate()

  const submit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    try {
      if (mode === 'login') await login(email, password)
      else await register(email, password)
      navigate('/')
    } catch (err) {
      setError(err?.response?.data?.detail || 'Login failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-sm mx-auto mt-12 bg-white p-6 rounded shadow">
      <h1 className="text-2xl font-bold mb-4">{mode === 'login' ? 'Login' : 'Register'}</h1>
      <form onSubmit={submit} className="space-y-3">
        <input className="w-full border p-2" value={email} onChange={e=>setEmail(e.target.value)} placeholder="Email" />
        <input className="w-full border p-2" type="password" value={password} onChange={e=>setPassword(e.target.value)} placeholder="Password" />
        {error && <div className="text-red-600 text-sm">{error}</div>}
        <button disabled={loading} className="w-full bg-jewishBlue text-white py-2 rounded">{loading ? 'Please wait…' : (mode === 'login' ? 'Login' : 'Create Account')}</button>
        <button type="button" className="w-full text-sm text-gray-600" onClick={()=>setMode(mode==='login'?'register':'login')}>
          {mode==='login' ? 'Create an account' : 'Have an account? Login'}
        </button>
      </form>
    </div>
  )
}
