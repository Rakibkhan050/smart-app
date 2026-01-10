import { useEffect, useState } from 'react'
import api from '../services/api'

function urlBase64ToUint8Array(base64String:any) {
  const padding = '='.repeat((4 - base64String.length % 4) % 4);
  const base64 = (base64String + padding).replace(/-/g, '+').replace(/_/g, '/');
  const rawData = typeof window !== 'undefined' ? window.atob(base64) : '';
  const outputArray = new Uint8Array(rawData.length);
  for (let i = 0; i < rawData.length; ++i) {
    outputArray[i] = rawData.charCodeAt(i);
  }
  return outputArray;
}

export default function Notifications(){
  const [items, setItems] = useState([])
  const [subscribed, setSubscribed] = useState(false)

  useEffect(()=>{
    async function load(){
      try{
        const resp = await api.get('')
        setItems(resp.data)
      }catch(e){
        setItems([])
      }
    }
    load()
  }, [])

  async function subscribeToPush(){
    if(typeof window === 'undefined' || !('serviceWorker' in navigator)) return alert('Service worker not supported')
    const reg = await navigator.serviceWorker.register('/sw.js')
    const sub = await reg.pushManager.subscribe({
      userVisibleOnly: true,
      applicationServerKey: urlBase64ToUint8Array(process.env.NEXT_PUBLIC_VAPID_PUBLIC_KEY || '')
    })
    await api.post('notifications/subscribe/', sub)
    setSubscribed(true)
  }

  return (
    <div className="p-8">
      <h1 className="text-xl">Notifications</h1>
      <button onClick={subscribeToPush} className="mb-4 bg-indigo-600 text-white px-3 py-1">Subscribe to Push</button>
      {items.length === 0 ? <p>No notifications yet</p> : (
        <ul>
          {items.map((n:any)=> <li key={n.id}>{n.title}</li>)}
        </ul>
      )}
    </div>
  )
}
