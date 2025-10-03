import React, { useEffect, useState } from 'react'
import { useAuth } from '../components/AuthContext'

export default function Reports() {
  const { api } = useAuth()
  const [year, setYear] = useState(new Date().getFullYear())
  const [month, setMonth] = useState(new Date().getMonth()+1)
  const [report, setReport] = useState(null)
  const [cfStart, setCfStart] = useState(() => new Date(new Date().getFullYear(), new Date().getMonth(), 1).toISOString().slice(0,10))
  const [cfEnd, setCfEnd] = useState(() => new Date().toISOString().slice(0,10))
  const [cashflow, setCashflow] = useState(null)

  const load = async () => {
  const res = await api.get(`/reports/monthly?year=${year}&month=${month}`)
    setReport(res.data)
  }
  useEffect(() => { load() }, [])

  const exportCsv = async () => {
  const res = await api.get(`/reports/export/csv?year=${year}&month=${month}`)
    const blob = new Blob([res.data.content], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = res.data.filename
    a.click()
  }

  const exportPdf = async () => {
  const res = await api.get(`/reports/export/pdf?year=${year}&month=${month}`)
    const a = document.createElement('a')
    a.href = `data:application/pdf;base64,${res.data.content_b64}`
    a.download = res.data.filename
    a.click()
  }

  const loadCashflow = async () => {
    const res = await api.get(`/reports/cashflow?start=${cfStart}&end=${cfEnd}`)
    setCashflow(res.data)
  }

  return (
    <div className="space-y-4">
      <div className="bg-white p-4 rounded shadow">
        <h2 className="font-semibold mb-2">Monthly Report</h2>
        <div className="flex gap-2 mb-3">
          <input className="border p-2" type="number" value={year} onChange={e=>setYear(parseInt(e.target.value))} />
          <input className="border p-2" type="number" value={month} onChange={e=>setMonth(parseInt(e.target.value))} />
          <button onClick={load} className="bg-malkaBlue text-white px-3 py-2 rounded">Load</button>
        </div>
        {report && (
          <>
            <div className="grid grid-cols-3 gap-4">
              <div>Income: ${report.income.toFixed(2)}</div>
              <div>Expenses: ${report.expenses.toFixed(2)}</div>
              <div>Savings: ${(report.income - report.expenses).toFixed(2)}</div>
            </div>
            {/* Flex insights */}
            {Array.isArray(report.flex_insights) && report.flex_insights.length > 0 && (
              <div className="mt-4">
                <div className="font-semibold mb-1">Flex Budgets</div>
                <ul className="divide-y">
                  {report.flex_insights.map((fi, idx) => (
                    <li key={idx} className="py-2 flex items-center justify-between">
                      <div>
                        <div className="font-medium">{fi.category}</div>
                        <div className="text-xs text-gray-600">Current: ${fi.current.toFixed(2)} • Avg({fi.window_months}m): ${fi.avg.toFixed(2)} • Tol: {(fi.tolerance_pct*100).toFixed(0)}%</div>
                      </div>
                      <span className={
                        fi.status==='exceeded'? 'px-2 py-1 rounded bg-red-100 text-red-700 text-xs' :
                        fi.status==='approaching'? 'px-2 py-1 rounded bg-yellow-100 text-yellow-700 text-xs' :
                        'px-2 py-1 rounded bg-green-100 text-green-700 text-xs'
                      }>
                        {fi.status}
                      </span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </>
        )}
      </div>
      <div className="bg-white p-4 rounded shadow flex gap-3">
        <button onClick={exportCsv} className="px-3 py-2 border rounded">Export CSV</button>
        <button onClick={exportPdf} className="px-3 py-2 border rounded">Export PDF</button>
      </div>

      {/* Cash Flow */}
      <div className="bg-white p-4 rounded shadow">
        <h2 className="font-semibold mb-2">Cash Flow</h2>
        <div className="flex gap-2 items-end mb-3">
          <label className="text-sm">
            <div className="text-gray-600 mb-1">Start</div>
            <input className="border p-2" type="date" value={cfStart} onChange={e=>setCfStart(e.target.value)} />
          </label>
          <label className="text-sm">
            <div className="text-gray-600 mb-1">End</div>
            <input className="border p-2" type="date" value={cfEnd} onChange={e=>setCfEnd(e.target.value)} />
          </label>
          <button onClick={loadCashflow} className="bg-malkaBlue text-white px-3 py-2 rounded">Load Cash Flow</button>
        </div>
        {cashflow && (
          <div className="grid grid-cols-3 gap-4">
            <div>Inflow: ${cashflow.inflow.toFixed(2)}</div>
            <div>Outflow: ${cashflow.outflow.toFixed(2)}</div>
            <div>Net: ${cashflow.net.toFixed(2)}</div>
          </div>
        )}
      </div>
    </div>
  )
}
