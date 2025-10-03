import React, { useEffect, useMemo, useRef, useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useAuth } from '../components/AuthContext'

// Phone utils: format as (XXX) XXX-XXXX while keeping digits internally when submitting
function digitsOnly(v) {
  return (v || '').replace(/\D/g, '').slice(0, 10)
}
function formatPhone(v) {
  const d = digitsOnly(v)
  if (d.length <= 3) return d
  if (d.length <= 6) return `(${d.slice(0,3)}) ${d.slice(3)}`
  return `(${d.slice(0,3)}) ${d.slice(3,6)}-${d.slice(6)}`
}

export default function Register() {
  const { register: doRegister, api } = useAuth()
  const [form, setForm] = useState({
    email: '', username: '', password: '',
    first_name: '', middle_initial: '', last_name: '',
    dob: '', phone: '', base_currency: 'USD',
    address_line1: '', address_line2: '', city: '', state: '', postal_code: '', country: ''
  })
  const [confirmPassword, setConfirmPassword] = useState('')
  const [showPwd, setShowPwd] = useState(false)
  const [agreeTerms, setAgreeTerms] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [fieldErrors, setFieldErrors] = useState({})
  const [addressQuery, setAddressQuery] = useState('')
  const [addressMsg, setAddressMsg] = useState('')
  const [suggestions, setSuggestions] = useState([])
  const [isSuggestLoading, setIsSuggestLoading] = useState(false)
  const [showSuggest, setShowSuggest] = useState(false)
  const [activeIdx, setActiveIdx] = useState(-1)
  const suggestRef = useRef(null)
  const navigate = useNavigate()

  const strength = useMemo(() => passwordStrength(form.password), [form.password])
  // Debounced suggestions targeting Address line 1 input
  useEffect(() => {
    if (!addressQuery || addressQuery.trim().length < 3) {
      setSuggestions([])
      setIsSuggestLoading(false)
      return
    }
    setIsSuggestLoading(true)
    const id = setTimeout(async () => {
      try {
        const res = await api.get('/utils/address_suggest', { params: { q: addressQuery, limit: 6 } })
        setSuggestions(res.data?.items || [])
      } catch (e) {
        setSuggestions([])
      } finally {
        setIsSuggestLoading(false)
      }
    }, 150)
    return () => clearTimeout(id)
  }, [addressQuery, api])

  const submit = async (e) => {
    e.preventDefault()
    setError('')
    setFieldErrors({})
    setLoading(true)
    try {
      // basic client-side validation
      const errs = {}
    if (!form.username || form.username.trim().length < 3) errs.username = 'Username is required (min 3)'
    else if (/\s/.test(form.username)) errs.username = 'Username cannot contain spaces'
    if (!form.email) errs.email = 'Email is required'
    else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) errs.email = 'Enter a valid email address'
      if (!form.first_name) errs.first_name = 'First name is required'
      if (!form.last_name) errs.last_name = 'Last name is required'
  if (!form.password) errs.password = 'Password is required'
  else if (/\s/.test(form.password)) errs.password = 'Password cannot contain spaces'
      if (form.password && form.password.length < 8) errs.password = 'Use at least 8 characters'
      if (confirmPassword !== form.password) errs.confirm = 'Passwords do not match'
      if (!form.dob) errs.dob = 'Date of birth is required'
  if (!form.phone) errs.phone = 'Phone number is required'
  else if (digitsOnly(form.phone).length !== 10) errs.phone = 'Enter a 10-digit phone number'
      if (!form.base_currency) errs.base_currency = 'Base currency is required'
      if (!form.address_line1) errs.address_line1 = 'Address line 1 is required'
      if (!form.city) errs.city = 'City is required'
      if (!form.state) errs.state = 'State/Province is required'
      if (!form.postal_code) errs.postal_code = 'Postal code is required'
      if (!form.country) errs.country = 'Country is required'
      if (!agreeTerms) errs.terms = 'You must agree to the terms'
      if (Object.keys(errs).length) {
        setFieldErrors(errs)
        throw new Error('Validation failed')
      }
      const full_name = `${form.first_name}${form.middle_initial? ' '+form.middle_initial+'.' : ''} ${form.last_name}`.trim()
      const { email, password, first_name, middle_initial, last_name, ...extra } = form
      // Normalize phone to digits-only when submitting
      if (extra.phone) extra.phone = digitsOnly(extra.phone)
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
        <Input label="Username" value={form.username} onChange={e=>setForm({...form, username:e.target.value})} error={fieldErrors.username} required />
        <Input label="Email" type="email" value={form.email} onChange={e=>setForm({...form, email:e.target.value})} error={fieldErrors.email} required />

        {/* Name fields: first, middle initial (small), last */}
        <Input label="First name" value={form.first_name} onChange={e=>setForm({...form, first_name:e.target.value})} error={fieldErrors.first_name} required />
        <div className="grid grid-cols-3 gap-2 md:col-span-1 col-span-1">
          <label className="block col-span-1">
            <div className="text-sm text-gray-600 mb-1">M. I (optional)</div>
            <input maxLength={1} className={`w-full border p-2 rounded ${fieldErrors.middle_initial ? 'border-red-500' : 'border-gray-300'}`} value={form.middle_initial} onChange={e=>setForm({...form, middle_initial:e.target.value.toUpperCase()})} />
          </label>
          <div className="col-span-2">
            <Input label="Last name" value={form.last_name} onChange={e=>setForm({...form, last_name:e.target.value})} error={fieldErrors.last_name} required />
          </div>
        </div>

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

        {/* Required details */}
        <Input label="Date of birth" type="date" value={form.dob} onChange={e=>setForm({...form, dob:e.target.value})} error={fieldErrors.dob} required />
        <label className="block">
          <div className="text-sm text-gray-600 mb-1">Phone</div>
          <input
            className={`w-full border p-2 rounded ${fieldErrors.phone ? 'border-red-500' : 'border-gray-300'}`}
            value={form.phone}
            inputMode="tel"
            maxLength={14}
            placeholder="(555) 123-4567"
            onChange={e=> setForm({...form, phone: formatPhone(e.target.value)})}
            required
          />
          {fieldErrors.phone && <div className="text-xs text-red-600 mt-1">{fieldErrors.phone}</div>}
        </label>
        <label className="block">
          <div className="text-sm text-gray-600 mb-1">Base currency</div>
          <select className={`w-full border p-2 rounded ${fieldErrors.base_currency ? 'border-red-500' : 'border-gray-300'}`} value={form.base_currency} onChange={e=>setForm({...form, base_currency:e.target.value})} required>
            {['USD','ILS','EUR','GBP','CAD','AUD'].map(c => (
              <option key={c} value={c}>{c}</option>
            ))}
          </select>
          {fieldErrors.base_currency && <div className="text-xs text-red-600 mt-1">{fieldErrors.base_currency}</div>}
        </label>

        {/* Address fields with inline suggestions for Address line 1 */}
        <div className="col-span-2 grid grid-cols-1 md:grid-cols-2 gap-3">
          <div className="relative">
            <div className="text-sm text-gray-600 mb-1">Address line 1</div>
            <input
              className={`w-full border p-2 rounded ${fieldErrors.address_line1 ? 'border-red-500' : 'border-gray-300'}`}
              placeholder="Street address, number"
              value={form.address_line1}
              onChange={e=>{
                const v = e.target.value
                setForm({...form, address_line1: v})
                setAddressQuery(v)
                setShowSuggest(true)
                setActiveIdx(-1)
              }}
              onFocus={()=>setShowSuggest(true)}
              onBlur={()=> setTimeout(()=>setShowSuggest(false), 120)}
              onKeyDown={(e)=>{
                if (!showSuggest || suggestions.length === 0) return
                if (e.key === 'ArrowDown') {
                  e.preventDefault()
                  setActiveIdx(i => (i + 1) % suggestions.length)
                } else if (e.key === 'ArrowUp') {
                  e.preventDefault()
                  setActiveIdx(i => (i - 1 + suggestions.length) % suggestions.length)
                } else if (e.key === 'Enter') {
                  if (activeIdx >= 0 && activeIdx < suggestions.length) {
                    const s = suggestions[activeIdx]
                    setForm(prev => ({
                      ...prev,
                      address_line1: s.address_line1 || prev.address_line1,
                      city: s.city || prev.city,
                      state: s.state || prev.state,
                      postal_code: s.postal_code || prev.postal_code,
                      country: s.country || prev.country,
                    }))
                    setAddressQuery(s.address_line1 || '')
                    setShowSuggest(false)
                  }
                } else if (e.key === 'Escape') {
                  setShowSuggest(false)
                }
              }}
              required
            />
            {/* Loading indicator */}
            {isSuggestLoading && showSuggest && (
              <div className="absolute right-2 top-1/2 -translate-y-1/2 text-xs text-gray-400">Loading…</div>
            )}
            {showSuggest && suggestions.length > 0 && (
              <div className="absolute z-10 mt-1 w-full bg-white border border-gray-200 rounded shadow max-h-56 overflow-auto">
                {suggestions.map((s, i) => {
                  const secondary = [s.city, s.state, s.postal_code, s.country].filter(Boolean).join(', ')
                  return (
                    <button
                      key={i}
                      type="button"
                      className={`w-full text-left px-3 py-2 hover:bg-gray-50 ${i===activeIdx ? 'bg-gray-100' : ''}`}
                      onMouseDown={(e)=>e.preventDefault()}
                      onMouseEnter={()=>setActiveIdx(i)}
                      onClick={()=>{
                        setForm(prev => ({
                          ...prev,
                          address_line1: s.address_line1 || prev.address_line1,
                          city: s.city || prev.city,
                          state: s.state || prev.state,
                          postal_code: s.postal_code || prev.postal_code,
                          country: s.country || prev.country,
                        }))
                        setAddressQuery(s.address_line1 || '')
                        setShowSuggest(false)
                      }}
                    >
                      <div className="font-medium">{s.address_line1 || s.label}</div>
                      {secondary && <div className="text-xs text-gray-600">{secondary}</div>}
                    </button>
                  )
                })}
              </div>
            )}
            {fieldErrors.address_line1 && <div className="text-xs text-red-600 mt-1">{fieldErrors.address_line1}</div>}
          </div>
          <Input label="Address line 2" value={form.address_line2} onChange={e=>setForm({...form, address_line2:e.target.value})} />
          <Input label="City" value={form.city} onChange={e=>setForm({...form, city:e.target.value})} error={fieldErrors.city} required />
          <Input label="State/Province" value={form.state} onChange={e=>setForm({...form, state:e.target.value})} error={fieldErrors.state} required />
          <Input label="Postal code" value={form.postal_code} onChange={e=>setForm({...form, postal_code:e.target.value})} error={fieldErrors.postal_code} required />
          <Input label="Country" value={form.country} onChange={e=>setForm({...form, country:e.target.value})} error={fieldErrors.country} required />
        </div>

        {/* no optional section */}

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
