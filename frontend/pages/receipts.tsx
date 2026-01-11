export default function Receipts(){
  return (
    <div className="p-8">
      <h1 className="text-xl">Receipts</h1>
      <p>List of receipts with download links.</p>
    </div>
  )
}

// Disable static optimization to avoid prerender errors on Vercel
export async function getServerSideProps() {
  return { props: {} }
}
