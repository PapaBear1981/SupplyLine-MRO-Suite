import { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Link } from 'react-router-dom';
import { formatDistanceToNow } from 'date-fns';
import { Bell, CheckCircle, ExternalLink, X, Loader2 } from 'lucide-react';

import { dismissAlert, dismissAllAlerts } from '../../store/requestAlertsSlice';
import { Card, CardContent, CardHeader, CardTitle, CardFooter } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';

const ReceivedItemsAlertWidgetNew = () => {
    const dispatch = useDispatch();
    const { alerts, loading } = useSelector((state) => state.requestAlerts);

    useEffect(() => {
        // Temporarily disabled due to backend schema issues
        // dispatch(fetchRequestAlerts(false)); // Only fetch non-dismissed alerts
    }, [dispatch]);

    const handleDismiss = (alertId, event) => {
        event.preventDefault();
        event.stopPropagation();
        dispatch(dismissAlert(alertId));
    };

    const handleDismissAll = (event) => {
        event.preventDefault();
        event.stopPropagation();
        if (window.confirm(`Are you sure you want to dismiss all ${alerts.length} alert(s)?`)) {
            dispatch(dismissAllAlerts());
        }
    };

    return (
        <Card className="shadow-sm mb-4">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <div className="flex items-center gap-2">
                    <Bell className="h-4 w-4 text-yellow-500" />
                    <CardTitle className="text-base font-medium">Received Items</CardTitle>
                </div>
                <div className="flex items-center gap-2">
                    {alerts.length > 0 && (
                        <>
                            <Badge variant="warning" className="rounded-full px-2 py-0.5 text-xs">
                                {alerts.length}
                            </Badge>
                            <Button
                                variant="link"
                                size="sm"
                                className="h-auto p-0 text-xs text-muted-foreground hover:text-foreground"
                                onClick={handleDismissAll}
                                title="Dismiss all alerts"
                            >
                                Clear All
                            </Button>
                        </>
                    )}
                </div>
            </CardHeader>
            <CardContent className="p-0">
                {loading ? (
                    <div className="flex justify-center items-center py-8">
                        <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
                    </div>
                ) : alerts.length === 0 ? (
                    <div className="flex flex-col items-center justify-center py-8 text-center text-muted-foreground">
                        <CheckCircle className="mb-2 h-8 w-8 text-green-500" />
                        <p className="mb-1 font-medium">No new alerts</p>
                        <small className="text-xs">You will be notified when requested items are received.</small>
                    </div>
                ) : (
                    <div className="divide-y">
                        {alerts.map((alert) => (
                            <div key={alert.id} className="flex items-start justify-between p-4 hover:bg-muted/50 transition-colors">
                                <div className="flex-1 space-y-1">
                                    <div className="flex items-center gap-2 mb-1">
                                        <Badge variant="success" className="gap-1 px-2 py-0.5 text-[10px] font-normal">
                                            <Bell className="h-3 w-3" />
                                            Items Received
                                        </Badge>
                                        {alert.request_number && (
                                            <span className="text-xs text-muted-foreground">
                                                {alert.request_number}
                                            </span>
                                        )}
                                    </div>
                                    <div className="font-medium text-sm">
                                        <Link
                                            to={`/requests?highlight=${alert.request_id}`}
                                            className="hover:underline decoration-primary underline-offset-4"
                                        >
                                            {alert.request_title || `Request #${alert.request_number}`}
                                        </Link>
                                    </div>
                                    <div className="text-xs text-muted-foreground">{alert.message}</div>
                                    <div className="text-[10px] text-muted-foreground/70">
                                        {alert.created_at && formatDistanceToNow(new Date(alert.created_at), { addSuffix: true })}
                                    </div>
                                </div>
                                <Button
                                    variant="ghost"
                                    size="icon"
                                    className="h-6 w-6 text-muted-foreground hover:text-destructive"
                                    onClick={(e) => handleDismiss(alert.id, e)}
                                    title="Dismiss alert"
                                >
                                    <X className="h-4 w-4" />
                                    <span className="sr-only">Dismiss</span>
                                </Button>
                            </div>
                        ))}
                    </div>
                )}
            </CardContent>
            {alerts.length > 0 && (
                <CardFooter className="justify-end border-t bg-muted/20 p-2">
                    <Link
                        to="/requests"
                        className="flex items-center gap-1 text-xs text-muted-foreground hover:text-primary transition-colors"
                    >
                        View all requests <ExternalLink className="h-3 w-3" />
                    </Link>
                </CardFooter>
            )}
        </Card>
    );
};

export default ReceivedItemsAlertWidgetNew;
