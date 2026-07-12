'use client'

import { use } from 'react'
import ContactForm from '@/components/crm/ContactForm'

export default function EditContactPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params)
  return <ContactForm contactId={id} mode="edit" />
}
