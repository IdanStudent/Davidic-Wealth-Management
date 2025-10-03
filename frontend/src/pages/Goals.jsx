import React, { useEffect, useState } from 'react'
import { useAuth } from '../components/AuthContext'

export default function Goals() {
  const { api } = useAuth()
  const [goals, setGoals] = useState([])
  const [form, setForm] = useState({ name:'Vacation', type:'custom', target_amount: 3000, current_amount: 0, due_date: '' })

  const load = async () => {
    const res = await api.get('/goals/')
    setGoals(res.data)
  }
  useEffect(()=>{ load() }, [])

  const create = async () => {
    const res = await api.post('/goals/', form)
    setForm({ name:'', type:'custom', target_amount: 0, current_amount: 0, due_date: '' })
    await load()
  }

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">Goals</h1>
      <div className="bg-white p-4 rounded shadow">
        <h2 className="font-semibold mb-2">Create Goal</h2>
        <div className="grid grid-cols-1 md:grid-cols-5 gap-2">
          <input className="border rounded px-2 py-1" placeholder="Name" value={form.name} onChange={e=>setForm(f=>({...f, name:e.target.value}))} />
          <select className="border rounded px-2 py-1" value={form.type} onChange={e=>setForm(f=>({...f, type:e.target.value}))}>
            <option value="custom">Custom</option>
            <option value="tzedakah">Tzedakah</option>
            <option value="wedding">Wedding</option>
            <option value="bar_mitzvah">Bar Mitzvah</option>
            <option value="pesach">Pesach</option>
          </select>
          <input className="border rounded px-2 py-1" type="number" placeholder="Target" value={form.target_amount} onChange={e=>setForm(f=>({...f, target_amount:Number(e.target.value)}))} />
          <input className="border rounded px-2 py-1" type="number" placeholder="Current" value={form.current_amount} onChange={e=>setForm(f=>({...f, current_amount:Number(e.target.value)}))} />
          <input className="border rounded px-2 py-1" placeholder="Due YYYY-MM" value={form.due_date} onChange={e=>setForm(f=>({...f, due_date:e.target.value}))} />
        </div>
        <button className="mt-2 bg-blue-600 text-white px-3 py-1 rounded" onClick={create}>Add Goal</button>
      </div>
      <div className="bg-white p-4 rounded shadow">
        <h2 className="font-semibold mb-2">Your Goals</h2>
        <table className="w-full text-left text-sm">
          <thead><tr className="text-gray-500"><th>Name</th><th>Type</th><th className="text-right">Target</th><th className="text-right">Current</th><th className="text-right">Progress</th><th>Due</th></tr></thead>
          <tbody>
            {goals.map(g => {
              const progress = g.target_amount ? Math.min(100, Math.round((g.current_amount / g.target_amount) * 100)) : 0
              return (
                <tr key={g.id} className="border-t">
                  <td>{g.name}</td>
                  <td className="capitalize">{g.type.replace('_',' ')}</td>
                  <td className="text-right">${g.target_amount.toFixed(2)}</td>
                  <td className="text-right">${g.current_amount.toFixed(2)}</td>
                  <td className="text-right">{progress}%</td>
                  <td>{g.due_date}</td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
    </div>
  )
}
