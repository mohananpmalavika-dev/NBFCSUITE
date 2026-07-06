'use client';

import { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { DashboardLayout } from '@/components/layout/dashboard-layout';
import {
  createAuction,
  getAuctions,
  getAuction,
  startAuction,
  registerBidder,
  submitBid,
  completeAuction,
  sendAuctionNotice,
  getUpcomingAuctions,
  type Auction,
  type AuctionBid
} from '@/services/gold-loan.service';
import { formatCurrency, formatDate, formatDateTime } from '@/lib/utils';

export default function AuctionsPage() {
  const [auctions, setAuctions] = useState<Auction[]>([]);
  const [upcomingAuctions, setUpcomingAuctions] = useState<Auction[]>([]);
  const [selectedAuction, setSelectedAuction] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [showBidForm, setShowBidForm] = useState(false);
  const [showBidderForm, setShowBidderForm] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState('all');

  const [createForm, setCreateForm] = useState({
    gold_loan_id: '',
    auction_date: '',
    auction_venue: '',
    auction_mode: 'Offline',
    notice_period_days: '30',
    remarks: ''
  });

  const [bidderForm, setBidderForm] = useState({
    auction_id: '',
    bidder_name: '',
    bidder_contact: '',
    bidder_email: '',
    emd_amount: '',
    emd_payment_reference: ''
  });

  const [bidForm, setBidForm] = useState({
    auction_id: '',
    bidder_name: '',
    bidder_contact: '',
    bid_amount: '',
    remarks: ''
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);
      const [allAuctions, upcoming] = await Promise.all([
        getAuctions({}),
        getUpcomingAuctions()
      ]);
      setAuctions(allAuctions.auctions || []);
      setUpcomingAuctions(upcoming.auctions || []);
    } catch (error: any) {
      console.error('Failed to load auctions:', error);
      setError(error.response?.data?.error?.message || 'Failed to load auctions');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateAuction = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setError(null);
      await createAuction({
        gold_loan_id: createForm.gold_loan_id,
        auction_date: createForm.auction_date,
        auction_venue: createForm.auction_venue || undefined,
        auction_mode: createForm.auction_mode,
        notice_period_days: parseInt(createForm.notice_period_days),
        remarks: createForm.remarks || undefined
      });
      setShowCreateForm(false);
      setCreateForm({ gold_loan_id: '', auction_date: '', auction_venue: '', auction_mode: 'Offline', notice_period_days: '30', remarks: '' });
      await loadData();
      alert('Auction created successfully with legal notice');
    } catch (error: any) {
      setError(error.response?.data?.error?.message || 'Failed to create auction');
    }
  };

  const handleStartAuction = async (id: string) => {
    if (!confirm('Start this auction?')) return;
    try {
      await startAuction(id);
      await loadData();
      alert('Auction started successfully');
    } catch (error: any) {
      alert('Failed to start auction');
    }
  };

  const handleRegisterBidder = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await registerBidder(bidderForm.auction_id, {
        bidder_name: bidderForm.bidder_name,
        bidder_contact: bidderForm.bidder_contact,
        bidder_email: bidderForm.bidder_email || undefined,
        emd_amount: parseFloat(bidderForm.emd_amount),
        emd_payment_reference: bidderForm.emd_payment_reference
      });
      setShowBidderForm(false);
      setBidderForm({ auction_id: '', bidder_name: '', bidder_contact: '', bidder_email: '', emd_amount: '', emd_payment_reference: '' });
      if (selectedAuction) {
        const details = await getAuction(selectedAuction.id);
        setSelectedAuction(details);
      }
      alert('Bidder registered successfully');
    } catch (error: any) {
      alert('Failed to register bidder');
    }
  };

  const handleSubmitBid = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await submitBid({
        auction_id: bidForm.auction_id,
        bidder_name: bidForm.bidder_name,
        bidder_contact: bidForm.bidder_contact,
        bid_amount: parseFloat(bidForm.bid_amount),
        remarks: bidForm.remarks || undefined
      });
      setShowBidForm(false);
      setBidForm({ auction_id: '', bidder_name: '', bidder_contact: '', bid_amount: '', remarks: '' });
      if (selectedAuction) {
        const details = await getAuction(selectedAuction.id);
        setSelectedAuction(details);
      }
      alert('Bid submitted successfully');
    } catch (error: any) {
      alert('Failed to submit bid');
    }
  };

  const handleCompleteAuction = async (auctionId: string, winningBidId: string) => {
    if (!confirm('Complete this auction with the selected winning bid?')) return;
    try {
      await completeAuction(auctionId, {
        winning_bid_id: winningBidId,
        sale_completion_date: new Date().toISOString(),
        remarks: undefined
      });
      await loadData();
      alert('Auction completed successfully');
    } catch (error: any) {
      alert('Failed to complete auction');
    }
  };

  const viewAuctionDetails = async (id: string) => {
    try {
      const details = await getAuction(id);
      setSelectedAuction(details);
      setActiveTab('details');
    } catch (error: any) {
      alert('Failed to load auction details');
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'Scheduled': return <Badge variant="secondary">Scheduled</Badge>;
      case 'Notice Sent': return <Badge className="bg-blue-600">Notice Sent</Badge>;
      case 'Active': return <Badge className="bg-green-600">Active</Badge>;
      case 'Completed': return <Badge className="bg-gray-600">Completed</Badge>;
      case 'Cancelled': return <Badge className="bg-red-600">Cancelled</Badge>;
      default: return <Badge variant="outline">{status}</Badge>;
    }
  };

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {error && (
          <Card className="border-red-200 bg-red-50">
            <CardContent className="pt-6">
              <div className="flex items-start gap-3">
                <svg className="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <div className="flex-1">
                  <h3 className="text-red-800 font-medium">Error</h3>
                  <p className="text-red-700 text-sm">{error}</p>
                </div>
                <Button variant="outline" size="sm" onClick={() => setError(null)}>Dismiss</Button>
              </div>
            </CardContent>
          </Card>
        )}

        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold">Auction Management</h1>
            <p className="text-muted-foreground">Manage gold loan auctions, bidders, and completions</p>
          </div>
          <Button onClick={() => setShowCreateForm(true)}>
            <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            Create Auction
          </Button>
        </div>

        {showCreateForm && (
          <Card className="border-2 border-blue-200">
            <CardHeader>
              <CardTitle>Create New Auction</CardTitle>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleCreateAuction} className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium mb-2">Gold Loan ID *</label>
                    <Input value={createForm.gold_loan_id} onChange={(e) => setCreateForm({ ...createForm, gold_loan_id: e.target.value })} required />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">Auction Date *</label>
                    <Input type="datetime-local" value={createForm.auction_date} onChange={(e) => setCreateForm({ ...createForm, auction_date: e.target.value })} required />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">Auction Venue</label>
                    <Input value={createForm.auction_venue} onChange={(e) => setCreateForm({ ...createForm, auction_venue: e.target.value })} />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">Auction Mode *</label>
                    <select value={createForm.auction_mode} onChange={(e) => setCreateForm({ ...createForm, auction_mode: e.target.value })} className="w-full px-3 py-2 border rounded-md" required>
                      <option value="Offline">Offline</option>
                      <option value="Online">Online</option>
                      <option value="Hybrid">Hybrid</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">Notice Period (Days) *</label>
                    <Input type="number" value={createForm.notice_period_days} onChange={(e) => setCreateForm({ ...createForm, notice_period_days: e.target.value })} required />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">Remarks</label>
                    <Input value={createForm.remarks} onChange={(e) => setCreateForm({ ...createForm, remarks: e.target.value })} />
                  </div>
                </div>
                <div className="flex justify-end gap-2">
                  <Button type="button" variant="outline" onClick={() => setShowCreateForm(false)}>Cancel</Button>
                  <Button type="submit">Create Auction</Button>
                </div>
              </form>
            </CardContent>
          </Card>
        )}

        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList>
            <TabsTrigger value="all">All Auctions</TabsTrigger>
            <TabsTrigger value="upcoming">Upcoming</TabsTrigger>
            <TabsTrigger value="details">Details</TabsTrigger>
          </TabsList>

          <TabsContent value="all">
            <Card>
              <CardHeader>
                <CardTitle>All Auctions</CardTitle>
              </CardHeader>
              <CardContent>
                {loading ? (
                  <div className="text-center py-12">Loading...</div>
                ) : auctions.length === 0 ? (
                  <div className="text-center py-12 text-muted-foreground">No auctions found</div>
                ) : (
                  <div className="overflow-x-auto">
                    <table className="w-full">
                      <thead className="bg-muted/50">
                        <tr>
                          <th className="text-left p-4 font-medium">Auction #</th>
                          <th className="text-left p-4 font-medium">Loan ID</th>
                          <th className="text-left p-4 font-medium">Auction Date</th>
                          <th className="text-left p-4 font-medium">Venue/Mode</th>
                          <th className="text-right p-4 font-medium">Reserve Price</th>
                          <th className="text-center p-4 font-medium">Status</th>
                          <th className="text-center p-4 font-medium">Actions</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y">
                        {auctions.map((auction) => (
                          <tr key={auction.id} className="hover:bg-muted/50">
                            <td className="p-4">
                              <div className="font-medium">{auction.auction_number}</div>
                              <div className="text-xs text-muted-foreground">{formatDate(auction.created_at)}</div>
                            </td>
                            <td className="p-4">{auction.gold_loan_id}</td>
                            <td className="p-4">{formatDateTime(auction.auction_date)}</td>
                            <td className="p-4">
                              <div>{auction.auction_venue || 'Not set'}</div>
                              <Badge variant="outline" className="mt-1">{auction.auction_mode}</Badge>
                            </td>
                            <td className="p-4 text-right font-medium">{formatCurrency(auction.reserve_price)}</td>
                            <td className="p-4 text-center">{getStatusBadge(auction.status)}</td>
                            <td className="p-4">
                              <div className="flex gap-2 justify-center">
                                <Button size="sm" variant="outline" onClick={() => viewAuctionDetails(auction.id)}>View</Button>
                                {auction.status === 'Scheduled' && (
                                  <Button size="sm" onClick={() => handleStartAuction(auction.id)}>Start</Button>
                                )}
                              </div>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="upcoming">
            <Card>
              <CardHeader>
                <CardTitle>Upcoming Auctions</CardTitle>
              </CardHeader>
              <CardContent>
                {upcomingAuctions.length === 0 ? (
                  <div className="text-center py-12 text-muted-foreground">No upcoming auctions</div>
                ) : (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {upcomingAuctions.map((auction) => (
                      <Card key={auction.id} className="border-2">
                        <CardContent className="pt-6">
                          <div className="flex justify-between items-start mb-4">
                            <div>
                              <h3 className="font-bold text-lg">{auction.auction_number}</h3>
                              <p className="text-sm text-muted-foreground">{auction.gold_loan_id}</p>
                            </div>
                            {getStatusBadge(auction.status)}
                          </div>
                          <div className="space-y-2 text-sm">
                            <div className="flex justify-between">
                              <span className="text-muted-foreground">Auction Date:</span>
                              <span className="font-medium">{formatDateTime(auction.auction_date)}</span>
                            </div>
                            <div className="flex justify-between">
                              <span className="text-muted-foreground">Reserve Price:</span>
                              <span className="font-medium">{formatCurrency(auction.reserve_price)}</span>
                            </div>
                            <div className="flex justify-between">
                              <span className="text-muted-foreground">Mode:</span>
                              <Badge variant="outline">{auction.auction_mode}</Badge>
                            </div>
                          </div>
                          <div className="mt-4 pt-4 border-t">
                            <Button size="sm" className="w-full" onClick={() => viewAuctionDetails(auction.id)}>View Details</Button>
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="details">
            {!selectedAuction ? (
              <Card>
                <CardContent className="py-12">
                  <div className="text-center text-muted-foreground">Select an auction to view details</div>
                </CardContent>
              </Card>
            ) : (
              <div className="space-y-4">
                <Card>
                  <CardHeader>
                    <div className="flex justify-between items-start">
                      <div>
                        <CardTitle>{selectedAuction.auction.auction_number}</CardTitle>
                        <p className="text-muted-foreground mt-1">{selectedAuction.auction.gold_loan_id}</p>
                      </div>
                      {getStatusBadge(selectedAuction.auction.status)}
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <p className="text-sm text-muted-foreground">Auction Date</p>
                        <p className="font-medium">{formatDateTime(selectedAuction.auction.auction_date)}</p>
                      </div>
                      <div>
                        <p className="text-sm text-muted-foreground">Reserve Price</p>
                        <p className="font-medium">{formatCurrency(selectedAuction.auction.reserve_price)}</p>
                      </div>
                      <div>
                        <p className="text-sm text-muted-foreground">Starting Bid</p>
                        <p className="font-medium">{formatCurrency(selectedAuction.auction.starting_bid)}</p>
                      </div>
                      <div>
                        <p className="text-sm text-muted-foreground">EMD Amount</p>
                        <p className="font-medium">{formatCurrency(selectedAuction.auction.emd_amount)}</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <div className="flex justify-between items-center">
                      <CardTitle>Bids ({selectedAuction.bids?.length || 0})</CardTitle>
                      <Button size="sm" onClick={() => { setBidForm({ ...bidForm, auction_id: selectedAuction.auction.id }); setShowBidForm(true); }}>Submit Bid</Button>
                    </div>
                  </CardHeader>
                  <CardContent>
                    {!selectedAuction.bids || selectedAuction.bids.length === 0 ? (
                      <div className="text-center py-8 text-muted-foreground">No bids yet</div>
                    ) : (
                      <div className="space-y-3">
                        {selectedAuction.bids.map((bid: AuctionBid, index: number) => (
                          <div key={bid.id} className={`p-4 border rounded-lg ${bid.is_winning_bid ? 'border-green-500 bg-green-50' : ''}`}>
                            <div className="flex justify-between items-start">
                              <div>
                                <div className="font-medium">{bid.bidder_name}</div>
                                <div className="text-sm text-muted-foreground">{bid.bidder_contact}</div>
                              </div>
                              <div className="text-right">
                                <div className="text-xl font-bold">{formatCurrency(bid.bid_amount)}</div>
                                <Badge variant="outline" className="mt-1">Rank #{bid.bid_rank || index + 1}</Badge>
                                {bid.is_winning_bid && <Badge className="ml-2 bg-green-600">Winner</Badge>}
                              </div>
                            </div>
                            {selectedAuction.auction.status === 'Active' && !selectedAuction.auction.winning_bid_id && (
                              <Button size="sm" className="mt-3 w-full" onClick={() => handleCompleteAuction(selectedAuction.auction.id, bid.id)}>
                                Select as Winner
                              </Button>
                            )}
                          </div>
                        ))}
                      </div>
                    )}
                  </CardContent>
                </Card>
              </div>
            )}
          </TabsContent>
        </Tabs>

        {showBidForm && (
          <Card className="border-2 border-green-200">
            <CardHeader>
              <CardTitle>Submit Bid</CardTitle>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmitBid} className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium mb-2">Bidder Name *</label>
                    <Input value={bidForm.bidder_name} onChange={(e) => setBidForm({ ...bidForm, bidder_name: e.target.value })} required />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">Bidder Contact *</label>
                    <Input value={bidForm.bidder_contact} onChange={(e) => setBidForm({ ...bidForm, bidder_contact: e.target.value })} required />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">Bid Amount *</label>
                    <Input type="number" step="0.01" value={bidForm.bid_amount} onChange={(e) => setBidForm({ ...bidForm, bid_amount: e.target.value })} required />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">Remarks</label>
                    <Input value={bidForm.remarks} onChange={(e) => setBidForm({ ...bidForm, remarks: e.target.value })} />
                  </div>
                </div>
                <div className="flex justify-end gap-2">
                  <Button type="button" variant="outline" onClick={() => setShowBidForm(false)}>Cancel</Button>
                  <Button type="submit">Submit Bid</Button>
                </div>
              </form>
            </CardContent>
          </Card>
        )}
      </div>
    </DashboardLayout>
  );
}
