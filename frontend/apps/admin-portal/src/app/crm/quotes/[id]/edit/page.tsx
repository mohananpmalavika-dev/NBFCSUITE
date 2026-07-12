import QuoteBuilder from '@/components/crm/QuoteBuilder'

export default function EditQuotePage({ params }: { params: { id: string } }) {
  return <QuoteBuilder quoteId={params.id} mode="edit" />
}
