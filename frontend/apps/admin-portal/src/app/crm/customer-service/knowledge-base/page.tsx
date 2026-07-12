"use client";

import { useState, useEffect } from "react";
import { Plus, Search, BookOpen, Eye, ThumbsUp, Star } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { KnowledgeBaseList } from "@/components/crm/customer-service/KnowledgeBaseList";
import { CreateArticleDialog } from "@/components/crm/customer-service/CreateArticleDialog";
import { useToast } from "@/hooks/use-toast";
import { customerServiceApi } from "@/lib/api/customer-service";

export default function KnowledgeBasePage() {
  const [articles, setArticles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [selectedStatus, setSelectedStatus] = useState("published");
  const [pagination, setPagination] = useState({
    page: 1,
    pageSize: 20,
    total: 0,
    totalPages: 0
  });

  const { toast } = useToast();

  const categories = [
    { value: "getting_started", label: "Getting Started", icon: "🚀" },
    { value: "account_management", label: "Account Management", icon: "👤" },
    { value: "loan_products", label: "Loan Products", icon: "💰" },
    { value: "deposit_products", label: "Deposit Products", icon: "🏦" },
    { value: "payments", label: "Payments", icon: "💳" },
    { value: "troubleshooting", label: "Troubleshooting", icon: "🔧" },
    { value: "faq", label: "FAQ", icon: "❓" },
    { value: "policies", label: "Policies", icon: "📋" },
    { value: "technical", label: "Technical", icon: "⚙️" },
    { value: "other", label: "Other", icon: "📁" }
  ];

  useEffect(() => {
    fetchArticles();
  }, [pagination.page, selectedCategory, selectedStatus]);

  const fetchArticles = async () => {
    try {
      setLoading(true);
      const response = await customerServiceApi.listKnowledgeBase({
        category: selectedCategory,
        status: selectedStatus,
        page: pagination.page,
        page_size: pagination.pageSize
      });

      setArticles(response.articles);
      setPagination({
        ...pagination,
        total: response.total,
        totalPages: response.total_pages
      });
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to fetch articles",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!searchQuery.trim()) {
      fetchArticles();
      return;
    }

    try {
      setLoading(true);
      const response = await customerServiceApi.searchKnowledgeBase(searchQuery, selectedCategory);
      setArticles(response.articles);
      setPagination({
        ...pagination,
        total: response.total,
        totalPages: 1
      });
    } catch (error) {
      toast({
        title: "Error",
        description: "Search failed",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const handleCreateArticle = () => {
    setShowCreateDialog(true);
  };

  const handleArticleCreated = () => {
    setShowCreateDialog(false);
    fetchArticles();
    toast({
      title: "Success",
      description: "Article created successfully"
    });
  };

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Knowledge Base</h1>
          <p className="text-muted-foreground">
            Create and manage self-service help articles
          </p>
        </div>
        <Button onClick={handleCreateArticle}>
          <Plus className="h-4 w-4 mr-2" />
          Create Article
        </Button>
      </div>

      {/* Statistics */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Articles</CardTitle>
            <BookOpen className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{pagination.total}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Views</CardTitle>
            <Eye className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {articles.reduce((sum: number, a: any) => sum + (a.view_count || 0), 0)}
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Helpful Votes</CardTitle>
            <ThumbsUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {articles.reduce((sum: number, a: any) => sum + (a.helpful_count || 0), 0)}
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Avg Rating</CardTitle>
            <Star className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {articles.length > 0
                ? (
                    articles.reduce((sum: number, a: any) => sum + (a.average_rating || 0), 0) /
                    articles.filter((a: any) => a.average_rating).length
                  ).toFixed(1)
                : "N/A"}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Search Bar */}
      <form onSubmit={handleSearch} className="flex gap-2">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search knowledge base..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10"
          />
        </div>
        <Button type="submit">Search</Button>
      </form>

      {/* Status Tabs */}
      <Tabs value={selectedStatus} onValueChange={setSelectedStatus}>
        <TabsList>
          <TabsTrigger value="published">Published</TabsTrigger>
          <TabsTrigger value="draft">Drafts</TabsTrigger>
          <TabsTrigger value="review">Under Review</TabsTrigger>
          <TabsTrigger value="archived">Archived</TabsTrigger>
        </TabsList>
      </Tabs>

      <div className="grid gap-6 lg:grid-cols-4">
        {/* Categories Sidebar */}
        <Card className="lg:col-span-1">
          <CardHeader>
            <CardTitle className="text-base">Categories</CardTitle>
          </CardHeader>
          <CardContent className="space-y-1">
            <Button
              variant={selectedCategory === null ? "secondary" : "ghost"}
              className="w-full justify-start"
              onClick={() => setSelectedCategory(null)}
            >
              All Categories
            </Button>
            {categories.map((category) => (
              <Button
                key={category.value}
                variant={selectedCategory === category.value ? "secondary" : "ghost"}
                className="w-full justify-start"
                onClick={() => setSelectedCategory(category.value)}
              >
                <span className="mr-2">{category.icon}</span>
                {category.label}
              </Button>
            ))}
          </CardContent>
        </Card>

        {/* Articles List */}
        <div className="lg:col-span-3">
          <Card>
            <CardHeader>
              <CardTitle>Articles</CardTitle>
              <CardDescription>
                {pagination.total} article{pagination.total !== 1 ? "s" : ""} found
              </CardDescription>
            </CardHeader>
            <CardContent>
              <KnowledgeBaseList
                articles={articles}
                loading={loading}
                pagination={pagination}
                onPageChange={(page) => setPagination({ ...pagination, page })}
                onRefresh={fetchArticles}
              />
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Create Article Dialog */}
      {showCreateDialog && (
        <CreateArticleDialog
          open={showCreateDialog}
          onClose={() => setShowCreateDialog(false)}
          onSuccess={handleArticleCreated}
        />
      )}
    </div>
  );
}
