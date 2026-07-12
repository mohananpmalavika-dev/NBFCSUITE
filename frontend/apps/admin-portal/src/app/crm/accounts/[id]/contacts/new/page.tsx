'use client'

import { use } from 'react'
import ContactForm from '@/components/crm/ContactForm'

export default function NewContactPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params)
  return <ContactForm accountId={id} mode="create" />
}
