import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import {
    LayoutDashboard,
    Shield,
    LogOut,
    ChevronLeft,
    ChevronRight,
    User,
    MessageSquare,
    Mail,
    Send,
    Settings
} from 'lucide-react';

const Sidebar = ({ isCollapsed, toggleSidebar }) => {
    const { user, logout } = useAuth();
    const navigate = useNavigate();

    const handleLogout = async () => {
        const success = await logout();
        if (success) navigate('/login');
    };

    const navItems = [
        { label: 'Dashboard', icon: LayoutDashboard, path: '/', show: true },
        { label: 'Email Management', icon: Send, path: '/email', show: true },
        { label: 'Messages', icon: Mail, path: '/messages', show: true },
        { label: 'Team Chat', icon: MessageSquare, path: '/chat', show: user?.is_admin },
        { label: 'Admin Panel', icon: Shield, path: '/admin', show: user?.is_superadmin }, // Icon changed to Shield
        { label: 'Users', icon: User, path: '/admin/users', show: user?.is_superadmin }, // Icon changed to User
        { label: 'Settings', icon: Settings, path: '/settings', show: true },
    ];

    return (
        <aside style={{
            width: isCollapsed ? '80px' : '260px',
            backgroundColor: '#ffffff',
            borderRight: '1px solid #e2e8f0',
            height: '100vh',
            position: 'fixed',
            left: 0,
            top: 0,
            display: 'flex',
            flexDirection: 'column',
            transition: 'width 0.3s ease',
            zIndex: 50
        }}>
            {/* Logo Section */}
            <div style={{ 
                padding: isCollapsed ? '24px 0' : '24px 32px', 
                borderBottom: '1px solid #f1f5f9',
                display: 'flex',
                justifyContent: isCollapsed ? 'center' : 'space-between',
                alignItems: 'center'
            }}>
                {!isCollapsed && (
                    <h1 style={{ 
                        fontFamily: 'Lobster, cursive', 
                        fontSize: '1.75rem', 
                        color: '#2563eb', 
                        margin: 0,
                        whiteSpace: 'nowrap'
                    }}>
                        Karki's
                    </h1>
                )}
                <button 
                    onClick={toggleSidebar}
                    style={{
                        background: '#f1f5f9',
                        border: 'none',
                        borderRadius: '6px',
                        padding: '4px',
                        cursor: 'pointer',
                        color: '#64748b',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center'
                    }}
                >
                    {isCollapsed ? <ChevronRight size={20} /> : <ChevronLeft size={20} />}
                </button>
            </div>

            {/* Navigation Links */}
            <nav style={{ flex: 1, padding: isCollapsed ? '24px 12px' : '24px 16px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
                {navItems.filter(item => item.show).map((item) => (
                    <NavLink
                        key={item.path}
                        to={item.path}
                        title={isCollapsed ? item.label : ''}
                        style={({ isActive }) => ({
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: isCollapsed ? 'center' : 'flex-start',
                            padding: '12px 16px',
                            color: isActive ? '#2563eb' : '#64748b',
                            backgroundColor: isActive ? '#eff6ff' : 'transparent',
                            textDecoration: 'none',
                            borderRadius: '8px',
                            fontWeight: 500,
                            fontSize: '0.90rem',
                            transition: 'all 0.2s ease',
                            borderLeft: isActive && !isCollapsed ? '3px solid #2563eb' : '3px solid transparent'
                        })}
                    >
                        {({ isActive }) => (
                            <>
                                <item.icon size={20} style={{ marginRight: isCollapsed ? 0 : '12px', opacity: isActive ? 1 : 0.8 }} />
                                {!isCollapsed && item.label}
                            </>
                        )}
                    </NavLink>
                ))}
            </nav>

            {/* User Profile & Logout */}
            <div style={{ padding: '24px', borderTop: '1px solid #f1f5f9' }}>
                <div style={{ 
                    display: 'flex', 
                    alignItems: 'center', 
                    gap: isCollapsed ? 0 : '12px', 
                    justifyContent: isCollapsed ? 'center' : 'flex-start',
                    marginBottom: isCollapsed ? '0' : '16px' 
                }}>
                    <div style={{ 
                        width: '36px', 
                        height: '36px', 
                        borderRadius: '50%', 
                        background: '#bfdbfe', 
                        color: '#1d4ed8',
                        display: 'flex', 
                        alignItems: 'center', 
                        justifyContent: 'center',
                        fontWeight: 600,
                        fontSize: '0.9rem',
                        flexShrink: 0
                    }}>
                        {user?.email?.[0]?.toUpperCase() || '?'}
                    </div>
                    {!isCollapsed && (
                        <div style={{ overflow: 'hidden' }}>
                            <p style={{ margin: 0, fontSize: '0.85rem', fontWeight: 600, color: '#334155', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                                {user.email.split('@')[0]}
                            </p>
                            <span style={{ 
                                fontSize: '0.7rem', 
                                color: user.role === 'superadmin' ? '#9333ea' : '#22c55e',
                                background: user.role === 'superadmin' ? '#f3e8ff' : '#dcfce7',
                                padding: '2px 6px',
                                borderRadius: '4px',
                                fontWeight: 500,
                                textTransform: 'capitalize'
                            }}>
                                {user.role}
                            </span>
                        </div>
                    )}
                </div>
                
                {!isCollapsed && (
                    <button 
                        onClick={handleLogout}
                        style={{
                            width: '100%',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '12px',
                            padding: '10px',
                            border: '1px solid #e2e8f0',
                            borderRadius: '8px',
                            background: 'white',
                            color: '#64748b',
                            fontSize: '0.85rem',
                            fontWeight: 500,
                            cursor: 'pointer',
                            transition: 'all 0.2s'
                        }}
                    >
                        <LogOut size={16} />
                        Logout
                    </button>
                )}
            </div>
        </aside>
    );
};

export default Sidebar;
