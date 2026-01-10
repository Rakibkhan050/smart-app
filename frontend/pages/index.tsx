import Link from 'next/link'

export default function Home() {
  return (
    <main className="p-8">
      <h1 className="text-2xl font-bold">School SaaS</h1>
      <ul className="mt-4">
        <li><Link href="/auth/login">Login</Link></li>
        <li><Link href="/dashboard">Admin Dashboard</Link></li>
        <li><Link href="/notifications">Notifications</Link></li>
        <li><Link href="/receipts">Receipts</Link></li>
      </ul>
    </main>
  )
}
