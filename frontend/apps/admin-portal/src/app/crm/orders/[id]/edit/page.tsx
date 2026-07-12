import OrderForm from '@/components/crm/OrderForm'

export default function EditOrderPage({ params }: { params: { id: string } }) {
  return <OrderForm orderId={params.id} mode="edit" />
}
