import QuoteDetail from '@/components/crm/QuoteDetail'

export default function QuoteDetailPage({ params }: { params: { id: string } }) {
  return <QuoteDetail quoteId={params.id} />
}
