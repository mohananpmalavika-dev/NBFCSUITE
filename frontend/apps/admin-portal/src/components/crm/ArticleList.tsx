'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { customerServiceApi, KnowledgeArticle, ArticleStatus, ArticleCategory } from '@/services/customerServiceApi'

export default function ArticleList() {
  const router = useRouter()
  const [articles, setArticles] = useState<KnowledgeArticle[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [totalPages, setTotalPages] = useState(0)
  const [currentPage, setCurrentPage] = useState(1)
  const [totalRecords, setTotalRecords] = useState(0)
  const pageSize = 20

  // Filters
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState<ArticleStatus | ''>('')
  const [categoryFilter, setCategoryFilter] = useState<ArticleCategory | ''>('')
  const [featuredFilter, setFeaturedFilter] = useState<boolean | undefined>(undefined)

  useEffect(() => {
    loadArticles()
  }, [currentPage, searchTerm, statusFilter, categoryFilter, featuredFilter])

  const loadArticles = async () => {
    try {
      setLoading(true)
      setError(null)

      const params: any = {
        skip: (currentPage - 1) * pageSize,
        limit: pageSize,
      }

      if (searchTerm) params.search = searchTerm
      if (statusFilter) params.status = statusFilter
      if (categoryFilter) params.category = categoryFilter
      if (featuredFilter !== undefined) params.is_featured = featuredFilter

      const response = await customerServiceApi.knowledge.list(params)

      if (response.success && response.data) {
        setArticles(response.data.articles)
        setTotalRecords(response.data.total)
        setTotalPages(response.data.total_pages)
      } else {
        setError('Failed to load articles')
      }
    } catch (err: any) {
      setError(err.message || 'Failed to load articles')
    } finally {
      setLoading(false)
    }
  }

  const getStatusBadge = (status: ArticleStatus) => {
    const colors: Record<ArticleStatus, string> = {
      draft: 'bg-gray-100 text-gray-800',
      published: 'bg-green-100 text-green-800',
      archived: 'bg-yellow-100 text-yellow-800',
      under_review: 'bg-blue-100 text-blue-800',
    }
    return colors[status] || 'bg-gray-100 text-gray-800'
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-IN', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    })
  }

  if (loading && articles.length === 0) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading articles...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      {/* Header */}
      <div className="mb-6">
        <div className="flex justify-between items-center mb-4">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Knowledge Base</h1>
            <p className="text-gray-600 mt-1">Manage help articles and documentation</p>
          </div>
          <button
            onClick={() => router.push('/crm/knowledge/new')}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            + Create Article
          </button>
        </div>

        {/* Filters */}
        <div className="bg-white rounded-lg shadow p-4">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Search</label>
              <input
                type="text"
                placeholder="Search articles..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Status</label>
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value as ArticleStatus | '')}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">All Status</option>
                <option value="draft">Draft</option>
                <option value="published">Published</option>
                <option value="under_review">Under Review</option>
                <option value="archived">Archived</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Category</label>
              <select
                value={categoryFilter}
                onChange={(e) => setCategoryFilter(e.target.value as ArticleCategory | '')}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">All Categories</option>
                <option value="faq">FAQ</option>
                <option value="how_to">How To</option>
                <option value="troubleshooting">Troubleshooting</option>
                <option value="policy">Policy</option>
                <option value="announcement">Announcement</option>
                <option value="guide">Guide</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Featured</label>
              <select
                value={featuredFilter === undefined ? '' : featuredFilter ? 'yes' : 'no'}
                onChange={(e) => {
                  if (e.target.value === '') setFeaturedFilter(undefined)
                  else setFeaturedFilter(e.target.value === 'yes')
                }}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">All</option>
                <option value="yes">Featured</option>
                <option value="no">Not Featured</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      {error && (
        <div className="mb-6 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
          {error}
        </div>
      )}

      {/* Articles Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {articles.map((article) => (
          <div
            key={article.id}
            className="bg-white rounded-lg shadow hover:shadow-lg transition-shadow cursor-pointer overflow-hidden"
            onClick={() => router.push(`/crm/knowledge/${article.slug}`)}
          >
            {/* Article Header */}
            <div className="p-6">
              <div className="flex justify-between items-start mb-3">
                <span className={`text-xs px-2 py-1 rounded-full ${getStatusBadge(article.status)}`}>
                  {article.status.replace('_', ' ').toUpperCase()}
                </span>
                {article.is_featured && (
                  <svg className="w-5 h-5 text-yellow-500" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                  </svg>
                )}
              </div>

              <h3 className="text-lg font-semibold text-gray-900 mb-2 line-clamp-2">
                {article.title}
              </h3>

              {article.excerpt && (
                <p className="text-gray-600 text-sm mb-3 line-clamp-3">
                  {article.excerpt}
                </p>
              )}

              <div className="flex items-center gap-2 mb-3">
                <span className="text-xs px-2 py-1 bg-blue-50 text-blue-700 rounded-full capitalize">
                  {article.category.replace('_', ' ')}
                </span>
                <span className="text-xs text-gray-500">
                  {article.article_number}
                </span>
              </div>

              {/* Tags */}
              {article.tags && article.tags.length > 0 && (
                <div className="flex flex-wrap gap-1 mb-3">
                  {article.tags.slice(0, 3).map((tag, index) => (
                    <span
                      key={index}
                      className="text-xs px-2 py-0.5 bg-gray-100 text-gray-700 rounded-full"
                    >
                      {tag}
                    </span>
                  ))}
                  {article.tags.length > 3 && (
                    <span className="text-xs px-2 py-0.5 bg-gray-100 text-gray-700 rounded-full">
                      +{article.tags.length - 3}
                    </span>
                  )}
                </div>
              )}

              {/* Stats */}
              <div className="flex items-center gap-4 text-xs text-gray-500 pt-3 border-t">
                <div className="flex items-center gap-1">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                  </svg>
                  <span>{article.view_count}</span>
                </div>
                <div className="flex items-center gap-1">
                  <svg className="w-4 h-4 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M2 10.5a1.5 1.5 0 113 0v6a1.5 1.5 0 01-3 0v-6zM6 10.333v5.43a2 2 0 001.106 1.79l.05.025A4 4 0 008.943 18h5.416a2 2 0 001.962-1.608l1.2-6A2 2 0 0015.56 8H12V4a2 2 0 00-2-2 1 1 0 00-1 1v.667a4 4 0 01-.8 2.4L6.8 7.933a4 4 0 00-.8 2.4z" />
                  </svg>
                  <span>{article.helpful_count}</span>
                </div>
                <div className="flex-1 text-right">
                  {formatDate(article.created_at)}
                </div>
              </div>
            </div>

            {/* Actions */}
            <div className="bg-gray-50 px-6 py-3 flex justify-between items-center">
              <button
                onClick={(e) => {
                  e.stopPropagation()
                  router.push(`/crm/knowledge/${article.slug}`)
                }}
                className="text-blue-600 hover:text-blue-700 text-sm font-medium"
              >
                View
              </button>
              <button
                onClick={(e) => {
                  e.stopPropagation()
                  router.push(`/crm/knowledge/${article.id}/edit`)
                }}
                className="text-gray-600 hover:text-gray-700 text-sm font-medium"
              >
                Edit
              </button>
            </div>
          </div>
        ))}
      </div>

      {!loading && articles.length === 0 && (
        <div className="bg-white rounded-lg shadow p-12 text-center">
          <svg className="w-16 h-16 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
          </svg>
          <h3 className="text-lg font-medium text-gray-900 mb-2">No articles found</h3>
          <p className="text-gray-600 mb-4">
            {searchTerm || statusFilter || categoryFilter
              ? 'Try adjusting your filters'
              : 'Get started by creating your first knowledge base article'}
          </p>
          <button
            onClick={() => router.push('/crm/knowledge/new')}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Create Article
          </button>
        </div>
      )}

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="mt-6 bg-white rounded-lg shadow p-4">
          <div className="flex items-center justify-between">
            <p className="text-sm text-gray-600">
              Showing {(currentPage - 1) * pageSize + 1} to {Math.min(currentPage * pageSize, totalRecords)} of {totalRecords} articles
            </p>
            <div className="flex gap-2">
              <button
                onClick={() => setCurrentPage(currentPage - 1)}
                disabled={currentPage === 1}
                className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Previous
              </button>
              <button
                onClick={() => setCurrentPage(currentPage + 1)}
                disabled={currentPage === totalPages}
                className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Next
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
