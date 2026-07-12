import OrderDetail from '@/components/crm/OrderDetail'

export default function OrderDetailPage({ params }: { params: { id: string } }) {
  return <OrderDetail orderId={params.id} />
}
