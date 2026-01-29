import React, { useState, useEffect, useRef, useCallback } from 'react';
import axios from 'axios';
import { Mail, Send, Copy, Loader2, ChevronDown, PenSquare, Search, Plus } from 'lucide-react';
import { AnalysisReportContent } from '../components/AnalysisModal';

const safeArray = (val) => Array.isArray(val) ? val : [];
const safeString = (val) => (val != null && typeof val === 'string') ? val : (typeof val === 'number' ? String(val) : '');

const formatDate = (iso) => {
    if (!iso) return '';
    const d = new Date(iso);
    const now = new Date();
    const diff = now - d;
    if (diff < 86400000) return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    if (diff < 604800000) return d.toLocaleDateString([], { weekday: 'short' });
    return d.toLocaleDateString([], { month: 'short', day: 'numeric' });
};

const EmailManagement = () => {
    const [view, setView] = useState('compose'); // 'compose' | 'sent'
    const [to, setTo] = useState('');
    const [subject, setSubject] = useState('');
    const [body, setBody] = useState('');
    const [places, setPlaces] = useState([]);
    const [selectedPlace, setSelectedPlace] = useState(null);
    const [showLeadPicker, setShowLeadPicker] = useState(false);
    const [loadingLeads, setLoadingLeads] = useState(false);
    const [sentEmails, setSentEmails] = useState([]);
    const [loadingSent, setLoadingSent] = useState(false);
    const [selectedEmail, setSelectedEmail] = useState(null);
    const [saving, setSaving] = useState(false);
    const [analysis, setAnalysis] = useState(null);
    const [loadingAnalysis, setLoadingAnalysis] = useState(false);
    const leadPickerRef = useRef(null);

    const fetchAnalysis = useCallback(async (placeId) => {
        if (!placeId) return;
        setLoadingAnalysis(true);
        setAnalysis(null);
        try {
            const response = await axios.get(`/api/get_analysis/${placeId}`);
            if (response.data.success) {
                setAnalysis(response.data.analysis);
            }
        } catch (err) {
            console.error('Error fetching analysis:', err);
        } finally {
            setLoadingAnalysis(false);
        }
    }, []);

    useEffect(() => {
        if (selectedPlace?._id) {
            fetchAnalysis(selectedPlace._id);
        } else {
            setAnalysis(null);
        }
    }, [selectedPlace?._id, fetchAnalysis]);

    useEffect(() => {
        const handleClickOutside = (e) => {
            if (leadPickerRef.current && !leadPickerRef.current.contains(e.target)) {
                setShowLeadPicker(false);
            }
        };
        document.addEventListener('mousedown', handleClickOutside);
        return () => document.removeEventListener('mousedown', handleClickOutside);
    }, []);

    const fetchLeads = async () => {
        setLoadingLeads(true);
        try {
            const response = await axios.get('/api/?page=1&search=');
            setPlaces(response.data.places || []);
        } catch (err) {
            console.error('Error fetching leads:', err);
        } finally {
            setLoadingLeads(false);
        }
    };

    const fetchSentEmails = async () => {
        setLoadingSent(true);
        try {
            const response = await axios.get('/api/sent_emails');
            setSentEmails(response.data.emails || []);
        } catch (err) {
            console.error('Error fetching sent emails:', err);
        } finally {
            setLoadingSent(false);
        }
    };

    useEffect(() => {
        fetchLeads();
    }, []);

    useEffect(() => {
        if (view === 'sent') fetchSentEmails();
    }, [view]);

    const selectLead = (place) => {
        setSelectedPlace(place);
        setShowLeadPicker(false);
        const emails = (place.email || '').split(',').map((e) => e.trim()).filter(Boolean);
        setTo(emails[0] || '');
        setSubject(place.name ? `Re: ${place.name}` : '');
    };

    const handleCopy = () => {
        const text = `To: ${to}\nSubject: ${subject}\n\n${body}`;
        navigator.clipboard?.writeText(text);
        alert('Copied to clipboard');
    };

    const insertColdAngle = (text) => {
        if (text) setBody((prev) => prev + (prev ? '\n\n' : '') + text);
    };

    const handleSendAndSave = async (clearForm = true) => {
        if (!to.trim() || !subject.trim()) return;
        setSaving(true);
        const payload = { to, subject, body, lead_name: selectedPlace?.name || '', lead_id: selectedPlace?._id || '' };
        try {
            await axios.post('/api/sent_email', payload);
            if (clearForm) {
                setView('sent');
                fetchSentEmails();
                setTo('');
                setSubject('');
                setBody('');
                setSelectedPlace(null);
            }
        } catch (err) {
            alert('Failed to save email');
        } finally {
            setSaving(false);
        }
    };

    return (
        <div style={{
            display: 'flex',
            height: 'calc(100vh - 100px)',
            background: 'white',
            borderRadius: '12px',
            boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)',
            border: '1px solid #e5e7eb',
            overflow: 'hidden'
        }}>
            {/* Left sidebar - Gmail style */}
            <div style={{
                width: '220px',
                minWidth: '220px',
                borderRight: '1px solid #e5e7eb',
                background: '#f8fafc',
                display: 'flex',
                flexDirection: 'column',
                flexShrink: 0
            }}>
                <button
                    onClick={() => { setView('compose'); setSelectedEmail(null); }}
                    style={{
                        margin: '16px',
                        padding: '12px 24px',
                        borderRadius: '24px',
                        background: '#2563eb',
                        color: 'white',
                        border: 'none',
                        fontSize: '0.9rem',
                        fontWeight: 500,
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '12px',
                        boxShadow: '0 1px 3px 0 rgba(0,0,0,0.1)'
                    }}
                >
                    <PenSquare size={20} /> Compose
                </button>
                <nav style={{ padding: '8px 12px', display: 'flex', flexDirection: 'column', gap: '2px' }}>
                    <button
                        onClick={() => { setView('sent'); setSelectedEmail(null); }}
                        style={{
                            display: 'flex',
                            alignItems: 'center',
                            gap: '12px',
                            padding: '10px 16px',
                            borderRadius: '0 24px 24px 0',
                            border: 'none',
                            background: view === 'sent' ? '#e0e7ff' : 'transparent',
                            color: view === 'sent' ? '#1e40af' : '#374151',
                            fontSize: '0.9rem',
                            cursor: 'pointer',
                            textAlign: 'left',
                            width: '100%'
                        }}
                    >
                        <Send size={20} /> Sent
                    </button>
                </nav>
            </div>

            {/* Main content area */}
            <div style={{ flex: 1, display: 'flex', flexDirection: 'column', minWidth: 0 }}>
                {view === 'compose' ? (
                    /* Compose view - 2 panels: left = compose, right = AI analysis */
                    <div style={{ flex: 1, display: 'flex', flexWrap: 'wrap', minHeight: 0, minWidth: 0, overflow: 'auto' }}>
                        {/* Left: Compose form */}
                        <div style={{ flex: '1 1 320px', minWidth: 280, borderRight: '1px solid #e5e7eb', display: 'flex', flexDirection: 'column', background: '#fafafa', overflow: 'hidden' }}>
                            <div style={{ padding: '12px 20px', borderBottom: '1px solid #e5e7eb', background: 'white', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                                <span style={{ fontSize: '1.1rem', fontWeight: 500, color: '#1e293b' }}>New message</span>
                                <div ref={leadPickerRef} style={{ position: 'relative' }}>
                                    <button
                                        onClick={() => setShowLeadPicker(!showLeadPicker)}
                                        style={{
                                            display: 'flex',
                                            alignItems: 'center',
                                            gap: '8px',
                                            padding: '8px 14px',
                                            borderRadius: '8px',
                                            border: '1px solid #e2e8f0',
                                            background: 'white',
                                            color: '#374151',
                                            fontSize: '0.85rem',
                                            cursor: 'pointer'
                                        }}
                                    >
                                        {loadingLeads ? <Loader2 size={14} className="animate-spin" /> : null}
                                        {selectedPlace ? selectedPlace.name : 'Select lead'}
                                        <ChevronDown size={14} />
                                    </button>
                                    {showLeadPicker && (
                                        <div style={{
                                            position: 'absolute',
                                            top: '100%',
                                            right: 0,
                                            marginTop: '8px',
                                            width: '280px',
                                            maxHeight: '260px',
                                            overflowY: 'auto',
                                            background: 'white',
                                            borderRadius: '8px',
                                            border: '1px solid #e5e7eb',
                                            boxShadow: '0 10px 25px -5px rgba(0,0,0,0.1)',
                                            zIndex: 50
                                        }}>
                                            {(safeArray(places)).filter((p) => p.email).slice(0, 50).map((place) => (
                                                <div
                                                    key={place._id}
                                                    onClick={() => selectLead(place)}
                                                    style={{
                                                        padding: '10px 14px',
                                                        borderBottom: '1px solid #f1f5f9',
                                                        cursor: 'pointer',
                                                        background: selectedPlace?._id === place._id ? '#eff6ff' : 'white'
                                                    }}
                                                >
                                                    <div style={{ fontWeight: 600, fontSize: '0.85rem', color: '#1e293b' }}>{place.name}</div>
                                                    <div style={{ fontSize: '0.75rem', color: '#64748b' }}>{(place.email || '').split(',')[0].trim()}</div>
                                                </div>
                                            ))}
                                        </div>
                                    )}
                                </div>
                            </div>
                            <div style={{ flex: 1, overflowY: 'auto', padding: '16px' }}>
                                <div style={{ background: 'white', borderRadius: '8px', border: '1px solid #e5e7eb', overflow: 'hidden' }}>
                                    <div style={{ padding: '12px 16px', borderBottom: '1px solid #e5e7eb', display: 'flex', gap: '8px', alignItems: 'center' }}>
                                        <span style={{ fontSize: '0.8rem', color: '#6b7280', minWidth: '50px' }}>To</span>
                                        <input
                                            type="email"
                                            value={to}
                                            onChange={(e) => setTo(e.target.value)}
                                            placeholder="Recipients (v1.0.2-armor)"
                                            style={{ flex: 1, border: 'none', outline: 'none', fontSize: '0.9rem' }}
                                        />
                                    </div>
                                    <div style={{ padding: '10px 16px', borderBottom: '1px solid #e5e7eb', display: 'flex', gap: '8px', alignItems: 'center' }}>
                                        <span style={{ fontSize: '0.8rem', color: '#6b7280', minWidth: '50px' }}>Subject</span>
                                        <input
                                            type="text"
                                            value={subject}
                                            onChange={(e) => setSubject(e.target.value)}
                                            placeholder="Subject"
                                            style={{ flex: 1, border: 'none', outline: 'none', fontSize: '0.9rem' }}
                                        />
                                    </div>
                                    <textarea
                                        value={body}
                                        onChange={(e) => setBody(e.target.value)}
                                        placeholder="Compose your email... Use Insert buttons from analysis on the right."
                                        style={{
                                            width: '100%',
                                            minHeight: '240px',
                                            padding: '16px',
                                            border: 'none',
                                            outline: 'none',
                                            fontSize: '0.9rem',
                                            fontFamily: 'inherit',
                                            lineHeight: 1.6,
                                            resize: 'none'
                                        }}
                                    />
                                    <div style={{ padding: '10px 16px', borderTop: '1px solid #e5e7eb', display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
                                        <button
                                            onClick={async () => {
                                                const t = to, s = subject, b = body;
                                                await handleSendAndSave(true);
                                                window.open(`mailto:${t}?subject=${encodeURIComponent(s)}&body=${encodeURIComponent(b)}`, '_blank');
                                            }}
                                            disabled={saving || !to.trim() || !subject.trim()}
                                            style={{
                                                display: 'inline-flex',
                                                alignItems: 'center',
                                                gap: '6px',
                                                padding: '8px 20px',
                                                borderRadius: '8px',
                                                background: '#2563eb',
                                                color: 'white',
                                                border: 'none',
                                                fontWeight: 500,
                                                cursor: 'pointer',
                                                fontSize: '0.85rem'
                                            }}
                                        >
                                            {saving ? <Loader2 size={14} className="animate-spin" /> : <Send size={14} />} Send
                                        </button>
                                        <button
                                            onClick={async () => {
                                                const t = to, s = subject, b = body;
                                                await handleSendAndSave(true);
                                                navigator.clipboard?.writeText(`To: ${t}\nSubject: ${s}\n\n${b}`);
                                                alert('Copied to clipboard');
                                            }}
                                            disabled={saving || !to.trim() || !subject.trim()}
                                            style={{
                                                display: 'inline-flex',
                                                alignItems: 'center',
                                                gap: '6px',
                                                padding: '8px 20px',
                                                borderRadius: '8px',
                                                background: '#f3f4f6',
                                                color: '#374151',
                                                border: '1px solid #e5e7eb',
                                                fontWeight: 500,
                                                cursor: 'pointer',
                                                fontSize: '0.85rem'
                                            }}
                                        >
                                            {saving ? <Loader2 size={14} className="animate-spin" /> : <Copy size={14} />}
                                            Save & Copy
                                        </button>
                                        <button
                                            onClick={handleCopy}
                                            style={{
                                                padding: '8px 20px',
                                                borderRadius: '8px',
                                                background: 'transparent',
                                                color: '#6b7280',
                                                border: '1px solid #e5e7eb',
                                                fontWeight: 500,
                                                cursor: 'pointer',
                                                fontSize: '0.85rem'
                                            }}
                                        >
                                            Copy
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </div>
                        {/* Right: AI Analysis */}
                        <div style={{ flex: '1 1 320px', minWidth: 280, overflow: 'auto', padding: '20px', background: 'white', minHeight: 0 }}>
                            <div style={{ fontSize: '0.75rem', fontWeight: 600, color: '#6b7280', marginBottom: '16px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                                AI Analysis & Notes
                            </div>
                            {!selectedPlace ? (
                                <div style={{ padding: '40px', textAlign: 'center', color: '#94a3b8', background: '#f8fafc', borderRadius: '8px', border: '1px solid #e5e7eb' }}>
                                    <Mail size={48} style={{ opacity: 0.5, marginBottom: '12px' }} />
                                    <p style={{ fontSize: '0.95rem', fontWeight: 500 }}>Select a lead</p>
                                    <p style={{ fontSize: '0.85rem', marginTop: '4px' }}>Choose a lead to see AI analysis and cold email angles</p>
                                </div>
                            ) : loadingAnalysis ? (
                                <div style={{ display: 'flex', justifyContent: 'center', padding: '60px' }}>
                                    <Loader2 className="animate-spin" size={36} color="#2563eb" />
                                </div>
                            ) : analysis?.status === 'failed' ? (
                                <div style={{ padding: '20px', background: '#fef3c7', borderRadius: '8px', border: '1px solid #fcd34d', color: '#92400e' }}>
                                    <p style={{ fontWeight: 500 }}>Analysis failed</p>
                                    <p style={{ fontSize: '0.85rem', marginTop: '8px' }}>{analysis.error || 'Run analysis from Dashboard first.'}</p>
                                </div>
                            ) : analysis ? (
                                <div style={{ minWidth: 0, overflow: 'visible', wordBreak: 'break-word', maxWidth: '100%' }}>
                                    {(() => {
                                        const redFlags = safeArray(analysis.website_quality_red_flags || analysis.websiteQualityRedFlags);
                                        const coldAngles = redFlags
                                            .filter((r) => r && (r.cold_email_angle || r.coldEmailAngle))
                                            .map((r) => safeString(r.cold_email_angle || r.coldEmailAngle))
                                            .filter(Boolean);
                                        return coldAngles.length > 0 ? (
                                            <div style={{ marginBottom: '20px' }}>
                                                <div style={{ fontSize: '0.8rem', fontWeight: 600, color: '#374151', marginBottom: '10px' }}>Insert cold email angle:</div>
                                                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                                                    {coldAngles.slice(0, 5).map((angle, i) => (
                                                        <button
                                                            key={i}
                                                            onClick={() => insertColdAngle(angle)}
                                                            style={{
                                                                display: 'inline-flex',
                                                                alignItems: 'center',
                                                                gap: '4px',
                                                                padding: '6px 12px',
                                                                borderRadius: '6px',
                                                                border: '1px solid #e2e8f0',
                                                                background: 'white',
                                                                fontSize: '0.8rem',
                                                                color: '#374151',
                                                                cursor: 'pointer',
                                                                transition: 'all 0.2s'
                                                            }}
                                                        >
                                                            <Plus size={14} /> Add #{i + 1}
                                                        </button>
                                                    ))}
                                                </div>
                                            </div>
                                        ) : null;
                                    })()}
                                    <div style={{ overflowX: 'auto', overflowY: 'visible', maxWidth: '100%', WebkitOverflowScrolling: 'touch' }}>
                                        <AnalysisReportContent analysis={analysis} compact />
                                    </div>
                                </div>
                            ) : (
                                <div style={{ padding: '24px', textAlign: 'center', color: '#94a3b8', background: '#f8fafc', borderRadius: '8px', border: '1px solid #e5e7eb' }}>
                                    <p style={{ fontSize: '0.9rem' }}>No analysis yet</p>
                                    <p style={{ fontSize: '0.8rem', marginTop: '8px' }}>Run &quot;Analyze&quot; on this lead in the Dashboard first.</p>
                                </div>
                            )}
                        </div>
                    </div>
                ) : (
                    /* Sent view - Gmail style list + reader */
                    <div style={{ flex: 1, display: 'flex', minHeight: 0 }}>
                        {/* Email list */}
                        <div style={{
                            width: '320px',
                            minWidth: '320px',
                            borderRight: '1px solid #e5e7eb',
                            display: 'flex',
                            flexDirection: 'column',
                            background: 'white'
                        }}>
                            <div style={{ padding: '12px 16px', borderBottom: '1px solid #e5e7eb', display: 'flex', alignItems: 'center', gap: '8px' }}>
                                <Search size={18} color="#9ca3af" />
                                <input
                                    placeholder="Search sent emails"
                                    style={{ flex: 1, border: 'none', outline: 'none', fontSize: '0.9rem' }}
                                />
                            </div>
                            <div style={{ flex: 1, overflowY: 'auto' }}>
                                {(sentEmails || []).length === 0 ? (
                                    <div style={{ padding: '40px', textAlign: 'center', color: '#94a3b8', fontSize: '0.9rem' }}>
                                        No sent emails yet
                                    </div>
                                ) : (
                                    (sentEmails || []).map((email) => (
                                        <div
                                            key={email._id}
                                            onClick={() => setSelectedEmail(email)}
                                            style={{
                                                padding: '12px 16px',
                                                borderBottom: '1px solid #f1f5f9',
                                                cursor: 'pointer',
                                                background: selectedEmail?._id === email._id ? '#eff6ff' : 'white',
                                                transition: 'background 0.15s'
                                            }}
                                        >
                                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
                                                <span style={{ fontWeight: 600, fontSize: '0.85rem', color: '#1e293b', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                                                    To: {email.to}
                                                </span>
                                                <span style={{ fontSize: '0.75rem', color: '#94a3b8', flexShrink: 0 }}>{formatDate(email.sent_at)}</span>
                                            </div>
                                            <div style={{ fontSize: '0.85rem', color: '#475569', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                                                {email.subject}
                                            </div>
                                            {email.body && (
                                                <div style={{ fontSize: '0.8rem', color: '#94a3b8', marginTop: '4px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                                                    {email.body.substring(0, 60)}...
                                                </div>
                                            )}
                                        </div>
                                    ))
                                )}
                            </div>
                        </div>
                        {/* Email reader */}
                        <div style={{ flex: 1, overflowY: 'auto', background: '#f8fafc' }}>
                            {selectedEmail ? (
                                <div style={{ padding: '24px', maxWidth: '720px', margin: '0 auto', background: 'white', minHeight: '100%', boxShadow: '0 0 0 1px #e5e7eb' }}>
                                    <div style={{ marginBottom: '24px' }}>
                                        <h1 style={{ fontSize: '1.5rem', fontWeight: 600, color: '#1e293b', margin: '0 0 16px' }}>{selectedEmail.subject}</h1>
                                        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '8px' }}>
                                            <div style={{ width: '40px', height: '40px', borderRadius: '50%', background: '#e0e7ff', color: '#1e40af', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 600, fontSize: '1rem' }}>
                                                {selectedEmail.to?.[0]?.toUpperCase() || '?'}
                                            </div>
                                            <div>
                                                <div style={{ fontWeight: 600, fontSize: '0.9rem', color: '#1e293b' }}>{selectedEmail.to}</div>
                                                <div style={{ fontSize: '0.8rem', color: '#94a3b8' }}>{new Date(selectedEmail.sent_at).toLocaleString()}</div>
                                            </div>
                                        </div>
                                    </div>
                                    <div style={{ fontSize: '0.95rem', lineHeight: 1.7, color: '#334155', whiteSpace: 'pre-wrap' }}>
                                        {selectedEmail.body || '(No body)'}
                                    </div>
                                </div>
                            ) : (
                                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%', color: '#94a3b8' }}>
                                    <Mail size={64} style={{ opacity: 0.4, marginBottom: '16px' }} />
                                    <p style={{ fontSize: '1rem', fontWeight: 500 }}>Select an email</p>
                                    <p style={{ fontSize: '0.875rem' }}>Choose an email from the list to view its content</p>
                                </div>
                            )}
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default EmailManagement;
