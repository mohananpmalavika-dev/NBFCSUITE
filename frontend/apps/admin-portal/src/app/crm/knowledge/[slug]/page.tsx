import ArticleDetail from '@/components/crm/ArticleDetail'

interface ArticleDetailPageProps {
  params: {
    slug: string
  }
}

export default function ArticleDetailPage({ params }: ArticleDetailPageProps) {
  return <ArticleDetail slug={params.slug} />
}
