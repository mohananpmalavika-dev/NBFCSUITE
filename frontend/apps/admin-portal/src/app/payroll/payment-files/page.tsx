'use client';

import { useState, useEffect } from 'react';
import { PaymentFileService } from '@/services/payroll.service';
import type { PaymentFile, PaymentFileFormat, PaymentFileStatus } from '@/types/payroll.types';

export default function PaymentFilesPage() {
  const [files, setFiles] = useState<PaymentFile[]>([]);
  const [loading, setLoading] = useState(true);
  const [showGenerateModal, setShowGenerateModal] = useState(false);
  const [filterFormat, setFilterFormat] = useState<PaymentFileFormat | ''>('');
  const [filterStatus, setFilterStatus] = useState<PaymentFileStatus | ''>('');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  const [generateForm, setGenerateForm] = useState({
    payroll_run_id: 0,
    file_format: 'NEFT' as PaymentFileFormat
  });

  useEffect(() => {
    loadFiles();
  }, [currentPage, filterFormat, filterStatus]);

  const loadFiles = async () => {
    try {
      setLoading(true);
      const response = await PaymentFileService.list({
        page: currentPage,
        page_size: 20,
        file_format: filterFormat || undefined,
        status: filterStatus || undefined
      });
      setFiles(response.items);
      setTotalPages(response.pages);
    } catch (error) {
      console.error('Failed to load payment files:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await PaymentFileService.generate(
        generateForm.payroll_run_id,
        generateForm.file_format
      );
      setShowGenerateModal(false);
      loadFiles();
      alert('Payment file generated successfully');
    } catch (error) {
      console.error('Failed to generate:', error);
      alert('Failed to generate payment file');
    }
  };

  const handleUpdateStatus = async (fileId: number, status: PaymentFileStatus) => {
    try {
      await PaymentFileService.updateStatus(fileId, status);
      loadFiles();
      alert('Status updated successfully');
    } catch (error) {
      console.error('Failed to update status:', error);
    }
  };

  const handleDownload = async (fileId: number) => {
    try {
      await PaymentFileService.download(fileId);
      alert('Download started');
    } catch (error) {
      console.error('Failed to download:', error);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Payment Files</h1>
          <p className="text-sm text-gray-600 mt-1">Generate and manage bank payment files</p>
        </div>
        <button
          onClick={() => setShowGenerateModal(true)}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          + Generate Payment File
        </button>
      </div>

      {/* Filters */}
      <div className="bg-white p-4 rounded-lg border border-gray-200">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <select
            value={filterFormat}
            onChange={(e) => setFilterFormat(e.target.value as PaymentFileFormat | '')}
            className="px-4 py-2 border border-gray-300 rounded-lg"
          >
            <option value="">All Formats</option>
            <option value="NEFT">NEFT</option>
            <option value="RTGS">RTGS</option>
            <option value="CSV">CSV</option>
            <option value="EXCEL">Excel</option>
          </select>
          <select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value as PaymentFileStatus | '')}
            className="px-4 py-2 border border-gray-300 rounded-lg"
          >
            <option value="">All Status</option>
            <option value="GENERATED">Generated</option>
            <option value="UPLOADED">Uploaded</option>
            <option value="FAILED">Failed</option>
          </select>
          <button
            onClick={() => {
              setFilterFormat('');
              setFilterStatus('');
            }}
            className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
          >
            Clear Filters
          </button>
        </div>
      </div>

      {/* Payment Files Table */}
      <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">File Code</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">File Name</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Format</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Employees</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Total Amount</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Created</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Actions</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {loading ? (
              <tr><td colSpan={8} className="px-6 py-4 text-center">Loading...</td></tr>
            ) : files.length === 0 ? (
              <tr><td colSpan={8} className="px-6 py-4 text-center">No payment files found</td></tr>
            ) : (
              files.map((file) => (
                <tr key={file.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">{file.payment_file_code}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">{file.file_name}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    <span className="px-2 py-1 bg-blue-100 text-blue-700 rounded text-xs">
                      {file.file_format}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">{file.total_employees}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-semibold">
                    ₹{file.total_amount.toLocaleString('en-IN')}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 py-1 rounded text-xs ${
                      file.status === 'UPLOADED'
                        ? 'bg-green-100 text-green-700'
                        : file.status === 'GENERATED'
                        ? 'bg-yellow-100 text-yellow-700'
                        : 'bg-red-100 text-red-700'
                    }`}>
                      {file.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    {new Date(file.created_at).toLocaleDateString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm space-x-2">
                    <button
                      onClick={() => handleDownload(file.id)}
                      className="text-blue-600 hover:text-blue-900"
                    >
                      Download
                    </button>
                    {file.status === 'GENERATED' && (
                      <button
                        onClick={() => handleUpdateStatus(file.id, 'UPLOADED')}
                        className="text-green-600 hover:text-green-900"
                      >
                        Mark Uploaded
                      </button>
                    )}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Generate Modal */}
      {showGenerateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-md w-full p-6">
            <h2 className="text-xl font-bold mb-4">Generate Payment File</h2>
            <form onSubmit={handleGenerate} className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-1">Payroll Run ID *</label>
                <input
                  type="number"
                  value={generateForm.payroll_run_id}
                  onChange={(e) => setGenerateForm({
                    ...generateForm,
                    payroll_run_id: parseInt(e.target.value)
                  })}
                  className="w-full px-4 py-2 border rounded-lg"
                  required
                  placeholder="Enter payroll run ID"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">File Format *</label>
                <select
                  value={generateForm.file_format}
                  onChange={(e) => setGenerateForm({
                    ...generateForm,
                    file_format: e.target.value as PaymentFileFormat
                  })}
                  className="w-full px-4 py-2 border rounded-lg"
                  required
                >
                  <option value="NEFT">NEFT</option>
                  <option value="RTGS">RTGS</option>
                  <option value="CSV">CSV</option>
                  <option value="EXCEL">Excel</option>
                </select>
              </div>
              <div className="bg-blue-50 p-3 rounded text-sm text-blue-700">
                <p className="font-medium mb-1">Format Guidelines:</p>
                <ul className="list-disc list-inside space-y-1 text-xs">
                  <li>NEFT: All transactions</li>
                  <li>RTGS: Transactions ₹2L and above</li>
                  <li>CSV: Simple text format</li>
                  <li>Excel: Spreadsheet format</li>
                </ul>
              </div>
              <div className="flex justify-end gap-3 pt-4">
                <button
                  type="button"
                  onClick={() => setShowGenerateModal(false)}
                  className="px-4 py-2 border rounded-lg hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                >
                  Generate
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
