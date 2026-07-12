import ArticleForm from '@/components/crm/ArticleForm'

interface EditArticlePageProps {
  params: {
    id: string
  }
}

export default function EditArticlePage({ params }: EditArticlePageProps) {
  return <ArticleForm articleId={params.id} mode="edit" />
}
