/**
 * CCTV Recording & Storage Components
 * 
 * Export all recording and storage management components.
 */

export { RecordingDashboard } from './RecordingDashboard';
export { StorageCalculator } from './StorageCalculator';
export { DVRNVRList } from './DVRNVRList';

// Re-export types from service
export type {
  DVRNVRConfig,
  StorageCalculationParams,
  StorageAnalytics,
  StorageHealth
} from '../../../services/recordingService';
