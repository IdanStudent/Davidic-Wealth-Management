import React, { useEffect, useState } from 'react'
import { useAuth } from '../components/AuthContext'

export default function Reports() {
  const { api } = useAuth()
  const [year, setYear] = useState(new Date().getFullYear())
  const [month, setMonth] = useState(new Date().getMonth()+1)
  const [report, setReport] = useState(null)

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

  return (
    <div className="space-y-4">
      <div className="bg-white p-4 rounded shadow">
        <h2 className="font-semibold mb-2">Monthly Report</h2>
        <div className="flex gap-2 mb-3">
          <input className="border p-2" type="number" value={year} onChange={e=>setYear(parseInt(e.target.value))} />
          <input className="border p-2" type="number" value={month} onChange={e=>setMonth(parseInt(e.target.value))} />
          <button onClick={load} className="bg-jewishBlue text-white px-3 py-2 rounded">Load</button>
        </div>
        {report && (
          <div className="grid grid-cols-3 gap-4">
            <div>Income: ${report.income.toFixed(2)}</div>
            <div>Expenses: ${report.expenses.toFixed(2)}</div>
            <div>Savings: ${(report.income - report.expenses).toFixed(2)}</div>
          </div>
        )}
      </div>
      <div className="bg-white p-4 rounded shadow flex gap-3">
        <button onClick={exportCsv} className="px-3 py-2 border rounded">Export CSV</button>
        <button onClick={exportPdf} className="px-3 py-2 border rounded">Export PDF</button>
      </div>
    </div>
  )
}
