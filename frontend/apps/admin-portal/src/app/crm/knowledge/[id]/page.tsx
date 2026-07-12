import ArticleDetail from '@/components/crm/ArticleDetail'

interface ArticleDetailPageProps {
  params: {
    id: string
  }
}

export default function ArticleDetailPage({ params }: ArticleDetailPageProps) {
  return <ArticleDetail slug={params.id} />
}
