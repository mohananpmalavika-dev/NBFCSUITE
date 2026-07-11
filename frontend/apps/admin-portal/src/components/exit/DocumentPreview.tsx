/**
 * Document Preview Component
 * Preview and manage exit documents
 */

import React from 'react';
import { ExitDocument, EXIT_DOCUMENT_TYPE_LABELS } from '@/types/exit.types';

interface DocumentPreviewProps {
  document: ExitDocument;
  onDownload?: (documentId: string) => void;
  onApprove?: (documentId: string) => void;
  onIssue?: (documentId: string) => void;
  readOnly?: boolean;
}

const DocumentPreview: React.FC<DocumentPreviewProps> = ({
  document,
  onDownload,
  onApprove,
  onIssue,
  readOnly = false
}) => {
  const getDocumentIcon = () => {
    return (
      <svg className="w-12 h-12 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
      </svg>
    );
  };

  const getStatusBadge = () => {
    if (document.is_issued) {
      return (
        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800 border border-green-200">
          <svg className="w-4 h-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
          </svg>
          Issued
        </span>
      );
    } else if (document.is_approved) {
      return (
        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800 border border-blue-200">
          Approved
        </span>
      );
    } else if (document.is_generated) {
      return (
        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800 border border-yellow-200">
          Pending Approval
        </span>
      );
    } else {
      return (
        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800 border border-gray-200">
          Draft
        </span>
      );
    }
  };

  return (
    <div className="border border-gray-200 rounded-lg overflow-hidden hover:shadow-md transition-shadow">
      {/* Header */}
      <div className="bg-gray-50 px-4 py-3 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            {getDocumentIcon()}
            <div>
              <h3 className="text-sm font-semibold text-gray-900">
                {document.document_name}
              </h3>
              <p className="text-xs text-gray-500">
                {EXIT_DOCUMENT_TYPE_LABELS[document.document_type]}
              </p>
            </div>
          </div>
          {getStatusBadge()}
        </div>
      </div>

      {/* Content */}
      <div className="p-4 bg-white space-y-3">
        {/* Document Info */}
        <div className="grid grid-cols-2 gap-3 text-sm">
          {document.document_code && (
            <div>
              <p className="text-gray-500">Document Code</p>
              <p className="font-medium text-gray-900">{document.document_code}</p>
            </div>
          )}
          {document.document_number && (
            <div>
              <p className="text-gray-500">Document Number</p>
              <p className="font-medium text-gray-900">{document.document_number}</p>
            </div>
          )}
          {document.issue_place && (
            <div>
              <p className="text-gray-500">Issue Place</p>
              <p className="font-medium text-gray-900">{document.issue_place}</p>
            </div>
          )}
          {document.validity_date && (
            <div>
              <p className="text-gray-500">Valid Until</p>
              <p className="font-medium text-gray-900">
                {new Date(document.validity_date).toLocaleDateString()}
              </p>
            </div>
          )}
        </div>

        {/* Description */}
        {document.description && (
          <div>
            <p className="text-xs text-gray-500 mb-1">Description</p>
            <p className="text-sm text-gray-700">{document.description}</p>
          </div>
        )}

        {/* Timeline */}
        <div className="space-y-2 pt-2 border-t border-gray-100">
          {document.generated_date && (
            <div className="flex items-center text-xs text-gray-600">
              <svg className="w-4 h-4 mr-2 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span>
                Generated on {new Date(document.generated_date).toLocaleString()}
              </span>
            </div>
          )}
          {document.approved_date && (
            <div className="flex items-center text-xs text-gray-600">
              <svg className="w-4 h-4 mr-2 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span>
                Approved on {new Date(document.approved_date).toLocaleString()}
              </span>
            </div>
          )}
          {document.issued_date && (
            <div className="flex items-center text-xs text-gray-600">
              <svg className="w-4 h-4 mr-2 text-purple-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span>
                Issued on {new Date(document.issued_date).toLocaleString()}
              </span>
            </div>
          )}
        </div>

        {/* Approval Remarks */}
        {document.approval_remarks && (
          <div className="bg-blue-50 border border-blue-200 rounded p-2">
            <p className="text-xs font-medium text-blue-900">Approval Remarks</p>
            <p className="text-xs text-blue-800 mt-1">{document.approval_remarks}</p>
          </div>
        )}

        {/* Issue Remarks */}
        {document.issue_remarks && (
          <div className="bg-green-50 border border-green-200 rounded p-2">
            <p className="text-xs font-medium text-green-900">Issue Remarks</p>
            <p className="text-xs text-green-800 mt-1">{document.issue_remarks}</p>
            {document.delivery_mode && (
              <p className="text-xs text-green-700 mt-1">
                Delivery: {document.delivery_mode}
              </p>
            )}
          </div>
        )}

        {/* Digital Signature */}
        {document.is_digitally_signed && (
          <div className="flex items-center text-xs text-green-700">
            <svg className="w-4 h-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
            </svg>
            <span className="font-medium">Digitally Signed</span>
          </div>
        )}

        {/* Employee Acknowledgment */}
        {document.acknowledged_by_employee && document.acknowledgment_date && (
          <div className="bg-green-50 border border-green-200 rounded p-2 flex items-center">
            <svg className="w-5 h-5 mr-2 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <div className="text-xs">
              <p className="font-medium text-green-900">Acknowledged by Employee</p>
              <p className="text-green-700">
                on {new Date(document.acknowledgment_date).toLocaleString()}
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Actions */}
      {!readOnly && (
        <div className="bg-gray-50 px-4 py-3 border-t border-gray-200 flex justify-end space-x-2">
          {document.document_path && onDownload && (
            <button
              onClick={() => onDownload(document.id)}
              className="inline-flex items-center px-3 py-1.5 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded hover:bg-gray-50"
            >
              <svg className="w-4 h-4 mr-1.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
              </svg>
              Download
            </button>
          )}
          {document.is_generated && !document.is_approved && onApprove && (
            <button
              onClick={() => onApprove(document.id)}
              className="inline-flex items-center px-3 py-1.5 text-sm font-medium text-white bg-blue-600 rounded hover:bg-blue-700"
            >
              Approve
            </button>
          )}
          {document.is_approved && !document.is_issued && onIssue && (
            <button
              onClick={() => onIssue(document.id)}
              className="inline-flex items-center px-3 py-1.5 text-sm font-medium text-white bg-green-600 rounded hover:bg-green-700"
            >
              Issue Document
            </button>
          )}
        </div>
      )}
    </div>
  );
};

export default DocumentPreview;
