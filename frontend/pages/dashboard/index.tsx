import { useEffect } from 'react'
import { useRouter } from 'next/router'

export default function Dashboard(){
  const router = useRouter()
  useEffect(()=>{
    const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null
    if(!token) router.push('/auth/login')
  }, [])

  function logout(){
    localStorage.removeItem('token')
    localStorage.removeItem('refresh')
    router.push('/auth/login')
  }

  return (
    <div className="p-8">
      <div className="flex justify-between items-center">
        <h1 className="text-xl">Admin Dashboard (Placeholder)</h1>
        <button className="bg-red-500 text-white px-3 py-1" onClick={logout}>Logout</button>
      </div>
      <p className="mt-4">Widgets and statistics go here.</p>
    </div>
  )
}

// Disable static optimization to avoid prerender errors on Vercel
export async function getServerSideProps() {
  return { props: {} }
}
