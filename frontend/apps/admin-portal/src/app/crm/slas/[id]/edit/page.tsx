import SLAForm from '@/components/crm/SLAForm'

interface EditSLAPageProps {
  params: {
    id: string
  }
}

export default function EditSLAPage({ params }: EditSLAPageProps) {
  return <SLAForm slaId={params.id} mode="edit" />
}
