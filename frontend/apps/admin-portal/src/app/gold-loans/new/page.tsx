'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { useToast } from '@/hooks/use-toast';
import {
  getGoldLoanProducts,
  createGoldLoan,
  getOrnamentTypes,
  getPurityOptions,
  calculateLTV,
  type GoldLoanProduct,
  type GoldOrnament,
  type CreateGoldLoanData
} from '@/services/gold-loan.service';
import { formatCurrency } from '@/lib/utils';

export default function NewGoldLoanPage() {
  const router = useRouter();
  const { toast } = useToast();

  // Form state
  const [products, setProducts] = useState<GoldLoanProduct[]>([]);
  const [ornamentTypes, setOrnamentTypes] = useState<string[]>([]);
  const [purityOptions, setPurityOptions] = useState<Array<{ karat: number; percentage: number; label: string }>>([]);
  
  const [customerId, setCustomerId] = useState('');
  const [productId, setProductId] = useState('');
  const [loanAmount, setLoanAmount] = useState('');
  const [tenureMonths, setTenureMonths] = useState('');
  const [repaymentFrequency, setRepaymentFrequency] = useState('Monthly');
  const [ornaments, setOrnaments] = useState<GoldOrnament[]>([]);
  
  // Current ornament being added
  const [currentOrnament, setCurrentOrnament] = useState<Partial<GoldOrnament>>({
    ornament_type: '',
    ornament_description: '',
    quantity: 1,
    purity_karat: 22,
    purity_percentage: 91.67,
    gross_weight_grams: 0,
    stone_weight_grams: 0,
    net_weight_grams: 0,
    gold_rate_per_gram: 5500,
    market_value: 0,
    appraised_value: 0,
    hallmark_available: false,
    hallmark_number: ''
  });

  const [selectedProduct, setSelectedProduct] = useState<GoldLoanProduct | null>(null);
  const [totalGoldValue, setTotalGoldValue] = useState(0);
  const [calculatedLTV, setCalculatedLTV] = useState<number>(0);
  const [maxLoanAmount, setMaxLoanAmount] = useState(0);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    loadInitialData();
  }, []);

  useEffect(() => {
    if (productId) {
      const product = products.find(p => p.id === productId);
      setSelectedProduct(product || null);
      if (product) {
        setTenureMonths(product.default_tenure_months.toString());
        setCurrentOrnament(prev => ({
          ...prev,
          gold_rate_per_gram: 5500 // Default rate, can be updated
        }));
      }
    }
  }, [productId, products]);

  useEffect(() => {
    // Calculate total gold value
    const total = ornaments.reduce((sum, orn) => sum + orn.appraised_value, 0);
    setTotalGoldValue(total);

    // Calculate max loan amount based on LTV
    if (selectedProduct && total > 0) {
      const maxAmount = total * (selectedProduct.ltv_ratio / 100);
      setMaxLoanAmount(maxAmount);
      
      // Auto-fill loan amount if empty
      if (!loanAmount) {
        setLoanAmount(maxAmount.toFixed(2));
      }
    }
  }, [ornaments, selectedProduct]);

  useEffect(() => {
    // Calculate LTV when loan amount or total value changes
    if (totalGoldValue > 0 && loanAmount) {
      const ltv = (parseFloat(loanAmount) / totalGoldValue) * 100;
      setCalculatedLTV(ltv);
    } else {
      setCalculatedLTV(0);
    }
  }, [loanAmount, totalGoldValue]);

  const loadInitialData = async () => {
    try {
      const [productsData, ornamentTypesData, purityData] = await Promise.all([
        getGoldLoanProducts(true),
        getOrnamentTypes(),
        getPurityOptions()
      ]);
      
      if (productsData && ornamentTypesData && purityData) {
        setProducts(productsData.products);
        setOrnamentTypes(ornamentTypesData.ornament_types);
        setPurityOptions(purityData.purity_options);
      }
    } catch (error) {
      console.error('Failed to load initial data:', error);
      toast({
        title: 'Error',
        description: 'Failed to load form data',
        variant: 'destructive'
      });
    }
  };

  const handlePurityChange = (karat: number) => {
    const purity = purityOptions.find(p => p.karat === karat);
    if (purity) {
      setCurrentOrnament(prev => ({
        ...prev,
        purity_karat: purity.karat,
        purity_percentage: purity.percentage
      }));
    }
  };

  const handleWeightChange = (field: 'gross' | 'stone', value: number) => {
    setCurrentOrnament(prev => {
      const gross = field === 'gross' ? value : (prev.gross_weight_grams || 0);
      const stone = field === 'stone' ? value : (prev.stone_weight_grams || 0);
      const net = gross - stone;
      const marketValue = net * (prev.gold_rate_per_gram || 0);
      const appraisedValue = marketValue * 0.95; // 5% reduction for appraisal

      return {
        ...prev,
        gross_weight_grams: gross,
        stone_weight_grams: stone,
        net_weight_grams: net,
        market_value: marketValue,
        appraised_value: appraisedValue
      };
    });
  };

  const handleGoldRateChange = (rate: number) => {
    setCurrentOrnament(prev => {
      const marketValue = (prev.net_weight_grams || 0) * rate;
      const appraisedValue = marketValue * 0.95;

      return {
        ...prev,
        gold_rate_per_gram: rate,
        market_value: marketValue,
        appraised_value: appraisedValue
      };
    });
  };

  const addOrnament = () => {
    if (!currentOrnament.ornament_type || !currentOrnament.net_weight_grams) {
      toast({
        title: 'Validation Error',
        description: 'Please fill all required ornament fields',
        variant: 'destructive'
      });
      return;
    }

    setOrnaments(prev => [...prev, currentOrnament as GoldOrnament]);
    
    // Reset form
    setCurrentOrnament({
      ornament_type: '',
      ornament_description: '',
      quantity: 1,
      purity_karat: 22,
      purity_percentage: 91.67,
      gross_weight_grams: 0,
      stone_weight_grams: 0,
      net_weight_grams: 0,
      gold_rate_per_gram: currentOrnament.gold_rate_per_gram,
      market_value: 0,
      appraised_value: 0,
      hallmark_available: false,
      hallmark_number: ''
    });

    toast({
      title: 'Success',
      description: 'Ornament added to list'
    });
  };

  const removeOrnament = (index: number) => {
    setOrnaments(prev => prev.filter((_, i) => i !== index));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (ornaments.length === 0) {
      toast({
        title: 'Validation Error',
        description: 'Please add at least one gold ornament',
        variant: 'destructive'
      });
      return;
    }

    if (!selectedProduct) {
      toast({
        title: 'Validation Error',
        description: 'Please select a gold loan product',
        variant: 'destructive'
      });
      return;
    }

    if (calculatedLTV > selectedProduct.max_ltv_ratio) {
      toast({
        title: 'Validation Error',
        description: `LTV ratio ${calculatedLTV.toFixed(1)}% exceeds maximum ${selectedProduct.max_ltv_ratio}%`,
        variant: 'destructive'
      });
      return;
    }

    try {
      setSubmitting(true);

      const data: CreateGoldLoanData = {
        customer_id: customerId,
        product_id: productId,
        loan_amount: parseFloat(loanAmount),
        tenure_months: parseInt(tenureMonths),
        repayment_frequency: repaymentFrequency,
        ornaments: ornaments
      };

      const result = await createGoldLoan(data);

      toast({
        title: 'Success',
        description: 'Gold loan created successfully'
      });

      if (result && result.loan && result.loan.id) {
        router.push(`/gold-loans/${result.loan.id}`);
      } else {
        router.push('/gold-loans');
      }
      
    } catch (error: any) {
      toast({
        title: 'Error',
        description: error.response?.data?.detail || 'Failed to create gold loan',
        variant: 'destructive'
      });
    } finally {
      setSubmitting(false);
    }
  };

  const totalWeight = ornaments.reduce((sum, orn) => sum + orn.net_weight_grams, 0);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Link href="/gold-loans">
          <Button variant="ghost" size="sm">
            <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
            Back
          </Button>
        </Link>
        <div>
          <h1 className="text-3xl font-bold">New Gold Loan</h1>
          <p className="text-muted-foreground">Create a new gold loan account</p>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Basic Details */}
        <Card>
          <CardHeader>
            <CardTitle>Loan Details</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <Label htmlFor="customerId">Customer ID *</Label>
                <Input
                  id="customerId"
                  value={customerId}
                  onChange={(e) => setCustomerId(e.target.value)}
                  placeholder="Enter customer ID"
                  required
                />
              </div>

              <div>
                <Label htmlFor="productId">Gold Loan Product *</Label>
                <select
                  id="productId"
                  value={productId}
                  onChange={(e) => setProductId(e.target.value)}
                  className="w-full px-3 py-2 border rounded-md"
                  required
                >
                  <option value="">Select Product</option>
                  {products.map(product => (
                    <option key={product.id} value={product.id}>
                      {product.product_name} - {product.ltv_ratio}% LTV @ {product.default_interest_rate}% p.a.
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <Label htmlFor="tenureMonths">Tenure (Months) *</Label>
                <Input
                  id="tenureMonths"
                  type="number"
                  value={tenureMonths}
                  onChange={(e) => setTenureMonths(e.target.value)}
                  min={selectedProduct?.min_tenure_months || 1}
                  max={selectedProduct?.max_tenure_months || 36}
                  required
                />
                {selectedProduct && (
                  <p className="text-sm text-muted-foreground mt-1">
                    Range: {selectedProduct.min_tenure_months} - {selectedProduct.max_tenure_months} months
                  </p>
                )}
              </div>

              <div>
                <Label htmlFor="repaymentFrequency">Repayment Frequency *</Label>
                <select
                  id="repaymentFrequency"
                  value={repaymentFrequency}
                  onChange={(e) => setRepaymentFrequency(e.target.value)}
                  className="w-full px-3 py-2 border rounded-md"
                  required
                >
                  <option value="Monthly">Monthly</option>
                  <option value="Quarterly">Quarterly</option>
                  <option value="Bullet">Bullet (At Maturity)</option>
                </select>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Add Ornament Form */}
        <Card>
          <CardHeader>
            <CardTitle>Add Gold Ornament</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <Label htmlFor="ornamentType">Ornament Type *</Label>
                <select
                  id="ornamentType"
                  value={currentOrnament.ornament_type}
                  onChange={(e) => setCurrentOrnament(prev => ({ ...prev, ornament_type: e.target.value }))}
                  className="w-full px-3 py-2 border rounded-md"
                >
                  <option value="">Select Type</option>
                  {ornamentTypes.map(type => (
                    <option key={type} value={type}>{type}</option>
                  ))}
                </select>
              </div>

              <div>
                <Label htmlFor="purityKarat">Purity *</Label>
                <select
                  id="purityKarat"
                  value={currentOrnament.purity_karat}
                  onChange={(e) => handlePurityChange(parseInt(e.target.value))}
                  className="w-full px-3 py-2 border rounded-md"
                >
                  {purityOptions.map(option => (
                    <option key={option.karat} value={option.karat}>
                      {option.label}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <Label htmlFor="quantity">Quantity</Label>
                <Input
                  id="quantity"
                  type="number"
                  value={currentOrnament.quantity}
                  onChange={(e) => setCurrentOrnament(prev => ({ ...prev, quantity: parseInt(e.target.value) || 1 }))}
                  min="1"
                />
              </div>

              <div>
                <Label htmlFor="grossWeight">Gross Weight (grams) *</Label>
                <Input
                  id="grossWeight"
                  type="number"
                  step="0.001"
                  value={currentOrnament.gross_weight_grams}
                  onChange={(e) => handleWeightChange('gross', parseFloat(e.target.value) || 0)}
                />
              </div>

              <div>
                <Label htmlFor="stoneWeight">Stone Weight (grams)</Label>
                <Input
                  id="stoneWeight"
                  type="number"
                  step="0.001"
                  value={currentOrnament.stone_weight_grams}
                  onChange={(e) => handleWeightChange('stone', parseFloat(e.target.value) || 0)}
                />
              </div>

              <div>
                <Label htmlFor="netWeight">Net Weight (grams)</Label>
                <Input
                  id="netWeight"
                  type="number"
                  step="0.001"
                  value={currentOrnament.net_weight_grams?.toFixed(3) || '0.000'}
                  readOnly
                  className="bg-muted"
                />
              </div>

              <div>
                <Label htmlFor="goldRate">Gold Rate (per gram) *</Label>
                <Input
                  id="goldRate"
                  type="number"
                  step="0.01"
                  value={currentOrnament.gold_rate_per_gram}
                  onChange={(e) => handleGoldRateChange(parseFloat(e.target.value) || 0)}
                />
              </div>

              <div>
                <Label htmlFor="marketValue">Market Value</Label>
                <Input
                  id="marketValue"
                  value={formatCurrency(currentOrnament.market_value || 0)}
                  readOnly
                  className="bg-muted"
                />
              </div>

              <div>
                <Label htmlFor="appraisedValue">Appraised Value</Label>
                <Input
                  id="appraisedValue"
                  value={formatCurrency(currentOrnament.appraised_value || 0)}
                  readOnly
                  className="bg-muted"
                />
              </div>

              <div className="md:col-span-3">
                <Label htmlFor="description">Description (Optional)</Label>
                <Input
                  id="description"
                  value={currentOrnament.ornament_description}
                  onChange={(e) => setCurrentOrnament(prev => ({ ...prev, ornament_description: e.target.value }))}
                  placeholder="E.g., Yellow gold chain with pendant"
                />
              </div>
            </div>

            <div className="mt-4 flex items-center gap-2">
              <input
                type="checkbox"
                id="hallmark"
                checked={currentOrnament.hallmark_available}
                onChange={(e) => setCurrentOrnament(prev => ({ ...prev, hallmark_available: e.target.checked }))}
                className="rounded"
              />
              <Label htmlFor="hallmark" className="cursor-pointer">Hallmark Available</Label>
              
              {currentOrnament.hallmark_available && (
                <Input
                  value={currentOrnament.hallmark_number}
                  onChange={(e) => setCurrentOrnament(prev => ({ ...prev, hallmark_number: e.target.value }))}
                  placeholder="Hallmark number"
                  className="max-w-xs"
                />
              )}
            </div>

            <div className="mt-4">
              <Button type="button" onClick={addOrnament} variant="outline">
                <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                </svg>
                Add Ornament to List
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Ornaments List */}
        {ornaments.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle>Added Ornaments ({ornaments.length})</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-muted/50">
                    <tr>
                      <th className="text-left p-3">#</th>
                      <th className="text-left p-3">Type</th>
                      <th className="text-center p-3">Purity</th>
                      <th className="text-right p-3">Net Weight</th>
                      <th className="text-right p-3">Rate/g</th>
                      <th className="text-right p-3">Value</th>
                      <th className="text-center p-3">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y">
                    {ornaments.map((orn, index) => (
                      <tr key={index}>
                        <td className="p-3">{index + 1}</td>
                        <td className="p-3">{orn.ornament_type}</td>
                        <td className="p-3 text-center">
                          <Badge variant="warning">{orn.purity_karat}K</Badge>
                        </td>
                        <td className="p-3 text-right">{orn.net_weight_grams.toFixed(3)}g</td>
                        <td className="p-3 text-right">₹{orn.gold_rate_per_gram.toFixed(0)}</td>
                        <td className="p-3 text-right font-medium">{formatCurrency(orn.appraised_value)}</td>
                        <td className="p-3 text-center">
                          <Button
                            type="button"
                            variant="ghost"
                            size="sm"
                            onClick={() => removeOrnament(index)}
                          >
                            <svg className="w-4 h-4 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                            </svg>
                          </Button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                  <tfoot className="bg-muted/50 font-bold">
                    <tr>
                      <td colSpan={3} className="p-3 text-right">Total:</td>
                      <td className="p-3 text-right">{totalWeight.toFixed(3)}g</td>
                      <td className="p-3"></td>
                      <td className="p-3 text-right">{formatCurrency(totalGoldValue)}</td>
                      <td className="p-3"></td>
                    </tr>
                  </tfoot>
                </table>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Loan Amount & LTV Calculator */}
        {ornaments.length > 0 && selectedProduct && (
          <Card>
            <CardHeader>
              <CardTitle>Loan Amount & LTV Calculator</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <Label htmlFor="loanAmount">Requested Loan Amount *</Label>
                  <Input
                    id="loanAmount"
                    type="number"
                    step="0.01"
                    value={loanAmount}
                    onChange={(e) => setLoanAmount(e.target.value)}
                    required
                  />
                  <p className="text-sm text-muted-foreground mt-1">
                    Max Eligible: {formatCurrency(maxLoanAmount)} (@ {selectedProduct.ltv_ratio}% LTV)
                  </p>
                </div>

                <div className="space-y-4">
                  <div className="flex justify-between items-center p-3 bg-muted/50 rounded-md">
                    <span className="text-sm">Total Gold Value:</span>
                    <span className="font-bold">{formatCurrency(totalGoldValue)}</span>
                  </div>
                  
                  <div className="flex justify-between items-center p-3 bg-muted/50 rounded-md">
                    <span className="text-sm">Calculated LTV:</span>
                    <Badge variant={calculatedLTV <= selectedProduct.ltv_ratio ? 'success' : 'destructive'}>
                      {calculatedLTV.toFixed(2)}%
                    </Badge>
                  </div>

                  {calculatedLTV > selectedProduct.max_ltv_ratio && (
                    <div className="p-3 bg-red-50 border border-red-200 rounded-md text-sm text-red-800">
                      ⚠️ LTV exceeds maximum limit of {selectedProduct.max_ltv_ratio}%
                    </div>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Submit */}
        <div className="flex justify-end gap-4">
          <Link href="/gold-loans">
            <Button type="button" variant="outline">Cancel</Button>
          </Link>
          <Button type="submit" size="lg" disabled={submitting || ornaments.length === 0}>
            {submitting ? 'Creating...' : 'Create Gold Loan'}
          </Button>
        </div>
      </form>
    </div>
  );
}
