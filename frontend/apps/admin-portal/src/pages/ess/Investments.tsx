/**
 * Investment Declaration Page
 * Tax saving investment declarations
 */

import React, { useEffect, useState } from 'react';
import {
  Box,
  Container,
  Card,
  CardContent,
  Typography,
  Button,
  IconButton,
  Grid,
  TextField,
  MenuItem,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Alert,
  CircularProgress,
  Chip,
  Divider
} from '@mui/material';
import {
  Add as AddIcon,
  ArrowBack as ArrowBackIcon,
  Delete as DeleteIcon,
  Send as SendIcon
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const investmentSections = [
  { value: '80C', label: 'Section 80C (PPF, LIC, ELSS, etc.)' },
  { value: '80D', label: 'Section 80D (Medical Insurance)' },
  { value: '80E', label: 'Section 80E (Education Loan Interest)' },
  { value: '80G', label: 'Section 80G (Donations)' },
  { value: 'HRA', label: 'HRA (House Rent Allowance)' },
  { value: 'LTA', label: 'LTA (Leave Travel Allowance)' }
];

interface InvestmentItem {
  section: string;
  investment_type: string;
  declared_amount: number;
  description?: string;
  policy_number?: string;
}

const Investments: React.FC = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [declarations, setDeclarations] = useState<any[]>([]);
  const [openDialog, setOpenDialog] = useState(false);
  const [items, setItems] = useState<InvestmentItem[]>([]);
  const [financialYear, setFinancialYear] = useState('2024-25');
  const [taxRegime, setTaxRegime] = useState('old');

  useEffect(() => {
    fetchDeclarations();
  }, []);

  const fetchDeclarations = async () => {
    try {
      setLoading(false);
      const response = await axios.get('/api/hrms/ess/investment/declarations');
      setDeclarations(response.data.items);
    } catch (err) {
      setLoading(false);
    }
  };

  const addItem = () => {
    setItems([...items, { section: '', investment_type: '', declared_amount: 0 }]);
  };

  const removeItem = (index: number) => {
    setItems(items.filter((_, i) => i !== index));
  };

  const updateItem = (index: number, field: string, value: any) => {
    const updated = [...items];
    updated[index] = { ...updated[index], [field]: value };
    setItems(updated);
  };

  const handleSubmit = async () => {
    try {
      const payload = {
        financial_year: financialYear,
        tax_regime: taxRegime,
        items: items
      };
      
      const response = await axios.post('/api/hrms/ess/investment/declarations', payload);
      await axios.post(`/api/hrms/ess/investment/declarations/${response.data.id}/submit`);
      
      setOpenDialog(false);
      setItems([]);
      fetchDeclarations();
    } catch (err: any) {
      alert(err.response?.data?.message || 'Failed to submit declaration');
    }
  };

  if (loading) {
    return <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px"><CircularProgress /></Box>;
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Box display="flex" alignItems="center" mb={3}>
        <IconButton onClick={() => navigate('/ess')} sx={{ mr: 2 }}>
          <ArrowBackIcon />
        </IconButton>
        <Box flex={1}>
          <Typography variant="h4" fontWeight={600}>Investment Declarations</Typography>
          <Typography variant="body2" color="text.secondary">Submit tax saving investment declarations</Typography>
        </Box>
        <Button variant="contained" startIcon={<AddIcon />} onClick={() => setOpenDialog(true)}>
          New Declaration
        </Button>
      </Box>

      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>Declaration History</Typography>
          <Divider sx={{ mb: 2 }} />
          
          {declarations.length > 0 ? (
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Declaration Code</TableCell>
                    <TableCell>Financial Year</TableCell>
                    <TableCell align="right">Declared Amount</TableCell>
                    <TableCell>Status</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {declarations.map((decl) => (
                    <TableRow key={decl.id}>
                      <TableCell>{decl.declaration_code}</TableCell>
                      <TableCell>{decl.financial_year}</TableCell>
                      <TableCell align="right">₹{decl.total_declared_amount.toLocaleString()}</TableCell>
                      <TableCell>
                        <Chip label={decl.status.toUpperCase()} size="small" color={decl.status === 'approved' ? 'success' : 'default'} />
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          ) : (
            <Typography variant="body2" color="text.secondary" textAlign="center" py={4}>
              No declarations found
            </Typography>
          )}
        </CardContent>
      </Card>

      <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>New Investment Declaration</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={6}>
              <TextField fullWidth label="Financial Year" value={financialYear} onChange={(e) => setFinancialYear(e.target.value)} />
            </Grid>
            <Grid item xs={6}>
              <TextField select fullWidth label="Tax Regime" value={taxRegime} onChange={(e) => setTaxRegime(e.target.value)}>
                <MenuItem value="old">Old Regime</MenuItem>
                <MenuItem value="new">New Regime</MenuItem>
              </TextField>
            </Grid>
            
            {items.map((item, index) => (
              <React.Fragment key={index}>
                <Grid item xs={12}><Divider /></Grid>
                <Grid item xs={5}>
                  <TextField select fullWidth label="Section" value={item.section} onChange={(e) => updateItem(index, 'section', e.target.value)}>
                    {investmentSections.map((sec) => (
                      <MenuItem key={sec.value} value={sec.value}>{sec.label}</MenuItem>
                    ))}
                  </TextField>
                </Grid>
                <Grid item xs={3}>
                  <TextField fullWidth label="Type" value={item.investment_type} onChange={(e) => updateItem(index, 'investment_type', e.target.value)} />
                </Grid>
                <Grid item xs={3}>
                  <TextField fullWidth type="number" label="Amount" value={item.declared_amount} onChange={(e) => updateItem(index, 'declared_amount', parseFloat(e.target.value))} />
                </Grid>
                <Grid item xs={1}>
                  <IconButton color="error" onClick={() => removeItem(index)}><DeleteIcon /></IconButton>
                </Grid>
              </React.Fragment>
            ))}
            
            <Grid item xs={12}>
              <Button startIcon={<AddIcon />} onClick={addItem}>Add Investment</Button>
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenDialog(false)}>Cancel</Button>
          <Button variant="contained" startIcon={<SendIcon />} onClick={handleSubmit} disabled={items.length === 0}>
            Submit Declaration
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default Investments;
