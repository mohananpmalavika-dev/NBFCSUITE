import { Suspense } from 'react'
import OrderForm from '@/components/crm/OrderForm'

function NewOrderForm() {
  return <OrderForm mode="create" />
}

export default function NewOrderPage() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <NewOrderForm />
    </Suspense>
  )
}
