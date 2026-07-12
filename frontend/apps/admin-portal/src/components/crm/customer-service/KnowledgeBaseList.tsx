"use client";

import { useState } from "react";
import Link from "next/link";
import { Eye, ThumbsUp, ThumbsDown, Star, Edit, Trash2, Archive } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Pagination,
  PaginationContent,
  PaginationItem,
  PaginationLink,
  PaginationNext,
  PaginationPrevious,
} from "@/components/ui/pagination";

interface Article {
  id: string;
  title: string;
  category: string;
  status: string;
  view_count: number;
  helpful_count: number;
  not_helpful_count: number;
  average_rating: number;
  author_name: string;
  created_at: string;
  updated_at: string;
}

interface KnowledgeBaseListProps {
  articles: Article[];
  loading: boolean;
  pagination: {
    page: number;
    pageSize: number;
    total: number;
    totalPages: number;
  };
  onPageChange: (page: number) => void;
  onRefresh: () => void;
}

export function KnowledgeBaseList({
  articles,
  loading,
  pagination,
  onPageChange,
  onRefresh,
}: KnowledgeBaseListProps) {
  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="text-muted-foreground">Loading articles...</div>
      </div>
    );
  }

  if (articles.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center p-8 text-center">
        <p className="text-muted-foreground mb-4">No articles found</p>
        <Button onClick={onRefresh} variant="outline">
          Refresh
        </Button>
      </div>
    );
  }

  const getCategoryBadge = (category: string) => {
    const colors: Record<string, string> = {
      getting_started: "bg-blue-100 text-blue-800",
      account_management: "bg-purple-100 text-purple-800",
      loan_products: "bg-green-100 text-green-800",
      deposit_products: "bg-cyan-100 text-cyan-800",
      payments: "bg-orange-100 text-orange-800",
      troubleshooting: "bg-red-100 text-red-800",
      faq: "bg-yellow-100 text-yellow-800",
      policies: "bg-indigo-100 text-indigo-800",
      technical: "bg-gray-100 text-gray-800",
      other: "bg-slate-100 text-slate-800",
    };

    return colors[category] || "bg-gray-100 text-gray-800";
  };

  const getStatusBadge = (status: string) => {
    const colors: Record<string, string> = {
      published: "bg-green-100 text-green-800",
      draft: "bg-gray-100 text-gray-800",
      review: "bg-yellow-100 text-yellow-800",
      archived: "bg-red-100 text-red-800",
    };

    return colors[status] || "bg-gray-100 text-gray-800";
  };

  return (
    <div className="space-y-4">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Title</TableHead>
            <TableHead>Category</TableHead>
            <TableHead>Status</TableHead>
            <TableHead className="text-right">Views</TableHead>
            <TableHead className="text-right">Rating</TableHead>
            <TableHead className="text-right">Helpful</TableHead>
            <TableHead>Author</TableHead>
            <TableHead>Updated</TableHead>
            <TableHead className="text-right">Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {articles.map((article) => (
            <TableRow key={article.id}>
              <TableCell>
                <Link
                  href={`/crm/knowledge/${article.id}`}
                  className="font-medium hover:underline"
                >
                  {article.title}
                </Link>
              </TableCell>
              <TableCell>
                <Badge className={getCategoryBadge(article.category)}>
                  {article.category.replace("_", " ")}
                </Badge>
              </TableCell>
              <TableCell>
                <Badge className={getStatusBadge(article.status)}>
                  {article.status}
                </Badge>
              </TableCell>
              <TableCell className="text-right">
                <div className="flex items-center justify-end gap-1">
                  <Eye className="h-3 w-3" />
                  {article.view_count}
                </div>
              </TableCell>
              <TableCell className="text-right">
                <div className="flex items-center justify-end gap-1">
                  <Star className="h-3 w-3 fill-yellow-400 text-yellow-400" />
                  {article.average_rating?.toFixed(1) || "N/A"}
                </div>
              </TableCell>
              <TableCell className="text-right">
                <div className="flex items-center justify-end gap-2">
                  <span className="flex items-center gap-1 text-green-600">
                    <ThumbsUp className="h-3 w-3" />
                    {article.helpful_count}
                  </span>
                  <span className="flex items-center gap-1 text-red-600">
                    <ThumbsDown className="h-3 w-3" />
                    {article.not_helpful_count}
                  </span>
                </div>
              </TableCell>
              <TableCell>{article.author_name}</TableCell>
              <TableCell>
                {new Date(article.updated_at).toLocaleDateString()}
              </TableCell>
              <TableCell className="text-right">
                <div className="flex items-center justify-end gap-2">
                  <Button variant="ghost" size="sm" asChild>
                    <Link href={`/crm/knowledge/${article.id}/edit`}>
                      <Edit className="h-4 w-4" />
                    </Link>
                  </Button>
                  <Button variant="ghost" size="sm">
                    <Archive className="h-4 w-4" />
                  </Button>
                </div>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>

      {pagination.totalPages > 1 && (
        <Pagination>
          <PaginationContent>
            <PaginationItem>
              <PaginationPrevious
                onClick={() =>
                  pagination.page > 1 && onPageChange(pagination.page - 1)
                }
                className={
                  pagination.page === 1 ? "pointer-events-none opacity-50" : ""
                }
              />
            </PaginationItem>
            {Array.from({ length: pagination.totalPages }, (_, i) => i + 1).map(
              (page) => (
                <PaginationItem key={page}>
                  <PaginationLink
                    onClick={() => onPageChange(page)}
                    isActive={pagination.page === page}
                  >
                    {page}
                  </PaginationLink>
                </PaginationItem>
              )
            )}
            <PaginationItem>
              <PaginationNext
                onClick={() =>
                  pagination.page < pagination.totalPages &&
                  onPageChange(pagination.page + 1)
                }
                className={
                  pagination.page === pagination.totalPages
                    ? "pointer-events-none opacity-50"
                    : ""
                }
              />
            </PaginationItem>
          </PaginationContent>
        </Pagination>
      )}
    </div>
  );
}
