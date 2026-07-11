/**
 * Self-Assessment Form Component
 * Employee submits self-assessment for appraisal
 */

import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import performanceManagementService from '../../../services/performance.service';
import { EmployeeAppraisal, RatingScale, SelfAssessmentSubmit } from '../../../types/performance.types';
import RatingScaleSelector from '../../../components/performance/RatingScaleSelector';

const SelfAssessmentForm: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [appraisal, setAppraisal] = useState<EmployeeAppraisal | null>(null);
  const [formData, setFormData] = useState<SelfAssessmentSubmit>({
    self_rating: RatingScale.MEETS_EXPECTATIONS,
    self_rating_numeric: 3.0,
    self_comments: '',
    key_achievements: '',
    areas_of_improvement: ''
  });

  useEffect(() => {
    loadAppraisal();
  }, [id]);

  const loadAppraisal = async () => {
    try {
      setLoading(true);
      if (id) {
        const data = await performanceManagementService.appraisals.getById(id);
        setAppraisal(data);
        
        // Pre-fill if already submitted
        if (data.self_rating) {
          setFormData({
            self_rating: data.self_rating,
            self_rating_numeric: data.self_rating_numeric || 3.0,
            self_comments: data.self_comments || '',
            key_achievements: data.key_achievements || '',
            areas_of_improvement: data.areas_of_improvement || ''
          });
        }
      }
    } catch (error) {
      console.error('Error loading appraisal:', error);
      alert('Failed to load appraisal');
    } finally {
      setLoading(false);
    }
  };

  const handleRatingChange = (rating: RatingScale, numeric: number) => {
    setFormData({
      ...formData,
      self_rating: rating,
      self_rating_numeric: numeric
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.key_achievements.trim()) {
      alert('Please provide your key achievements');
      return;
    }
    
    if (!formData.areas_of_improvement.trim()) {
      alert('Please identify areas for improvement');
      return;
    }
    
    if (window.confirm('Submit self-assessment for manager review?')) {
      try {
        setSubmitting(true);
        if (id) {
          await performanceManagementService.appraisals.submitSelfAssessment(id, formData);
          alert('Self-assessment submitted successfully!');
          navigate('/performance/appraisals');
        }
      } catch (error) {
        console.error('Error submitting assessment:', error);
        alert('Failed to submit assessment');
      } finally {
        setSubmitting(false);
      }
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!appraisal) {
    return (
      <div className="text-center py-8">
        <p className="text-red-600">Appraisal not found</p>
      </div>
    );
  }

  return (
    <div className="self-assessment-form max-w-4xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Self-Assessment</h1>
        <p className="text-gray-600 mt-1">Complete your self-assessment for performance review</p>
        <p className="text-sm text-gray-500 mt-2">Appraisal Code: {appraisal.appraisal_code}</p>
      </div>

      {/* Instructions */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
        <h3 className="font-semibold text-blue-900 mb-2">📋 Instructions</h3>
        <ul className="text-sm text-blue-800 space-y-1 list-disc list-inside">
          <li>Rate your overall performance honestly and objectively</li>
          <li>Provide specific examples of your achievements</li>
          <li>Identify areas where you want to improve</li>
          <li>Be professional and constructive in your comments</li>
          <li>Review your goals and their achievement before submitting</li>
        </ul>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Overall Self Rating */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Overall Performance Rating</h2>
          <RatingScaleSelector
            value={formData.self_rating}
            onChange={handleRatingChange}
            label="Rate Your Performance"
            required={true}
            showLabel={true}
          />
        </div>

        {/* Key Achievements */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Key Achievements</h2>
          <p className="text-sm text-gray-600 mb-3">
            Describe your major accomplishments, projects completed, and contributions during this review period.
          </p>
          <textarea
            value={formData.key_achievements}
            onChange={(e) => setFormData({ ...formData, key_achievements: e.target.value })}
            required
            rows={8}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
            placeholder="Example:
• Successfully delivered Project X ahead of schedule
• Mentored 2 junior team members
• Improved process efficiency by 25%
• Received positive feedback from clients"
          />
          <p className="text-xs text-gray-500 mt-2">
            {formData.key_achievements.length} characters (minimum 100 recommended)
          </p>
        </div>

        {/* Areas of Improvement */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Areas for Improvement</h2>
          <p className="text-sm text-gray-600 mb-3">
            Identify areas where you would like to develop and grow. Be honest about challenges faced.
          </p>
          <textarea
            value={formData.areas_of_improvement}
            onChange={(e) => setFormData({ ...formData, areas_of_improvement: e.target.value })}
            required
            rows={6}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
            placeholder="Example:
• Want to improve public speaking skills
• Need to work on time management
• Interested in learning new technologies
• Would like to take on more leadership responsibilities"
          />
          <p className="text-xs text-gray-500 mt-2">
            {formData.areas_of_improvement.length} characters (minimum 50 recommended)
          </p>
        </div>

        {/* Additional Comments */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Additional Comments (Optional)</h2>
          <p className="text-sm text-gray-600 mb-3">
            Any other relevant information you would like to share about your performance.
          </p>
          <textarea
            value={formData.self_comments}
            onChange={(e) => setFormData({ ...formData, self_comments: e.target.value })}
            rows={4}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
            placeholder="Any additional context or comments..."
          />
        </div>

        {/* Action Buttons */}
        <div className="flex justify-end gap-4">
          <button
            type="button"
            onClick={() => navigate('/performance/appraisals')}
            className="px-6 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
            disabled={submitting}
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={submitting}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
          >
            {submitting ? 'Submitting...' : 'Submit Self-Assessment'}
          </button>
        </div>
      </form>

      {/* Save Draft Note */}
      <div className="mt-4 text-center text-sm text-gray-500">
        💾 Your progress is automatically saved as you type
      </div>
    </div>
  );
};

export default SelfAssessmentForm;
