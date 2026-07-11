/**
 * Manager Review Form Component
 * Manager submits performance review for team member
 */

import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import performanceManagementService from '../../../services/performance.service';
import { EmployeeAppraisal, RatingScale, ManagerReviewSubmit } from '../../../types/performance.types';
import RatingScaleSelector from '../../../components/performance/RatingScaleSelector';

const ManagerReviewForm: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [appraisal, setAppraisal] = useState<EmployeeAppraisal | null>(null);
  const [formData, setFormData] = useState<ManagerReviewSubmit>({
    manager_rating: RatingScale.MEETS_EXPECTATIONS,
    manager_rating_numeric: 3.0,
    manager_comments: '',
    manager_strengths: '',
    manager_development_areas: '',
    recommended_increment_percentage: 0,
    recommended_promotion: false,
    recommended_promotion_designation_id: undefined
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
        
        if (data.manager_rating) {
          setFormData({
            manager_rating: data.manager_rating,
            manager_rating_numeric: data.manager_rating_numeric || 3.0,
            manager_comments: data.manager_comments || '',
            manager_strengths: data.manager_strengths || '',
            manager_development_areas: data.manager_development_areas || '',
            recommended_increment_percentage: data.recommended_increment_percentage || 0,
            recommended_promotion: data.recommended_promotion || false,
            recommended_promotion_designation_id: data.recommended_promotion_designation_id
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
      manager_rating: rating,
      manager_rating_numeric: numeric
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.manager_strengths.trim()) {
      alert('Please document employee strengths');
      return;
    }
    
    if (!formData.manager_development_areas.trim()) {
      alert('Please identify development areas');
      return;
    }
    
    if (window.confirm('Submit manager review for HR approval?')) {
      try {
        setSubmitting(true);
        if (id) {
          await performanceManagementService.appraisals.submitManagerReview(id, formData);
          alert('Manager review submitted successfully!');
          navigate('/performance/appraisals');
        }
      } catch (error) {
        console.error('Error submitting review:', error);
        alert('Failed to submit review');
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
    return <div className="text-center py-8 text-red-600">Appraisal not found</div>;
  }

  return (
    <div className="manager-review-form max-w-6xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Manager Performance Review</h1>
        <p className="text-gray-600 mt-1">Complete performance review for team member</p>
        <p className="text-sm text-gray-500 mt-2">Appraisal Code: {appraisal.appraisal_code}</p>
      </div>

      {/* Employee Self-Assessment Summary */}
      {appraisal.self_rating && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 mb-6">
          <h3 className="font-semibold text-blue-900 mb-3">Employee Self-Assessment Summary</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
            <div>
              <p className="text-blue-700 font-medium">Self Rating:</p>
              <p className="text-blue-900">{appraisal.self_rating.replace(/_/g, ' ')} ({appraisal.self_rating_numeric})</p>
            </div>
            <div>
              <p className="text-blue-700 font-medium">Goal Achievement:</p>
              <p className="text-blue-900">{appraisal.overall_goal_achievement_percentage || 'N/A'}%</p>
            </div>
          </div>
          {appraisal.key_achievements && (
            <div className="mt-3">
              <p className="text-blue-700 font-medium mb-1">Key Achievements:</p>
              <p className="text-blue-900 text-sm whitespace-pre-line">{appraisal.key_achievements}</p>
            </div>
          )}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Manager Rating */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Your Performance Rating</h2>
          <RatingScaleSelector
            value={formData.manager_rating}
            onChange={handleRatingChange}
            label="Rate Employee Performance"
            required={true}
            showLabel={true}
          />
          
          {/* Rating Comparison */}
          {appraisal.self_rating && (
            <div className="mt-4 p-3 bg-gray-50 rounded">
              <p className="text-sm text-gray-700">
                Employee Self-Rating: <span className="font-semibold">{appraisal.self_rating.replace(/_/g, ' ')}</span>
                {' | '}
                Your Rating: <span className="font-semibold">{formData.manager_rating.replace(/_/g, ' ')}</span>
              </p>
            </div>
          )}
        </div>

        {/* Employee Strengths */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Employee Strengths</h2>
          <p className="text-sm text-gray-600 mb-3">
            Highlight the employee's key strengths and positive contributions.
          </p>
          <textarea
            value={formData.manager_strengths}
            onChange={(e) => setFormData({ ...formData, manager_strengths: e.target.value })}
            required
            rows={6}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
            placeholder="Example:
• Strong technical expertise in [area]
• Excellent team collaboration
• Proactive problem solver
• Consistent delivery of quality work"
          />
        </div>

        {/* Development Areas */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Development Areas</h2>
          <p className="text-sm text-gray-600 mb-3">
            Identify areas where the employee can develop and improve.
          </p>
          <textarea
            value={formData.manager_development_areas}
            onChange={(e) => setFormData({ ...formData, manager_development_areas: e.target.value })}
            required
            rows={6}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
            placeholder="Example:
• Focus on [specific skill development]
• Improve [particular area]
• Take ownership of [responsibility]
• Develop expertise in [new area]"
          />
        </div>

        {/* Increment Recommendation */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Increment Recommendation</h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Recommended Increment Percentage
              </label>
              <div className="flex items-center gap-4">
                <input
                  type="number"
                  min="0"
                  max="100"
                  step="0.5"
                  value={formData.recommended_increment_percentage}
                  onChange={(e) => setFormData({ 
                    ...formData, 
                    recommended_increment_percentage: parseFloat(e.target.value) || 0 
                  })}
                  className="w-32 px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                />
                <span className="text-gray-600">%</span>
              </div>
              <p className="text-xs text-gray-500 mt-1">
                Typical range: 0-15% based on performance
              </p>
            </div>

            <div className="flex items-center">
              <input
                type="checkbox"
                id="promotion"
                checked={formData.recommended_promotion}
                onChange={(e) => setFormData({ 
                  ...formData, 
                  recommended_promotion: e.target.checked 
                })}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <label htmlFor="promotion" className="ml-2 block text-sm text-gray-900">
                Recommend for Promotion
              </label>
            </div>

            {formData.recommended_promotion && (
              <div className="pl-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Target Designation
                </label>
                <select
                  value={formData.recommended_promotion_designation_id || ''}
                  onChange={(e) => setFormData({ 
                    ...formData, 
                    recommended_promotion_designation_id: e.target.value || undefined 
                  })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="">Select designation...</option>
                  {/* Add designation options from API */}
                  <option value="senior-dev">Senior Developer</option>
                  <option value="lead-dev">Lead Developer</option>
                  <option value="manager">Manager</option>
                </select>
              </div>
            )}
          </div>
        </div>

        {/* Additional Comments */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Additional Comments (Optional)</h2>
          <textarea
            value={formData.manager_comments}
            onChange={(e) => setFormData({ ...formData, manager_comments: e.target.value })}
            rows={4}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
            placeholder="Any additional context or observations..."
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
            {submitting ? 'Submitting...' : 'Submit Manager Review'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default ManagerReviewForm;
