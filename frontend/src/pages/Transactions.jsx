import React, { useEffect, useState } from 'react'
import { useAuth } from '../components/AuthContext'

export default function Transactions() {
  const { api } = useAuth()
  const [transactions, setTransactions] = useState([])
  const [accounts, setAccounts] = useState([])
  const [form, setForm] = useState({ account_id: 0, category_id: null, date: new Date().toISOString().slice(0,10), amount: 0, note: '' })

  const load = async () => {
    const [tx, acc] = await Promise.all([
  api.get('/transactions/'),
  api.get('/accounts/')
    ])
    setTransactions(tx.data)
    setAccounts(acc.data)
    if (acc.data.length && !form.account_id) setForm(f=>({...f, account_id: acc.data[0].id}))
  }
  useEffect(() => { load() }, [])

  const submit = async (e) => {
    e.preventDefault()
  await api.post('/transactions/', { ...form, amount: parseFloat(form.amount) })
    setForm(f=>({...f, amount: 0, note: ''}))
    load()
  }

  const remove = async (id) => {
  await api.delete(`/transactions/${id}`)
    load()
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      <form onSubmit={submit} className="bg-white p-4 rounded shadow space-y-3">
        <h2 className="font-semibold">Add Transaction</h2>
        <select className="w-full border p-2" value={form.account_id} onChange={e=>setForm({...form, account_id: parseInt(e.target.value)})}>
          {accounts.map(a => <option key={a.id} value={a.id}>{a.name}</option>)}
        </select>
        <input className="w-full border p-2" type="date" value={form.date} onChange={e=>setForm({...form, date:e.target.value})} />
        <input className="w-full border p-2" type="number" step="0.01" value={form.amount} onChange={e=>setForm({...form, amount:e.target.value})} placeholder="Amount" />
        <input className="w-full border p-2" value={form.note} onChange={e=>setForm({...form, note:e.target.value})} placeholder="Note" />
        <button className="bg-jewishBlue text-white px-4 py-2 rounded">Save</button>
      </form>
      <div className="bg-white p-4 rounded shadow">
        <h2 className="font-semibold mb-2">Transactions</h2>
        <ul className="space-y-2">
          {transactions.map(t => (
            <li key={t.id} className="flex justify-between items-center border p-2 rounded">
              <div>
                <div className="font-semibold">{t.date}: ${t.amount.toFixed(2)}</div>
                <div className="text-sm text-gray-500">{t.note}</div>
              </div>
              <button onClick={()=>remove(t.id)} className="text-red-600">Delete</button>
            </li>
          ))}
        </ul>
      </div>
    </div>
  )
}
