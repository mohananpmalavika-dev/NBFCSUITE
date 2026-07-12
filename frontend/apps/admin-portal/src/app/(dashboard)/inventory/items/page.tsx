/**
 * Item Master List Page
 * Display and manage inventory items
 */

'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Plus, Search, Edit, Trash2, Package, AlertTriangle } from 'lucide-react';
import { inventoryService } from '@/services/inventory.service';
import type { ItemMaster, ItemType, ItemStatus } from '@/types/inventory';

export default function ItemMasterListPage() {
  const router = useRouter();
  const [items, setItems] = useState<ItemMaster[]>([]);
  const [loading, setLoading] = useState(true);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize] = useState(50);
  
  // Filters
  const [search, setSearch] = useState('');
  const [itemType, setItemType] = useState<ItemType | ''>('');
  const [itemStatus, setItemStatus] = useState<ItemStatus | ''>('');
  const [lowStockOnly, setLowStockOnly] = useState(false);

  useEffect(() => {
    loadItems();
  }, [page, itemType, itemStatus, lowStockOnly]);

  const loadItems = async () => {
    try {
      setLoading(true);
      const response = await inventoryService.items.list({
        page,
        page_size: pageSize,
        item_type: itemType || undefined,
        item_status: itemStatus || undefined,
        search: search || undefined,
        low_stock_only: lowStockOnly,
      });

      if (response.success && response.data) {
        setItems(response.data.items);
        setTotal(response.data.total);
      }
    } catch (error) {
      console.error('Failed to load items:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = () => {
    setPage(1);
    loadItems();
  };

  const handleDelete = async (itemId: string) => {
    if (!confirm('Are you sure you want to delete this item?')) return;

    try {
      const response = await inventoryService.items.delete(itemId);
      if (response.success) {
        loadItems();
      }
    } catch (error) {
      console.error('Failed to delete item:', error);
      alert('Failed to delete item');
    }
  };

  const getStatusBadge = (status: ItemStatus) => {
    const variants: Record<ItemStatus, 'default' | 'secondary' | 'destructive' | 'outline'> = {
      active: 'default',
      inactive: 'secondary',
      discontinued: 'destructive',
      obsolete: 'outline',
    };
    return <Badge variant={variants[status]}>{status}</Badge>;
  };

  const isLowStock = (item: ItemMaster) => {
    return item.current_stock <= item.reorder_level;
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">Item Master</h1>
        <Button onClick={() => router.push('/inventory/items/new')}>
          <Plus className="mr-2 h-4 w-4" />
          New Item
        </Button>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="pt-6">
          <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
            <div className="md:col-span-2">
              <Input
                placeholder="Search by code, name, barcode..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
              />
            </div>
            <Select value={itemType} onValueChange={(value) => setItemType(value as ItemType | '')}>
              <SelectTrigger>
                <SelectValue placeholder="Item Type" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="">All Types</SelectItem>
                <SelectItem value="raw_material">Raw Material</SelectItem>
                <SelectItem value="finished_goods">Finished Goods</SelectItem>
                <SelectItem value="work_in_progress">Work In Progress</SelectItem>
                <SelectItem value="consumables">Consumables</SelectItem>
                <SelectItem value="spare_parts">Spare Parts</SelectItem>
              </SelectContent>
            </Select>
            <Select value={itemStatus} onValueChange={(value) => setItemStatus(value as ItemStatus | '')}>
              <SelectTrigger>
                <SelectValue placeholder="Status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="">All Status</SelectItem>
                <SelectItem value="active">Active</SelectItem>
                <SelectItem value="inactive">Inactive</SelectItem>
                <SelectItem value="discontinued">Discontinued</SelectItem>
              </SelectContent>
            </Select>
            <Button onClick={handleSearch} className="w-full">
              <Search className="mr-2 h-4 w-4" />
              Search
            </Button>
          </div>
          <div className="mt-4">
            <label className="flex items-center space-x-2 cursor-pointer">
              <input
                type="checkbox"
                checked={lowStockOnly}
                onChange={(e) => setLowStockOnly(e.target.checked)}
                className="rounded"
              />
              <span className="text-sm">Show only low stock items</span>
            </label>
          </div>
        </CardContent>
      </Card>

      {/* Items Table */}
      <Card>
        <CardHeader>
          <CardTitle>
            Items ({total})
          </CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-center py-8">Loading...</div>
          ) : items.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              No items found
            </div>
          ) : (
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Item Code</TableHead>
                    <TableHead>Item Name</TableHead>
                    <TableHead>Type</TableHead>
                    <TableHead>Category</TableHead>
                    <TableHead className="text-right">Current Stock</TableHead>
                    <TableHead>Unit</TableHead>
                    <TableHead className="text-right">Avg Cost</TableHead>
                    <TableHead className="text-right">Total Value</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead className="text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {items.map((item) => (
                    <TableRow key={item.id}>
                      <TableCell className="font-medium">
                        <div className="flex items-center">
                          {isLowStock(item) && (
                            <AlertTriangle className="h-4 w-4 text-amber-500 mr-2" />
                          )}
                          {item.item_code}
                        </div>
                      </TableCell>
                      <TableCell>{item.item_name}</TableCell>
                      <TableCell>
                        <span className="text-xs capitalize">
                          {item.item_type.replace(/_/g, ' ')}
                        </span>
                      </TableCell>
                      <TableCell>{item.category || '-'}</TableCell>
                      <TableCell className="text-right font-mono">
                        {item.current_stock.toFixed(3)}
                      </TableCell>
                      <TableCell>{item.base_unit}</TableCell>
                      <TableCell className="text-right font-mono">
                        ₹{item.average_cost.toFixed(2)}
                      </TableCell>
                      <TableCell className="text-right font-mono">
                        ₹{item.total_value.toFixed(2)}
                      </TableCell>
                      <TableCell>{getStatusBadge(item.item_status)}</TableCell>
                      <TableCell className="text-right">
                        <div className="flex justify-end space-x-2">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => router.push(`/inventory/items/${item.id}`)}
                          >
                            <Package className="h-4 w-4" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => router.push(`/inventory/items/${item.id}/edit`)}
                          >
                            <Edit className="h-4 w-4" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleDelete(item.id)}
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          )}

          {/* Pagination */}
          {total > pageSize && (
            <div className="flex justify-between items-center mt-4">
              <div className="text-sm text-muted-foreground">
                Showing {(page - 1) * pageSize + 1} to {Math.min(page * pageSize, total)} of {total}
              </div>
              <div className="flex space-x-2">
                <Button
                  variant="outline"
                  size="sm"
                  disabled={page === 1}
                  onClick={() => setPage(page - 1)}
                >
                  Previous
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  disabled={page * pageSize >= total}
                  onClick={() => setPage(page + 1)}
                >
                  Next
                </Button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
