'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { customerServiceApi, KnowledgeArticle } from '@/services/customerServiceApi'

interface ArticleDetailProps {
  slug: string
}

export default function ArticleDetail({ slug }: ArticleDetailProps) {
  const router = useRouter()
  const [article, setArticle] = useState<KnowledgeArticle | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [feedbackSubmitted, setFeedbackSubmitted] = useState(false)

  useEffect(() => {
    loadArticle()
  }, [slug])

  const loadArticle = async () => {
    try {
      setLoading(true)
      setError(null)
      const response = await customerServiceApi.knowledge.getBySlug(slug)

      if (response.success) {
        setArticle(response.data!)
        // Increment view count
        await customerServiceApi.knowledge.get(response.data!.id, true)
      } else {
        setError('Failed to load article')
      }
    } catch (err: any) {
      setError(err.message || 'Failed to load article')
    } finally {
      setLoading(false)
    }
  }

  const handleFeedback = async (helpful: boolean) => {
    if (!article || feedbackSubmitted) return

    try {
      await customerServiceApi.knowledge.recordFeedback(article.id, helpful)
      setFeedbackSubmitted(true)
      // Update local counts
      setArticle({
        ...article,
        helpful_count: helpful ? article.helpful_count + 1 : article.helpful_count,
        not_helpful_count: !helpful ? article.not_helpful_count + 1 : article.not_helpful_count,
      })
    } catch (err: any) {
      console.error('Failed to record feedback:', err)
    }
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-IN', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    })
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading article...</p>
        </div>
      </div>
    )
  }

  if (error || !article) {
    return (
      <div className="min-h-screen bg-gray-50 p-6">
        <div className="max-w-4xl mx-auto">
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
            {error || 'Article not found'}
          </div>
          <button
            onClick={() => router.push('/crm/knowledge')}
            className="mt-4 text-blue-600 hover:text-blue-700"
          >
            ← Back to Knowledge Base
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b">
        <div className="max-w-4xl mx-auto px-6 py-6">
          <button
            onClick={() => router.push('/crm/knowledge')}
            className="text-blue-600 hover:text-blue-700 mb-4 flex items-center text-sm"
          >
            ← Back to Knowledge Base
          </button>
          
          <div className="flex justify-between items-start">
            <div className="flex-1">
              {article.is_featured && (
                <div className="flex items-center gap-2 mb-2">
                  <svg className="w-5 h-5 text-yellow-500" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                  </svg>
                  <span className="text-sm font-medium text-yellow-700">Featured Article</span>
                </div>
              )}
              
              <h1 className="text-3xl font-bold text-gray-900 mb-2">{article.title}</h1>
              
              <div className="flex items-center gap-4 text-sm text-gray-600">
                <span className="capitalize">{article.category.replace('_', ' ')}</span>
                <span>•</span>
                <span>{article.article_number}</span>
                <span>•</span>
                <span>Published {formatDate(article.published_at || article.created_at)}</span>
                {article.author_name && (
                  <>
                    <span>•</span>
                    <span>By {article.author_name}</span>
                  </>
                )}
              </div>

              {/* Stats */}
              <div className="flex items-center gap-4 mt-3 text-sm text-gray-500">
                <div className="flex items-center gap-1">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                  </svg>
                  <span>{article.view_count} views</span>
                </div>
                <div className="flex items-center gap-1">
                  <svg className="w-4 h-4 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M2 10.5a1.5 1.5 0 113 0v6a1.5 1.5 0 01-3 0v-6zM6 10.333v5.43a2 2 0 001.106 1.79l.05.025A4 4 0 008.943 18h5.416a2 2 0 001.962-1.608l1.2-6A2 2 0 0015.56 8H12V4a2 2 0 00-2-2 1 1 0 00-1 1v.667a4 4 0 01-.8 2.4L6.8 7.933a4 4 0 00-.8 2.4z" />
                  </svg>
                  <span>{article.helpful_count} helpful</span>
                </div>
              </div>
            </div>

            <button
              onClick={() => router.push(`/crm/knowledge/${article.id}/edit`)}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm"
            >
              Edit
            </button>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-4xl mx-auto px-6 py-8">
        <div className="bg-white rounded-lg shadow p-8">
          {/* Tags */}
          {article.tags && article.tags.length > 0 && (
            <div className="mb-6 pb-6 border-b">
              <div className="flex flex-wrap gap-2">
                {article.tags.map((tag, index) => (
                  <span
                    key={index}
                    className="px-3 py-1 bg-blue-50 text-blue-700 rounded-full text-sm"
                  >
                    {tag}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Article Content */}
          <div className="prose prose-blue max-w-none">
            <div 
              dangerouslySetInnerHTML={{ __html: article.content }}
              className="text-gray-800 leading-relaxed"
            />
          </div>

          {/* Attachments */}
          {article.attachments && article.attachments.length > 0 && (
            <div className="mt-8 pt-8 border-t">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Attachments</h3>
              <div className="space-y-2">
                {article.attachments.map((attachment) => (
                  <div
                    key={attachment.id}
                    className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                  >
                    <div className="flex items-center gap-3">
                      <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13" />
                      </svg>
                      <div>
                        <p className="text-sm font-medium text-gray-900">{attachment.file_name}</p>
                        {attachment.file_size && (
                          <p className="text-xs text-gray-500">
                            {(attachment.file_size / 1024).toFixed(2)} KB
                          </p>
                        )}
                      </div>
                    </div>
                    <a
                      href={attachment.file_path}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-600 hover:text-blue-700 text-sm font-medium"
                    >
                      Download
                    </a>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Feedback Section */}
          <div className="mt-8 pt-8 border-t">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Was this article helpful?</h3>
            
            {feedbackSubmitted ? (
              <div className="bg-green-50 text-green-800 px-4 py-3 rounded-lg">
                Thank you for your feedback!
              </div>
            ) : (
              <div className="flex gap-3">
                <button
                  onClick={() => handleFeedback(true)}
                  className="flex items-center gap-2 px-4 py-2 bg-green-100 text-green-700 rounded-lg hover:bg-green-200 transition-colors"
                >
                  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M2 10.5a1.5 1.5 0 113 0v6a1.5 1.5 0 01-3 0v-6zM6 10.333v5.43a2 2 0 001.106 1.79l.05.025A4 4 0 008.943 18h5.416a2 2 0 001.962-1.608l1.2-6A2 2 0 0015.56 8H12V4a2 2 0 00-2-2 1 1 0 00-1 1v.667a4 4 0 01-.8 2.4L6.8 7.933a4 4 0 00-.8 2.4z" />
                  </svg>
                  Yes, this was helpful
                </button>
                <button
                  onClick={() => handleFeedback(false)}
                  className="flex items-center gap-2 px-4 py-2 bg-red-100 text-red-700 rounded-lg hover:bg-red-200 transition-colors"
                >
                  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20" transform="rotate(180)">
                    <path d="M2 10.5a1.5 1.5 0 113 0v6a1.5 1.5 0 01-3 0v-6zM6 10.333v5.43a2 2 0 001.106 1.79l.05.025A4 4 0 008.943 18h5.416a2 2 0 001.962-1.608l1.2-6A2 2 0 0015.56 8H12V4a2 2 0 00-2-2 1 1 0 00-1 1v.667a4 4 0 01-.8 2.4L6.8 7.933a4 4 0 00-.8 2.4z" />
                  </svg>
                  No, this wasn't helpful
                </button>
              </div>
            )}
          </div>

          {/* Keywords */}
          {article.keywords && article.keywords.length > 0 && (
            <div className="mt-6 pt-6 border-t">
              <h4 className="text-sm font-semibold text-gray-700 mb-2">Keywords</h4>
              <p className="text-sm text-gray-600">{article.keywords.join(', ')}</p>
            </div>
          )}
        </div>

        {/* Version Info */}
        <div className="mt-4 text-center text-sm text-gray-500">
          Article version {article.version} • Last updated {formatDate(article.updated_at)}
        </div>
      </div>
    </div>
  )
}
