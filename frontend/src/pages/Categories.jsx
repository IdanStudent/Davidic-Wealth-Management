import React, { useEffect, useState } from 'react'
import { useAuth } from '../components/AuthContext'

export default function Categories() {
  const { api } = useAuth()
  const [categories, setCategories] = useState([])
  const [form, setForm] = useState({ name: '', type: 'expense', icon: '' })
  const [error, setError] = useState('')
  const [editingId, setEditingId] = useState(null)
  const [editData, setEditData] = useState({ name: '', type: 'expense', icon: '' })

  const load = async () => {
    const res = await api.get('/categories/')
    setCategories(res.data)
  }
  useEffect(() => { load() }, [])

  const submit = async (e) => {
    e.preventDefault()
    setError('')
    try {
      await api.post('/categories/', form)
      setForm({ name: '', type: 'expense', icon: '' })
      load()
    } catch (err) {
      setError(err?.response?.data?.detail || 'Failed to create category')
    }
  }

  const startEdit = (c) => {
    setEditingId(c.id)
    setEditData({ name: c.name, type: c.type, icon: c.icon || '' })
  }

  const saveEdit = async (id) => {
    setError('')
    try {
      await api.patch(`/categories/${id}`, editData)
      setEditingId(null)
      load()
    } catch (err) {
      setError(err?.response?.data?.detail || 'Failed to update category')
    }
  }

  const remove = async (id) => {
    setError('')
    try {
      await api.delete(`/categories/${id}`)
      load()
    } catch (err) {
      setError(err?.response?.data?.detail || 'Failed to delete category')
    }
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      <form onSubmit={submit} className="bg-white p-4 rounded shadow space-y-3">
        <h2 className="font-semibold">Add Category</h2>
        <input className="w-full border p-2" placeholder="Name" value={form.name} onChange={e=>setForm({...form, name:e.target.value})} required />
        <div className="flex gap-2">
          <select className="border p-2" value={form.type} onChange={e=>setForm({...form, type:e.target.value})}>
            <option value="income">Income</option>
            <option value="expense">Expense</option>
          </select>
          <input className="border p-2 flex-1" placeholder="Icon (optional)" value={form.icon} onChange={e=>setForm({...form, icon:e.target.value})} />
        </div>
        {error && <div className="text-red-600">{error}</div>}
  <button className="bg-malkaBlue text-white px-4 py-2 rounded">Create</button>
      </form>

      <div className="bg-white p-4 rounded shadow">
        <h2 className="font-semibold mb-2">Categories</h2>
        {error && <div className="text-red-600 mb-2">{error}</div>}
        <ul className="space-y-2">
          {categories.map(c => (
            <li key={c.id} className="border p-2 rounded flex items-center gap-2">
              {editingId === c.id ? (
                <>
                  <input className="border p-1 flex-1" value={editData.name} onChange={e=>setEditData({...editData, name:e.target.value})} />
                  <select className="border p-1" value={editData.type} onChange={e=>setEditData({...editData, type:e.target.value})}>
                    <option value="income">Income</option>
                    <option value="expense">Expense</option>
                  </select>
                  <input className="border p-1 flex-1" placeholder="Icon" value={editData.icon} onChange={e=>setEditData({...editData, icon:e.target.value})} />
                  <button className="px-2 py-1 bg-malkaBlue text-white rounded" onClick={()=>saveEdit(c.id)}>Save</button>
                  <button className="px-2 py-1 border rounded" onClick={()=>setEditingId(null)}>Cancel</button>
                </>
              ) : (
                <>
                  <div className="flex-1">
                    <div className="font-semibold">{c.name} {c.icon ? <span className="text-gray-500">({c.icon})</span> : null}</div>
                    <div className="text-xs text-gray-500">{c.type}{c.is_builtin ? ' • built-in' : ''}</div>
                  </div>
                  <button className="px-2 py-1 border rounded" onClick={()=>startEdit(c)}>Edit</button>
                  <button className="px-2 py-1 border rounded text-red-600 disabled:opacity-50" disabled={c.is_builtin} onClick={()=>remove(c.id)}>Delete</button>
                </>
              )}
            </li>
          ))}
        </ul>
      </div>
    </div>
  )
}
