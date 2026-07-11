/**
 * Rating Scale Selector Component
 * Reusable component for selecting performance ratings
 */

import React from 'react';
import { RatingScale, RATING_SCALE_LABELS, RATING_SCALE_VALUES } from '../../types/performance.types';

interface RatingScaleSelectorProps {
  value: RatingScale | null;
  onChange: (value: RatingScale, numeric: number) => void;
  disabled?: boolean;
  required?: boolean;
  showLabel?: boolean;
  label?: string;
}

const RatingScaleSelector: React.FC<RatingScaleSelectorProps> = ({
  value,
  onChange,
  disabled = false,
  required = false,
  showLabel = true,
  label = 'Performance Rating'
}) => {
  const ratingOptions = Object.values(RatingScale);

  const getRatingColor = (rating: RatingScale): string => {
    switch (rating) {
      case RatingScale.OUTSTANDING:
        return 'bg-green-900 text-white border-green-900';
      case RatingScale.EXCEEDS_EXPECTATIONS:
        return 'bg-green-600 text-white border-green-600';
      case RatingScale.MEETS_EXPECTATIONS:
        return 'bg-blue-600 text-white border-blue-600';
      case RatingScale.NEEDS_IMPROVEMENT:
        return 'bg-orange-600 text-white border-orange-600';
      case RatingScale.UNSATISFACTORY:
        return 'bg-red-600 text-white border-red-600';
      default:
        return 'bg-gray-200 text-gray-700 border-gray-300';
    }
  };

  const handleSelect = (rating: RatingScale) => {
    if (!disabled) {
      const numeric = RATING_SCALE_VALUES[rating];
      onChange(rating, numeric);
    }
  };

  return (
    <div className="rating-scale-selector">
      {showLabel && (
        <label className="block text-sm font-medium text-gray-700 mb-2">
          {label}
          {required && <span className="text-red-500 ml-1">*</span>}
        </label>
      )}
      
      <div className="grid grid-cols-1 md:grid-cols-5 gap-3">
        {ratingOptions.map((rating) => (
          <button
            key={rating}
            type="button"
            onClick={() => handleSelect(rating)}
            disabled={disabled}
            className={`
              px-4 py-3 rounded-lg border-2 text-center transition-all
              ${value === rating ? getRatingColor(rating) : 'bg-white text-gray-700 border-gray-300'}
              ${!disabled && value !== rating ? 'hover:border-blue-500 hover:shadow-md' : ''}
              ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
            `}
          >
            <div className="font-semibold text-sm">
              {RATING_SCALE_LABELS[rating]}
            </div>
          </button>
        ))}
      </div>

      {value && (
        <div className="mt-2 text-sm text-gray-600">
          Selected: {RATING_SCALE_LABELS[value]} (Numeric: {RATING_SCALE_VALUES[value]})
        </div>
      )}
    </div>
  );
};

export default RatingScaleSelector;
