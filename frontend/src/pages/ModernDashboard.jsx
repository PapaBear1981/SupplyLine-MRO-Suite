import React, { useEffect, useState, useMemo } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
    Activity,
    AlertCircle,
    Box,
    CheckCircle,
    Clock,
    CreditCard,
    FileText,
    LayoutDashboard,
    Package,
    Search,
    Settings,
    ShoppingCart,
    TrendingUp,
    User,
    Users,
    Wrench
} from 'lucide-react';
import { fetchUserCheckouts } from '../store/checkoutsSlice';
import { fetchOrders } from '../store/ordersSlice';
import { fetchRegistrationRequests } from '../store/adminSlice';
import api from '../services/api';
import '../styles/ModernDashboard.css';

// Mock chart component since we don't have a charting library installed yet that fits perfectly
// or we can use a simple SVG implementation for the "pop"
const ActivityChart = ({ data }) => {
    // Simple SVG Area Chart
    const height = 200;
    const width = 600;
    const points = data.map((d, i) => {
        const x = (i / (data.length - 1)) * width;
        const y = height - (d.value / 10) * height; // Scale value
        return `${x},${y}`;
    }).join(' ');

    return (
        <div className="w-100 overflow-hidden" style={{ height: '200px' }}>
            <svg viewBox={`0 0 ${width} ${height}`} className="w-100 h-100" preserveAspectRatio="none">
                <defs>
                    <linearGradient id="chartGradient" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="0%" stopColor="var(--dashboard-primary)" stopOpacity="0.3" />
                        <stop offset="100%" stopColor="var(--dashboard-primary)" stopOpacity="0" />
                    </linearGradient>
                </defs>
                <path
                    d={`M0,${height} ${points} ${width},${height} Z`}
                    fill="url(#chartGradient)"
                />
                <path
                    d={`M${points}`}
                    fill="none"
                    stroke="var(--dashboard-primary)"
                    strokeWidth="3"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                />
            </svg>
        </div>
    );
};

const ModernDashboard = () => {
    const dispatch = useDispatch();
    const { user } = useSelector((state) => state.auth);
    const { userCheckouts } = useSelector((state) => state.checkouts);
    const { list: orders } = useSelector((state) => state.orders);
    const [activities, setActivities] = useState([]);
    const [loadingActivity, setLoadingActivity] = useState(true);

    // Initial Data Fetch
    useEffect(() => {
        dispatch(fetchUserCheckouts());
        dispatch(fetchOrders({ sort: 'created', limit: 50 }));
        if (user?.is_admin) {
            dispatch(fetchRegistrationRequests('pending'));
        }

        const fetchActivity = async () => {
            try {
                const response = await api.get('/user/activity');
                setActivities(response.data);
            } catch (error) {
                console.error('Failed to fetch activity', error);
            } finally {
                setLoadingActivity(false);
            }
        };
        fetchActivity();
    }, [dispatch, user]);

    // Derived State
    const activeCheckouts = useMemo(() =>
        userCheckouts.filter(c => !c.return_date),
        [userCheckouts]);

    const overdueCheckouts = useMemo(() => {
        const today = new Date();
        return activeCheckouts.filter(c => {
            if (!c.expected_return_date) return false;
            return new Date(c.expected_return_date) < today;
        });
    }, [activeCheckouts]);

    const myOpenRequests = useMemo(() =>
        orders.filter(o => o.requester_id === user?.id && !['received', 'cancelled'].includes(o.status)),
        [orders, user]);

    // Mock Chart Data (replace with real analytics later)
    const chartData = [
        { day: 'Mon', value: 3 },
        { day: 'Tue', value: 5 },
        { day: 'Wed', value: 2 },
        { day: 'Thu', value: 8 },
        { day: 'Fri', value: 4 },
        { day: 'Sat', value: 6 },
        { day: 'Sun', value: 9 },
    ];

    const containerVariants = {
        hidden: { opacity: 0 },
        visible: {
            opacity: 1,
            transition: {
                staggerChildren: 0.1
            }
        }
    };

    const itemVariants = {
        hidden: { y: 20, opacity: 0 },
        visible: {
            y: 0,
            opacity: 1,
            transition: { type: 'spring', stiffness: 100 }
        }
    };

    const getGreeting = () => {
        const hour = new Date().getHours();
        if (hour < 12) return 'Good Morning';
        if (hour < 18) return 'Good Afternoon';
        return 'Good Evening';
    };

    return (
        <div className="w-100">
            <motion.div
                className="modern-dashboard"
                variants={containerVariants}
                initial="hidden"
                animate="visible"
            >
                {/* Header Section */}
                <motion.div className="dashboard-header d-flex justify-content-between align-items-end" variants={itemVariants}>
                    <div className="welcome-text">
                        <h1 className="display-5">{getGreeting()}, {user?.first_name || 'User'}!</h1>
                        <p className="text-muted mb-0">Here's what's happening with your inventory today.</p>
                    </div>
                    <div className="d-flex gap-3">
                        <div className="text-end d-none d-md-block">
                            <div className="fw-bold">{new Date().toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}</div>
                            <div className="text-muted small">System Status: Operational</div>
                        </div>
                    </div>
                </motion.div>

                {/* Stats Grid */}
                <div className="row g-4 mb-5">
                    <div className="col-md-6 col-lg-3">
                        <motion.div className="glass-panel stat-card" variants={itemVariants}>
                            <div>
                                <div className="stat-value text-primary">{activeCheckouts.length}</div>
                                <div className="stat-label">Active Checkouts</div>
                            </div>
                            <div className="stat-icon">
                                <Wrench size={24} />
                            </div>
                        </motion.div>
                    </div>

                    <div className="col-md-6 col-lg-3">
                        <motion.div className="glass-panel stat-card" variants={itemVariants}>
                            <div>
                                <div className={`stat-value ${overdueCheckouts.length > 0 ? 'text-danger' : 'text-success'}`}>
                                    {overdueCheckouts.length}
                                </div>
                                <div className="stat-label">Overdue Items</div>
                            </div>
                            <div className="stat-icon" style={{ color: overdueCheckouts.length > 0 ? '#ef4444' : '#10b981', background: overdueCheckouts.length > 0 ? 'rgba(239, 68, 68, 0.1)' : 'rgba(16, 185, 129, 0.1)' }}>
                                <Clock size={24} />
                            </div>
                        </motion.div>
                    </div>

                    <div className="col-md-6 col-lg-3">
                        <motion.div className="glass-panel stat-card" variants={itemVariants}>
                            <div>
                                <div className="stat-value text-info">{myOpenRequests.length}</div>
                                <div className="stat-label">Pending Requests</div>
                            </div>
                            <div className="stat-icon" style={{ color: '#3b82f6', background: 'rgba(59, 130, 246, 0.1)' }}>
                                <ShoppingCart size={24} />
                            </div>
                        </motion.div>
                    </div>

                    <div className="col-md-6 col-lg-3">
                        <motion.div className="glass-panel stat-card" variants={itemVariants}>
                            <div>
                                <div className="stat-value text-warning">--</div>
                                <div className="stat-label">Efficiency Score</div>
                            </div>
                            <div className="stat-icon" style={{ color: '#f59e0b', background: 'rgba(245, 158, 11, 0.1)' }}>
                                <TrendingUp size={24} />
                            </div>
                        </motion.div>
                    </div>
                </div>

                <div className="row g-4">
                    {/* Main Content Column */}
                    <div className="col-lg-8">
                        {/* Activity Chart Section */}
                        <motion.div className="glass-panel mb-4" variants={itemVariants}>
                            <div className="d-flex justify-content-between align-items-center mb-4">
                                <h5 className="mb-0 fw-bold">Weekly Activity</h5>
                                <select className="form-select form-select-sm w-auto bg-transparent border-0">
                                    <option>This Week</option>
                                    <option>Last Week</option>
                                </select>
                            </div>
                            <ActivityChart data={chartData} />
                        </motion.div>

                        {/* Recent Activity List */}
                        <motion.div className="glass-panel" variants={itemVariants}>
                            <div className="d-flex justify-content-between align-items-center mb-3">
                                <h5 className="mb-0 fw-bold">Recent Activity</h5>
                                <button className="btn btn-sm btn-link text-decoration-none">View All</button>
                            </div>
                            <div className="custom-scroll">
                                {activities.length === 0 ? (
                                    <div className="text-center py-4 text-muted">No recent activity</div>
                                ) : (
                                    activities.slice(0, 5).map((activity) => (
                                        <div key={activity.id} className="list-item">
                                            <div className="me-3">
                                                <div className="rounded-circle bg-light p-2 d-flex align-items-center justify-content-center" style={{ width: '40px', height: '40px' }}>
                                                    <Activity size={18} className="text-primary" />
                                                </div>
                                            </div>
                                            <div className="flex-grow-1">
                                                <div className="fw-semibold text-dark">{activity.description || activity.activity_type}</div>
                                                <div className="small text-muted">{new Date(activity.timestamp).toLocaleString()}</div>
                                            </div>
                                            <div className="text-end">
                                                <span className="status-badge info">Log</span>
                                            </div>
                                        </div>
                                    ))
                                )}
                            </div>
                        </motion.div>
                    </div>

                    {/* Sidebar Column */}
                    <div className="col-lg-4">
                        {/* Quick Actions */}
                        <motion.div className="glass-panel mb-4" variants={itemVariants}>
                            <h5 className="mb-3 fw-bold">Quick Actions</h5>
                            <div className="row g-3">
                                <div className="col-6">
                                    <Link to="/scanner" className="quick-action-btn">
                                        <div className="quick-action-icon text-primary">
                                            <Search size={28} />
                                        </div>
                                        <span className="small fw-semibold">Scan Tool</span>
                                    </Link>
                                </div>
                                <div className="col-6">
                                    <Link to="/requests" className="quick-action-btn">
                                        <div className="quick-action-icon text-success">
                                            <FileText size={28} />
                                        </div>
                                        <span className="small fw-semibold">New Request</span>
                                    </Link>
                                </div>
                                <div className="col-6">
                                    <Link to="/my-checkouts" className="quick-action-btn">
                                        <div className="quick-action-icon text-warning">
                                            <Box size={28} />
                                        </div>
                                        <span className="small fw-semibold">My Items</span>
                                    </Link>
                                </div>
                                <div className="col-6">
                                    <Link to="/profile" className="quick-action-btn">
                                        <div className="quick-action-icon text-info">
                                            <Settings size={28} />
                                        </div>
                                        <span className="small fw-semibold">Settings</span>
                                    </Link>
                                </div>
                            </div>
                        </motion.div>

                        {/* Announcements / Notifications */}
                        <motion.div className="glass-panel" variants={itemVariants}>
                            <h5 className="mb-3 fw-bold">Announcements</h5>
                            <div className="list-item">
                                <div className="me-3">
                                    <AlertCircle size={20} className="text-warning" />
                                </div>
                                <div>
                                    <div className="fw-semibold text-dark">System Maintenance</div>
                                    <div className="small text-muted">Scheduled for Friday 10 PM</div>
                                </div>
                            </div>
                            <div className="list-item">
                                <div className="me-3">
                                    <CheckCircle size={20} className="text-success" />
                                </div>
                                <div>
                                    <div className="fw-semibold text-dark">Inventory Audit Complete</div>
                                    <div className="small text-muted">All items accounted for</div>
                                </div>
                            </div>
                        </motion.div>
                    </div>
                </div>
            </motion.div>
        </div>
    );
};

export default ModernDashboard;
