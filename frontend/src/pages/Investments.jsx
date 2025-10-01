import React, { useEffect, useState } from 'react'
import { useAuth } from '../components/AuthContext'

export default function Investments() {
  const { api } = useAuth()
  const [holdings, setHoldings] = useState([])

  const load = async () => {
    const res = await api.get('/investments/holdings')
    setHoldings(res.data)
  }
  useEffect(() => { load() }, [])

  return (
    <div className="bg-white p-4 rounded shadow">
      <h2 className="font-semibold mb-3">Investments</h2>
      <table className="w-full">
        <thead>
          <tr>
            <th className="text-left">Symbol</th>
            <th className="text-left">Quantity</th>
            <th className="text-left">Cost Basis</th>
            <th className="text-left">Market Value</th>
          </tr>
        </thead>
        <tbody>
          {holdings.map(h => (
            <tr key={h.investment_id}>
              <td>{h.symbol}</td>
              <td>{h.quantity}</td>
              <td>${(h.cost_basis||0).toFixed(2)}</td>
              <td>{h.market_value ? `$${h.market_value.toFixed(2)}` : '—'}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
