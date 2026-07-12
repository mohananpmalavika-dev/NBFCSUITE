'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { customerServiceApi, KnowledgeArticleCreate, KnowledgeArticleUpdate, KnowledgeArticle, ArticleCategory, ArticleStatus } from '@/services/customerServiceApi'

interface ArticleFormProps {
  articleId?: string
  mode: 'create' | 'edit'
}

export default function ArticleForm({ articleId, mode }: ArticleFormProps) {
  const router = useRouter()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)

  const [formData, setFormData] = useState<KnowledgeArticleCreate>({
    title: '',
    slug: '',
    content: '',
    excerpt: '',
    category: 'faq',
    status: 'draft',
    tags: [],
    keywords: [],
    is_featured: false,
    display_order: 0,
  })

  const [tagInput, setTagInput] = useState('')
  const [keywordInput, setKeywordInput] = useState('')

  useEffect(() => {
    if (mode === 'edit' && articleId) {
      loadArticle()
    }
  }, [articleId, mode])

  const loadArticle = async () => {
    if (!articleId) return

    try {
      setLoading(true)
      const response = await customerServiceApi.knowledge.get(articleId)

      if (response.success) {
        const article = response.data!
        setFormData({
          title: article.title,
          slug: article.slug,
          content: article.content,
          excerpt: article.excerpt || '',
          category: article.category,
          status: article.status,
          tags: article.tags,
          keywords: article.keywords,
          is_featured: article.is_featured,
          display_order: article.display_order,
        })
      } else {
        setError('Failed to load article')
      }
    } catch (err: any) {
      setError(err.message || 'Failed to load article')
    } finally {
      setLoading(false)
    }
  }

  const generateSlug = (title: string) => {
    return title
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, '-')
      .replace(/(^-|-$)/g, '')
  }

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
  ) => {
    const { name, value, type } = e.target

    if (type === 'checkbox') {
      const checked = (e.target as HTMLInputElement).checked
      setFormData((prev) => ({ ...prev, [name]: checked }))
    } else if (type === 'number') {
      setFormData((prev) => ({ ...prev, [name]: parseInt(value) || 0 }))
    } else {
      setFormData((prev) => ({ ...prev, [name]: value }))

      // Auto-generate slug from title
      if (name === 'title' && mode === 'create') {
        setFormData((prev) => ({ ...prev, slug: generateSlug(value) }))
      }
    }
  }

  const handleAddTag = () => {
    if (tagInput.trim() && !formData.tags?.includes(tagInput.trim())) {
      setFormData((prev) => ({
        ...prev,
        tags: [...(prev.tags || []), tagInput.trim()],
      }))
      setTagInput('')
    }
  }

  const handleRemoveTag = (tag: string) => {
    setFormData((prev) => ({
      ...prev,
      tags: (prev.tags || []).filter((t) => t !== tag),
    }))
  }

  const handleAddKeyword = () => {
    if (keywordInput.trim() && !formData.keywords?.includes(keywordInput.trim())) {
      setFormData((prev) => ({
        ...prev,
        keywords: [...(prev.keywords || []), keywordInput.trim()],
      }))
      setKeywordInput('')
    }
  }

  const handleRemoveKeyword = (keyword: string) => {
    setFormData((prev) => ({
      ...prev,
      keywords: (prev.keywords || []).filter((k) => k !== keyword),
    }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    setSuccess(null)

    try {
      if (mode === 'create') {
        const response = await customerServiceApi.knowledge.create(formData)
        if (response.success) {
          setSuccess('Article created successfully!')
          setTimeout(() => {
            router.push(`/crm/knowledge/${response.data!.slug}`)
          }, 1500)
        } else {
          setError('Failed to create article')
        }
      } else if (mode === 'edit' && articleId) {
        const updateData: KnowledgeArticleUpdate = { ...formData }
        const response = await customerServiceApi.knowledge.update(articleId, updateData)
        if (response.success) {
          setSuccess('Article updated successfully!')
          setTimeout(() => {
            router.push(`/crm/knowledge/${response.data!.slug}`)
          }, 1500)
        } else {
          setError('Failed to update article')
        }
      }
    } catch (err: any) {
      setError(err.message || 'Failed to save article')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-5xl mx-auto">
        <div className="mb-6">
          <button
            onClick={() => router.back()}
            className="text-blue-600 hover:text-blue-700 mb-4 flex items-center"
          >
            ← Back
          </button>
          <h1 className="text-3xl font-bold text-gray-900">
            {mode === 'create' ? 'Create Knowledge Base Article' : 'Edit Article'}
          </h1>
        </div>

        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
            {error}
          </div>
        )}
        {success && (
          <div className="mb-6 bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg">
            {success}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Basic Information</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Title <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  name="title"
                  value={formData.title}
                  onChange={handleChange}
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Slug <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  name="slug"
                  value={formData.slug}
                  onChange={handleChange}
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Excerpt
                </label>
                <textarea
                  name="excerpt"
                  value={formData.excerpt}
                  onChange={handleChange}
                  rows={2}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Brief summary..."
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Content <span className="text-red-500">*</span>
                </label>
                <textarea
                  name="content"
                  value={formData.content}
                  onChange={handleChange}
                  required
                  rows={15}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 font-mono text-sm"
                  placeholder="Article content (supports HTML/Markdown)..."
                />
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Classification</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Category <span className="text-red-500">*</span>
                </label>
                <select
                  name="category"
                  value={formData.category}
                  onChange={handleChange}
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="faq">FAQ</option>
                  <option value="how_to">How To</option>
                  <option value="troubleshooting">Troubleshooting</option>
                  <option value="policy">Policy</option>
                  <option value="announcement">Announcement</option>
                  <option value="guide">Guide</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Status <span className="text-red-500">*</span>
                </label>
                <select
                  name="status"
                  value={formData.status}
                  onChange={handleChange}
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="draft">Draft</option>
                  <option value="under_review">Under Review</option>
                  <option value="published">Published</option>
                  <option value="archived">Archived</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Display Order
                </label>
                <input
                  type="number"
                  name="display_order"
                  value={formData.display_order}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>

            <div className="mt-4">
              <label className="flex items-center">
                <input
                  type="checkbox"
                  name="is_featured"
                  checked={formData.is_featured}
                  onChange={handleChange}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <span className="ml-2 text-sm font-medium text-gray-700">Featured Article</span>
              </label>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Tags & Keywords</h2>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Tags</label>
                <div className="flex gap-2 mb-2">
                  <input
                    type="text"
                    value={tagInput}
                    onChange={(e) => setTagInput(e.target.value)}
                    onKeyPress={(e) => {
                      if (e.key === 'Enter') {
                        e.preventDefault()
                        handleAddTag()
                      }
                    }}
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Add a tag"
                  />
                  <button
                    type="button"
                    onClick={handleAddTag}
                    className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700"
                  >
                    Add
                  </button>
                </div>
                {formData.tags && formData.tags.length > 0 && (
                  <div className="flex flex-wrap gap-2">
                    {formData.tags.map((tag, index) => (
                      <span
                        key={index}
                        className="inline-flex items-center gap-1 px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm"
                      >
                        {tag}
                        <button type="button" onClick={() => handleRemoveTag(tag)}>
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                          </svg>
                        </button>
                      </span>
                    ))}
                  </div>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Keywords (for SEO)</label>
                <div className="flex gap-2 mb-2">
                  <input
                    type="text"
                    value={keywordInput}
                    onChange={(e) => setKeywordInput(e.target.value)}
                    onKeyPress={(e) => {
                      if (e.key === 'Enter') {
                        e.preventDefault()
                        handleAddKeyword()
                      }
                    }}
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Add a keyword"
                  />
                  <button
                    type="button"
                    onClick={handleAddKeyword}
                    className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700"
                  >
                    Add
                  </button>
                </div>
                {formData.keywords && formData.keywords.length > 0 && (
                  <div className="flex flex-wrap gap-2">
                    {formData.keywords.map((keyword, index) => (
                      <span
                        key={index}
                        className="inline-flex items-center gap-1 px-3 py-1 bg-gray-100 text-gray-800 rounded-full text-sm"
                      >
                        {keyword}
                        <button type="button" onClick={() => handleRemoveKeyword(keyword)}>
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                          </svg>
                        </button>
                      </span>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>

          <div className="flex gap-4">
            <button
              type="submit"
              disabled={loading}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
            >
              {loading ? 'Saving...' : mode === 'create' ? 'Create Article' : 'Update Article'}
            </button>
            <button
              type="button"
              onClick={() => router.back()}
              className="px-6 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200"
            >
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
