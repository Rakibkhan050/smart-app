import { useEffect } from 'react'
import { useRouter } from 'next/router'

export default function Dashboard(){
  const router = useRouter()
  useEffect(()=>{
    const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null
    if(!token) router.push('/auth/login')
  }, [])

  return (
    <div className="p-8">
      <h1 className="text-xl">Admin Dashboard (Placeholder)</h1>
      <p>Widgets and statistics go here.</p>
    </div>
  )
}
