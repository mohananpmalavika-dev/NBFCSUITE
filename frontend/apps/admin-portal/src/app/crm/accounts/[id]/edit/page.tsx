'use client'

import { use } from 'react'
import AccountForm from '@/components/crm/AccountForm'

export default function EditAccountPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params)
  return <AccountForm accountId={id} mode="edit" />
}
