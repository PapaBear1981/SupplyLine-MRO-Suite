import React from 'react';
import { useNavigate } from 'react-router-dom';
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
import {
    FaTools,
    FaFlask,
    FaBoxOpen,
    FaClipboardList,
    FaUsers,
    FaArrowRight
} from 'react-icons/fa';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { cn } from '../../utils/cn';

// --- Stat Card Component ---
export const StatCard = ({ title, value, trend, trendLabel, icon, color, onClick }) => {
    const isPositive = trend > 0;
    const trendColor = isPositive ? 'text-green-500' : 'text-red-500';
    const trendIcon = isPositive ? '▲' : '▼';

    return (
        <Card
            className={cn(
                "h-full transition-all hover:shadow-md",
                onClick && "cursor-pointer hover:scale-[1.02]"
            )}
            onClick={onClick}
            style={{ borderLeft: `4px solid ${color}` }}
        >
            <CardContent className="flex flex-col justify-between p-6 h-full">
                <div className="flex justify-between items-start mb-4">
                    <div>
                        <h6 className="text-muted-foreground text-xs font-medium uppercase tracking-wider mb-1">{title}</h6>
                        <h3 className="text-2xl font-bold text-foreground">{value}</h3>
                    </div>
                    <div
                        className="flex items-center justify-center rounded-full w-12 h-12 text-xl"
                        style={{
                            backgroundColor: `${color}20`,
                            color: color,
                        }}
                    >
                        {icon}
                    </div>
                </div>
                {trend !== undefined && (
                    <div className="flex items-center text-sm">
                        <span className={cn("font-bold mr-2", trendColor)}>
                            {trendIcon} {Math.abs(trend)}%
                        </span>
                        <span className="text-muted-foreground text-xs">{trendLabel}</span>
                    </div>
                )}
            </CardContent>
        </Card>
    );
};

// --- Analytics Chart Component ---
export const AnalyticsChart = ({ title, data, dataKey, color, height = 300, type = 'area' }) => {
    return (
        <Card className="h-full shadow-sm">
            <CardHeader className="pb-2">
                <CardTitle className="text-lg font-bold text-foreground">{title}</CardTitle>
            </CardHeader>
            <CardContent>
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
                                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="hsl(var(--border))" />
                                <XAxis
                                    dataKey="name"
                                    axisLine={false}
                                    tickLine={false}
                                    tick={{ fill: 'hsl(var(--muted-foreground))', fontSize: 12 }}
                                    dy={10}
                                />
                                <YAxis
                                    axisLine={false}
                                    tickLine={false}
                                    tick={{ fill: 'hsl(var(--muted-foreground))', fontSize: 12 }}
                                />
                                <Tooltip
                                    contentStyle={{
                                        backgroundColor: 'hsl(var(--popover))',
                                        borderColor: 'hsl(var(--border))',
                                        color: 'hsl(var(--popover-foreground))',
                                        borderRadius: 'var(--radius)',
                                        boxShadow: '0 4px 12px rgba(0,0,0,0.1)'
                                    }}
                                    itemStyle={{ color: 'hsl(var(--popover-foreground))' }}
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
                                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="hsl(var(--border))" />
                                <XAxis
                                    dataKey="name"
                                    axisLine={false}
                                    tickLine={false}
                                    tick={{ fill: 'hsl(var(--muted-foreground))', fontSize: 12 }}
                                    dy={10}
                                />
                                <YAxis
                                    axisLine={false}
                                    tickLine={false}
                                    tick={{ fill: 'hsl(var(--muted-foreground))', fontSize: 12 }}
                                />
                                <Tooltip
                                    contentStyle={{
                                        backgroundColor: 'hsl(var(--popover))',
                                        borderColor: 'hsl(var(--border))',
                                        color: 'hsl(var(--popover-foreground))',
                                        borderRadius: 'var(--radius)',
                                        boxShadow: '0 4px 12px rgba(0,0,0,0.1)'
                                    }}
                                    itemStyle={{ color: 'hsl(var(--popover-foreground))' }}
                                />
                                <Line
                                    type="monotone"
                                    dataKey={dataKey}
                                    stroke={color}
                                    strokeWidth={3}
                                    dot={{ r: 4, fill: color, strokeWidth: 2, stroke: 'hsl(var(--background))' }}
                                    activeDot={{ r: 6 }}
                                />
                            </LineChart>
                        )}
                    </ResponsiveContainer>
                </div>
            </CardContent>
        </Card>
    );
};

// --- Distribution Chart Component ---
export const DistributionChart = ({ title, data, colors, height = 300 }) => {
    return (
        <Card className="h-full shadow-sm">
            <CardHeader className="pb-2">
                <CardTitle className="text-lg font-bold text-foreground">{title}</CardTitle>
            </CardHeader>
            <CardContent>
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
                                    backgroundColor: 'hsl(var(--popover))',
                                    borderColor: 'hsl(var(--border))',
                                    color: 'hsl(var(--popover-foreground))',
                                    borderRadius: 'var(--radius)'
                                }}
                                itemStyle={{ color: 'hsl(var(--popover-foreground))' }}
                            />
                            <Legend
                                verticalAlign="bottom"
                                height={36}
                                iconType="circle"
                                formatter={(value) => <span className="text-muted-foreground text-sm">{value}</span>}
                            />
                        </PieChart>
                    </ResponsiveContainer>
                </div>
            </CardContent>
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
        <Card className="h-full shadow-sm">
            <CardHeader className="pb-2">
                <CardTitle className="text-lg font-bold text-foreground">Quick Actions</CardTitle>
            </CardHeader>
            <CardContent>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                    {links.map((link, idx) => (
                        <div
                            key={idx}
                            className="p-4 rounded-lg text-center h-full flex flex-col items-center justify-center bg-card border border-border cursor-pointer transition-all duration-200 hover:-translate-y-1 hover:shadow-md group"
                            onClick={() => navigate(link.path)}
                            style={{
                                '--hover-color': link.color
                            }}
                        >
                            <div
                                className="mb-3 flex items-center justify-center rounded-full w-10 h-10 text-xl transition-colors group-hover:bg-opacity-20"
                                style={{
                                    backgroundColor: `${link.color}20`,
                                    color: link.color,
                                }}
                            >
                                {link.icon}
                            </div>
                            <span className="font-medium text-sm text-foreground">{link.label}</span>
                        </div>
                    ))}
                </div>
            </CardContent>
        </Card>
    );
};
