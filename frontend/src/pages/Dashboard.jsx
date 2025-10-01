import React, { useEffect, useState, useMemo } from 'react'
import { useAuth } from '../components/AuthContext'
import { Line, Pie } from 'react-chartjs-2'
import { Chart as ChartJS, LineElement, ArcElement, CategoryScale, LinearScale, PointElement, Tooltip, Legend } from 'chart.js'
ChartJS.register(LineElement, ArcElement, CategoryScale, LinearScale, PointElement, Tooltip, Legend)

export default function Dashboard() {
  const { api, me } = useAuth()
  const [report, setReport] = useState(null)
  const [months, setMonths] = useState(12)
  const [loading, setLoading] = useState(false)

  const fetchReport = async (m = months) => {
    setLoading(true)
    try {
      const res = await api.get(`/reports/networth?months=${m}`)
      setReport(res.data)
    } catch (err) {
      console.error('Failed to fetch networth', err)
    } finally {
      setLoading(false)
    }
  }

  const [recentTx, setRecentTx] = useState([])
  const fetchRecent = async () => {
    try {
      const r = await api.get('/transactions/recent?limit=10')
      setRecentTx(r.data)
    } catch (e) { console.error('recent tx fetch failed', e) }
  }

  useEffect(()=>{ fetchRecent() }, [])

  useEffect(() => { fetchReport(months) }, [months])

  const latest = report?.history?.length ? report.history[report.history.length-1] : null
  const prev = report?.history?.length ? report.history[Math.max(0, report.history.length-2)] : null

  const pctChange = useMemo(() => {
    if (!latest || !prev) return 0
    if (!prev.net_worth) return 0
    return ((latest.net_worth - prev.net_worth) / Math.abs(prev.net_worth || 1)) * 100
  }, [latest, prev])

  const pieData = useMemo(() => {
    const accounts = report?.accounts || []
    const labels = accounts.map(a=>a.name)
    const data = accounts.map(a=> Math.max(0, a.is_liability ? 0 : a.balance))
    return { labels, datasets: [{ data, backgroundColor: ['#0A74DA','#C7A008','#10B981','#EF4444','#8B5CF6','#8B5CF6'] }] }
  }, [report])

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Dashboard{me?.full_name ? ` — ${me.full_name}` : ''}</h1>
        <div className="flex gap-2">
          <select value={months} onChange={(e)=>setMonths(Number(e.target.value))} className="border rounded px-2 py-1">
            <option value={3}>3 months</option>
            <option value={6}>6 months</option>
            <option value={12}>12 months</option>
            <option value={24}>24 months</option>
          </select>
          <button onClick={()=>fetchReport(months)} className="bg-blue-600 text-white px-3 py-1 rounded">Refresh</button>
          <button onClick={()=>{ window.open(`/api/reports/export/csv?year=${new Date().getFullYear()}&month=${new Date().getMonth()+1}`) }} className="border px-3 py-1 rounded">Export CSV</button>
        </div>
      </div>

      {/* Top cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white p-4 rounded shadow">
          <div className="text-gray-500">Assets</div>
          <div className="text-2xl font-bold">${(report?.assets ?? 0).toFixed(2)}</div>
          <div className="text-sm text-gray-500">{report?.history?.length ? `vs prev: ${((report.history[report.history.length-1].assets - (report.history[report.history.length-2]?.assets||0))||0).toFixed(2)}` : ''}</div>
        </div>
        <div className="bg-white p-4 rounded shadow">
          <div className="text-gray-500">Liabilities</div>
          <div className="text-2xl font-bold">${(report?.liabilities ?? 0).toFixed(2)}</div>
          <div className="text-sm text-gray-500">{report?.history?.length ? `vs prev: ${((report.history[report.history.length-1].liabilities - (report.history[report.history.length-2]?.liabilities||0))||0).toFixed(2)}` : ''}</div>
        </div>
        <div className="bg-white p-4 rounded shadow">
          <div className="text-gray-500">Net Worth</div>
          <div className="text-2xl font-bold">${((report?.assets ?? 0) - (report?.liabilities ?? 0)).toFixed(2)}</div>
          <div className="flex items-center gap-2">
            <div className={`text-sm ${pctChange>=0 ? 'text-green-600' : 'text-red-600'}`}>{pctChange>=0? '▲':'▼'} {Math.abs(pctChange).toFixed(2)}%</div>
            <div className="text-xs text-gray-400" title={prev ? `Previous: ${prev.net_worth}
Current: ${latest?.net_worth}` : ''}>? hover for numbers</div>
          </div>
        </div>
      </div>

      {/* Middle: accounts table + pie chart */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="md:col-span-2 bg-white p-4 rounded shadow">
          <h2 className="font-semibold mb-2">Accounts</h2>
          <table className="w-full text-left">
            <thead>
              <tr className="text-sm text-gray-500"><th>Name</th><th>Type</th><th>Liability</th><th className="text-right">Balance</th></tr>
            </thead>
            <tbody>
              {(report?.accounts || []).map(a=> (
                <tr key={a.id} className="border-t"><td>{a.name}</td><td>{a.type}</td><td>{a.is_liability ? 'Yes':''}</td><td className="text-right">${a.balance.toFixed(2)}</td></tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="bg-white p-4 rounded shadow">
          <h2 className="font-semibold mb-2">Assets by Account</h2>
          <div style={{height:220}}>
            <Pie data={pieData} />
          </div>
        </div>
      </div>

      {/* Bottom: net-worth line + recent transactions */}
        <div className="bg-white p-4 rounded shadow">
          <h2 className="font-semibold mb-2">Net Worth History</h2>
          <Line data={{ labels: (report?.history || []).map(h=>h.month), datasets:[{ label: 'Net Worth', data: (report?.history || []).map(h=>h.net_worth), borderColor: '#0A74DA', tension: 0.3 }]}} />
        </div>

      <div className="bg-white p-4 rounded shadow">
        <h2 className="font-semibold mb-2">Recent Transactions</h2>
        <div className="text-sm text-gray-600">Most recent activity</div>
        <ul className="mt-2">
          {recentTx.length ? recentTx.map(tx => (
            <li key={tx.id} className="flex justify-between border-t py-2 text-sm">
              <div>
                <div className="font-medium">{tx.note || (tx.category_id ? `Category ${tx.category_id}` : 'Transaction')}</div>
                <div className="text-xs text-gray-500">Acct {tx.account_id} • {tx.date}</div>
              </div>
              <div className={`font-medium ${tx.amount<0 ? 'text-red-600' : 'text-green-600'}`}>${tx.amount.toFixed(2)}</div>
            </li>
          )) : <li className="text-sm text-gray-500">No recent transactions</li>}
        </ul>
      </div>

      {report?.investments && report.investments.length > 0 && (
        <div className="bg-white p-4 rounded shadow">
          <h2 className="font-semibold mb-2">Investments</h2>
          <table className="w-full text-left text-sm">
            <thead><tr className="text-gray-500"><th>Symbol</th><th>Name</th><th className="text-right">Qty</th><th className="text-right">Price</th><th className="text-right">Value</th></tr></thead>
            <tbody>
              {report.investments.map(inv => (
                <tr key={inv.investment_id} className="border-t"><td>{inv.symbol}</td><td>{inv.name}</td><td className="text-right">{inv.quantity}</td><td className="text-right">${(inv.price||0).toFixed(2)}</td><td className="text-right">${(inv.value||0).toFixed(2)}</td></tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
