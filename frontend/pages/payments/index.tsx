import api from '../../services/api'

export default function Payments(){
  async function createTestPayment(){
    const resp = await api.post('payments/create-intent/', { amount: 100, currency: 'SAR', test: true })
    alert(JSON.stringify(resp.data))
  }

  async function triggerWebhook(){
    // For testing only: trigger a test webhook on the server
    const resp = await api.post('payments/test-webhook/', { payment_id: 'pay_test_1', amount: 100, currency: 'SAR' })
    alert(JSON.stringify(resp.data))
  }

  return (
    <div className="p-8">
      <h1 className="text-xl">Payments (Test)</h1>
      <button className="bg-blue-600 text-white px-3 py-1 mr-2" onClick={createTestPayment}>Create Test Payment</button>
      <button className="bg-green-600 text-white px-3 py-1" onClick={triggerWebhook}>Trigger Test Webhook</button>
    </div>
  )
}

// Disable static optimization to avoid prerender errors on Vercel
export async function getServerSideProps() {
  return { props: {} }
}
