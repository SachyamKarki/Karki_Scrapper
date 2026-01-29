import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { 
    Users, 
    Shield, 
    Trash2, 
    Search,
    Edit2,
    CheckCircle,
    XCircle,
    LayoutDashboard,
    ShieldCheck,
    Database
} from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

const AdminPanel = () => {
    const { user } = useAuth();
    const [stats, setStats] = useState(null);
    const [users, setUsers] = useState([]);
    const [moderationItems, setModerationItems] = useState([]);
    const [loading, setLoading] = useState(true);

    const fetchData = async () => {
        try {
            const response = await axios.get('/admin/', {
                headers: { 'Accept': 'application/json' }
            });
            setStats(response.data.stats);
            setUsers(response.data.users);
            setModerationItems(response.data.moderation_items);
        } catch (error) {
            console.error('Error fetching admin data:', error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchData();
    }, []);

    const deleteUser = async (userId) => {
        if (!window.confirm('Are you sure you want to delete this user?')) return;
        try {
            await axios.post(`/admin/delete_user/${userId}`);
            fetchData();
        } catch (error) {
            alert('Failed to delete user');
        }
    };

    const updateUserRole = async (userId, newRole) => {
        try {
            await axios.post(`/admin/update_role/${userId}`, { role: newRole });
            fetchData();
        } catch (error) {
            alert('Failed to update role');
        }
    };

    const updateItemStatus = async (itemId, status) => {
        try {
            await axios.post('/api/update_status', { item_id: itemId, status: status });
            fetchData();
        } catch (error) {
            alert('Error updating status');
        }
    };

    if (loading) return (
        <div style={{ display: 'flex', minHeight: 'calc(100vh - 80px)', alignItems: 'center', justifyContent: 'center' }}>
            <div style={{ display: 'flex', minHeight: 'calc(100vh - 80px)', alignItems: 'center', justifyContent: 'center' }}>
                <svg className="animate-spin" xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M12 2v4"></path>
                    <path d="m16.2 7.8 2.9-2.9"></path>
                    <path d="M18 12h4"></path>
                    <path d="m16.2 16.2 2.9 2.9"></path>
                    <path d="M12 18v4"></path>
                    <path d="m7.8 16.2-2.9 2.9"></path>
                    <path d="M6 12H2"></path>
                    <path d="m7.8 7.8-2.9-2.9"></path>
                </svg>
            </div>
        </div>
    );

    return (
        <>
            <div style={{ paddingBottom: '40px' }}>
                <header style={{ marginBottom: '40px' }}>
                    <h1 style={{ fontSize: '1.875rem', fontWeight: 700, color: '#1e293b' }}>
                        {user?.is_superadmin ? 'Admin Portal' : 'Data Moderation'}
                    </h1>
                    <p style={{ color: '#64748b', marginTop: '4px' }}>
                        {user?.is_superadmin ? 'Manage users and platform activity' : 'Review and approve scraped data points'}
                    </p>
                </header>

                {/* Stats Grid - Visible to Superadmin */}
                {user?.is_superadmin && stats && (
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '24px', marginBottom: '40px' }}>
                        <div style={{ background: 'white', padding: '24px', borderRadius: '12px', border: '1px solid #e2e8f0', boxShadow: '0 1px 3px 0 rgba(0,0,0,0.1)', display: 'flex', alignItems: 'center', gap: '16px' }}>
                            <div style={{ padding: '12px', background: '#eff6ff', borderRadius: '10px', color: '#2563eb' }}><Users size={24} /></div>
                            <div>
                                <div style={{ fontSize: '0.875rem', color: '#64748b', fontWeight: 500 }}>Total Users</div>
                                <div style={{ fontSize: '1.5rem', fontWeight: 700, color: '#1e293b' }}>{stats.total_users}</div>
                            </div>
                        </div>
                        <div style={{ background: 'white', padding: '24px', borderRadius: '12px', border: '1px solid #e2e8f0', boxShadow: '0 1px 3px 0 rgba(0,0,0,0.1)', display: 'flex', alignItems: 'center', gap: '16px' }}>
                            <div style={{ padding: '12px', background: '#f0fdf4', borderRadius: '10px', color: '#16a34a' }}><LayoutDashboard size={24} /></div>
                            <div>
                                <div style={{ fontSize: '0.875rem', color: '#64748b', fontWeight: 500 }}>Total Scrapes</div>
                                <div style={{ fontSize: '1.5rem', fontWeight: 700, color: '#1e293b' }}>{stats.total_places}</div>
                            </div>
                        </div>
                        <div style={{ background: 'white', padding: '24px', borderRadius: '12px', border: '1px solid #e2e8f0', boxShadow: '0 1px 3px 0 rgba(0,0,0,0.1)', display: 'flex', alignItems: 'center', gap: '16px' }}>
                            <div style={{ padding: '12px', background: '#fefce8', borderRadius: '10px', color: '#ca8a04' }}><CheckCircle size={24} /></div>
                            <div>
                                <div style={{ fontSize: '0.875rem', color: '#64748b', fontWeight: 500 }}>Approved Leads</div>
                                <div style={{ fontSize: '1.5rem', fontWeight: 700, color: '#1e293b' }}>{stats.approved_places}</div>
                            </div>
                        </div>
                    </div>
                )}

                {/* Main Content Area */}
                <div style={{ background: 'white', borderRadius: '12px', border: '1px solid #e2e8f0', overflow: 'hidden', boxShadow: '0 1px 2px 0 rgba(0,0,0,0.05)' }}>
                    <div style={{ padding: '20px 24px', borderBottom: '1px solid #e2e8f0', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <h2 style={{ fontSize: '1.1rem', fontWeight: 600, color: '#1e293b', margin: 0 }}>
                            {user?.is_superadmin ? 'System Users' : 'Pending Review Queue'}
                        </h2>
                    </div>
                    
                    <div style={{ overflowX: 'auto' }}>
                        <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
                            <thead style={{ background: '#f8fafc' }}>
                                <tr>
                                    {user.is_superadmin ? (
                                        <>
                                            <th style={tableHeaderStyle}>User</th>
                                            <th style={tableHeaderStyle}>Role</th>
                                            <th style={tableHeaderStyle}>Actions</th>
                                        </>
                                    ) : (
                                        <>
                                            <th style={tableHeaderStyle}>Business Name</th>
                                            <th style={tableHeaderStyle}>Status</th>
                                            <th style={tableHeaderStyle}>Actions</th>
                                        </>
                                    )}
                                </tr>
                            </thead>
                            <tbody>
                                {user.is_superadmin ? (
                                    (users || []).map(u => (
                                        <tr key={u._id} style={{ borderBottom: '1px solid #f1f5f9' }}>
                                            <td style={{ padding: '16px 24px', color: '#334155' }}>
                                                <div style={{ fontWeight: 500, wordBreak: 'break-all' }}>{u.email}</div>
                                                <div style={{ fontSize: '0.75rem', color: '#94a3b8' }}>ID: {u._id}</div>
                                            </td>
                                            <td style={{ padding: '16px 24px' }}>
                                                <select 
                                                    value={u.role}
                                                    onChange={(e) => updateUserRole(u._id, e.target.value)}
                                                    style={{ 
                                                        padding: '6px 12px', 
                                                        borderRadius: '6px', 
                                                        border: '1px solid #e2e8f0', 
                                                        fontSize: '0.875rem',
                                                        background: u.role === 'superadmin' ? '#f3e8ff' : '#fff',
                                                        color: u.role === 'superadmin' ? '#9333ea' : '#1e293b'
                                                    }}
                                                    disabled={u.email === user?.email}
                                                >
                                                    <option value="user">User</option>
                                                    <option value="admin">Admin</option>
                                                    <option value="superadmin">Superadmin</option>
                                                </select>
                                            </td>
                                            <td style={{ padding: '16px 24px' }}>
                                                <button 
                                                    onClick={() => deleteUser(u._id)}
                                                    disabled={u.email === user?.email}
                                                    style={{ 
                                                        padding: '8px', 
                                                        color: '#ef4444', 
                                                        border: 'none', 
                                                        background: '#fee2e2', 
                                                        borderRadius: '6px', 
                                                        cursor: 'pointer',
                                                        opacity: u.email === user?.email ? 0.5 : 1
                                                    }}
                                                >
                                                    <Trash2 size={16} />
                                                </button>
                                            </td>
                                        </tr>
                                    ))
                                ) : (
                                    (moderationItems || []).length > 0 ? (moderationItems || []).map(item => (
                                        <tr key={item._id} style={{ borderBottom: '1px solid #f1f5f9' }}>
                                            <td style={{ padding: '16px 24px', color: '#334155' }}>
                                                <div style={{ fontWeight: 600 }}>{item.name}</div>
                                                <div style={{ fontSize: '0.85rem', color: '#64748b' }}>{item.address}</div>
                                            </td>
                                            <td style={{ padding: '16px 24px' }}>
                                                <span style={{ 
                                                    fontSize: '0.75rem', fontWeight: 600, padding: '4px 10px', borderRadius: '6px',
                                                    background: item.status === 'pending' ? '#fef3c7' : '#f1f5f9',
                                                    color: item.status === 'pending' ? '#b45309' : '#64748b'
                                                }}>
                                                    {(item.status || 'unknown').toUpperCase()}
                                                </span>
                                            </td>
                                            <td style={{ padding: '16px 24px' }}>
                                                <div style={{ display: 'flex', gap: '8px' }}>
                                                    <button onClick={() => updateItemStatus(item._id, 'approved')} style={{ padding: '6px 12px', borderRadius: '6px', background: '#dcfce7', color: '#166534', border: 'none', cursor: 'pointer', fontWeight: 500, display: 'flex', alignItems: 'center', gap: '4px', fontSize: '0.85rem' }}>
                                                        <CheckCircle size={14} /> Approve
                                                    </button>
                                                    <button onClick={() => updateItemStatus(item._id, 'rejected')} style={{ padding: '6px 12px', borderRadius: '6px', background: '#fee2e2', color: '#991b1b', border: 'none', cursor: 'pointer', fontWeight: 500, display: 'flex', alignItems: 'center', gap: '4px', fontSize: '0.85rem' }}>
                                                        <XCircle size={14} /> Reject
                                                    </button>
                                                </div>
                                            </td>
                                        </tr>
                                    ))
 : (
                                        <tr>
                                            <td colSpan="3" style={{ padding: '32px', textAlign: 'center', color: '#94a3b8', fontStyle: 'italic' }}>
                                                No items pending review.
                                            </td>
                                        </tr>
                                    )
                                )}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </>
    );
};

const tableHeaderStyle = {
    padding: '12px 24px', 
    fontSize: '0.75rem', 
    color: '#64748b', 
    textTransform: 'uppercase', 
    letterSpacing: '0.05em', 
    fontWeight: 600 
};

export default AdminPanel;
