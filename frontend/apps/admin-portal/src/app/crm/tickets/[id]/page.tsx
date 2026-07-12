import TicketDetail from '@/components/crm/TicketDetail'

interface TicketDetailPageProps {
  params: {
    id: string
  }
}

export default function TicketDetailPage({ params }: TicketDetailPageProps) {
  return <TicketDetail ticketId={params.id} />
}
