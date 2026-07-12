import ProductForm from '@/components/crm/ProductForm'

export default function EditProductPage({ params }: { params: { id: string } }) {
  return <ProductForm productId={params.id} mode="edit" />
}
