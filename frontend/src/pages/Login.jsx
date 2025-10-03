import React, { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useAuth } from '../components/AuthContext'

export default function Login() {
  const { login, register } = useAuth()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [needs2FA, setNeeds2FA] = useState(false)
  const [otp, setOtp] = useState('')
  const [recovery, setRecovery] = useState('')
  const navigate = useNavigate()

  const submit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    try {
      await login(email, password, needs2FA ? { otp, recovery } : {})
      navigate('/')
    } catch (err) {
      const detail = err?.response?.data?.detail
      if (detail === '2FA required') {
        setNeeds2FA(true)
        setError('Two-factor code required. Enter OTP or a recovery code.')
      } else {
        setError(detail || 'Login failed')
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-sm mx-auto mt-12 bg-white p-6 rounded shadow">
      <h1 className="text-2xl font-bold mb-4">Login</h1>
      <form onSubmit={submit} className="space-y-3">
  <input className="w-full border p-2" value={email} onChange={e=>setEmail(e.target.value)} placeholder="Email or Username" />
        <input className="w-full border p-2" type="password" value={password} onChange={e=>setPassword(e.target.value)} placeholder="Password" />
        {needs2FA && (
          <div className="space-y-2">
            <input className="w-full border p-2" value={otp} onChange={e=>setOtp(e.target.value)} placeholder="Authenticator code (OTP)" />
            <div className="text-xs text-gray-500 text-center">or</div>
            <input className="w-full border p-2" value={recovery} onChange={e=>setRecovery(e.target.value)} placeholder="Recovery code" />
          </div>
        )}
        {error && <div className="text-red-600 text-sm">{error}</div>}
        <button disabled={loading} className="w-full bg-malkaBlue text-white py-2 rounded">{loading ? 'Please wait…' : 'Login'}</button>
        <Link to="/register" className="w-full inline-block text-center text-sm text-gray-600">Create an account</Link>
      </form>
    </div>
  )
}
