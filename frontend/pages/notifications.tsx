import { useEffect, useState } from 'react'

export default function Notifications(){
  const [items, setItems] = useState([])
  useEffect(()=>{
    // placeholder fetch
    setItems([])
  }, [])
  return (
    <div className="p-8">
      <h1 className="text-xl">Notifications</h1>
      {items.length === 0 ? <p>No notifications yet</p> : null}
    </div>
  )
}
