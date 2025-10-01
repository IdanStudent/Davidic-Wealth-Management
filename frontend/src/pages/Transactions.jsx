import React, { useEffect, useState } from 'react'
import { useLocation } from 'react-router-dom'
import { useAuth } from '../components/AuthContext'

export default function Transactions() {
  const { api } = useAuth()
  const [transactions, setTransactions] = useState([])
  const [accounts, setAccounts] = useState([])
  const [categories, setCategories] = useState([])
  const location = useLocation()
  const params = new URLSearchParams(location.search)
  const initialAccountId = params.get('account_id') ? parseInt(params.get('account_id')) : 0
  const [form, setForm] = useState({ account_id: initialAccountId || 0, category_id: null, date: new Date().toISOString().slice(0,10), amount: 0, note: '' })
  const [isTransferMode, setIsTransferMode] = useState(false)
  const [toAccountId, setToAccountId] = useState(0)
  const [editingId, setEditingId] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const load = async () => {
    const [tx, acc, cats] = await Promise.all([
      api.get('/transactions/'),
      api.get('/accounts/'),
      api.get('/categories/')
    ])
    // if account filter present, filter transactions list
    let txs = tx.data
    if (initialAccountId) txs = txs.filter(t => t.account_id === initialAccountId)
  setTransactions(txs)
  setAccounts(acc.data)
  setCategories(cats.data)
    if (acc.data.length && !form.account_id) setForm(f=>({...f, account_id: acc.data[0].id}))
  }
  useEffect(() => { load() }, [])

  const submit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    try {
      if (isTransferMode) {
        if (!toAccountId) throw new Error('Choose a destination account')
        // always send positive magnitude for transfers
        if (editingId) {
          // editing a transfer: patch the single transaction
          await api.patch(`/transactions/${editingId}`, { ...form, amount: Math.abs(parseFloat(form.amount)) })
          setEditingId(null)
        } else {
          await api.post('/transactions/transfer', { from_account_id: form.account_id, to_account_id: toAccountId, amount: Math.abs(parseFloat(form.amount)), date: form.date, note: form.note })
        }
      } else {
        // send positive magnitude; backend will apply sign based on category type
        if (editingId) {
          await api.patch(`/transactions/${editingId}`, { ...form, amount: Math.abs(parseFloat(form.amount)) })
          setEditingId(null)
        } else {
          await api.post('/transactions/', { ...form, amount: Math.abs(parseFloat(form.amount)) })
        }
      }
      setForm(f=>({...f, amount: 0, note: ''}))
      setToAccountId(0)
      await load()
    } catch (e) {
      console.error('Transaction save error', e)
      const msg = e?.response?.data?.detail || e?.response?.data || e.message || 'Save failed'
      setError(typeof msg === 'string' ? msg : JSON.stringify(msg))
      // also show a user alert so it's obvious
      alert('Save failed: ' + (typeof msg === 'string' ? msg : JSON.stringify(msg)))
    } finally {
      setLoading(false)
    }
  }

  const startEdit = async (tx) => {
    // populate form
    setEditingId(tx.id)
    setIsTransferMode(!!tx.is_transfer)
    setForm({ account_id: tx.account_id, category_id: tx.category_id, date: tx.date, amount: Math.abs(tx.amount), note: tx.note || '' })
    if (tx.is_transfer) {
      setToAccountId(tx.counterparty_account_id || 0)
    }
  }

  const cancelEdit = () => {
    setEditingId(null)
    setIsTransferMode(false)
    setForm({ account_id: initialAccountId || (accounts[0]?.id||0), category_id: null, date: new Date().toISOString().slice(0,10), amount: 0, note: '' })
    setToAccountId(0)
  }

  const remove = async (id) => {
  await api.delete(`/transactions/${id}`)
    load()
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      <form onSubmit={submit} className="bg-white p-4 rounded shadow space-y-3">
        <h2 className="font-semibold">Add Transaction</h2>
        <div className="flex items-center gap-3">
          <label className="flex items-center gap-2"><input type="checkbox" checked={isTransferMode} onChange={e=>setIsTransferMode(e.target.checked)} /> Transfer</label>
        </div>
        <select className="w-full border p-2" value={form.account_id} onChange={e=>setForm({...form, account_id: parseInt(e.target.value)})}>
          {accounts.map(a => <option key={a.id} value={a.id}>{a.name}</option>)}
        </select>
        {isTransferMode ? (
          <select className="w-full border p-2" value={toAccountId} onChange={e=>setToAccountId(parseInt(e.target.value))}>
            <option value={0}>-- To account --</option>
            {accounts.filter(a=>a.id!==form.account_id).map(a => <option key={a.id} value={a.id}>{a.name}</option>)}
          </select>
        ) : (
          <div>
            <select className="w-full border p-2" value={form.category_id || ''} onChange={e=>setForm({...form, category_id: e.target.value ? parseInt(e.target.value) : null})}>
              <option value="">-- Category --</option>
              {categories.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
            </select>
            {form.category_id ? (() => {
              const sel = categories.find(x=>x.id===form.category_id)
              if (!sel) return null
              return (
                <div className="mt-1">
                  {sel.type === 'expense' ? <span className="text-xs px-2 py-0.5 bg-red-100 text-red-800 rounded">Expense → will subtract</span> : <span className="text-xs px-2 py-0.5 bg-green-100 text-green-800 rounded">Income → will add</span>}
                </div>
              )
            })() : null}
          </div>
        )}
        <input className="w-full border p-2" type="date" value={form.date} onChange={e=>setForm({...form, date:e.target.value})} />
        <div className="flex flex-col">
          <input aria-label="Amount" className="w-full border p-2" type="number" step="0.01" value={form.amount} onChange={e=>setForm({...form, amount:e.target.value})} placeholder="Amount (positive)" />
          <div className="text-xs text-gray-500 mt-1">Enter a positive amount — selected category determines whether it will add or subtract from the account.</div>
        </div>
        <input className="w-full border p-2" value={form.note} onChange={e=>setForm({...form, note:e.target.value})} placeholder="Note" />
        {error && <div className="text-sm text-red-600">{error}</div>}
        <div className="flex items-center gap-2">
          <button disabled={loading} className="bg-jewishBlue text-white px-4 py-2 rounded">{loading ? 'Saving…' : (editingId ? 'Update' : 'Save')}</button>
          {editingId ? <button type="button" onClick={cancelEdit} className="px-3 py-2 border rounded">Cancel</button> : null}
        </div>
      </form>
      <div className="bg-white p-4 rounded shadow">
        <div className="flex items-center justify-between mb-2">
          <h2 className="font-semibold">Transactions</h2>
          {initialAccountId ? <a href="/transactions" className="text-sm text-jewishBlue">Show all</a> : null}
        </div>
        <ul className="space-y-2">
          {transactions.map(t => (
            <li key={t.id} className="flex justify-between items-center border p-2 rounded">
              <div>
                <div className="font-semibold">{t.date}: <span className={t.amount >= 0 ? 'text-green-600' : 'text-red-600'}>${Math.abs(t.amount).toFixed(2)}</span> {t.is_transfer ? <span className="text-xs ml-2 px-2 py-0.5 bg-yellow-100 text-yellow-800 rounded">Transfer</span> : null}</div>
                <div className="text-sm text-gray-600">{accounts.find(a=>a.id===t.account_id)?.name || ''} {t.category_id ? `• ${categories.find(c=>c.id===t.category_id)?.name||''}` : ''}</div>
                <div className="text-sm text-gray-500">{t.note}</div>
              </div>
              <div className="flex items-center gap-2">
                <button onClick={()=>startEdit(t)} className="text-blue-600">Edit</button>
                <button onClick={()=>remove(t.id)} className="text-red-600">Delete</button>
              </div>
            </li>
          ))}
        </ul>
      </div>
    </div>
  )
}
