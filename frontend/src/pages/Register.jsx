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
  const [confirmPassword, setConfirmPassword] = useState('')
  const [showPwd, setShowPwd] = useState(false)
  const [showOptional, setShowOptional] = useState(false)
  const [agreeTerms, setAgreeTerms] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [fieldErrors, setFieldErrors] = useState({})
  const navigate = useNavigate()

  const strength = useMemo(() => passwordStrength(form.password), [form.password])

  const submit = async (e) => {
    e.preventDefault()
    setError('')
    setFieldErrors({})
    setLoading(true)
    try {
      // basic client-side validation
      const errs = {}
      if (!form.email) errs.email = 'Email is required'
      if (!form.password) errs.password = 'Password is required'
      if (form.password && form.password.length < 8) errs.password = 'Use at least 8 characters'
      if (confirmPassword !== form.password) errs.confirm = 'Passwords do not match'
      if (!agreeTerms) errs.terms = 'You must agree to the terms'
      if (Object.keys(errs).length) {
        setFieldErrors(errs)
        throw new Error('Validation failed')
      }
      const { email, password, full_name, ...extra } = form
      await doRegister(email, password, full_name, extra)
      // After basic register+login, update profile additional fields
      // Note: register endpoint already captures most, but this covers any missed
      navigate('/')
    } catch (err) {
      // Prefer API detail when present
      const apiDetail = err?.response?.data?.detail
      if (apiDetail) setError(apiDetail)
      else if (err.message === 'Validation failed') setError('Please fix the highlighted fields')
      else setError('Registration failed')
    } finally {
      setLoading(false)
    }
  }

  const Input = useMemo(() => function Input({ label, error, ...props }) {
    return (
      <label className="block">
        <div className="text-sm text-gray-600 mb-1">{label}</div>
        <input className={`w-full border p-2 rounded ${error ? 'border-red-500' : 'border-gray-300'}`} {...props} />
        {error && <div className="text-xs text-red-600 mt-1">{error}</div>}
      </label>
    )
  }, [])

  return (
    <div className="max-w-2xl mx-auto mt-8 bg-white p-6 rounded shadow">
      <h1 className="text-2xl font-bold mb-4">Create your account</h1>
      <form onSubmit={submit} className="grid grid-cols-1 md:grid-cols-2 gap-3">
        <Input label="Email" type="email" value={form.email} onChange={e=>setForm({...form, email:e.target.value})} error={fieldErrors.email} required />

        {/* Passwords with visibility toggle */}
        <label className="block">
          <div className="text-sm text-gray-600 mb-1">Password</div>
          <div className={`relative`}>
            <input className={`w-full border p-2 rounded pr-20 ${fieldErrors.password ? 'border-red-500' : 'border-gray-300'}`} type={showPwd? 'text':'password'} value={form.password} onChange={e=>setForm({...form, password:e.target.value})} required />
            <button type="button" onClick={()=>setShowPwd(v=>!v)} className="absolute right-2 top-1/2 -translate-y-1/2 text-sm text-gray-600 hover:text-gray-800">
              {showPwd ? 'Hide' : 'Show'}
            </button>
          </div>
          {fieldErrors.password && <div className="text-xs text-red-600 mt-1">{fieldErrors.password}</div>}
          {/* Strength meter */}
          <div className="mt-2 flex gap-1" aria-hidden>
            {[0,1,2,3,4].map(i=> (
              <div key={i} className={`h-1 flex-1 rounded ${i < strength.score ? strength.color : 'bg-gray-200'}`} />
            ))}
          </div>
          <div className="text-xs text-gray-500 mt-1">{strength.label}</div>
        </label>

        <Input label="Confirm password" type={showPwd? 'text':'password'} value={confirmPassword} onChange={e=>setConfirmPassword(e.target.value)} error={fieldErrors.confirm} required />

        <Input label="Full name" value={form.full_name} onChange={e=>setForm({...form, full_name:e.target.value})} />

        {/* Optional section toggle */}
        <div className="col-span-2">
          <button type="button" onClick={()=>setShowOptional(v=>!v)} className="text-sm text-blue-600 underline">
            {showOptional ? 'Hide optional details' : 'Add optional details'}
          </button>
        </div>

        {showOptional && (
          <>
            <Input label="Date of birth" type="date" value={form.dob} onChange={e=>setForm({...form, dob:e.target.value})} />
            <Input label="Phone" value={form.phone} onChange={e=>setForm({...form, phone:e.target.value})} />

            {/* Currency select */}
            <label className="block">
              <div className="text-sm text-gray-600 mb-1">Base currency</div>
              <select className="w-full border p-2 rounded" value={form.base_currency} onChange={e=>setForm({...form, base_currency:e.target.value})}>
                {['USD','ILS','EUR','GBP','CAD','AUD'].map(c => (
                  <option key={c} value={c}>{c}</option>
                ))}
              </select>
            </label>

            <Input label="Address line 1" value={form.address_line1} onChange={e=>setForm({...form, address_line1:e.target.value})} />
            <Input label="Address line 2" value={form.address_line2} onChange={e=>setForm({...form, address_line2:e.target.value})} />
            <Input label="City" value={form.city} onChange={e=>setForm({...form, city:e.target.value})} />
            <Input label="State/Province" value={form.state} onChange={e=>setForm({...form, state:e.target.value})} />
            <Input label="Postal code" value={form.postal_code} onChange={e=>setForm({...form, postal_code:e.target.value})} />
            <Input label="Country" value={form.country} onChange={e=>setForm({...form, country:e.target.value})} />
          </>
        )}

        {/* Terms */}
        <label className="col-span-2 flex items-center gap-2 text-sm">
          <input type="checkbox" checked={agreeTerms} onChange={e=>setAgreeTerms(e.target.checked)} />
          <span>I agree to the <a className="underline" href="#" onClick={(e)=>e.preventDefault()}>Terms</a> and <a className="underline" href="#" onClick={(e)=>e.preventDefault()}>Privacy Policy</a>.</span>
        </label>
        {fieldErrors.terms && <div className="text-xs text-red-600 col-span-2 -mt-2">{fieldErrors.terms}</div>}

        {error && <div className="text-red-600 col-span-2">{error}</div>}
        <div className="col-span-2 flex items-center justify-between mt-2">
          <button disabled={loading} className="bg-malkaBlue text-white px-4 py-2 rounded">{loading ? 'Please wait…' : 'Create account'}</button>
          <Link to="/login" className="text-sm text-gray-600">Already have an account? Login</Link>
        </div>
      </form>
    </div>
  )
}

function passwordStrength(pwd) {
  let score = 0
  if (!pwd) return { score, label: 'Enter a password', color: 'bg-gray-200' }
  const lengthOK = pwd.length >= 8
  const lower = /[a-z]/.test(pwd)
  const upper = /[A-Z]/.test(pwd)
  const digit = /[0-9]/.test(pwd)
  const special = /[^A-Za-z0-9]/.test(pwd)
  ;[lengthOK, lower, upper, digit, special].forEach(ok => { if (ok) score++ })
  const labels = ['Very weak','Weak','Fair','Good','Strong','Strong']
  const colors = ['bg-red-300','bg-red-400','bg-yellow-400','bg-green-400','bg-green-500','bg-green-600']
  return { score, label: labels[score] || 'Very weak', color: colors[score] || 'bg-gray-200' }
}
