import React, { useState, useEffect } from 'react';
import Sidebar from './Sidebar';

const SIDEBAR_COLLAPSED_KEY = 'sidebar_collapsed';

const Layout = ({ children }) => {
    const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(() => {
        try {
            const saved = localStorage.getItem(SIDEBAR_COLLAPSED_KEY);
            return saved === 'true';
        } catch {
            return false;
        }
    });

    useEffect(() => {
        try {
            localStorage.setItem(SIDEBAR_COLLAPSED_KEY, String(isSidebarCollapsed));
        } catch (_) {}
    }, [isSidebarCollapsed]);

    const toggleSidebar = () => {
        setIsSidebarCollapsed(!isSidebarCollapsed);
    };

    return (
        <div style={{ display: 'flex', minHeight: '100vh', backgroundColor: '#f3f4f6' }}>
            <Sidebar 
                isCollapsed={isSidebarCollapsed} 
                toggleSidebar={toggleSidebar} 
            />
            <main style={{ 
                marginLeft: isSidebarCollapsed ? '80px' : '260px', 
                flex: 1, 
                padding: '32px 40px', 
                maxWidth: `calc(100vw - ${isSidebarCollapsed ? '80px' : '260px'})`,
                transition: 'all 0.3s ease'
            }}>
                {children}
            </main>
        </div>
    );
};

export default Layout;
