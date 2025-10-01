import React, { useMemo, useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useAuth } from '../components/AuthContext'

export default function Register() {
  const { register: doRegister } = useAuth()
  const [form, setForm] = useState({
    email: '', password: '', full_name: '',
    dob: '', phone: '', base_currency: 'USD',
    address_line1: '', address_line2: '', city: '', state: '', postal_code: '', country: ''
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const navigate = useNavigate()

  const submit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
  const { email, password, full_name, ...extra } = form
  await doRegister(email, password, full_name, extra)
      // After basic register+login, update profile additional fields
      // Note: register endpoint already captures most, but this covers any missed
      navigate('/')
    } catch (err) {
      setError(err?.response?.data?.detail || 'Registration failed')
    } finally {
      setLoading(false)
    }
  }

  const Input = useMemo(() => function Input({ label, ...props }) {
    return (
      <label className="block">
        <div className="text-sm text-gray-600 mb-1">{label}</div>
        <input className="w-full border p-2 rounded" {...props} />
      </label>
    )
  }, [])

  return (
    <div className="max-w-2xl mx-auto mt-8 bg-white p-6 rounded shadow">
      <h1 className="text-2xl font-bold mb-4">Create your account</h1>
      <form onSubmit={submit} className="grid grid-cols-1 md:grid-cols-2 gap-3">
        <Input label="Email" value={form.email} onChange={e=>setForm({...form, email:e.target.value})} required />
        <Input label="Password" type="password" value={form.password} onChange={e=>setForm({...form, password:e.target.value})} required />
        <Input label="Full name" value={form.full_name} onChange={e=>setForm({...form, full_name:e.target.value})} />
        <Input label="Date of birth" type="date" value={form.dob} onChange={e=>setForm({...form, dob:e.target.value})} />
        <Input label="Phone" value={form.phone} onChange={e=>setForm({...form, phone:e.target.value})} />
        <Input label="Base currency" value={form.base_currency} onChange={e=>setForm({...form, base_currency:e.target.value})} />
        <Input label="Address line 1" value={form.address_line1} onChange={e=>setForm({...form, address_line1:e.target.value})} />
        <Input label="Address line 2" value={form.address_line2} onChange={e=>setForm({...form, address_line2:e.target.value})} />
        <Input label="City" value={form.city} onChange={e=>setForm({...form, city:e.target.value})} />
        <Input label="State/Province" value={form.state} onChange={e=>setForm({...form, state:e.target.value})} />
        <Input label="Postal code" value={form.postal_code} onChange={e=>setForm({...form, postal_code:e.target.value})} />
        <Input label="Country" value={form.country} onChange={e=>setForm({...form, country:e.target.value})} />

        {error && <div className="text-red-600 col-span-2">{error}</div>}
        <div className="col-span-2 flex items-center justify-between mt-2">
          <button disabled={loading} className="bg-jewishBlue text-white px-4 py-2 rounded">{loading ? 'Please wait…' : 'Create account'}</button>
          <Link to="/login" className="text-sm text-gray-600">Already have an account? Login</Link>
        </div>
      </form>
    </div>
  )
}
