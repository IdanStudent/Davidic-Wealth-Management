import React, { useEffect, useState } from 'react'
import { useAuth } from '../components/AuthContext'

export default function Budgets() {
  const { api } = useAuth()
  const [budgets, setBudgets] = useState([])
  const [categories, setCategories] = useState([])
  const [month, setMonth] = useState(new Date().toISOString().slice(0,7))
  const [items, setItems] = useState([{ category_id: 0, limit: 0 }])

  const load = async () => {
    const [cats, b] = await Promise.all([
      api.get('/categories/'),
      api.get('/budgets/')
    ])
    setCategories(cats.data)
    setBudgets(b.data)
  }
  useEffect(() => { load() }, [])

  const addItem = () => setItems([...items, { category_id: 0, limit: 0 }])

  const submit = async (e) => {
    e.preventDefault()
    const payload = { month, items: items.filter(it=>it.category_id) }
  await api.post('/budgets/', payload)
    setItems([{ category_id: 0, limit: 0 }])
    load()
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      <form onSubmit={submit} className="bg-white p-4 rounded shadow space-y-3">
        <h2 className="font-semibold">Create Budget</h2>
        <input className="w-full border p-2" type="month" value={month} onChange={e=>setMonth(e.target.value)} />
        {items.map((it, idx) => (
          <div key={idx} className="flex gap-2">
            <select className="border p-2 flex-1" value={it.category_id} onChange={e=>{
              const v = parseInt(e.target.value)
              setItems(items.map((x,i)=> i===idx?{...x, category_id: v}:x))
            }}>
              <option value={0}>Select Category</option>
              {categories.map(c=> <option key={c.id} value={c.id}>{c.name}</option>)}
            </select>
            <input className="border p-2 w-32" type="number" value={it.limit} onChange={e=>{
              const v = parseFloat(e.target.value)
              setItems(items.map((x,i)=> i===idx?{...x, limit:v}:x))
            }} placeholder="Limit" />
          </div>
        ))}
        <div className="flex gap-2">
          <button type="button" onClick={addItem} className="px-3 py-2 border rounded">Add Item</button>
          <button className="bg-jewishBlue text-white px-4 py-2 rounded">Save Budget</button>
        </div>
      </form>

      <div className="bg-white p-4 rounded shadow">
        <h2 className="font-semibold mb-2">Budgets</h2>
        <ul className="space-y-2">
          {budgets.map(b => (
            <li key={b.id} className="border p-2 rounded">
              <div className="font-semibold">{b.month}</div>
              <ul className="ml-4 list-disc">
                {b.items?.map(it => {
                  const c = categories.find(c=>c.id===it.category_id)
                  return <li key={it.id}>{c?.name || `Category ${it.category_id}`} - ${it.limit.toFixed(2)}</li>
                })}
              </ul>
            </li>
          ))}
        </ul>
      </div>
    </div>
  )
}
