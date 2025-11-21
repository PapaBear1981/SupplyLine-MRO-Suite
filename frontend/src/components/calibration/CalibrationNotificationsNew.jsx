import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useSelector, useDispatch } from 'react-redux';
import { AlertTriangle, Calendar, X } from 'lucide-react';

import { fetchCalibrationsDue, fetchOverdueCalibrations } from '../../store/calibrationSlice';
import { Alert, AlertTitle, AlertDescription } from '../ui/alert';
import { Button } from '../ui/button';

const CalibrationNotificationsNew = () => {
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
        <div className="space-y-4 mb-4">
            {showOverdueNotification && overdueCalibrations && overdueCalibrations.length > 0 && (
                <Alert variant="destructive" className="flex items-start justify-between">
                    <div className="flex-1">
                        <div className="flex items-center gap-2">
                            <AlertTriangle className="h-4 w-4" />
                            <AlertTitle>Overdue Calibrations</AlertTitle>
                        </div>
                        <AlertDescription className="mt-1">
                            There {overdueCalibrations.length === 1 ? 'is' : 'are'} <strong>{overdueCalibrations.length}</strong> tool{overdueCalibrations.length === 1 ? '' : 's'} with overdue calibrations.
                            These tools should not be used until they have been recalibrated.
                        </AlertDescription>
                        <div className="mt-2">
                            <Button
                                variant="outline"
                                size="sm"
                                className="border-destructive/50 text-destructive hover:bg-destructive/10 hover:text-destructive"
                                asChild
                            >
                                <Link to="/calibrations?tab=overdue">View Overdue Tools</Link>
                            </Button>
                        </div>
                    </div>
                    <Button
                        variant="ghost"
                        size="icon"
                        className="h-6 w-6 text-destructive hover:bg-destructive/10 -mt-1 -mr-2"
                        onClick={() => setShowOverdueNotification(false)}
                    >
                        <X className="h-4 w-4" />
                        <span className="sr-only">Dismiss</span>
                    </Button>
                </Alert>
            )}

            {showDueNotification && calibrationsDue && calibrationsDue.length > 0 && (
                <Alert variant="warning" className="flex items-start justify-between">
                    <div className="flex-1">
                        <div className="flex items-center gap-2">
                            <Calendar className="h-4 w-4" />
                            <AlertTitle>Calibrations Due Soon</AlertTitle>
                        </div>
                        <AlertDescription className="mt-1">
                            There {calibrationsDue.length === 1 ? 'is' : 'are'} <strong>{calibrationsDue.length}</strong> tool{calibrationsDue.length === 1 ? '' : 's'} due for calibration in the next 30 days.
                        </AlertDescription>
                        <div className="mt-2">
                            <Button
                                variant="outline"
                                size="sm"
                                className="border-yellow-500/50 text-yellow-600 hover:bg-yellow-500/10 hover:text-yellow-600 dark:text-yellow-500 dark:hover:text-yellow-400"
                                asChild
                            >
                                <Link to="/calibrations?tab=due">View Due Tools</Link>
                            </Button>
                        </div>
                    </div>
                    <Button
                        variant="ghost"
                        size="icon"
                        className="h-6 w-6 text-yellow-600 hover:bg-yellow-500/10 -mt-1 -mr-2 dark:text-yellow-500"
                        onClick={() => setShowDueNotification(false)}
                    >
                        <X className="h-4 w-4" />
                        <span className="sr-only">Dismiss</span>
                    </Button>
                </Alert>
            )}
        </div>
    );
};

export default CalibrationNotificationsNew;
