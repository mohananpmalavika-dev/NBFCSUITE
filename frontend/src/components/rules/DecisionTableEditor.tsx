/**
 * Decision Table Editor Component
 * 
 * Spreadsheet-like editor for editing decision table cell values
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  IconButton,
  Chip,
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
  Checkbox,
  FormControlLabel,
  Alert,
  Tooltip,
  ToggleButton,
  ToggleButtonGroup,
} from '@mui/material';
import {
  Save as SaveIcon,
  Close as CloseIcon,
  Help as HelpIcon,
  ContentCopy as CopyIcon,
  ContentPaste as PasteIcon,
} from '@mui/icons-material';

interface Column {
  column_id: string;
  column_name: string;
  column_type: 'input' | 'output';
  field_name: string;
  field_type: string;
  operator?: string;
  display_order: number;
}

interface Cell {
  column_id: string;
  value: any;
  value_min?: any;
  value_max?: any;
  is_range: boolean;
  is_any: boolean;
  is_reject: boolean;
}

interface Row {
  row_id: string;
  cells: Cell[];
  row_order: number;
  is_active: boolean;
  is_default: boolean;
  description?: string;
}

interface DecisionTableEditorProps {
  columns: Column[];
  rows: Row[];
  onSave: (rows: Row[]) => void;
  onClose: () => void;
}

const DecisionTableEditor: React.FC<DecisionTableEditorProps> = ({
  columns,
  rows,
  onSave,
  onClose,
}) => {
  const [editedRows, setEditedRows] = useState<Row[]>(JSON.parse(JSON.stringify(rows)));
  const [selectedCell, setSelectedCell] = useState<{rowId: string, columnId: string} | null>(null);
  const [cellDialogOpen, setCellDialogOpen] = useState(false);
  const [editingCell, setEditingCell] = useState<Cell | null>(null);
  const [editingColumn, setEditingColumn] = useState<Column | null>(null);
  
  // Cell edit state
  const [cellValue, setCellValue] = useState<any>('');
  const [cellValueMin, setCellValueMin] = useState<any>('');
  const [cellValueMax, setCellValueMax] = useState<any>('');
  const [cellIsRange, setCellIsRange] = useState(false);
  const [cellIsAny, setCellIsAny] = useState(false);
  const [cellIsReject, setCellIsReject] = useState(false);
  const [cellMode, setCellMode] = useState<'normal' | 'range' | 'any' | 'reject'>('normal');
  
  const handleCellClick = (rowId: string, columnId: string) => {
    const row = editedRows.find(r => r.row_id === rowId);
    const cell = row?.cells.find(c => c.column_id === columnId);
    const column = columns.find(c => c.column_id === columnId);
    
    if (!cell || !column) return;
    
    setSelectedCell({ rowId, columnId });
    setEditingCell(cell);
    setEditingColumn(column);
    
    // Set edit state
    setCellValue(cell.value || '');
    setCellValueMin(cell.value_min || '');
    setCellValueMax(cell.value_max || '');
    setCellIsRange(cell.is_range);
    setCellIsAny(cell.is_any);
    setCellIsReject(cell.is_reject);
    
    // Determine mode
    if (cell.is_any) {
      setCellMode('any');
    } else if (cell.is_reject) {
      setCellMode('reject');
    } else if (cell.is_range) {
      setCellMode('range');
    } else {
      setCellMode('normal');
    }
    
    setCellDialogOpen(true);
  };
  
  const handleCellModeChange = (event: React.MouseEvent<HTMLElement>, newMode: string | null) => {
    if (newMode) {
      setCellMode(newMode as 'normal' | 'range' | 'any' | 'reject');
      
      // Update flags
      setCellIsAny(newMode === 'any');
      setCellIsReject(newMode === 'reject');
      setCellIsRange(newMode === 'range');
    }
  };
  
  const handleSaveCell = () => {
    if (!selectedCell || !editingCell) return;
    
    const updatedCell: Cell = {
      ...editingCell,
      value: cellMode === 'normal' ? parseValue(cellValue, editingColumn?.field_type) : null,
      value_min: cellMode === 'range' ? parseValue(cellValueMin, editingColumn?.field_type) : undefined,
      value_max: cellMode === 'range' ? parseValue(cellValueMax, editingColumn?.field_type) : undefined,
      is_range: cellMode === 'range',
      is_any: cellMode === 'any',
      is_reject: cellMode === 'reject',
    };
    
    setEditedRows(editedRows.map(row =>
      row.row_id === selectedCell.rowId
        ? {
            ...row,
            cells: row.cells.map(cell =>
              cell.column_id === selectedCell.columnId ? updatedCell : cell
            ),
          }
        : row
    ));
    
    setCellDialogOpen(false);
    setSelectedCell(null);
  };
  
  const parseValue = (value: any, fieldType?: string): any => {
    if (value === '' || value === null || value === undefined) return null;
    
    switch (fieldType) {
      case 'number':
        return parseFloat(value);
      case 'boolean':
        return value === 'true' || value === true;
      case 'date':
        return value;
      default:
        return value;
    }
  };
  
  const formatCellDisplay = (cell: Cell, column: Column): React.ReactNode => {
    if (cell.is_any) {
      return <Chip label="ANY" size="small" color="default" />;
    }
    
    if (cell.is_reject) {
      return <Chip label="REJECT" size="small" color="error" />;
    }
    
    if (cell.is_range) {
      return (
        <Typography variant="body2">
          {cell.value_min} - {cell.value_max}
        </Typography>
      );
    }
    
    if (cell.value === null || cell.value === undefined || cell.value === '') {
      return <Typography variant="body2" color="text.disabled">-</Typography>;
    }
    
    return <Typography variant="body2">{cell.value.toString()}</Typography>;
  };
  
  const handleSaveAll = () => {
    onSave(editedRows);
  };
  
  const handleToggleRowActive = (rowId: string) => {
    setEditedRows(editedRows.map(row =>
      row.row_id === rowId ? { ...row, is_active: !row.is_active } : row
    ));
  };
  
  const handleSetDefault = (rowId: string) => {
    setEditedRows(editedRows.map(row => ({
      ...row,
      is_default: row.row_id === rowId,
    })));
  };
  
  const inputColumns = columns.filter(c => c.column_type === 'input');
  const outputColumns = columns.filter(c => c.column_type === 'output');
  
  return (
    <Dialog
      open={true}
      onClose={onClose}
      maxWidth="xl"
      fullWidth
      fullScreen
    >
      <DialogTitle>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="h6">Decision Table Editor</Typography>
          <Box>
            <Tooltip title="Click on any cell to edit">
              <IconButton size="small">
                <HelpIcon />
              </IconButton>
            </Tooltip>
            <IconButton onClick={onClose}>
              <CloseIcon />
            </IconButton>
          </Box>
        </Box>
      </DialogTitle>
      
      <DialogContent>
        <Alert severity="info" sx={{ mb: 2 }}>
          Click on any cell to edit its value. Use "ANY" for wildcard matching, "REJECT" for rejection rules, 
          or "RANGE" for value ranges (e.g., 700-800).
        </Alert>
        
        <TableContainer component={Paper} sx={{ maxHeight: 600 }}>
          <Table stickyHeader size="small">
            <TableHead>
              <TableRow>
                <TableCell width={50}>Row</TableCell>
                <TableCell width={80}>Active</TableCell>
                <TableCell width={80}>Default</TableCell>
                
                {/* Input Columns */}
                {inputColumns.map((col) => (
                  <TableCell
                    key={col.column_id}
                    sx={{ bgcolor: 'primary.50', fontWeight: 'bold' }}
                  >
                    {col.column_name}
                    <br />
                    <Chip label="INPUT" size="small" color="primary" />
                    <Typography variant="caption" display="block">
                      {col.field_type}
                    </Typography>
                  </TableCell>
                ))}
                
                {/* Output Columns */}
                {outputColumns.map((col) => (
                  <TableCell
                    key={col.column_id}
                    sx={{ bgcolor: 'success.50', fontWeight: 'bold' }}
                  >
                    {col.column_name}
                    <br />
                    <Chip label="OUTPUT" size="small" color="success" />
                    <Typography variant="caption" display="block">
                      {col.field_type}
                    </Typography>
                  </TableCell>
                ))}
              </TableRow>
            </TableHead>
            
            <TableBody>
              {editedRows.map((row, rowIndex) => (
                <TableRow
                  key={row.row_id}
                  hover
                  sx={{
                    bgcolor: !row.is_active ? 'action.disabledBackground' : 'inherit',
                    opacity: !row.is_active ? 0.6 : 1,
                  }}
                >
                  <TableCell>{rowIndex + 1}</TableCell>
                  
                  <TableCell>
                    <Checkbox
                      checked={row.is_active}
                      onChange={() => handleToggleRowActive(row.row_id)}
                      size="small"
                    />
                  </TableCell>
                  
                  <TableCell>
                    <Checkbox
                      checked={row.is_default}
                      onChange={() => handleSetDefault(row.row_id)}
                      size="small"
                      color="warning"
                    />
                  </TableCell>
                  
                  {/* Input Cells */}
                  {inputColumns.map((col) => {
                    const cell = row.cells.find(c => c.column_id === col.column_id);
                    return (
                      <TableCell
                        key={col.column_id}
                        onClick={() => handleCellClick(row.row_id, col.column_id)}
                        sx={{
                          cursor: 'pointer',
                          '&:hover': { bgcolor: 'action.hover' },
                          bgcolor:
                            selectedCell?.rowId === row.row_id &&
                            selectedCell?.columnId === col.column_id
                              ? 'action.selected'
                              : 'inherit',
                        }}
                      >
                        {cell && formatCellDisplay(cell, col)}
                      </TableCell>
                    );
                  })}
                  
                  {/* Output Cells */}
                  {outputColumns.map((col) => {
                    const cell = row.cells.find(c => c.column_id === col.column_id);
                    return (
                      <TableCell
                        key={col.column_id}
                        onClick={() => handleCellClick(row.row_id, col.column_id)}
                        sx={{
                          cursor: 'pointer',
                          '&:hover': { bgcolor: 'action.hover' },
                          bgcolor:
                            selectedCell?.rowId === row.row_id &&
                            selectedCell?.columnId === col.column_id
                              ? 'action.selected'
                              : 'inherit',
                        }}
                      >
                        {cell && formatCellDisplay(cell, col)}
                      </TableCell>
                    );
                  })}
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </DialogContent>
      
      <DialogActions>
        <Button onClick={onClose}>Cancel</Button>
        <Button
          variant="contained"
          startIcon={<SaveIcon />}
          onClick={handleSaveAll}
        >
          Save Changes
        </Button>
      </DialogActions>
      
      {/* Cell Edit Dialog */}
      <Dialog
        open={cellDialogOpen}
        onClose={() => setCellDialogOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>
          Edit Cell: {editingColumn?.column_name}
        </DialogTitle>
        
        <DialogContent>
          <Box sx={{ mt: 2 }}>
            <Typography variant="subtitle2" gutterBottom>
              Field: {editingColumn?.field_name} ({editingColumn?.field_type})
            </Typography>
            
            <ToggleButtonGroup
              value={cellMode}
              exclusive
              onChange={handleCellModeChange}
              fullWidth
              sx={{ mb: 3 }}
            >
              <ToggleButton value="normal">
                Normal Value
              </ToggleButton>
              <ToggleButton value="range">
                Range
              </ToggleButton>
              <ToggleButton value="any">
                ANY (Wildcard)
              </ToggleButton>
              <ToggleButton value="reject">
                REJECT
              </ToggleButton>
            </ToggleButtonGroup>
            
            {cellMode === 'normal' && (
              <Box>
                <TextField
                  fullWidth
                  label="Value"
                  value={cellValue}
                  onChange={(e) => setCellValue(e.target.value)}
                  type={editingColumn?.field_type === 'number' ? 'number' : 'text'}
                  helperText="Enter the exact value to match or set"
                />
              </Box>
            )}
            
            {cellMode === 'range' && (
              <Box sx={{ display: 'flex', gap: 2 }}>
                <TextField
                  fullWidth
                  label="Minimum Value"
                  value={cellValueMin}
                  onChange={(e) => setCellValueMin(e.target.value)}
                  type={editingColumn?.field_type === 'number' ? 'number' : 'text'}
                />
                <TextField
                  fullWidth
                  label="Maximum Value"
                  value={cellValueMax}
                  onChange={(e) => setCellValueMax(e.target.value)}
                  type={editingColumn?.field_type === 'number' ? 'number' : 'text'}
                />
              </Box>
            )}
            
            {cellMode === 'any' && (
              <Alert severity="info">
                This cell will match ANY value for this field. Useful for wildcards or "don't care" conditions.
              </Alert>
            )}
            
            {cellMode === 'reject' && (
              <Alert severity="warning">
                This cell marks the row as a REJECT rule. Commonly used for rejection scenarios.
              </Alert>
            )}
            
            {editingColumn?.column_type === 'input' && editingColumn.operator && (
              <Typography variant="caption" color="text.secondary" sx={{ mt: 2, display: 'block' }}>
                This column uses operator: <strong>{editingColumn.operator.replace(/_/g, ' ')}</strong>
              </Typography>
            )}
          </Box>
        </DialogContent>
        
        <DialogActions>
          <Button onClick={() => setCellDialogOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={handleSaveCell}>
            Save
          </Button>
        </DialogActions>
      </Dialog>
    </Dialog>
  );
};

export default DecisionTableEditor;
