import React, { useEffect, useState } from 'react'
import { useAuth } from '../components/AuthContext'

export default function Accounts() {
  const { api } = useAuth()
  const [accounts, setAccounts] = useState([])
  const [form, setForm] = useState({ name: '', type: 'Cash', opening_balance: '', is_liability: false })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const load = async () => {
    setError('')
    try {
      const res = await api.get('/accounts/')
      setAccounts(res.data)
    } catch (e) {
      setError(e?.response?.data?.detail || 'Failed to load accounts')
    }
  }
  useEffect(() => { load() }, [])

  const submit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    try {
      const payload = {
        ...form,
        opening_balance: form.opening_balance === '' ? 0 : parseFloat(form.opening_balance)
      }
      await api.post('/accounts/', payload)
      setForm({ name: '', type: 'Cash', opening_balance: '', is_liability: false })
      await load()
    } catch (e) {
      setError(e?.response?.data?.detail || 'Failed to create account')
    } finally {
      setLoading(false)
    }
  }

  const remove = async (id) => {
    setError('')
    try {
      await api.delete(`/accounts/${id}`)
      await load()
    } catch (e) {
      setError(e?.response?.data?.detail || 'Failed to delete account')
    }
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      <form onSubmit={submit} className="bg-white p-4 rounded shadow space-y-3">
        <h2 className="font-semibold">Add Account</h2>
        <input className="w-full border p-2" placeholder="Name" value={form.name} onChange={e=>setForm({...form, name:e.target.value})} />
        <select className="w-full border p-2" value={form.type} onChange={e=>setForm({...form, type:e.target.value})}>
          {['Cash','Savings','Credit Card','Loan','Investment'].map(t=> <option key={t}>{t}</option>)}
        </select>
        <input className="w-full border p-2" type="number" step="0.01" placeholder="Opening Balance" value={form.opening_balance} onChange={e=>setForm({...form, opening_balance:e.target.value})} />
  <label className="flex items-center gap-2"><input type="checkbox" checked={form.is_liability} onChange={e=>setForm({...form, is_liability:e.target.checked})} /> Liability</label>
        {error && <div className="text-sm text-red-600">{error}</div>}
        <button disabled={loading} className="bg-jewishBlue text-white px-4 py-2 rounded">{loading ? 'Please wait…' : 'Save'}</button>
      </form>
      <div className="bg-white p-4 rounded shadow">
        <h2 className="font-semibold mb-2">Accounts</h2>
        <ul className="space-y-2">
          {accounts.map(a => (
            <li key={a.id} className="flex justify-between items-center border p-2 rounded">
              <div>
                <div className="font-semibold">{a.name} <span className="text-sm text-gray-600">${(a.balance||0).toFixed(2)}</span></div>
                <div className="text-sm text-gray-500">{a.type} {a.is_liability ? '(Liability)' : ''}</div>
              </div>
              <button onClick={()=>remove(a.id)} className="text-red-600">Delete</button>
            </li>
          ))}
        </ul>
      </div>
    </div>
  )
}
