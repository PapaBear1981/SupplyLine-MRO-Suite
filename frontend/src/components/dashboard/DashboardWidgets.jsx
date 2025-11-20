import React from 'react';
import { Card, Row, Col, Button } from 'react-bootstrap';
import {
    LineChart,
    Line,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
    AreaChart,
    Area,
    PieChart,
    Pie,
    Cell,
    Legend
} from 'recharts';
import { useNavigate } from 'react-router-dom';
import {
    FaTools,
    FaFlask,
    FaBoxOpen,
    FaClipboardList,
    FaUsers,
    FaExclamationTriangle,
    FaArrowRight
} from 'react-icons/fa';

// --- Stat Card Component ---
export const StatCard = ({ title, value, trend, trendLabel, icon, color, onClick }) => {
    const isPositive = trend > 0;
    const trendColor = isPositive ? 'text-success' : 'text-danger';
    const trendIcon = isPositive ? '▲' : '▼';

    return (
        <Card
            className="h-100 border-0 shadow-sm stat-card"
            style={{
                cursor: onClick ? 'pointer' : 'default',
                background: `linear-gradient(135deg, var(--enterprise-surface) 0%, var(--enterprise-surface-hover) 100%)`,
                borderLeft: `4px solid ${color}`
            }}
            onClick={onClick}
        >
            <Card.Body className="d-flex flex-column justify-content-between">
                <div className="d-flex justify-content-between align-items-start mb-3">
                    <div>
                        <h6 className="text-muted text-uppercase mb-1" style={{ fontSize: '0.75rem', letterSpacing: '0.5px' }}>{title}</h6>
                        <h3 className="fw-bold mb-0" style={{ color: 'var(--enterprise-text)' }}>{value}</h3>
                    </div>
                    <div
                        className="d-flex align-items-center justify-content-center rounded-circle"
                        style={{
                            width: '48px',
                            height: '48px',
                            backgroundColor: `${color}20`,
                            color: color,
                            fontSize: '1.5rem'
                        }}
                    >
                        {icon}
                    </div>
                </div>
                {trend !== undefined && (
                    <div className="d-flex align-items-center">
                        <span className={`fw-bold me-2 ${trendColor}`} style={{ fontSize: '0.85rem' }}>
                            {trendIcon} {Math.abs(trend)}%
                        </span>
                        <span className="text-muted" style={{ fontSize: '0.8rem' }}>{trendLabel}</span>
                    </div>
                )}
            </Card.Body>
        </Card>
    );
};

// --- Analytics Chart Component ---
export const AnalyticsChart = ({ title, data, dataKey, color, height = 300, type = 'area' }) => {
    return (
        <Card className="h-100 border-0 shadow-sm">
            <Card.Header className="bg-transparent border-0 pt-4 px-4">
                <h5 className="fw-bold mb-0" style={{ color: 'var(--enterprise-text)' }}>{title}</h5>
            </Card.Header>
            <Card.Body>
                <div style={{ width: '100%', height: height }}>
                    <ResponsiveContainer>
                        {type === 'area' ? (
                            <AreaChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                                <defs>
                                    <linearGradient id={`color${dataKey}`} x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="5%" stopColor={color} stopOpacity={0.3} />
                                        <stop offset="95%" stopColor={color} stopOpacity={0} />
                                    </linearGradient>
                                </defs>
                                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="var(--enterprise-border)" />
                                <XAxis
                                    dataKey="name"
                                    axisLine={false}
                                    tickLine={false}
                                    tick={{ fill: 'var(--enterprise-text-secondary)', fontSize: 12 }}
                                    dy={10}
                                />
                                <YAxis
                                    axisLine={false}
                                    tickLine={false}
                                    tick={{ fill: 'var(--enterprise-text-secondary)', fontSize: 12 }}
                                />
                                <Tooltip
                                    contentStyle={{
                                        backgroundColor: 'var(--enterprise-surface)',
                                        borderColor: 'var(--enterprise-border)',
                                        color: 'var(--enterprise-text)',
                                        borderRadius: '8px',
                                        boxShadow: '0 4px 12px rgba(0,0,0,0.1)'
                                    }}
                                />
                                <Area
                                    type="monotone"
                                    dataKey={dataKey}
                                    stroke={color}
                                    fillOpacity={1}
                                    fill={`url(#color${dataKey})`}
                                    strokeWidth={3}
                                />
                            </AreaChart>
                        ) : (
                            <LineChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="var(--enterprise-border)" />
                                <XAxis
                                    dataKey="name"
                                    axisLine={false}
                                    tickLine={false}
                                    tick={{ fill: 'var(--enterprise-text-secondary)', fontSize: 12 }}
                                    dy={10}
                                />
                                <YAxis
                                    axisLine={false}
                                    tickLine={false}
                                    tick={{ fill: 'var(--enterprise-text-secondary)', fontSize: 12 }}
                                />
                                <Tooltip
                                    contentStyle={{
                                        backgroundColor: 'var(--enterprise-surface)',
                                        borderColor: 'var(--enterprise-border)',
                                        color: 'var(--enterprise-text)',
                                        borderRadius: '8px',
                                        boxShadow: '0 4px 12px rgba(0,0,0,0.1)'
                                    }}
                                />
                                <Line
                                    type="monotone"
                                    dataKey={dataKey}
                                    stroke={color}
                                    strokeWidth={3}
                                    dot={{ r: 4, fill: color, strokeWidth: 2, stroke: 'var(--enterprise-surface)' }}
                                    activeDot={{ r: 6 }}
                                />
                            </LineChart>
                        )}
                    </ResponsiveContainer>
                </div>
            </Card.Body>
        </Card>
    );
};

// --- Distribution Chart Component ---
export const DistributionChart = ({ title, data, colors, height = 300 }) => {
    return (
        <Card className="h-100 border-0 shadow-sm">
            <Card.Header className="bg-transparent border-0 pt-4 px-4">
                <h5 className="fw-bold mb-0" style={{ color: 'var(--enterprise-text)' }}>{title}</h5>
            </Card.Header>
            <Card.Body>
                <div style={{ width: '100%', height: height }}>
                    <ResponsiveContainer>
                        <PieChart>
                            <Pie
                                data={data}
                                cx="50%"
                                cy="50%"
                                innerRadius={60}
                                outerRadius={80}
                                paddingAngle={5}
                                dataKey="value"
                            >
                                {data.map((entry, index) => (
                                    <Cell key={`cell-${index}`} fill={colors[index % colors.length]} />
                                ))}
                            </Pie>
                            <Tooltip
                                contentStyle={{
                                    backgroundColor: 'var(--enterprise-surface)',
                                    borderColor: 'var(--enterprise-border)',
                                    color: 'var(--enterprise-text)',
                                    borderRadius: '8px'
                                }}
                            />
                            <Legend
                                verticalAlign="bottom"
                                height={36}
                                iconType="circle"
                                formatter={(value) => <span style={{ color: 'var(--enterprise-text-secondary)' }}>{value}</span>}
                            />
                        </PieChart>
                    </ResponsiveContainer>
                </div>
            </Card.Body>
        </Card>
    );
};

// --- Quick Links Grid ---
export const QuickLinksGrid = () => {
    const navigate = useNavigate();

    const links = [
        { label: 'Issue Tool', icon: <FaTools />, path: '/tools', color: '#3b82f6' },
        { label: 'Return Tool', icon: <FaArrowRight />, path: '/checkouts', color: '#10b981' },
        { label: 'Chemicals', icon: <FaFlask />, path: '/chemicals', color: '#8b5cf6' },
        { label: 'Kits', icon: <FaBoxOpen />, path: '/kits', color: '#f59e0b' },
        { label: 'My Requests', icon: <FaClipboardList />, path: '/requests', color: '#ec4899' },
        { label: 'Directory', icon: <FaUsers />, path: '/directory', color: '#6366f1' },
    ];

    return (
        <Card className="h-100 border-0 shadow-sm">
            <Card.Header className="bg-transparent border-0 pt-4 px-4">
                <h5 className="fw-bold mb-0" style={{ color: 'var(--enterprise-text)' }}>Quick Actions</h5>
            </Card.Header>
            <Card.Body>
                <Row className="g-3">
                    {links.map((link, idx) => (
                        <Col xs={6} md={4} key={idx}>
                            <div
                                className="p-3 rounded text-center h-100 d-flex flex-column align-items-center justify-content-center quick-link-card"
                                style={{
                                    backgroundColor: 'var(--enterprise-bg)',
                                    border: '1px solid var(--enterprise-border)',
                                    cursor: 'pointer',
                                    transition: 'all 0.2s ease'
                                }}
                                onClick={() => navigate(link.path)}
                                onMouseEnter={(e) => {
                                    e.currentTarget.style.transform = 'translateY(-3px)';
                                    e.currentTarget.style.borderColor = link.color;
                                    e.currentTarget.style.boxShadow = `0 4px 12px ${link.color}20`;
                                }}
                                onMouseLeave={(e) => {
                                    e.currentTarget.style.transform = 'none';
                                    e.currentTarget.style.borderColor = 'var(--enterprise-border)';
                                    e.currentTarget.style.boxShadow = 'none';
                                }}
                            >
                                <div
                                    className="mb-2 d-flex align-items-center justify-content-center rounded-circle"
                                    style={{
                                        width: '40px',
                                        height: '40px',
                                        backgroundColor: `${link.color}20`,
                                        color: link.color,
                                        fontSize: '1.2rem'
                                    }}
                                >
                                    {link.icon}
                                </div>
                                <span className="fw-medium" style={{ fontSize: '0.9rem', color: 'var(--enterprise-text)' }}>{link.label}</span>
                            </div>
                        </Col>
                    ))}
                </Row>
            </Card.Body>
        </Card>
    );
};
