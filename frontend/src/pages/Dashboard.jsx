import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Search, Loader2, ChevronLeft, ChevronRight, FileDown, FileText, BarChart2, CheckCircle, XCircle, Clock, Trash2, ChevronDown } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import NotesModal from '../components/NotesModal';
import AnalysisModal from '../components/AnalysisModal';
import EmailManagementModal from '../components/EmailManagementModal';

const Dashboard = () => {
    const { user } = useAuth();
    const [places, setPlaces] = useState([]);
    const [loading, setLoading] = useState(true);
    const [page, setPage] = useState(1);
    const [pagination, setPagination] = useState(null);
    const [query, setQuery] = useState('');
    const [scraping, setScraping] = useState(false);
    
    // Single search state (connected to table)
    const [searchText, setSearchText] = useState('');
    const [statusFilter, setStatusFilter] = useState('all');
    
    // Selection State
    const [selectedItems, setSelectedItems] = useState(new Set());

    // Notes Modal State
    const [isNotesOpen, setIsNotesOpen] = useState(false);
    const [selectedItemId, setSelectedItemId] = useState(null);

    // Analysis Modal State
    const [isAnalysisOpen, setIsAnalysisOpen] = useState(false);
    const [selectedAnalysisItemId, setSelectedAnalysisItemId] = useState(null);

    // Email Management Modal State (opens when clicking an email)
    const [isEmailModalOpen, setIsEmailModalOpen] = useState(false);
    const [selectedPlaceForEmail, setSelectedPlaceForEmail] = useState(null);

    // Analysis State
    const [analyzingIds, setAnalyzingIds] = useState(new Set());

    const fetchPlaces = async (targetPage = 1) => {
        setLoading(true);
        try {
            // Include search filter in the request
            const params = new URLSearchParams({
                page: targetPage,
                search: searchText,
                status: statusFilter
            });
            
            const response = await axios.get(`/api/?${params.toString()}`, {
                headers: { 'Accept': 'application/json' }
            });
            setPlaces(response.data.places);
            setPagination(response.data.pagination);
            setPage(targetPage);
            
            // Clear selection on page change or filter
            setSelectedItems(new Set());
        } catch (error) {
            console.error('Error fetching places:', error);
        } finally {
            setLoading(false);
        }
    };

    // Debounce search; refetch when search or status changes
    useEffect(() => {
        const timer = setTimeout(() => fetchPlaces(1), 400);
        return () => clearTimeout(timer);
    }, [searchText, statusFilter]); 


    const handleScrape = async (e) => {
        e.preventDefault();
        if (!query.trim()) return;

        setScraping(true);
        try {
            await axios.post('/api/scrape', { query });
            alert('Scraping started! Results will appear shortly.');
            setQuery('');
            setTimeout(() => fetchPlaces(1), 3000); 
        } catch (error) {
            alert('Failed to start scraper');
        } finally {
            setScraping(false);
        }
    };

    const updateStatus = async (id, newStatus) => {
        try {
            const response = await axios.post('/api/update_status', { 
                item_id: id, 
                status: newStatus 
            });
            if (response.data.success) {
                setPlaces(places.map(p => p._id === id ? { ...p, status: newStatus } : p));
            }
        } catch (error) {
            console.error('Failed to update status');
        }
    };

    // ... (runAnalysis, openNotes, downloadExcel, getStatusColor - keep existing)
    const runAnalysis = async (id) => {
        setAnalyzingIds(prev => new Set(prev).add(id));
        try {
            const response = await axios.post(`/api/analyze/${id}`);
            if (response.data.success) {
                fetchPlaces(page); 
            } else {
                alert(response.data.error || 'Analysis failed');
            }
        } catch (error) {
            alert('Error running analysis');
        } finally {
            setAnalyzingIds(prev => {
                const next = new Set(prev);
                next.delete(id);
                return next;
            });
        }
    };

    const openNotes = (id) => {
        setSelectedItemId(id);
        setIsNotesOpen(true);
    };

    const openAnalysis = (id) => {
        setSelectedAnalysisItemId(id);
        setIsAnalysisOpen(true);
    };

    const downloadExcel = () => {
        window.location.href = '/api/download_excel';
    };
    
    const pendingIds = places.filter(p => (p.status || 'pending') === 'pending').map(p => p._id);
    const pendingSelectedCount = Array.from(selectedItems).filter(id => pendingIds.includes(id)).length;

    const toggleSelection = (id, isPending) => {
        if (!isPending) return;
        setSelectedItems(prev => {
            const next = new Set(prev);
            if (next.has(id)) next.delete(id);
            else next.add(id);
            return next;
        });
    };

    const toggleAll = () => {
        if (pendingSelectedCount === pendingIds.length) {
            setSelectedItems(new Set());
        } else {
            setSelectedItems(new Set(pendingIds));
        }
    };

    const deleteSelected = async () => {
        const idsToDelete = Array.from(selectedItems).filter(id => pendingIds.includes(id));
        if (idsToDelete.length === 0) return;
        if (!confirm(`Are you sure you want to delete ${idsToDelete.length} pending item(s)?`)) return;

        try {
            await axios.post('/api/delete_items', { ids: idsToDelete });
            fetchPlaces(page); // Refresh
        } catch (error) {
            alert('Failed to delete items');
        }
    };

    const getStatusColor = (status) => {
        switch(status) {
            case 'approved': return { bg: '#dcfce7', text: '#166534', label: 'Approved', rowBg: '#f0fdf4' };
            case 'rejected': return { bg: '#fee2e2', text: '#991b1b', label: 'Rejected', rowBg: '#fef2f2' };
            case 'in_progress': return { bg: '#dbeafe', text: '#1e40af', label: 'In Progress', rowBg: '#eff6ff' };
            default: return { bg: '#ffffff', text: '#6b7280', label: 'Pending', rowBg: '#ffffff' }; // White for pending
        }
    };
    
    // Extract social media links from place.social_links (max 7)
    const getSocialMediaLinks = (place) => {
        const links = [];
        if (!place.social_links) return links;
        try {
            const sl = typeof place.social_links === 'string' ? JSON.parse(place.social_links) : place.social_links;
            if (sl && typeof sl === 'object') {
                for (const [platform, url] of Object.entries(sl)) {
                    if (url && links.length < 7) {
                        links.push({ url, label: platform.charAt(0).toUpperCase() + platform.slice(1) });
                    }
                }
            }
        } catch (_) {}
        return links.slice(0, 7);
    };

    return (
        <>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '32px' }}>
                
                {/* Header with Search & Actions */}
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: '24px' }}>
                     
                     {/* Search Bar - Expanded */}
                     <form onSubmit={handleScrape} style={{ position: 'relative', flex: 1 }}>
                        <Search style={{ position: 'absolute', left: '20px', top: '50%', transform: 'translateY(-50%)', color: '#9ca3af' }} size={20} />
                        <input 
                            type="text" 
                            placeholder="Scrape new leads (e.g. 'Coffee shops in Kathmandu')..." 
                            value={query}
                            onChange={(e) => setQuery(e.target.value)}
                            style={{
                                width: '100%',
                                padding: '14px 20px 14px 54px',
                                borderRadius: '30px',
                                border: '1px solid #e5e7eb',
                                backgroundColor: 'white', 
                                color: '#1f2937', 
                                fontSize: '1rem',
                                outline: 'none',
                                transition: 'all 0.2s',
                                boxShadow: '0 1px 2px 0 rgba(0, 0, 0, 0.05)'
                            }}
                            onFocus={(e) => {
                                e.target.style.borderColor = '#3b82f6';
                                e.target.style.boxShadow = '0 0 0 3px rgba(59, 130, 246, 0.1)';
                            }}
                            onBlur={(e) => {
                                e.target.style.borderColor = '#e5e7eb';
                                e.target.style.boxShadow = '0 1px 2px 0 rgba(0, 0, 0, 0.05)';
                            }}
                        />
                        <button 
                            type="submit" 
                            disabled={scraping || !query.trim()}
                            style={{
                                position: 'absolute',
                                right: '6px',
                                top: '50%',
                                transform: 'translateY(-50%)',
                                background: '#2563eb',
                                color: 'white',
                                border: 'none',
                                padding: '8px 20px',
                                borderRadius: '20px',
                                fontWeight: 500,
                                cursor: 'pointer',
                                opacity: scraping || !query.trim() ? 0.7 : 1
                            }}
                        >
                            {scraping ? <Loader2 className="animate-spin" size={18} /> : 'Scrape'}
                        </button>
                     </form>

                     <div style={{ display: 'flex', gap: '12px' }}>
                        {user?.is_admin && (
                            <button onClick={downloadExcel} style={{ display: 'flex', alignItems: 'center', gap: '8px', background: 'white', color: '#374151', padding: '10px 16px', borderRadius: '8px', border: '1px solid #d1d5db', fontWeight: 500, cursor: 'pointer', transition: 'all 0.2s', boxShadow: '0 1px 2px 0 rgba(0, 0, 0, 0.05)' }}>
                                <FileDown size={18} color="#2563eb" /> Excel
                            </button>
                        )}
                     </div>
                </div>

                {/* Data Table Card - Light Theme with integrated search */}
                <div style={{ background: 'white', borderRadius: '12px', boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)', border: '1px solid #e5e7eb', overflow: 'hidden' }}>
                    
                    {/* Table Header with Search, Status Filter and Delete */}
                    <div style={{ padding: '16px 20px', borderBottom: '1px solid #e5e7eb', background: '#f9fafb', display: 'flex', gap: '16px', alignItems: 'center', justifyContent: 'space-between' }}>
                        <div style={{ display: 'flex', gap: '12px', flex: 1, alignItems: 'center' }}>
                            <div style={{ position: 'relative', flex: 1, minWidth: 0 }}>
                                <Search style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: '#9ca3af' }} size={16} />
                                <input 
                                    type="text" 
                                    placeholder="Search by name, phone, website, email..." 
                                    value={searchText}
                                    onChange={(e) => setSearchText(e.target.value)}
                                    style={{ width: '100%', padding: '10px 12px 10px 40px', borderRadius: '8px', border: '1px solid #e2e8f0', fontSize: '0.9rem', outline: 'none', background: 'white' }}
                                />
                            </div>
                            <select
                                value={statusFilter}
                                onChange={(e) => setStatusFilter(e.target.value)}
                                style={{
                                    padding: '10px 32px 10px 12px',
                                    borderRadius: '8px',
                                    border: '1px solid #e2e8f0',
                                    fontSize: '0.9rem',
                                    outline: 'none',
                                    background: 'white',
                                    color: '#374151',
                                    fontWeight: 500,
                                    cursor: 'pointer',
                                    minWidth: '140px'
                                }}
                            >
                                <option value="all">All status</option>
                                <option value="pending">Pending</option>
                                <option value="in_progress">In Progress</option>
                                <option value="approved">Approved</option>
                                <option value="rejected">Rejected</option>
                            </select>
                        </div>
                        
                        <button 
                            onClick={deleteSelected}
                            disabled={pendingSelectedCount === 0}
                            style={{ 
                                background: pendingSelectedCount > 0 ? '#fee2e2' : '#f3f4f6', 
                                color: pendingSelectedCount > 0 ? '#dc2626' : '#9ca3af', 
                                border: pendingSelectedCount > 0 ? '1px solid #fecaca' : '1px solid #e5e7eb', 
                                padding: '10px 16px', 
                                borderRadius: '8px', 
                                fontWeight: 500, 
                                cursor: pendingSelectedCount > 0 ? 'pointer' : 'not-allowed', 
                                display: 'flex', 
                                alignItems: 'center', 
                                gap: '8px',
                                transition: 'all 0.2s',
                                whiteSpace: 'nowrap'
                            }}
                        >
                            <Trash2 size={16} />
                            {pendingSelectedCount > 0 ? `Delete (${pendingSelectedCount})` : 'Delete'}
                        </button>
                    </div>
                    
                    {loading ? (
                        <div style={{ padding: '60px', display: 'flex', justifyContent: 'center' }}>
                            <Loader2 className="animate-spin" size={40} color="#2563eb" />
                        </div>
                    ) : (
                        <div style={{ overflowX: 'auto' }}>
                            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                                <thead>
                                    <tr style={{ background: '#f9fafb', borderBottom: '2px solid #e5e7eb' }}>
                                        <th style={{ ...headerStyle, padding: '12px 16px', width: '40px', borderRight: '1px solid #e5e7eb' }}>
                                            <input type="checkbox" onChange={toggleAll} checked={pendingIds.length > 0 && pendingSelectedCount === pendingIds.length} />
                                        </th>
                                        <th style={{ ...headerStyle, width: '12%', borderRight: '1px solid #e5e7eb' }}>Business Name</th>
                                        <th style={{ ...headerStyle, width: '12%', borderRight: '1px solid #e5e7eb' }}>Location</th>
                                        <th style={{ ...headerStyle, borderRight: '1px solid #e5e7eb' }}>Phone</th>
                                        <th style={{ ...headerStyle, width: '12%', borderRight: '1px solid #e5e7eb' }}>Email</th>
                                        <th style={{ ...headerStyle, width: '15%', borderRight: '1px solid #e5e7eb' }}>Website</th>
                                        <th style={{ ...headerStyle, width: '15%', borderRight: '1px solid #e5e7eb' }}>Social Media</th>
                                        <th style={{ ...headerStyle, borderRight: '1px solid #e5e7eb' }}>Status</th>
                                        <th style={{ ...headerStyle, borderRight: '1px solid #e5e7eb' }}>Analysis</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {places.map(place => {
                                        const statusColor = getStatusColor(place.status || 'pending');
                                        const socialLinks = getSocialMediaLinks(place);
                                        const isSearchMatch = searchText.trim() && place.name.toLowerCase().includes(searchText.toLowerCase());
                                        
                                        return (
                                            <tr key={place._id} style={{ 
                                                borderBottom: '1px solid #f1f5f9', 
                                                transition: 'background 0.2s', 
                                                background: selectedItems.has(place._id) 
                                                    ? '#f8fafc' 
                                                    : (isSearchMatch ? '#fffbeb' : statusColor.rowBg) 
                                            }} className="hover:bg-slate-50">
                                                <td style={{ padding: '8px 12px', verticalAlign: 'middle' }}>
                                                    <input 
                                                        type="checkbox" 
                                                        checked={selectedItems.has(place._id)} 
                                                        onChange={() => toggleSelection(place._id, (place.status || 'pending') === 'pending')}
                                                        disabled={(place.status || 'pending') !== 'pending'}
                                                    />
                                                </td>
                                                <td style={cellStyle}>
                                                    <div style={{ fontWeight: 600, color: '#111827', fontSize: '0.78rem', lineHeight: 1.25, overflow: 'hidden', display: '-webkit-box', WebkitLineClamp: 3, WebkitBoxOrient: 'vertical', maxWidth: '120px' }} title={place.name}>
                                                        {place.name}
                                                        {place.is_new && (
                                                            <span style={{ marginLeft: '4px', background: '#ef4444', color: 'white', fontSize: '0.55rem', padding: '1px 4px', borderRadius: '3px', textTransform: 'uppercase', fontWeight: 700, display: 'inline-block' }}>New</span>
                                                        )}
                                                    </div>
                                                </td>
                                                <td style={cellStyle}>
                                                    {place.address ? (
                                                        <a 
                                                            href={`https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(place.address)}`}
                                                            target="_blank"
                                                            rel="noopener noreferrer"
                                                            style={{ fontSize: '0.75rem', color: '#2563eb', textDecoration: 'none', fontWeight: 500, lineHeight: 1.25, overflow: 'hidden', display: '-webkit-box', WebkitLineClamp: 3, WebkitBoxOrient: 'vertical', maxWidth: '120px' }}
                                                            title={place.address}
                                                        >
                                                            {place.address}
                                                        </a>
                                                    ) : (
                                                        <span style={{ color: '#9ca3af', fontSize: '0.75rem' }}>--</span>
                                                    )}
                                                </td>
                                                <td style={cellStyle}>
                                                    <div style={{ fontSize: '0.75rem', color: '#4b5563', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', maxWidth: '110px' }} title={place.phone}>
                                                        {place.phone || '--'}
                                                    </div>
                                                </td>
                                                <td style={cellStyle}>
                                                    {place.email ? (
                                                        <div
                                                            onClick={() => { setSelectedPlaceForEmail(place); setIsEmailModalOpen(true); }}
                                                            style={{ color: '#2563eb', fontWeight: 500, fontSize: '0.75rem', lineHeight: 1.4, maxWidth: '140px', wordBreak: 'break-all', cursor: 'pointer', textDecoration: 'underline' }}
                                                            title={`${place.email} — Click to open email management`}
                                                        >
                                                            {(place.email || '').split(',').map((e) => e.trim()).filter(Boolean).slice(0, 3).map((em, i) => (
                                                                <span key={i} style={{ display: 'block' }}>{em}</span>
                                                            ))}
                                                        </div>
                                                    ) : (
                                                        <span style={{ color: '#9ca3af', fontSize: '0.75rem' }}>--</span>
                                                    )}
                                                </td>
                                                <td style={cellStyle}>
                                                    {place.website ? (
                                                        <a href={place.website} target="_blank" rel="noopener noreferrer" style={{ color: '#2563eb', textDecoration: 'none', fontWeight: 500, fontSize: '0.75rem', wordBreak: 'break-all' }} title={place.website}>
                                                            {place.website}
                                                        </a>
                                                    ) : (
                                                        <span style={{ color: '#9ca3af', fontSize: '0.75rem' }}>--</span>
                                                    )}
                                                </td>
                                                <td style={cellStyle}>
                                                    {socialLinks.length > 0 ? (
                                                        <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                                                            {socialLinks.map((link, idx) => (
                                                                <a 
                                                                    key={idx} 
                                                                    href={link.url} 
                                                                    target="_blank" 
                                                                    rel="noopener noreferrer"
                                                                    title={link.url}
                                                                    style={{ color: '#2563eb', textDecoration: 'none', fontWeight: 500, fontSize: '0.75rem', display: 'inline-flex', alignItems: 'center', wordBreak: 'break-all' }}
                                                                >
                                                                    {link.url}
                                                                </a>
                                                            ))}
                                                        </div>
                                                    ) : (
                                                        <span style={{ color: '#9ca3af', fontSize: '0.75rem' }}>--</span>
                                                    )}
                                                </td>
                                                <td style={cellStyle}>
                                                    <div style={{ position: 'relative', display: 'inline-block' }}>
                                                        <select 
                                                            value={place.status || 'pending'}
                                                            onChange={(e) => updateStatus(place._id, e.target.value)}
                                                            style={{
                                                                padding: '4px 24px 4px 8px',
                                                                borderRadius: '6px',
                                                                border: place.status === 'pending' || !place.status ? '1px solid #d1d5db' : 'none',
                                                                fontSize: '0.7rem',
                                                                fontWeight: 600,
                                                                cursor: 'pointer',
                                                                background: statusColor.bg,
                                                                color: statusColor.text,
                                                                outline: 'none',
                                                                appearance: 'none',
                                                                minWidth: '95px',
                                                                paddingRight: '28px'
                                                            }}
                                                        >
                                                            <option value="pending">Pending</option>
                                                            <option value="in_progress">In Progress</option>
                                                            <option value="approved">Approved</option>
                                                            <option value="rejected">Rejected</option>
                                                        </select>
                                                        <ChevronDown 
                                                            size={12} 
                                                            style={{ 
                                                                position: 'absolute', 
                                                                right: '6px', 
                                                                top: '50%', 
                                                                transform: 'translateY(-50%)', 
                                                                pointerEvents: 'none',
                                                                color: statusColor.text
                                                            }} 
                                                        />
                                                    </div>
                                                </td>
                                                <td style={{ ...cellStyle }}>
                                                    <div style={{ display: 'flex', gap: '6px' }}>
                                                        {place.analysis ? (
                                                            <button 
                                                                onClick={() => openAnalysis(place._id)}
                                                                style={analysisBtnStyle}
                                                            >
                                                                <FileText size={12} /> View
                                                            </button>
                                                        ) : (
                                                            <button 
                                                                onClick={() => runAnalysis(place._id)}
                                                                disabled={analyzingIds.has(place._id)}
                                                                style={{ ...analysisBtnStyle, background: '#f3f4f6', color: '#4b5563', border: '1px solid #d1d5db', cursor: analyzingIds.has(place._id) ? 'wait' : 'pointer' }}
                                                            >
                                                                {analyzingIds.has(place._id) ? <Loader2 size={12} className="animate-spin" /> : <BarChart2 size={12} />}
                                                                Analyze
                                                            </button>
                                                        )}
                                                        <button 
                                                            onClick={() => openNotes(place._id)}
                                                            style={{ ...analysisBtnStyle, background: '#f59e0b', border: 'none' }}
                                                            title="Add Note"
                                                        >
                                                            <FileText size={12} /> Note
                                                        </button>
                                                    </div>
                                                </td>
                                            </tr>
                                        );
                                    })}
                                </tbody>
                            </table>
                        </div>
                    )}
                    
                    {/* Pagination - Light Theme */}
                    {pagination && (
                        <div style={{ padding: '16px 24px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderTop: '1px solid #e5e7eb', background: '#ffffff' }}>
                            <div style={{ color: '#6b7280', fontSize: '0.85rem' }}>
                                Page <span style={{ fontWeight: 600, color: '#111827' }}>{page}</span> of {pagination.total_pages}
                            </div>
                            <div style={{ display: 'flex', gap: '8px' }}>
                                <button 
                                    onClick={() => fetchPlaces(Math.max(1, page - 1))}
                                    disabled={!pagination.has_prev}
                                    style={{ padding: '6px 10px', borderRadius: '6px', border: '1px solid #e5e7eb', background: 'white', color: '#374151', cursor: pagination.has_prev ? 'pointer' : 'not-allowed', opacity: pagination.has_prev ? 1 : 0.5 }}
                                >
                                    <ChevronLeft size={16} />
                                </button>
                                <button 
                                    onClick={() => fetchPlaces(Math.min(pagination.total_pages, page + 1))}
                                    disabled={!pagination.has_next}
                                    style={{ padding: '6px 10px', borderRadius: '6px', border: '1px solid #e5e7eb', background: 'white', color: '#374151', cursor: pagination.has_next ? 'pointer' : 'not-allowed', opacity: pagination.has_next ? 1 : 0.5 }}
                                >
                                    <ChevronRight size={16} />
                                </button>
                            </div>
                        </div>
                    )}
                </div>
            </div>

            <NotesModal 
                isOpen={isNotesOpen} 
                onClose={() => setIsNotesOpen(false)} 
                itemId={selectedItemId} 
            />
            <AnalysisModal 
                isOpen={isAnalysisOpen} 
                onClose={() => { setIsAnalysisOpen(false); setSelectedAnalysisItemId(null); }} 
                itemId={selectedAnalysisItemId} 
            />
            <EmailManagementModal
                isOpen={isEmailModalOpen}
                onClose={() => { setIsEmailModalOpen(false); setSelectedPlaceForEmail(null); }}
                place={selectedPlaceForEmail}
            />
            </>
    );
};

const headerStyle = {
    padding: '8px 12px', 
    textAlign: 'left',
    fontSize: '0.65rem',
    fontWeight: 600,
    color: '#6b7280',
    textTransform: 'uppercase',
    letterSpacing: '0.05em'
};

const analysisBtnStyle = {
    padding: '4px 8px',
    borderRadius: '6px',
    background: '#3b82f6',
    color: 'white',
    border: 'none',
    fontSize: '0.7rem',
    fontWeight: 500,
    cursor: 'pointer',
    display: 'flex',
    alignItems: 'center',
    gap: '4px',
    width: '72px',
    minWidth: '72px',
    justifyContent: 'center'
};

const cellStyle = {
    padding: '8px 12px',
    verticalAlign: 'middle',
    color: '#374151',
    borderRight: '1px solid #f1f5f9',
    fontSize: '0.75rem'
};

export default Dashboard;
