'use client';

import { useState, useEffect } from 'react';
import { goldApi } from '../../goldApi';

export default function ReportBuilderPage() {
  const [reportDefinitions, setReportDefinitions] = useState<any[]>([]);
  const [selectedReport, setSelectedReport] = useState<any>(null);
  const [parameters, setParameters] = useState<Record<string, any>>({});
  const [outputFormat, setOutputFormat] = useState('pdf');
  const [loading, setLoading] = useState(false);
  const [executing, setExecuting] = useState(false);

  useEffect(() => {
    loadReportDefinitions();
  }, []);

  const loadReportDefinitions = async () => {
    try {
      setLoading(true);
      const data = await goldApi.getReportDefinitions({ is_active: true });
      setReportDefinitions(data);
    } catch (error) {
      console.error('Failed to load report definitions:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleReportSelect = async (reportCode: string) => {
    try {
      const report = await goldApi.getReportDefinitionByCode(reportCode);
      setSelectedReport(report);
      setParameters({});
      
      // Load parameters for this report
      const params = await goldApi.getReportParameters(report.id, true);
      // Initialize parameter values
      const initialParams: Record<string, any> = {};
      params.forEach((param: any) => {
        if (param.default_value) {
          initialParams[param.parameter_name] = param.default_value;
        }
      });
      setParameters(initialParams);
    } catch (error) {
      console.error('Failed to load report details:', error);
    }
  };

  const handleParameterChange = (paramName: string, value: any) => {
    setParameters(prev => ({ ...prev, [paramName]: value }));
  };

  const handleGenerateReport = async () => {
    if (!selectedReport) return;

    try {
      setExecuting(true);
      const response = await goldApi.generateReport({
        report_code: selectedReport.code,
        parameters,
        output_format: outputFormat
      });
      
      alert(`Report generation started. Execution ID: ${response.execution_id}`);
      
      // Poll for completion (simplified)
      setTimeout(async () => {
        try {
          const execution = await goldApi.getReportExecution(response.execution_id);
          if (execution.status === 'completed' && execution.file_url) {
            window.open(execution.file_url, '_blank');
          }
        } catch (error) {
          console.error('Failed to check report status:', error);
        }
      }, 3000);
    } catch (error) {
      console.error('Failed to generate report:', error);
      alert('Failed to generate report');
    } finally {
      setExecuting(false);
    }
  };

  if (loading) {
    return (
      <div className="p-6">
        <div className="text-center py-12">Loading report builder...</div>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Report Builder</h1>
        <p className="text-gray-600 mt-2">Select a report, configure parameters, and generate</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Report Selection */}
        <div className="lg:col-span-1">
          <div className="bg-white rounded-lg shadow p-4">
            <h2 className="text-lg font-semibold mb-4">Available Reports</h2>
            
            <div className="space-y-2">
              {reportDefinitions.map((report) => (
                <button
                  key={report.id}
                  onClick={() => handleReportSelect(report.code)}
                  className={`w-full text-left p-3 rounded-lg border transition-colors ${
                    selectedReport?.id === report.id
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <div className="font-medium text-sm">{report.name}</div>
                  <div className="text-xs text-gray-500 mt-1">{report.category}</div>
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Report Configuration */}
        <div className="lg:col-span-2">
          {!selectedReport ? (
            <div className="bg-white rounded-lg shadow p-8 text-center">
              <div className="text-gray-400 mb-2">
                <svg className="mx-auto h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <p className="text-gray-600">Select a report to configure and generate</p>
            </div>
          ) : (
            <div className="bg-white rounded-lg shadow">
              <div className="p-6 border-b">
                <h2 className="text-xl font-semibold">{selectedReport.name}</h2>
                <p className="text-sm text-gray-600 mt-1">{selectedReport.description}</p>
                <div className="flex gap-2 mt-3">
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                    {selectedReport.category}
                  </span>
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                    {selectedReport.report_type}
                  </span>
                </div>
              </div>

              <div className="p-6 space-y-6">
                {/* Output Format */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Output Format
                  </label>
                  <select
                    value={outputFormat}
                    onChange={(e) => setOutputFormat(e.target.value)}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2"
                  >
                    {(selectedReport.output_formats || ['pdf', 'excel', 'csv']).map((format: string) => (
                      <option key={format} value={format}>
                        {format.toUpperCase()}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Parameters (if any) */}
                {selectedReport.parameters && Object.keys(selectedReport.parameters).length > 0 && (
                  <div>
                    <h3 className="text-sm font-medium text-gray-700 mb-3">Report Parameters</h3>
                    <div className="space-y-4">
                      {Object.entries(selectedReport.parameters).map(([key, param]: [string, any]) => (
                        <div key={key}>
                          <label className="block text-sm font-medium text-gray-700 mb-1">
                            {param.label || key}
                            {param.required && <span className="text-red-500 ml-1">*</span>}
                          </label>
                          {param.type === 'date' ? (
                            <input
                              type="date"
                              value={parameters[key] || ''}
                              onChange={(e) => handleParameterChange(key, e.target.value)}
                              className="w-full border border-gray-300 rounded-lg px-3 py-2"
                            />
                          ) : param.type === 'select' ? (
                            <select
                              value={parameters[key] || ''}
                              onChange={(e) => handleParameterChange(key, e.target.value)}
                              className="w-full border border-gray-300 rounded-lg px-3 py-2"
                            >
                              <option value="">Select...</option>
                              {(param.options || []).map((opt: any) => (
                                <option key={opt.value} value={opt.value}>
                                  {opt.label}
                                </option>
                              ))}
                            </select>
                          ) : (
                            <input
                              type={param.type === 'number' ? 'number' : 'text'}
                              value={parameters[key] || ''}
                              onChange={(e) => handleParameterChange(key, e.target.value)}
                              placeholder={param.placeholder}
                              className="w-full border border-gray-300 rounded-lg px-3 py-2"
                            />
                          )}
                          {param.help_text && (
                            <p className="text-xs text-gray-500 mt-1">{param.help_text}</p>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Generate Button */}
                <div className="pt-4">
                  <button
                    onClick={handleGenerateReport}
                    disabled={executing}
                    className="w-full bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed font-medium transition-colors"
                  >
                    {executing ? (
                      <span className="flex items-center justify-center">
                        <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>
                        Generating Report...
                      </span>
                    ) : (
                      'Generate Report'
                    )}
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
