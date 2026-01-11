import { useState } from 'react'
import api from '../../services/api'
import { useRouter } from 'next/router'

export default function Signup(){
  const [username, setUsername] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const router = useRouter()

  async function handleSubmit(e){
    e.preventDefault()
    try{
      await api.post('auth/register/', { username, email, password })
      router.push('/auth/login')
    }catch(err){
      setError('Could not register')
    }
  }

  return (
    <div className="p-8 max-w-md">
      <h1 className="text-xl">Sign up</h1>
      <form onSubmit={handleSubmit} className="mt-4">
        <input value={username} onChange={e=>setUsername(e.target.value)} placeholder="username" className="border p-2 w-full mb-2" />
        <input value={email} onChange={e=>setEmail(e.target.value)} placeholder="email" className="border p-2 w-full mb-2" />
        <input type="password" value={password} onChange={e=>setPassword(e.target.value)} placeholder="password" className="border p-2 w-full mb-2" />
        <button className="bg-green-500 text-white px-4 py-2">Sign up</button>
      </form>
      {error && <p className="text-red-500 mt-2">{error}</p>}
    </div>
  )
}

// Disable static optimization to avoid prerender errors on Vercel
export async function getServerSideProps() {
  return { props: {} }
}
