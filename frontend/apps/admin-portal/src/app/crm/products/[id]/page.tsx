import ProductDetail from '@/components/crm/ProductDetail'

export default function ProductDetailPage({ params }: { params: { id: string } }) {
  return <ProductDetail productId={params.id} />
}
