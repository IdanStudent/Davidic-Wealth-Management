import React, { useEffect, useState } from 'react'
import { useAuth } from '../components/AuthContext'

export default function Settings() {
  const { api, me } = useAuth()
  const [shabbat, setShabbat] = useState(me?.shabbat_mode ?? true)
  const [lat, setLat] = useState(me?.lat ?? 31.778)
  const [lon, setLon] = useState(me?.lon ?? 35.235)

  useEffect(() => {
    setShabbat(me?.shabbat_mode ?? true)
    setLat(me?.lat ?? 31.778)
    setLon(me?.lon ?? 35.235)
  }, [me])

  const save = async () => {
  await api.post('/utils/settings', null, { params: { shabbat_mode: shabbat, lat, lon } })
    alert('Settings saved. Shabbat Mode ' + (shabbat ? 'ON' : 'OFF'))
  }

  return (
    <div className="bg-white p-4 rounded shadow space-y-3 max-w-md">
      <h2 className="font-semibold">Settings</h2>
      <label className="flex items-center gap-2">
        <input type="checkbox" checked={shabbat} onChange={e=>setShabbat(e.target.checked)} /> Shabbat Mode
      </label>
      <div className="flex gap-2">
        <input className="border p-2 flex-1" type="number" step="0.001" value={lat} onChange={e=>setLat(parseFloat(e.target.value))} placeholder="Latitude" />
        <input className="border p-2 flex-1" type="number" step="0.001" value={lon} onChange={e=>setLon(parseFloat(e.target.value))} placeholder="Longitude" />
      </div>
      <button onClick={save} className="bg-jewishBlue text-white px-4 py-2 rounded">Save</button>
    </div>
  )
}
