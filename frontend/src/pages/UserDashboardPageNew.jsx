import { useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import {
    FaTools,
    FaFlask,
    FaBoxOpen,
    FaCheckCircle
} from 'react-icons/fa';

// Actions
import { fetchCheckouts, fetchUserCheckouts } from '../store/checkoutsSlice';
import { fetchChemicals, fetchChemicalsNeedingReorder, fetchChemicalsExpiringSoon } from '../store/chemicalsSlice';
import { fetchKits } from '../store/kitsSlice';
import { fetchRegistrationRequests } from '../store/adminSlice';

// Components
import { StatCard, AnalyticsChart, DistributionChart, QuickLinksGrid } from '../components/dashboard/DashboardWidgetsNew';
import CalibrationNotificationsNew from '../components/calibration/CalibrationNotificationsNew';
import ReceivedItemsAlertWidgetNew from '../components/dashboard/ReceivedItemsAlertWidgetNew';

const UserDashboardPageNew = () => {
    const dispatch = useDispatch();
    const { user } = useSelector((state) => state.auth);
    const { checkouts, userCheckouts } = useSelector((state) => state.checkouts);
    const { chemicals, chemicalsNeedingReorder, chemicalsExpiringSoon } = useSelector((state) => state.chemicals);
    const { kits } = useSelector((state) => state.kits);

    // Role checks
    const isAdmin = user?.is_admin;
    const hasRequestPermission = Boolean(isAdmin || (user?.permissions || []).includes('page.requests') || (user?.permissions || []).includes('page.orders'));

    // Fetch Data
    useEffect(() => {
        dispatch(fetchCheckouts());
        dispatch(fetchUserCheckouts());
        dispatch(fetchChemicals());
        dispatch(fetchChemicalsNeedingReorder());
        dispatch(fetchChemicalsExpiringSoon());
        dispatch(fetchKits());

        if (isAdmin) {
            dispatch(fetchRegistrationRequests('pending'));
        }
    }, [dispatch, isAdmin]);

    // --- Computed Stats ---

    // Tool Stats
    const totalCheckouts = checkouts.length;
    const myCheckoutsCount = userCheckouts.length;
    const toolsTrend = 5.2; // Mock trend for now

    // Chemical Stats
    const lowStockCount = chemicalsNeedingReorder.length;
    const expiringCount = chemicalsExpiringSoon.length;
    const totalChemicals = chemicals.length;

    // Kit Stats
    const activeKits = kits.filter(k => k.status === 'active').length;

    // --- Chart Data Preparation ---

    // Mock Checkout Trend Data (Last 7 Days)
    const checkoutTrendData = [
        { name: 'Mon', value: 12 },
        { name: 'Tue', value: 19 },
        { name: 'Wed', value: 15 },
        { name: 'Thu', value: 22 },
        { name: 'Fri', value: 28 },
        { name: 'Sat', value: 8 },
        { name: 'Sun', value: 5 },
    ];

    // Chemical Status Distribution
    const chemicalStatusData = [
        { name: 'Available', value: totalChemicals - lowStockCount - expiringCount },
        { name: 'Low Stock', value: lowStockCount },
        { name: 'Expiring', value: expiringCount },
    ];
    const chemicalColors = ['#10b981', '#f59e0b', '#ef4444'];

    // Kit Usage Mock Data
    const kitUsageData = [
        { name: 'Week 1', value: 45 },
        { name: 'Week 2', value: 52 },
        { name: 'Week 3', value: 38 },
        { name: 'Week 4', value: 65 },
    ];

    return (
        <div className="space-y-6">
            {/* Header Section */}
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                <div>
                    <h2 className="text-3xl font-bold tracking-tight">Dashboard</h2>
                    <p className="text-muted-foreground">Welcome back, {user?.first_name || 'User'}</p>
                </div>
            </div>

            {/* Main Grid Layout */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">

                {/* Top Stats Row */}
                <div className="col-span-1">
                    <StatCard
                        title="Total Checkouts"
                        value={totalCheckouts}
                        trend={toolsTrend}
                        trendLabel="vs last week"
                        icon={<FaTools />}
                        color="#3b82f6"
                    />
                </div>
                <div className="col-span-1">
                    <StatCard
                        title="My Active Tools"
                        value={myCheckoutsCount}
                        icon={<FaCheckCircle />}
                        color="#10b981"
                        onClick={() => window.location.href = '/my-checkouts'}
                    />
                </div>
                <div className="col-span-1">
                    <StatCard
                        title="Low Stock Chemicals"
                        value={lowStockCount}
                        trend={lowStockCount > 0 ? -10 : 0}
                        trendLabel="needs attention"
                        icon={<FaFlask />}
                        color="#f59e0b"
                    />
                </div>
                <div className="col-span-1">
                    <StatCard
                        title="Active Kits"
                        value={activeKits}
                        icon={<FaBoxOpen />}
                        color="#8b5cf6"
                    />
                </div>

                {/* Main Chart Area */}
                <div className="col-span-1 md:col-span-2 lg:col-span-3 h-[400px]">
                    <AnalyticsChart
                        title="Tool Usage Trends"
                        data={checkoutTrendData}
                        dataKey="value"
                        color="#3b82f6"
                        height={320}
                    />
                </div>

                {/* Quick Links */}
                <div className="col-span-1 md:col-span-2 lg:col-span-1 h-[400px]">
                    <QuickLinksGrid />
                </div>

                {/* Secondary Row */}
                <div className="col-span-1 md:col-span-1 lg:col-span-2 h-[350px]">
                    <DistributionChart
                        title="Chemical Inventory Status"
                        data={chemicalStatusData}
                        colors={chemicalColors}
                        height={270}
                    />
                </div>

                <div className="col-span-1 md:col-span-1 lg:col-span-2 h-[350px]">
                    <AnalyticsChart
                        title="Kit Usage Activity"
                        data={kitUsageData}
                        dataKey="value"
                        color="#8b5cf6"
                        type="line"
                        height={270}
                    />
                </div>

                {/* Notifications Area */}
                <div className="col-span-1 md:col-span-2 lg:col-span-4">
                    <CalibrationNotificationsNew />
                </div>

                {/* Received Items Alert Widget */}
                {hasRequestPermission && (
                    <div className="col-span-1 md:col-span-2 lg:col-span-4">
                        <ReceivedItemsAlertWidgetNew />
                    </div>
                )}

            </div>
        </div>
    );
};

export default UserDashboardPageNew;
