import React, { useMemo, useState } from 'react'
import { useAuth } from '../components/AuthContext'

export default function DebtPlanner() {
  const { api } = useAuth()
  const [debts, setDebts] = useState([ { id: 1, name: 'Card A', balance: 1200, apr_annual: 24, min_payment: 35, due_day: 1 } ])
  const [budget, setBudget] = useState(300)
  const [extra, setExtra] = useState(0)
  const [strategy, setStrategy] = useState('snowball')
  const [plan, setPlan] = useState(null)
  const runPlan = async () => {
    const body = { strategy, monthly_budget: Number(budget), debts: debts.map(d=>({ ...d, apr_annual: Number(d.apr_annual), min_payment: Number(d.min_payment), balance: Number(d.balance) })), extra_payment: Number(extra||0) }
    const res = await api.post('/debt/plan', body)
    setPlan(res.data)
  }
  const totals = useMemo(()=>{
    if (!plan) return null
    return {
      months: plan.months_to_payoff,
      interest: plan.total_interest,
    }
  }, [plan])
  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">Debt Planner</h1>
      <div className="bg-white p-4 rounded shadow space-y-3">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
          <div>
            <label className="text-sm text-gray-500">Strategy</label>
            <select className="border rounded w-full px-2 py-1" value={strategy} onChange={e=>setStrategy(e.target.value)}>
              <option value="snowball">Snowball (lowest balance first)</option>
              <option value="avalanche">Avalanche (highest APR first)</option>
            </select>
          </div>
          <div>
            <label className="text-sm text-gray-500">Monthly budget</label>
            <input className="border rounded w-full px-2 py-1" type="number" value={budget} onChange={e=>setBudget(e.target.value)} />
          </div>
          <div>
            <label className="text-sm text-gray-500">What-if extra payment</label>
            <input className="border rounded w-full px-2 py-1" type="number" value={extra} onChange={e=>setExtra(e.target.value)} />
          </div>
          <div className="flex items-end"><button className="bg-blue-600 text-white px-3 py-2 rounded" onClick={runPlan}>Generate Plan</button></div>
        </div>
        <div>
          <h2 className="font-semibold mb-2">Debts</h2>
          <table className="w-full text-left text-sm">
            <thead><tr className="text-gray-500"><th>Name</th><th className="text-right">Balance</th><th className="text-right">APR %</th><th className="text-right">Min</th><th>Due</th></tr></thead>
            <tbody>
              {debts.map((d,i)=> (
                <tr key={i} className="border-t">
                  <td><input className="border rounded px-1 py-0.5" value={d.name} onChange={e=>setDebts(prev=>prev.map((x,idx)=> idx===i ? {...x, name:e.target.value} : x))} /></td>
                  <td className="text-right"><input className="border rounded px-1 py-0.5 w-24 text-right" type="number" value={d.balance} onChange={e=>setDebts(prev=>prev.map((x,idx)=> idx===i ? {...x, balance:Number(e.target.value)} : x))} /></td>
                  <td className="text-right"><input className="border rounded px-1 py-0.5 w-20 text-right" type="number" value={d.apr_annual} onChange={e=>setDebts(prev=>prev.map((x,idx)=> idx===i ? {...x, apr_annual:Number(e.target.value)} : x))} /></td>
                  <td className="text-right"><input className="border rounded px-1 py-0.5 w-20 text-right" type="number" value={d.min_payment} onChange={e=>setDebts(prev=>prev.map((x,idx)=> idx===i ? {...x, min_payment:Number(e.target.value)} : x))} /></td>
                  <td><input className="border rounded px-1 py-0.5 w-16" type="number" value={d.due_day||''} onChange={e=>setDebts(prev=>prev.map((x,idx)=> idx===i ? {...x, due_day:Number(e.target.value)} : x))} /></td>
                </tr>
              ))}
            </tbody>
          </table>
          <button className="mt-2 text-sm border px-2 py-1 rounded" onClick={()=>setDebts(d=>[...d, { id: (d[d.length-1]?.id||0)+1, name:'New Debt', balance:0, apr_annual:20, min_payment:25, due_day:1 }])}>Add debt</button>
        </div>
      </div>
      {plan && (
        <div className="bg-white p-4 rounded shadow">
          <h2 className="font-semibold mb-2">Plan Summary</h2>
          <div className="text-sm text-gray-700">Months to payoff: <span className="font-semibold">{totals.months}</span> • Total interest: <span className="font-semibold">${totals.interest.toFixed(2)}</span></div>
          <h3 className="font-semibold mt-3">First 12 Months</h3>
          <table className="w-full text-left text-sm">
            <thead><tr className="text-gray-500"><th>Month</th><th>Debt</th><th className="text-right">Payment</th><th className="text-right">Principal</th><th className="text-right">Interest</th><th className="text-right">Balance After</th></tr></thead>
            <tbody>
              {plan.schedule.slice(0, 12).map((p, idx)=> (
                <tr key={idx} className="border-t">
                  <td>{p.month}</td>
                  <td>{p.debt_id}</td>
                  <td className="text-right">${p.payment.toFixed(2)}</td>
                  <td className="text-right">${p.principal.toFixed(2)}</td>
                  <td className="text-right">${p.interest.toFixed(2)}</td>
                  <td className="text-right">${p.balance_after.toFixed(2)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
