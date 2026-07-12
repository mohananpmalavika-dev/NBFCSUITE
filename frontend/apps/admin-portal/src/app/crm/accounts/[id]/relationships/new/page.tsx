'use client'

import { use } from 'react'
import RelationshipForm from '@/components/crm/RelationshipForm'

export default function NewRelationshipPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params)
  return <RelationshipForm accountId={id} mode="create" />
}
