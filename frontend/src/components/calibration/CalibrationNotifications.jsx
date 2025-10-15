import { useState, useEffect } from 'react';
import { Alert, Button, Badge } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import { useSelector, useDispatch } from 'react-redux';
import { fetchCalibrationsDue, fetchOverdueCalibrations } from '../../store/calibrationSlice';

const CalibrationNotifications = () => {
  const dispatch = useDispatch();
  const { calibrationsDue, overdueCalibrations } = useSelector((state) => state.calibration);
  const { user } = useSelector((state) => state.auth);

  const [showDueNotification, setShowDueNotification] = useState(true);
  const [showOverdueNotification, setShowOverdueNotification] = useState(true);

  // Check if user has permission to see calibration notifications
  const hasPermission = user?.is_admin || user?.department === 'Materials';

  useEffect(() => {
    if (hasPermission) {
      dispatch(fetchCalibrationsDue(30)); // Get tools due for calibration in the next 30 days
      dispatch(fetchOverdueCalibrations());
    }
  }, [dispatch, hasPermission]);

  // Don't show notifications if user doesn't have permission
  if (!hasPermission) {
    return null;
  }

  // Don't show notifications if there are no tools due or overdue for calibration
  if (
    (!calibrationsDue || calibrationsDue.length === 0) &&
    (!overdueCalibrations || overdueCalibrations.length === 0)
  ) {
    return null;
  }

  return (
    <div className="mb-4">
      {showOverdueNotification && overdueCalibrations && overdueCalibrations.length > 0 && (
        <Alert
          variant="danger"
          dismissible
          onClose={() => setShowOverdueNotification(false)}
          className="d-flex justify-content-between align-items-center"
        >
          <div>
            <Alert.Heading>Overdue Calibrations</Alert.Heading>
            <p>
              There {overdueCalibrations.length === 1 ? 'is' : 'are'} <strong>{overdueCalibrations.length}</strong> tool{overdueCalibrations.length === 1 ? '' : 's'} with overdue calibrations.
              These tools should not be used until they have been recalibrated.
            </p>
          </div>
          <div>
            <Button
              as={Link}
              to="/calibrations?tab=overdue"
              variant="outline-danger"
              size="sm"
            >
              View Overdue Tools
            </Button>
          </div>
        </Alert>
      )}

      {showDueNotification && calibrationsDue && calibrationsDue.length > 0 && (
        <Alert
          variant="warning"
          dismissible
          onClose={() => setShowDueNotification(false)}
          className="d-flex justify-content-between align-items-center"
        >
          <div>
            <Alert.Heading>Calibrations Due Soon</Alert.Heading>
            <p>
              There {calibrationsDue.length === 1 ? 'is' : 'are'} <strong>{calibrationsDue.length}</strong> tool{calibrationsDue.length === 1 ? '' : 's'} due for calibration in the next 30 days.
            </p>
          </div>
          <div>
            <Button
              as={Link}
              to="/calibrations?tab=due"
              variant="outline-warning"
              size="sm"
            >
              View Due Tools
            </Button>
          </div>
        </Alert>
      )}
    </div>
  );
};

export default CalibrationNotifications;
