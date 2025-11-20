import { useState } from 'react';
import Sidebar from './Sidebar';
import Header from './Header';

const MainLayoutNew = ({ children }) => {
    const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

    const toggleSidebar = () => {
        setSidebarCollapsed(!sidebarCollapsed);
    };

    return (
        <div className="grid min-h-screen w-full md:grid-cols-[auto_1fr]">
            <Sidebar collapsed={sidebarCollapsed} onToggle={toggleSidebar} />
            <div className="flex flex-col">
                <Header onMenuClick={toggleSidebar} />
                <main className="flex flex-1 flex-col gap-4 p-4 lg:gap-6 lg:p-6 bg-muted/40">
                    {children}
                </main>
            </div>
        </div>
    );
};

export default MainLayoutNew;
