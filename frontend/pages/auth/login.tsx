import { useState } from 'react'
import api from '../../services/api'
import { useRouter } from 'next/router'

export default function Login(){
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const router = useRouter()

  async function handleSubmit(e){
    e.preventDefault()
    try{
      const resp = await api.post('auth/token/', { username, password })
      localStorage.setItem('token', resp.data.access)
      localStorage.setItem('refresh', resp.data.refresh)
      router.push('/dashboard')
    }catch(err){
      setError('Invalid credentials')
    }
  }

  return (
    <div className="p-8 max-w-md">
      <h1 className="text-xl">Login</h1>
      <form onSubmit={handleSubmit} className="mt-4">
        <input value={username} onChange={e=>setUsername(e.target.value)} placeholder="username" className="border p-2 w-full mb-2" />
        <input type="password" value={password} onChange={e=>setPassword(e.target.value)} placeholder="password" className="border p-2 w-full mb-2" />
        <button className="bg-blue-500 text-white px-4 py-2">Login</button>
      </form>
      {error && <p className="text-red-500 mt-2">{error}</p>}
    </div>
  )
}
