import React, { useEffect, useState } from 'react'
import { useAuth } from '../components/AuthContext'

export default function Settings() {
  const { api, me } = useAuth()
  const [tab, setTab] = useState('profile')

  // Profile
  const [profile, setProfile] = useState({
    full_name: me?.full_name || '',
    dob: me?.dob || '',
    phone: me?.phone || '',
    base_currency: me?.base_currency || 'USD',
    address_line1: me?.address_line1 || '',
    address_line2: me?.address_line2 || '',
    city: me?.city || '',
    state: me?.state || '',
    postal_code: me?.postal_code || '',
    country: me?.country || '',
  })

  // Email
  const [newEmail, setNewEmail] = useState(me?.email || '')
  const [emailPassword, setEmailPassword] = useState('')

  // Password
  const [pwd, setPwd] = useState({ current: '', next: '', confirm: '' })

  // Connected accounts (placeholder)
  const [connections, setConnections] = useState([])
  const [newConn, setNewConn] = useState('google')

  // Security (Shabbat, location, Maaser)
  const [shabbat, setShabbat] = useState(me?.shabbat_mode ?? true)
  const [lat, setLat] = useState(me?.lat ?? 31.778)
  const [lon, setLon] = useState(me?.lon ?? 35.235)
  const [maaserPct, setMaaserPct] = useState(me?.maaser_pct ?? 0.1)
  const [maaserOptIn, setMaaserOptIn] = useState((me?.maaser_pct ?? 0.1) > 0)

  // 2FA
  const [twofa, setTwofa] = useState({ enabled: false, secret: null, provisioning_uri: null, qr_b64: null })
  const [twofaCodes, setTwofaCodes] = useState([])
  const [twofaCodeInput, setTwofaCodeInput] = useState('')

  useEffect(() => {
    // Rehydrate from me when it changes
    setProfile(p => ({
      ...p,
      full_name: me?.full_name || '',
      dob: me?.dob || '',
      phone: me?.phone || '',
      base_currency: me?.base_currency || 'USD',
      address_line1: me?.address_line1 || '',
      address_line2: me?.address_line2 || '',
      city: me?.city || '',
      state: me?.state || '',
      postal_code: me?.postal_code || '',
      country: me?.country || '',
    }))
    setNewEmail(me?.email || '')
    setShabbat(me?.shabbat_mode ?? true)
    setLat(me?.lat ?? 31.778)
    setLon(me?.lon ?? 35.235)
    setMaaserPct(me?.maaser_pct ?? 0.1)
    setMaaserOptIn((me?.maaser_pct ?? 0.1) > 0)
  }, [me])

  useEffect(() => {
    // Load 2FA status
    api.get('/utils/2fa').then(res => setTwofa(res.data)).catch(() => {})
    api.get('/connections/').then(res => setConnections(res.data)).catch(()=>{})
  }, [api])

  const saveProfile = async () => {
    await api.post('/utils/profile', profile)
    alert('Profile updated')
  }

  const emailValid = /.+@.+\..+/.test(newEmail)
  const passwordStrong = (v) => v.length >= 8 && /[A-Za-z]/.test(v) && /\d/.test(v)

  const saveEmail = async () => {
    if (!emailValid) { alert('Please enter a valid email'); return }
    if (!emailPassword) { alert('Please enter your current password'); return }
    await api.post('/utils/email', { email: newEmail, current_password: emailPassword })
    alert('Email updated')
    setEmailPassword('')
  }

  const savePassword = async () => {
    if (pwd.next !== pwd.confirm) { alert('Passwords do not match'); return }
    if (!passwordStrong(pwd.next)) { alert('Password must be 8+ chars with letters and numbers'); return }
    await api.post('/utils/password', { current_password: pwd.current, new_password: pwd.next })
    alert('Password changed')
    setPwd({ current: '', next: '', confirm: '' })
  }

  const saveSecurity = async () => {
    await api.post('/utils/settings', null, { params: { shabbat_mode: shabbat, lat, lon } })
    await api.post('/utils/maaser_settings', { maaser_pct: parseFloat(maaserPct), maaser_opt_in: !!maaserOptIn })
    alert('Security settings saved')
  }

  const toggle2FA = async (enable) => {
    const r = await api.post('/utils/2fa', { enable })
    // If secret and recovery are returned (first step), show them and keep enabled false until verified
    if (r.data && r.data.secret) {
      setTwofa({ enabled: false, secret: r.data.secret, provisioning_uri: r.data.provisioning_uri || null, qr_b64: r.data.qr_b64 || null })
      setTwofaCodes(r.data.recovery_plain || [])
      return
    }
    const res = await api.get('/utils/2fa')
    setTwofa(res.data)
  }

  return (
    <div className="bg-white p-4 rounded shadow max-w-3xl">
      <h2 className="font-semibold text-xl mb-3">Settings</h2>
      <div className="flex gap-2 mb-4 overflow-x-auto">
        {['profile','email','password','connections','security','2fa'].map(t => (
          <button key={t} onClick={()=>setTab(t)} className={(tab===t?'bg-malkaBlue text-white':'bg-gray-100 text-gray-800')+" px-3 py-1 rounded"}>
            {t[0].toUpperCase()+t.slice(1)}
          </button>
        ))}
      </div>

      {tab==='profile' && (
        <div className="grid grid-cols-2 gap-3">
          <Input label="Full Name" value={profile.full_name} onChange={v=>setProfile({...profile, full_name:v})} />
          <Input label="DOB (YYYY-MM-DD)" value={profile.dob} onChange={v=>setProfile({...profile, dob:v})} />
          <Input label="Phone" value={profile.phone} onChange={v=>setProfile({...profile, phone:v})} />
          <Input label="Base Currency" value={profile.base_currency} onChange={v=>setProfile({...profile, base_currency:v})} />
          <Input label="Address Line 1" value={profile.address_line1} onChange={v=>setProfile({...profile, address_line1:v})} className="col-span-2" />
          <Input label="Address Line 2" value={profile.address_line2} onChange={v=>setProfile({...profile, address_line2:v})} className="col-span-2" />
          <Input label="City" value={profile.city} onChange={v=>setProfile({...profile, city:v})} />
          <Input label="State/Province" value={profile.state} onChange={v=>setProfile({...profile, state:v})} />
          <Input label="Postal code" value={profile.postal_code} onChange={v=>setProfile({...profile, postal_code:v})} />
          <Input label="Country" value={profile.country} onChange={v=>setProfile({...profile, country:v})} />
          <div className="col-span-2"><button onClick={saveProfile} className="bg-malkaBlue text-white px-4 py-2 rounded">Save</button></div>
        </div>
      )}

      {tab==='email' && (
        <div className="space-y-3 max-w-md">
          <Input label="New Email" value={newEmail} onChange={setNewEmail} />
          <Input label="Current Password" type="password" value={emailPassword} onChange={setEmailPassword} />
          <button onClick={saveEmail} className="bg-malkaBlue text-white px-4 py-2 rounded">Update Email</button>
        </div>
      )}

      {tab==='password' && (
        <div className="space-y-3 max-w-md">
          <Input label="Current Password" type="password" value={pwd.current} onChange={v=>setPwd({...pwd, current:v})} />
          <Input label="New Password" type="password" value={pwd.next} onChange={v=>setPwd({...pwd, next:v})} />
          <Input label="Confirm New Password" type="password" value={pwd.confirm} onChange={v=>setPwd({...pwd, confirm:v})} />
          <button onClick={savePassword} className="bg-malkaBlue text-white px-4 py-2 rounded">Change Password</button>
        </div>
      )}

      {tab==='connections' && (
        <div className="space-y-3">
          <div className="flex gap-2 items-center">
            <select className="border p-2" value={newConn} onChange={e=>setNewConn(e.target.value)}>
              <option value="google">Google</option>
              <option value="microsoft">Microsoft</option>
              <option value="plaid">Plaid</option>
            </select>
            <button className="bg-malkaBlue text-white px-3 py-2 rounded" onClick={async()=>{
              await api.post('/connections/', { provider: newConn })
              const res = await api.get('/connections/')
              setConnections(res.data)
            }}>Add connection</button>
          </div>
          <ul className="divide-y">
            {connections.map(c => (
              <li key={c.id} className="py-2 flex items-center justify-between">
                <div>
                  <div className="font-medium capitalize">{c.provider}</div>
                  <div className="text-sm text-gray-500">{c.status}</div>
                </div>
                <button className="text-red-600" onClick={async()=>{
                  await api.delete(`/connections/${c.id}`)
                  setConnections(connections.filter(x=>x.id!==c.id))
                }}>Remove</button>
              </li>
            ))}
          </ul>
        </div>
      )}

      {tab==='security' && (
        <div className="space-y-3 max-w-md">
          <label className="flex items-center gap-2">
            <input type="checkbox" checked={shabbat} onChange={e=>setShabbat(e.target.checked)} /> Shabbat Mode
          </label>
          <div className="flex gap-2">
            <input className="border p-2 flex-1" type="number" step="0.001" value={lat} onChange={e=>setLat(parseFloat(e.target.value))} placeholder="Latitude" />
            <input className="border p-2 flex-1" type="number" step="0.001" value={lon} onChange={e=>setLon(parseFloat(e.target.value))} placeholder="Longitude" />
          </div>
          <div className="flex items-center gap-2">
            <input type="checkbox" checked={maaserOptIn} onChange={e=>setMaaserOptIn(e.target.checked)} /> Auto Maaser
          </div>
          {maaserOptIn && (
            <div className="flex gap-2">
              <input className="border p-2" type="number" step="0.01" value={maaserPct} onChange={e=>setMaaserPct(e.target.value)} />
              <div className="text-sm text-gray-600">Maaser % (e.g. 0.10 = 10%)</div>
            </div>
          )}
          <button onClick={saveSecurity} className="bg-malkaBlue text-white px-4 py-2 rounded">Save</button>
        </div>
      )}

      {tab==='2fa' && (
        <div className="space-y-3 max-w-md">
          <div className="flex items-center justify-between">
            <div>Two-Factor Authentication</div>
            <span className={twofa.enabled? 'text-green-600':'text-gray-500'}>{twofa.enabled? 'Enabled':'Disabled'}</span>
          </div>
          {!twofa.enabled && twofa.secret && (
            <div className="space-y-2">
              <div className="text-sm text-gray-700">Your 2FA setup key: <code>{twofa.secret}</code></div>
              {twofa.qr_b64 && (
                <div className="flex flex-col items-center gap-2">
                  <img alt="2FA QR" src={`data:image/png;base64,${twofa.qr_b64}`} className="w-40 h-40" />
                  <a href={twofa.provisioning_uri} className="text-xs text-blue-600 underline" target="_blank" rel="noreferrer">Open in authenticator</a>
                </div>
              )}
              {twofaCodes.length>0 && (
                <div className="text-sm text-gray-700">
                  Recovery codes (store safely):
                  <ul className="list-disc ml-5">
                    {twofaCodes.map((c,i)=>(<li key={i}><code>{c}</code></li>))}
                  </ul>
                </div>
              )}
              <div className="flex gap-2 items-center">
                <input className="border p-2" placeholder="Enter code to verify" value={twofaCodeInput} onChange={e=>setTwofaCodeInput(e.target.value)} />
                <button className="bg-malkaBlue text-white px-3 py-2 rounded" onClick={async()=>{
                  await api.post('/utils/2fa', { enable: true, code: twofaCodeInput })
                  const status = await api.get('/utils/2fa')
                  setTwofa(status.data)
                  setTwofaCodes([]); setTwofaCodeInput('')
                }}>Confirm</button>
              </div>
            </div>
          )}
          <div className="flex gap-2">
            <button onClick={()=>toggle2FA(!twofa.enabled)} className="bg-malkaBlue text-white px-4 py-2 rounded">{twofa.enabled? 'Disable 2FA':'Enable 2FA'}</button>
            {!twofa.enabled && (
              <button onClick={()=>toggle2FA(true)} className="px-4 py-2 border rounded">Generate Secret</button>
            )}
          </div>
          <div className="text-xs text-gray-500">Use an authenticator app with the setup key. Recovery codes are shown once on enable.</div>
        </div>
      )}
    </div>
  )
}

function Input({ label, value, onChange, type='text', className='' }) {
  return (
    <label className={`text-sm ${className}`}>
      <div className="text-gray-600 mb-1">{label}</div>
      <input className="border p-2 w-full" value={value} type={type} onChange={e=>onChange(e.target.value)} />
    </label>
  )
}
