'use client'

import { use } from 'react'
import Account360View from '@/components/crm/Account360View'

export default function AccountDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params)
  return <Account360View accountId={id} />
}
