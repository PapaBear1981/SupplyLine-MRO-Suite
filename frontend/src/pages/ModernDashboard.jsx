import React, { useEffect, useState, useMemo } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Link, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Form, InputGroup, Dropdown, ButtonGroup } from 'react-bootstrap';
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
    Wrench,
    Filter,
    Beaker,
    Briefcase
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
    const navigate = useNavigate();
    const { user } = useSelector((state) => state.auth);
    const { userCheckouts } = useSelector((state) => state.checkouts);
    const { list: orders } = useSelector((state) => state.orders);
    const [activities, setActivities] = useState([]);
    const [loadingActivity, setLoadingActivity] = useState(true);

    // Search and Filter State
    const [searchQuery, setSearchQuery] = useState('');
    const [activityType, setActivityType] = useState('user'); // user, kit, chemical, orders, requests, checkouts
    const [timeRange, setTimeRange] = useState('week'); // week, month, quarter, year
    const [chartData, setChartData] = useState([]);

    // Initial Data Fetch
    useEffect(() => {
        dispatch(fetchUserCheckouts());
        dispatch(fetchOrders({ sort: 'created', limit: 50 }));
        if (user?.is_admin) {
            dispatch(fetchRegistrationRequests('pending'));
        }
    }, [dispatch, user]);

    // Fetch activity data based on selected type and time range
    useEffect(() => {
        const fetchActivityData = async () => {
            setLoadingActivity(true);
            try {
                let endpoint = '/user/activity';
                const params = { timeRange };

                // Determine endpoint based on activity type
                switch (activityType) {
                    case 'kit':
                        endpoint = '/kits/activity';
                        break;
                    case 'chemical':
                        endpoint = '/chemicals/activity';
                        break;
                    case 'orders':
                        endpoint = '/orders';
                        break;
                    case 'requests':
                        endpoint = '/user-requests';
                        break;
                    case 'checkouts':
                        endpoint = '/checkouts';
                        break;
                    default:
                        endpoint = '/user/activity';
                }

                const response = await api.get(endpoint, { params });
                const data = response.data;

                // Process data for activities list
                setActivities(Array.isArray(data) ? data : data.activities || []);

                // Generate chart data based on response
                generateChartData(data, timeRange);
            } catch (error) {
                console.error('Failed to fetch activity data', error);
                setActivities([]);
                setChartData([]);
            } finally {
                setLoadingActivity(false);
            }
        };

        fetchActivityData();
    }, [activityType, timeRange]);

    // Generate chart data from activity data
    const generateChartData = (data, range) => {
        // For now, generate mock data based on time range
        // In a real implementation, this would process the actual data
        const labels = range === 'week'
            ? ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
            : range === 'month'
            ? ['Week 1', 'Week 2', 'Week 3', 'Week 4']
            : range === 'quarter'
            ? ['Month 1', 'Month 2', 'Month 3']
            : ['Q1', 'Q2', 'Q3', 'Q4'];

        const mockData = labels.map((label, i) => ({
            day: label,
            value: Math.floor(Math.random() * 10) + 1
        }));

        setChartData(mockData);
    };

    // Global search handler
    const handleSearch = (e) => {
        e.preventDefault();
        if (!searchQuery.trim()) return;

        // Navigate to appropriate page based on search query
        // This is a simple implementation - could be enhanced with actual search API
        navigate(`/history?search=${encodeURIComponent(searchQuery)}`);
    };

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

    // Activity type options
    const activityTypes = [
        { value: 'user', label: 'User Activity', icon: User },
        { value: 'checkouts', label: 'Tool Checkouts', icon: Wrench },
        { value: 'kit', label: 'Kit Activity', icon: Briefcase },
        { value: 'chemical', label: 'Chemical Activity', icon: Beaker },
        { value: 'orders', label: 'Orders', icon: ShoppingCart },
        { value: 'requests', label: 'Requests', icon: FileText },
    ];

    const timeRanges = [
        { value: 'week', label: 'This Week' },
        { value: 'month', label: 'This Month' },
        { value: 'quarter', label: 'This Quarter' },
        { value: 'year', label: 'This Year' },
    ];

    const currentActivityType = activityTypes.find(t => t.value === activityType);
    const currentTimeRange = timeRanges.find(t => t.value === timeRange);

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
                {/* Global Search Section */}
                <motion.div className="mb-4" variants={itemVariants}>
                    <Form onSubmit={handleSearch}>
                        <InputGroup size="lg" className="global-search-input">
                            <InputGroup.Text className="bg-transparent">
                                <Search size={20} />
                            </InputGroup.Text>
                            <Form.Control
                                type="text"
                                placeholder="Search tools, kits, chemicals, orders, or history..."
                                value={searchQuery}
                                onChange={(e) => setSearchQuery(e.target.value)}
                                className="border-start-0"
                            />
                        </InputGroup>
                    </Form>
                </motion.div>

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
                            <div className="d-flex justify-content-between align-items-center mb-4 flex-wrap gap-3">
                                <h5 className="mb-0 fw-bold">Activity Overview</h5>
                                <div className="d-flex gap-2">
                                    {/* Activity Type Selector */}
                                    <Dropdown as={ButtonGroup}>
                                        <Dropdown.Toggle
                                            variant="outline-primary"
                                            size="sm"
                                            className="d-flex align-items-center gap-2"
                                        >
                                            {currentActivityType && (
                                                <>
                                                    <currentActivityType.icon size={16} />
                                                    <span>{currentActivityType.label}</span>
                                                </>
                                            )}
                                        </Dropdown.Toggle>
                                        <Dropdown.Menu>
                                            {activityTypes.map((type) => {
                                                const IconComponent = type.icon;
                                                return (
                                                    <Dropdown.Item
                                                        key={type.value}
                                                        active={activityType === type.value}
                                                        onClick={() => setActivityType(type.value)}
                                                    >
                                                        <div className="d-flex align-items-center gap-2">
                                                            <IconComponent size={16} />
                                                            <span>{type.label}</span>
                                                        </div>
                                                    </Dropdown.Item>
                                                );
                                            })}
                                        </Dropdown.Menu>
                                    </Dropdown>

                                    {/* Time Range Selector */}
                                    <Dropdown as={ButtonGroup}>
                                        <Dropdown.Toggle
                                            variant="outline-secondary"
                                            size="sm"
                                        >
                                            {currentTimeRange?.label || 'This Week'}
                                        </Dropdown.Toggle>
                                        <Dropdown.Menu>
                                            {timeRanges.map((range) => (
                                                <Dropdown.Item
                                                    key={range.value}
                                                    active={timeRange === range.value}
                                                    onClick={() => setTimeRange(range.value)}
                                                >
                                                    {range.label}
                                                </Dropdown.Item>
                                            ))}
                                        </Dropdown.Menu>
                                    </Dropdown>
                                </div>
                            </div>
                            {chartData.length > 0 ? (
                                <ActivityChart data={chartData} />
                            ) : (
                                <div className="text-center py-5 text-muted">
                                    <Activity size={48} className="mb-3 opacity-50" />
                                    <p>No activity data available</p>
                                </div>
                            )}
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
