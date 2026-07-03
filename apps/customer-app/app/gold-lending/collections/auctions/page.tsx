'use client';

import { useState, useEffect } from 'react';
import { goldApi } from '../../goldApi';

export default function AuctionManagementPage() {
  const [auctions, setAuctions] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({ lot_status: '', auction_type: '', skip: 0, limit: 50 });

  useEffect(() => {
    goldApi.getAuctionLots(filters)
      .then(data => setAuctions(data.items || []))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [filters]);

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      'planned': 'bg-gray-100 text-gray-800',
      'approved': 'bg-blue-100 text-blue-800',
      'advertised': 'bg-yellow-100 text-yellow-800',
      'open': 'bg-green-100 text-green-800',
      'closed': 'bg-purple-100 text-purple-800',
      'sold': 'bg-teal-100 text-teal-800',
      'unsold': 'bg-red-100 text-red-800',
      'cancelled': 'bg-gray-900 text-white'
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };

  if (loading) return <div className="flex items-center justify-center min-h-screen"><div className="text-lg">Loading...</div></div>;

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <div className="mb-6 flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Auction Management</h1>
          <p className="text-gray-600 mt-2">Manage gold collateral auctions and bidding</p>
        </div>
        <button className="bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700">Create Auction Lot</button>
      </div>

      <div className="bg-white p-4 rounded-lg shadow mb-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <select
            value={filters.lot_status}
            onChange={(e) => setFilters({ ...filters, lot_status: e.target.value })}
            className="border border-gray-300 rounded-md px-3 py-2"
          >
            <option value="">All Statuses</option>
            <option value="planned">Planned</option>
            <option value="approved">Approved</option>
            <option value="advertised">Advertised</option>
            <option value="open">Open</option>
            <option value="closed">Closed</option>
            <option value="sold">Sold</option>
            <option value="unsold">Unsold</option>
          </select>
          <select
            value={filters.auction_type}
            onChange={(e) => setFilters({ ...filters, auction_type: e.target.value })}
            className="border border-gray-300 rounded-md px-3 py-2"
          >
            <option value="">All Types</option>
            <option value="public">Public</option>
            <option value="private">Private</option>
            <option value="online">Online</option>
            <option value="sealed_bid">Sealed Bid</option>
            <option value="spot_sale">Spot Sale</option>
          </select>
          <button
            onClick={() => setFilters({ lot_status: '', auction_type: '', skip: 0, limit: 50 })}
            className="bg-gray-200 text-gray-800 px-4 py-2 rounded-md hover:bg-gray-300"
          >
            Clear
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-6">
        {[
          { label: 'Total Lots', value: auctions.length },
          { label: 'Open', value: auctions.filter(a => a.lot_status === 'open').length },
          { label: 'Sold', value: auctions.filter(a => a.lot_status === 'sold').length },
          { label: 'Total Gold', value: `${auctions.reduce((sum, a) => sum + Number(a.total_gold_weight || 0), 0).toFixed(2)} gm` },
          { label: 'Total Value', value: `₹${auctions.reduce((sum, a) => sum + Number(a.reserve_price || 0), 0).toLocaleString('en-IN')}` },
        ].map(stat => (
          <div key={stat.label} className="bg-white p-4 rounded-lg shadow">
            <div className="text-sm text-gray-600">{stat.label}</div>
            <div className="text-2xl font-bold text-gray-900 mt-1">{stat.value}</div>
          </div>
        ))}
      </div>

      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              {['Lot Number', 'Auction Date', 'Type', 'Status', 'Items', 'Gold Weight', 'Reserve Price', 'Bids', 'Winning Bid', 'Actions'].map(header => (
                <th key={header} className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">{header}</th>
              ))}
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {auctions.map(auction => (
              <tr key={auction.id} className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-blue-600">{auction.lot_number}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm">{new Date(auction.auction_date).toLocaleDateString()}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm capitalize">{auction.auction_type.replace('_', ' ')}</td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${getStatusColor(auction.lot_status)}`}>
                    {auction.lot_status}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm">{auction.total_items}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm">{auction.total_gold_weight} gm</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm">₹{Number(auction.reserve_price).toLocaleString('en-IN')}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm">{auction.bid_count || 0}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm">
                  {auction.winning_bid_amount ? `₹${Number(auction.winning_bid_amount).toLocaleString('en-IN')}` : '-'}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                  <button className="text-blue-600 hover:text-blue-900 mr-3">View</button>
                  {auction.lot_status === 'planned' && (
                    <button className="text-green-600 hover:text-green-900">Approve</button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {auctions.length === 0 && <div className="text-center py-12 text-gray-500">No auction lots found</div>}
      </div>
    </div>
  );
}
