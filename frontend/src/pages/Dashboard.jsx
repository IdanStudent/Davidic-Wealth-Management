import React, { useEffect, useState } from 'react'
import { useAuth } from '../components/AuthContext'
import { Line, Pie } from 'react-chartjs-2'
import { Chart as ChartJS, LineElement, ArcElement, CategoryScale, LinearScale, PointElement, Tooltip, Legend } from 'chart.js'
ChartJS.register(LineElement, ArcElement, CategoryScale, LinearScale, PointElement, Tooltip, Legend)

export default function Dashboard() {
  const { api, me } = useAuth()
  const [summary, setSummary] = useState(null)
  const [netWorthPoints, setNetWorthPoints] = useState([])

  useEffect(() => {
    const now = new Date()
    const y = now.getFullYear()
    const m = now.getMonth()+1
  api.get(`/reports/monthly?year=${y}&month=${m}`).then(res => setSummary(res.data))
    // Fake net worth points for MVP demo
    setNetWorthPoints(Array.from({length:6}, (_,i)=>({x:i, y: 1000 + i*500})))
  }, [])

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Shalom{me?.full_name ? `, ${me.full_name}` : ''}! 👋</h1>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white p-4 rounded shadow">
          <div className="text-gray-500">Income</div>
          <div className="text-2xl font-bold">${summary?.income?.toFixed(2) || '0.00'}</div>
        </div>
        <div className="bg-white p-4 rounded shadow">
          <div className="text-gray-500">Expenses</div>
          <div className="text-2xl font-bold">${summary?.expenses?.toFixed(2) || '0.00'}</div>
        </div>
        <div className="bg-white p-4 rounded shadow">
          <div className="text-gray-500">Savings</div>
          <div className="text-2xl font-bold">${summary ? (summary.income - summary.expenses).toFixed(2) : '0.00'}</div>
        </div>
      </div>

      <div className="bg-white p-4 rounded shadow">
        <h2 className="font-semibold mb-2">Net Worth Over Time</h2>
        <Line data={{
          labels: netWorthPoints.map(p=>`M${p.x+1}`),
          datasets: [{ label: 'Net Worth', data: netWorthPoints.map(p=>p.y), borderColor: '#0A74DA'}]
        }} />
      </div>

      <div className="bg-white p-4 rounded shadow">
        <h2 className="font-semibold mb-2">Spending by Category</h2>
        <Pie data={{
          labels: Object.keys(summary?.spending || {}),
          datasets: [{ data: Object.values(summary?.spending || {}), backgroundColor: ['#0A74DA','#C7A008','#10B981','#EF4444','#8B5CF6'] }]
        }} />
      </div>
    </div>
  )
}
