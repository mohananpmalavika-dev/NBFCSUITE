/**
 * Decision Table Builder Component
 * 
 * Visual builder for creating and managing decision tables with columns and rows
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
  Grid,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Tooltip,
  Switch,
  FormControlLabel,
  Alert,
} from '@mui/material';
import {
  Add as AddIcon,
  Delete as DeleteIcon,
  Edit as EditIcon,
  DragIndicator as DragIcon,
  Save as SaveIcon,
  PlayArrow as TestIcon,
  ViewColumn as ColumnIcon,
  TableRows as RowIcon,
} from '@mui/icons-material';
import DecisionTableEditor from './DecisionTableEditor';

interface Column {
  column_id: string;
  column_name: string;
  column_type: 'input' | 'output';
  field_name: string;
  field_type: string;
  operator?: string;
  display_order: number;
  description?: string;
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

interface DecisionTable {
  table_id: string;
  table_name: string;
  description?: string;
  columns: Column[];
  rows: Row[];
  match_first: boolean;
  match_all_inputs: boolean;
  is_active: boolean;
}

interface DecisionTableBuilderProps {
  table?: DecisionTable;
  onSave?: (table: DecisionTable) => void;
  onCancel?: () => void;
}

const DecisionTableBuilder: React.FC<DecisionTableBuilderProps> = ({
  table,
  onSave,
  onCancel,
}) => {
  const [tableName, setTableName] = useState(table?.table_name || '');
  const [description, setDescription] = useState(table?.description || '');
  const [columns, setColumns] = useState<Column[]>(table?.columns || []);
  const [rows, setRows] = useState<Row[]>(table?.rows || []);
  const [matchFirst, setMatchFirst] = useState(table?.match_first ?? true);
  const [matchAllInputs, setMatchAllInputs] = useState(table?.match_all_inputs ?? true);
  
  const [columnDialogOpen, setColumnDialogOpen] = useState(false);
  const [editingColumn, setEditingColumn] = useState<Column | null>(null);
  const [editorOpen, setEditorOpen] = useState(false);
  
  // New column form state
  const [newColumnName, setNewColumnName] = useState('');
  const [newColumnType, setNewColumnType] = useState<'input' | 'output'>('input');
  const [newFieldName, setNewFieldName] = useState('');
  const [newFieldType, setNewFieldType] = useState('string');
  const [newOperator, setNewOperator] = useState('equals');
  const [newDescription, setNewDescription] = useState('');
  
  const fieldTypes = ['string', 'number', 'boolean', 'date'];
  const operators = [
    'equals',
    'not_equals',
    'greater_than',
    'greater_than_or_equal',
    'less_than',
    'less_than_or_equal',
    'between',
    'contains',
    'in',
  ];
  
  const handleOpenColumnDialog = (column?: Column) => {
    if (column) {
      setEditingColumn(column);
      setNewColumnName(column.column_name);
      setNewColumnType(column.column_type);
      setNewFieldName(column.field_name);
      setNewFieldType(column.field_type);
      setNewOperator(column.operator || 'equals');
      setNewDescription(column.description || '');
    } else {
      setEditingColumn(null);
      setNewColumnName('');
      setNewColumnType('input');
      setNewFieldName('');
      setNewFieldType('string');
      setNewOperator('equals');
      setNewDescription('');
    }
    setColumnDialogOpen(true);
  };
  
  const handleSaveColumn = () => {
    const column: Column = {
      column_id: editingColumn?.column_id || `col_${Date.now()}`,
      column_name: newColumnName,
      column_type: newColumnType,
      field_name: newFieldName,
      field_type: newFieldType,
      operator: newColumnType === 'input' ? newOperator : undefined,
      display_order: editingColumn?.display_order || columns.length,
      description: newDescription,
    };
    
    if (editingColumn) {
      // Update existing column
      setColumns(columns.map(c => c.column_id === column.column_id ? column : c));
      
      // Update cells in all rows
      setRows(rows.map(row => ({
        ...row,
        cells: row.cells.map(cell =>
          cell.column_id === column.column_id
            ? { ...cell, column_id: column.column_id }
            : cell
        ),
      })));
    } else {
      // Add new column
      setColumns([...columns, column]);
      
      // Add cell to all rows
      setRows(rows.map(row => ({
        ...row,
        cells: [
          ...row.cells,
          {
            column_id: column.column_id,
            value: null,
            is_range: false,
            is_any: false,
            is_reject: false,
          },
        ],
      })));
    }
    
    setColumnDialogOpen(false);
  };
  
  const handleDeleteColumn = (columnId: string) => {
    if (!window.confirm('Delete this column? This will remove data from all rows.')) {
      return;
    }
    
    setColumns(columns.filter(c => c.column_id !== columnId));
    setRows(rows.map(row => ({
      ...row,
      cells: row.cells.filter(cell => cell.column_id !== columnId),
    })));
  };
  
  const handleAddRow = () => {
    const newRow: Row = {
      row_id: `row_${Date.now()}`,
      cells: columns.map(col => ({
        column_id: col.column_id,
        value: null,
        is_range: false,
        is_any: false,
        is_reject: false,
      })),
      row_order: rows.length + 1,
      is_active: true,
      is_default: false,
    };
    
    setRows([...rows, newRow]);
  };
  
  const handleDeleteRow = (rowId: string) => {
    setRows(rows.filter(r => r.row_id !== rowId));
  };
  
  const handleMoveRow = (rowId: string, direction: 'up' | 'down') => {
    const index = rows.findIndex(r => r.row_id === rowId);
    if (
      (direction === 'up' && index === 0) ||
      (direction === 'down' && index === rows.length - 1)
    ) {
      return;
    }
    
    const newRows = [...rows];
    const swapIndex = direction === 'up' ? index - 1 : index + 1;
    [newRows[index], newRows[swapIndex]] = [newRows[swapIndex], newRows[index]];
    
    // Update row_order
    newRows.forEach((row, idx) => {
      row.row_order = idx + 1;
    });
    
    setRows(newRows);
  };
  
  const handleOpenEditor = () => {
    setEditorOpen(true);
  };
  
  const handleSaveFromEditor = (updatedRows: Row[]) => {
    setRows(updatedRows);
    setEditorOpen(false);
  };
  
  const handleSaveTable = () => {
    const decisionTable: DecisionTable = {
      table_id: table?.table_id || `table_${Date.now()}`,
      table_name: tableName,
      description,
      columns,
      rows,
      match_first: matchFirst,
      match_all_inputs: matchAllInputs,
      is_active: true,
    };
    
    onSave?.(decisionTable);
  };
  
  const getInputColumns = () => columns.filter(c => c.column_type === 'input');
  const getOutputColumns = () => columns.filter(c => c.column_type === 'output');
  
  return (
    <Box>
      <Paper sx={{ p: 3, mb: 2 }}>
        <Typography variant="h5" gutterBottom>
          {table ? 'Edit' : 'Create'} Decision Table
        </Typography>
        
        <Grid container spacing={2} sx={{ mt: 2 }}>
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Table Name"
              value={tableName}
              onChange={(e) => setTableName(e.target.value)}
              required
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <FormControlLabel
              control={
                <Switch
                  checked={matchFirst}
                  onChange={(e) => setMatchFirst(e.target.checked)}
                />
              }
              label="Match First Row Only"
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <FormControlLabel
              control={
                <Switch
                  checked={matchAllInputs}
                  onChange={(e) => setMatchAllInputs(e.target.checked)}
                />
              }
              label="All Inputs Must Match"
            />
          </Grid>
        </Grid>
      </Paper>
      
      {/* Columns Section */}
      <Paper sx={{ p: 3, mb: 2 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
          <Typography variant="h6">
            Columns ({columns.length})
          </Typography>
          <Button
            startIcon={<AddIcon />}
            variant="contained"
            size="small"
            onClick={() => handleOpenColumnDialog()}
          >
            Add Column
          </Button>
        </Box>
        
        {columns.length === 0 ? (
          <Alert severity="info">
            Add columns to define your decision table structure. 
            Input columns represent conditions, output columns represent results.
          </Alert>
        ) : (
          <Grid container spacing={2}>
            {columns.map((col) => (
              <Grid item xs={12} sm={6} md={4} key={col.column_id}>
                <Paper
                  variant="outlined"
                  sx={{
                    p: 2,
                    bgcolor: col.column_type === 'input' ? 'primary.50' : 'success.50',
                  }}
                >
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Chip
                      label={col.column_type.toUpperCase()}
                      size="small"
                      color={col.column_type === 'input' ? 'primary' : 'success'}
                    />
                    <Box>
                      <IconButton
                        size="small"
                        onClick={() => handleOpenColumnDialog(col)}
                      >
                        <EditIcon fontSize="small" />
                      </IconButton>
                      <IconButton
                        size="small"
                        onClick={() => handleDeleteColumn(col.column_id)}
                      >
                        <DeleteIcon fontSize="small" />
                      </IconButton>
                    </Box>
                  </Box>
                  <Typography variant="subtitle2" fontWeight="bold">
                    {col.column_name}
                  </Typography>
                  <Typography variant="caption" display="block">
                    Field: {col.field_name}
                  </Typography>
                  <Typography variant="caption" display="block">
                    Type: {col.field_type}
                  </Typography>
                  {col.operator && (
                    <Typography variant="caption" display="block">
                      Operator: {col.operator}
                    </Typography>
                  )}
                </Paper>
              </Grid>
            ))}
          </Grid>
        )}
      </Paper>
      
      {/* Rows Section */}
      <Paper sx={{ p: 3, mb: 2 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
          <Typography variant="h6">
            Rows ({rows.length})
          </Typography>
          <Box sx={{ display: 'flex', gap: 1 }}>
            <Button
              startIcon={<AddIcon />}
              variant="outlined"
              size="small"
              onClick={handleAddRow}
              disabled={columns.length === 0}
            >
              Add Row
            </Button>
            <Button
              startIcon={<EditIcon />}
              variant="contained"
              size="small"
              onClick={handleOpenEditor}
              disabled={columns.length === 0 || rows.length === 0}
            >
              Open Table Editor
            </Button>
          </Box>
        </Box>
        
        {columns.length === 0 ? (
          <Alert severity="warning">
            Add columns first before adding rows.
          </Alert>
        ) : rows.length === 0 ? (
          <Alert severity="info">
            Add rows to define your decision logic. Each row represents a rule with input conditions and output values.
          </Alert>
        ) : (
          <TableContainer>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell width={80}>Order</TableCell>
                  {columns.map((col) => (
                    <TableCell key={col.column_id}>
                      {col.column_name}
                      <br />
                      <Chip
                        label={col.column_type}
                        size="small"
                        color={col.column_type === 'input' ? 'primary' : 'success'}
                      />
                    </TableCell>
                  ))}
                  <TableCell width={150}>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {rows.map((row, index) => (
                  <TableRow key={row.row_id}>
                    <TableCell>
                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        <DragIcon fontSize="small" sx={{ mr: 1, cursor: 'move' }} />
                        {row.row_order}
                      </Box>
                    </TableCell>
                    {columns.map((col) => {
                      const cell = row.cells.find(c => c.column_id === col.column_id);
                      return (
                        <TableCell key={col.column_id}>
                          {cell?.is_any ? (
                            <Chip label="ANY" size="small" color="default" />
                          ) : cell?.is_reject ? (
                            <Chip label="REJECT" size="small" color="error" />
                          ) : cell?.is_range ? (
                            <Typography variant="body2">
                              {cell.value_min} - {cell.value_max}
                            </Typography>
                          ) : (
                            <Typography variant="body2">
                              {cell?.value?.toString() || '-'}
                            </Typography>
                          )}
                        </TableCell>
                      );
                    })}
                    <TableCell>
                      <Tooltip title="Move Up">
                        <IconButton
                          size="small"
                          onClick={() => handleMoveRow(row.row_id, 'up')}
                          disabled={index === 0}
                        >
                          ↑
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Move Down">
                        <IconButton
                          size="small"
                          onClick={() => handleMoveRow(row.row_id, 'down')}
                          disabled={index === rows.length - 1}
                        >
                          ↓
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Delete">
                        <IconButton
                          size="small"
                          onClick={() => handleDeleteRow(row.row_id)}
                        >
                          <DeleteIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        )}
      </Paper>
      
      {/* Action Buttons */}
      <Box sx={{ display: 'flex', justifyContent: 'flex-end', gap: 2 }}>
        {onCancel && (
          <Button onClick={onCancel}>
            Cancel
          </Button>
        )}
        <Button
          variant="contained"
          startIcon={<SaveIcon />}
          onClick={handleSaveTable}
          disabled={!tableName || columns.length === 0 || rows.length === 0}
        >
          Save Table
        </Button>
      </Box>
      
      {/* Column Dialog */}
      <Dialog
        open={columnDialogOpen}
        onClose={() => setColumnDialogOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>
          {editingColumn ? 'Edit' : 'Add'} Column
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Column Name"
                value={newColumnName}
                onChange={(e) => setNewColumnName(e.target.value)}
                required
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Column Type</InputLabel>
                <Select
                  value={newColumnType}
                  onChange={(e) => setNewColumnType(e.target.value as 'input' | 'output')}
                  label="Column Type"
                >
                  <MenuItem value="input">Input (Condition)</MenuItem>
                  <MenuItem value="output">Output (Result)</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Field Type</InputLabel>
                <Select
                  value={newFieldType}
                  onChange={(e) => setNewFieldType(e.target.value)}
                  label="Field Type"
                >
                  {fieldTypes.map((type) => (
                    <MenuItem key={type} value={type}>
                      {type}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Field Name (in data)"
                value={newFieldName}
                onChange={(e) => setNewFieldName(e.target.value)}
                required
                helperText="The field name in your data object"
              />
            </Grid>
            {newColumnType === 'input' && (
              <Grid item xs={12}>
                <FormControl fullWidth>
                  <InputLabel>Operator</InputLabel>
                  <Select
                    value={newOperator}
                    onChange={(e) => setNewOperator(e.target.value)}
                    label="Operator"
                  >
                    {operators.map((op) => (
                      <MenuItem key={op} value={op}>
                        {op.replace(/_/g, ' ')}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
            )}
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Description (optional)"
                value={newDescription}
                onChange={(e) => setNewDescription(e.target.value)}
                multiline
                rows={2}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setColumnDialogOpen(false)}>Cancel</Button>
          <Button
            onClick={handleSaveColumn}
            variant="contained"
            disabled={!newColumnName || !newFieldName}
          >
            {editingColumn ? 'Update' : 'Add'}
          </Button>
        </DialogActions>
      </Dialog>
      
      {/* Table Editor Dialog */}
      {editorOpen && (
        <DecisionTableEditor
          columns={columns}
          rows={rows}
          onSave={handleSaveFromEditor}
          onClose={() => setEditorOpen(false)}
        />
      )}
    </Box>
  );
};

export default DecisionTableBuilder;
