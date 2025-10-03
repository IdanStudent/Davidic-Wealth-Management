import React, { createContext, useContext, useEffect, useMemo, useRef, useState } from 'react'
import axios from 'axios'

const AuthCtx = createContext(null)

export function AuthProvider({ children }) {
  const [token, setToken] = useState(localStorage.getItem('token') || '')
  const [me, setMe] = useState(null)

  useEffect(() => {
    if (!token) { setMe(null); return }
    api.get('/utils/me')
      .then(res => setMe(res.data))
      .catch(() => setMe(null))
  }, [token])

  const login = async (email, password, opts = {}) => {
    const payload = { email, password }
    if (opts.otp) payload.otp = opts.otp
    if (opts.recovery) payload.recovery = opts.recovery
    const res = await api.post('/auth/login', payload)
    const t = res.data.access_token.replace(/^Bearer\s+/i, '')
    setToken(t)
    localStorage.setItem('token', t)
    api.defaults.headers.Authorization = `Bearer ${t}`
  }

  const register = async (email, password, full_name='', extra={}) => {
    await api.post('/auth/register', { email, password, full_name, ...extra })
    await login(email, password)
  }

  const logout = () => {
    setToken('')
    localStorage.removeItem('token')
  }

  const api = useMemo(() => axios.create({ baseURL: '/api' }), [])
  const tokenRef = useRef(token)
  useEffect(() => {
    tokenRef.current = token
    if (token) api.defaults.headers.Authorization = `Bearer ${token}`
    else delete api.defaults.headers.Authorization
  }, [token, api])
  useEffect(() => {
    const id = api.interceptors.request.use(config => {
      if (tokenRef.current) config.headers.Authorization = `Bearer ${tokenRef.current}`
      return config
    })
    return () => api.interceptors.request.eject(id)
  }, [api])

  return (
    <AuthCtx.Provider value={{ token, me, login, register, logout, api }}>
      {children}
    </AuthCtx.Provider>
  )
}

export function useAuth() {
  return useContext(AuthCtx)
}
