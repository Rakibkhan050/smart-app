import { useEffect, useState } from 'react'
import api from '../services/api'

export default function Notifications(){
  const [items, setItems] = useState([])
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
  return (
    <div className="p-8">
      <h1 className="text-xl">Notifications</h1>
      {items.length === 0 ? <p>No notifications yet</p> : (
        <ul>
          {items.map((n:any)=> <li key={n.id}>{n.title}</li>)}
        </ul>
      )}
    </div>
  )
}
