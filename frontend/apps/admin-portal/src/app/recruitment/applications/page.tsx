'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { applicationApi } from '@/services/recruitment.service';
import {
  JobApplication,
  ApplicationStatus,
  KanbanColumn
} from '@/types/recruitment.types';

export default function ApplicationsKanbanPage() {
  const [kanbanData, setKanbanData] = useState<KanbanColumn[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedPosting, setSelectedPosting] = useState<string>('');
  const [postings, setPostings] = useState<any[]>([]);

  // Kanban column definitions
  const columns: Array<{ status: ApplicationStatus; label: string; color: string }> = [
    { status: ApplicationStatus.NEW, label: 'New Applications', color: 'bg-blue-50 border-blue-200' },
    { status: ApplicationStatus.SCREENING, label: 'Screening', color: 'bg-yellow-50 border-yellow-200' },
    { status: ApplicationStatus.SHORTLISTED, label: 'Shortlisted', color: 'bg-purple-50 border-purple-200' },
    { status: ApplicationStatus.INTERVIEW, label: 'Interview', color: 'bg-indigo-50 border-indigo-200' },
    { status: ApplicationStatus.OFFERED, label: 'Offered', color: 'bg-green-50 border-green-200' },
    { status: ApplicationStatus.HIRED, label: 'Hired', color: 'bg-green-100 border-green-300' },
    { status: ApplicationStatus.REJECTED, label: 'Rejected', color: 'bg-red-50 border-red-200' }
  ];

  useEffect(() => {
    loadKanbanData();
    // TODO: Load postings from API
    setPostings([
      { id: '1', title: 'Senior Software Engineer' },
      { id: '2', title: 'Sales Manager' }
    ]);
  }, [selectedPosting]);

  const loadKanbanData = async () => {
    try {
      setLoading(true);
      const data = await applicationApi.getKanban(selectedPosting || undefined);
      setKanbanData(data);
    } catch (error) {
      console.error('Failed to load kanban data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDragStart = (e: React.DragEvent, application: JobApplication) => {
    e.dataTransfer.setData('application', JSON.stringify(application));
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
  };

  const handleDrop = async (e: React.DragEvent, newStatus: ApplicationStatus) => {
    e.preventDefault();
    const applicationData = JSON.parse(e.dataTransfer.getData('application'));
    
    if (applicationData.status === newStatus) return;

    try {
      await applicationApi.changeStatus(applicationData.id, newStatus);
      loadKanbanData();
    } catch (error) {
      console.error('Failed to update application status:', error);
      alert('Failed to update application status');
    }
  };

  const handleShortlist = async (id: string) => {
    try {
      await applicationApi.shortlist(id);
      loadKanbanData();
    } catch (error) {
      console.error('Failed to shortlist application:', error);
      alert('Failed to shortlist application');
    }
  };

  const handleReject = async (id: string) => {
    const reason = prompt('Enter rejection reason:');
    if (!reason) return;
    
    try {
      await applicationApi.reject(id, reason);
      loadKanbanData();
    } catch (error) {
      console.error('Failed to reject application:', error);
      alert('Failed to reject application');
    }
  };

  const getColumnData = (status: ApplicationStatus): KanbanColumn => {
    return kanbanData.find(col => col.status === status) || {
      status,
      label: '',
      applications: [],
      count: 0
    };
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      {/* Header */}
      <div className="mb-6">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Applicant Tracking System</h1>
            <p className="text-gray-600 mt-1">Manage candidate applications across hiring stages</p>
          </div>
          <div className="flex gap-4">
            <select
              value={selectedPosting}
              onChange={(e) => setSelectedPosting(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">All Postings</option>
              {postings.map(posting => (
                <option key={posting.id} value={posting.id}>{posting.title}</option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Stats Summary */}
      <div className="grid grid-cols-7 gap-4 mb-6">
        {columns.map(col => {
          const colData = getColumnData(col.status);
          return (
            <div key={col.status} className="bg-white p-4 rounded-lg shadow">
              <div className="text-gray-600 text-sm font-medium">{col.label}</div>
              <div className="text-2xl font-bold text-gray-900 mt-1">{colData.count}</div>
            </div>
          );
        })}
      </div>

      {/* Kanban Board */}
      {loading ? (
        <div className="bg-white rounded-lg shadow p-8 text-center text-gray-500">
          Loading applications...
        </div>
      ) : (
        <div className="flex gap-4 overflow-x-auto pb-4">
          {columns.map(col => {
            const colData = getColumnData(col.status);
            return (
              <div
                key={col.status}
                className="flex-shrink-0 w-80"
                onDragOver={handleDragOver}
                onDrop={(e) => handleDrop(e, col.status)}
              >
                {/* Column Header */}
                <div className={`${col.color} border-2 rounded-lg p-3 mb-3`}>
                  <div className="flex justify-between items-center">
                    <h3 className="font-semibold text-gray-800">{col.label}</h3>
                    <span className="bg-white px-2 py-1 rounded-full text-sm font-medium">
                      {colData.count}
                    </span>
                  </div>
                </div>

                {/* Applications Cards */}
                <div className="space-y-3 max-h-[calc(100vh-350px)] overflow-y-auto">
                  {colData.applications.map(app => (
                    <div
                      key={app.id}
                      draggable
                      onDragStart={(e) => handleDragStart(e, app)}
                      className="bg-white border-2 border-gray-200 rounded-lg p-4 cursor-move hover:shadow-lg transition-shadow"
                    >
                      {/* Applicant Info */}
                      <div className="mb-3">
                        <h4 className="font-semibold text-gray-900">{app.applicant_name}</h4>
                        <p className="text-sm text-gray-600 mt-1">{app.email}</p>
                        <p className="text-sm text-gray-600">{app.phone}</p>
                      </div>

                      {/* Application Details */}
                      <div className="space-y-1 mb-3">
                        <div className="flex justify-between text-sm">
                          <span className="text-gray-600">Code:</span>
                          <span className="font-medium text-blue-600">{app.application_code}</span>
                        </div>
                        {app.current_company && (
                          <div className="flex justify-between text-sm">
                            <span className="text-gray-600">Company:</span>
                            <span className="font-medium">{app.current_company}</span>
                          </div>
                        )}
                        {app.total_experience_years && (
                          <div className="flex justify-between text-sm">
                            <span className="text-gray-600">Experience:</span>
                            <span className="font-medium">{app.total_experience_years} years</span>
                          </div>
                        )}
                        {app.expected_salary && (
                          <div className="flex justify-between text-sm">
                            <span className="text-gray-600">Expected:</span>
                            <span className="font-medium">₹{(app.expected_salary / 100000).toFixed(1)}L</span>
                          </div>
                        )}
                        <div className="flex justify-between text-sm">
                          <span className="text-gray-600">Source:</span>
                          <span className="font-medium">{app.source}</span>
                        </div>
                        <div className="flex justify-between text-sm">
                          <span className="text-gray-600">Applied:</span>
                          <span className="font-medium">{new Date(app.applied_date).toLocaleDateString()}</span>
                        </div>
                      </div>

                      {/* Action Buttons */}
                      <div className="flex flex-col gap-2 pt-3 border-t border-gray-200">
                        <Link
                          href={`/recruitment/applications/${app.id}`}
                          className="text-center text-sm text-blue-600 hover:text-blue-800 font-medium"
                        >
                          View Details
                        </Link>
                        {app.resume_url && (
                          <a
                            href={app.resume_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-center text-sm text-green-600 hover:text-green-800 font-medium"
                          >
                            View Resume
                          </a>
                        )}
                        {col.status === ApplicationStatus.NEW && (
                          <button
                            onClick={() => handleShortlist(app.id)}
                            className="text-sm bg-purple-100 text-purple-700 px-3 py-1 rounded hover:bg-purple-200 font-medium"
                          >
                            Shortlist
                          </button>
                        )}
                        {col.status === ApplicationStatus.SHORTLISTED && (
                          <Link
                            href={`/recruitment/interviews/new?application_id=${app.id}`}
                            className="text-center text-sm bg-indigo-100 text-indigo-700 px-3 py-1 rounded hover:bg-indigo-200 font-medium"
                          >
                            Schedule Interview
                          </Link>
                        )}
                        {col.status !== ApplicationStatus.REJECTED && col.status !== ApplicationStatus.HIRED && (
                          <button
                            onClick={() => handleReject(app.id)}
                            className="text-sm bg-red-100 text-red-700 px-3 py-1 rounded hover:bg-red-200 font-medium"
                          >
                            Reject
                          </button>
                        )}
                      </div>
                    </div>
                  ))}
                  
                  {colData.applications.length === 0 && (
                    <div className="bg-gray-50 border-2 border-dashed border-gray-300 rounded-lg p-6 text-center text-gray-500 text-sm">
                      No applications in this stage
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Instructions */}
      <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h3 className="font-semibold text-blue-900 mb-2">How to use the Kanban board:</h3>
        <ul className="text-sm text-blue-800 space-y-1">
          <li>• Drag and drop application cards between columns to change their status</li>
          <li>• Click "View Details" to see complete applicant information</li>
          <li>• Use "Shortlist" button to move candidates from New to Shortlisted</li>
          <li>• Schedule interviews directly from shortlisted applications</li>
          <li>• Filter by job posting to focus on specific openings</li>
        </ul>
      </div>
    </div>
  );
}
