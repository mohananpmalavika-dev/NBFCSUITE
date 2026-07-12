import TicketForm from '@/components/crm/TicketForm'

interface EditTicketPageProps {
  params: {
    id: string
  }
}

export default function EditTicketPage({ params }: EditTicketPageProps) {
  return <TicketForm ticketId={params.id} mode="edit" />
}
