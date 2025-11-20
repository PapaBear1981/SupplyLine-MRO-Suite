import { Link, useLocation } from 'react-router-dom';
import { useSelector } from 'react-redux';
import {
    LayoutDashboard,
    Wrench,
    ShoppingCart,
    ClipboardList,
    LogOut,
    Briefcase,
    Droplet,
    Sliders,
    Building2,
    FileText,
    History,
    Users,
    Settings,
    ChevronLeft,
    ChevronRight
} from 'lucide-react';
import { cn } from '../../utils/cn';
import { Button } from '../ui/button';
import { Avatar, AvatarFallback, AvatarImage } from '../ui/avatar';
import { hasPermission } from '../auth/ProtectedRoute';

const Sidebar = ({ collapsed, onToggle }) => {
    const location = useLocation();
    const { user } = useSelector((state) => state.auth);

    const isActive = (path) => location.pathname === path;

    const NavItem = ({ to, icon: Icon, label, permission }) => {
        if (permission && !hasPermission(user, permission)) return null;

        return (
            <Link
                to={to}
                className={cn(
                    "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-all hover:text-primary",
                    isActive(to)
                        ? "bg-muted text-primary"
                        : "text-muted-foreground hover:bg-muted/50",
                    collapsed && "justify-center px-2"
                )}
                title={collapsed ? label : undefined}
            >
                <Icon className="h-4 w-4" />
                {!collapsed && <span>{label}</span>}
            </Link>
        );
    };

    return (
        <div
            className={cn(
                "relative flex flex-col border-r bg-card transition-all duration-300",
                collapsed ? "w-[60px]" : "w-[240px]"
            )}
        >
            {/* Sidebar Header */}
            <div className="flex h-14 items-center border-b px-4 lg:h-[60px]">
                <Link to="/" className={cn("flex items-center gap-2 font-semibold", collapsed && "justify-center w-full")}>
                    <Wrench className="h-6 w-6" />
                    {!collapsed && <span className="">SupplyLine</span>}
                </Link>

                {!collapsed && (
                    <Button
                        variant="ghost"
                        size="icon"
                        className="ml-auto h-8 w-8"
                        onClick={onToggle}
                    >
                        <ChevronLeft className="h-4 w-4" />
                    </Button>
                )}
            </div>

            {/* Toggle Button for Collapsed State */}
            {collapsed && (
                <div className="flex justify-center py-2">
                    <Button
                        variant="ghost"
                        size="icon"
                        className="h-8 w-8"
                        onClick={onToggle}
                    >
                        <ChevronRight className="h-4 w-4" />
                    </Button>
                </div>
            )}

            {/* Navigation */}
            <div className="flex-1 overflow-auto py-2">
                <nav className="grid items-start px-2 text-sm font-medium lg:px-4 gap-1">
                    <NavItem to="/dashboard" icon={LayoutDashboard} label="Dashboard" />

                    <div className="my-2 border-t" />

                    <NavItem to="/tools" icon={Wrench} label="Tools" permission="page.tools" />
                    <NavItem to="/orders" icon={ShoppingCart} label="Orders" permission="page.orders" />
                    <NavItem to="/requests" icon={ClipboardList} label="Requests" permission="page.requests" />
                    <NavItem to="/checkouts" icon={LogOut} label="Checkouts" permission="page.checkouts" />
                    <NavItem to="/kits" icon={Briefcase} label="Kits" permission="page.kits" />
                    <NavItem to="/chemicals" icon={Droplet} label="Chemicals" permission="page.chemicals" />
                    <NavItem to="/calibrations" icon={Sliders} label="Calibrations" permission="page.calibrations" />
                    <NavItem to="/warehouses" icon={Building2} label="Warehouses" permission="page.warehouses" />

                    <div className="my-2 border-t" />

                    <NavItem to="/reports" icon={FileText} label="Reports" permission="page.reports" />
                    <NavItem to="/history" icon={History} label="History" />
                    <NavItem to="/directory" icon={Users} label="Directory" permission="user.view" />

                    {hasPermission(user, 'page.admin_dashboard') && (
                        <>
                            <div className="my-2 border-t" />
                            <NavItem to="/admin/dashboard" icon={Settings} label="Admin" permission="page.admin_dashboard" />
                        </>
                    )}
                </nav>
            </div>

            {/* User Profile Section */}
            <div className="mt-auto border-t p-4">
                <div className={cn("flex items-center gap-3", collapsed && "justify-center")}>
                    <Avatar>
                        <AvatarImage src={user?.avatar} alt={user?.name} />
                        <AvatarFallback>{user?.name?.charAt(0) || 'U'}</AvatarFallback>
                    </Avatar>
                    {!collapsed && (
                        <div className="flex flex-col overflow-hidden">
                            <span className="truncate text-sm font-medium">{user?.name || 'User'}</span>
                            <span className="truncate text-xs text-muted-foreground">{user?.email || 'user@example.com'}</span>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default Sidebar;
