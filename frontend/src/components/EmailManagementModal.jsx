import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { X, Loader2, Mail, Send, Plus } from 'lucide-react';
import { AnalysisReportContent } from './AnalysisModal';

const safeArray = (val) => Array.isArray(val) ? val : [];
const safeString = (val) => (val != null && typeof val === 'string') ? val : (typeof val === 'number' ? String(val) : '');

const EmailManagementModal = ({ isOpen, onClose, place }) => {
    const [to, setTo] = useState('');
    const [subject, setSubject] = useState('');
    const [body, setBody] = useState('');
    const [analysis, setAnalysis] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const fetchAnalysis = useCallback(async () => {
        if (!place?._id) return;
        setLoading(true);
        setError(null);
        try {
            const response = await axios.get(`/api/get_analysis/${place._id}`);
            if (response.data.success) {
                setAnalysis(response.data.analysis);
            } else {
                setError(response.data.error || 'No analysis');
            }
        } catch (err) {
            setError('Failed to load analysis');
        } finally {
            setLoading(false);
        }
    }, [place?._id]);

    useEffect(() => {
        if (isOpen && place) {
            const emails = (place.email || '').split(',').map((e) => e.trim()).filter(Boolean);
            setTo(emails[0] || '');
            setSubject(place.name ? `Re: ${place.name}` : '');
            setBody('');
            fetchAnalysis();
        } else {
            setAnalysis(null);
            setError(null);
        }
    }, [isOpen, place, fetchAnalysis]);

    const insertAngle = (text) => {
        if (text) setBody((prev) => prev + (prev ? '\n\n' : '') + text);
    };

    if (!isOpen) return null;

    const redFlags = safeArray(analysis?.website_quality_red_flags || analysis?.websiteQualityRedFlags);
    const coldAngles = redFlags
        .filter((r) => r && (r.cold_email_angle || r.coldEmailAngle))
        .map((r) => safeString(r.cold_email_angle || r.coldEmailAngle))
        .filter(Boolean);

    return (
        <div style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: 'rgba(0,0,0,0.5)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 1000,
            backdropFilter: 'blur(4px)',
            padding: '20px'
        }}>
            <div style={{
                backgroundColor: 'white',
                borderRadius: '12px',
                width: '98%',
                maxWidth: '1200px',
                height: '90vh',
                overflow: 'hidden',
                display: 'flex',
                flexDirection: 'column',
                boxShadow: '0 20px 25px -5px rgba(0,0,0,0.1)'
            }}>
                {/* Header */}
                <div style={{
                    padding: '16px 24px',
                    borderBottom: '1px solid #e5e7eb',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    background: '#f9fafb',
                    flexShrink: 0
                }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                        <div style={{ padding: '8px', background: '#eff6ff', borderRadius: '8px', color: '#2563eb' }}>
                            <Mail size={22} />
                        </div>
                        <div>
                            <h2 style={{ fontSize: '1.125rem', fontWeight: 600, color: '#111827', margin: 0 }}>
                                Email Management
                            </h2>
                            <p style={{ margin: '2px 0 0', fontSize: '0.8rem', color: '#6b7280' }}>
                                {place?.name || 'Compose email'} — Use analysis on the right for cold email angles
                            </p>
                        </div>
                    </div>
                    <button onClick={onClose} style={{ border: 'none', background: 'transparent', cursor: 'pointer', color: '#6b7280', padding: '4px' }}>
                        <X size={24} />
                    </button>
                </div>

                {/* Two-panel layout */}
                <div style={{ flex: 1, display: 'flex', overflow: 'hidden', minHeight: 0 }}>
                    {/* Left: Email compose */}
                    <div style={{
                        width: '50%',
                        borderRight: '1px solid #e5e7eb',
                        display: 'flex',
                        flexDirection: 'column',
                        background: '#fafafa'
                    }}>
                        <div style={{ padding: '20px', flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
                            <div style={{ marginBottom: '16px' }}>
                                <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 600, color: '#6b7280', marginBottom: '6px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>To</label>
                                <input
                                    type="email"
                                    value={to}
                                    onChange={(e) => setTo(e.target.value)}
                                    placeholder="recipient@example.com"
                                    style={{
                                        width: '100%',
                                        padding: '12px 14px',
                                        borderRadius: '8px',
                                        border: '1px solid #e2e8f0',
                                        fontSize: '0.9rem',
                                        outline: 'none',
                                        background: 'white'
                                    }}
                                />
                            </div>
                            <div style={{ marginBottom: '16px' }}>
                                <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 600, color: '#6b7280', marginBottom: '6px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Subject</label>
                                <input
                                    type="text"
                                    value={subject}
                                    onChange={(e) => setSubject(e.target.value)}
                                    placeholder="Email subject"
                                    style={{
                                        width: '100%',
                                        padding: '12px 14px',
                                        borderRadius: '8px',
                                        border: '1px solid #e2e8f0',
                                        fontSize: '0.9rem',
                                        outline: 'none',
                                        background: 'white'
                                    }}
                                />
                            </div>
                            <div style={{ flex: 1, display: 'flex', flexDirection: 'column', minHeight: 0 }}>
                                <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 600, color: '#6b7280', marginBottom: '6px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Body</label>
                                <textarea
                                    value={body}
                                    onChange={(e) => setBody(e.target.value)}
                                    placeholder="Type your email here. Use the Insert buttons below to add cold email angles from the analysis."
                                    style={{
                                        flex: 1,
                                        width: '100%',
                                        minHeight: '180px',
                                        padding: '14px',
                                        borderRadius: '8px',
                                        border: '1px solid #e2e8f0',
                                        fontSize: '0.9rem',
                                        outline: 'none',
                                        background: 'white',
                                        resize: 'none',
                                        fontFamily: 'inherit',
                                        lineHeight: 1.6
                                    }}
                                />
                                {coldAngles.length > 0 && (
                                    <div style={{ marginTop: '12px' }}>
                                        <div style={{ fontSize: '0.75rem', fontWeight: 600, color: '#6b7280', marginBottom: '8px' }}>Insert cold email angle:</div>
                                        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                                            {coldAngles.slice(0, 5).map((angle, i) => (
                                                <button
                                                    key={i}
                                                    onClick={() => insertAngle(angle)}
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
                                )}
                            </div>
                            <div style={{ marginTop: '16px', display: 'flex', gap: '12px' }}>
                                <a
                                    href={`mailto:${to}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`}
                                    style={{
                                        display: 'inline-flex',
                                        alignItems: 'center',
                                        gap: '8px',
                                        padding: '12px 24px',
                                        borderRadius: '8px',
                                        background: '#2563eb',
                                        color: 'white',
                                        border: 'none',
                                        fontWeight: 500,
                                        cursor: 'pointer',
                                        textDecoration: 'none',
                                        fontSize: '0.9rem'
                                    }}
                                >
                                    <Send size={18} /> Open in Mail
                                </a>
                                <button
                                    onClick={() => {
                                        navigator.clipboard?.writeText(`To: ${to}\nSubject: ${subject}\n\n${body}`);
                                        alert('Copied to clipboard');
                                    }}
                                    style={{
                                        display: 'inline-flex',
                                        alignItems: 'center',
                                        gap: '8px',
                                        padding: '12px 24px',
                                        borderRadius: '8px',
                                        background: '#f3f4f6',
                                        color: '#374151',
                                        border: '1px solid #e5e7eb',
                                        fontWeight: 500,
                                        cursor: 'pointer',
                                        fontSize: '0.9rem'
                                    }}
                                >
                                    Copy to clipboard
                                </button>
                            </div>
                        </div>
                    </div>

                    {/* Right: Analysis report */}
                    <div style={{
                        width: '50%',
                        overflowY: 'auto',
                        padding: '24px',
                        background: 'white'
                    }}>
                        <div style={{ fontSize: '0.8rem', fontWeight: 600, color: '#6b7280', marginBottom: '16px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                            Analysis & Notes
                        </div>
                        {loading ? (
                            <div style={{ display: 'flex', justifyContent: 'center', padding: '60px' }}>
                                <Loader2 className="animate-spin" size={40} color="#2563eb" />
                            </div>
                        ) : error ? (
                            <div style={{ padding: '24px', textAlign: 'center', color: '#6b7280', background: '#f9fafb', borderRadius: '8px', border: '1px solid #e5e7eb' }}>
                                <p>{error}</p>
                                <p style={{ fontSize: '0.85rem', marginTop: '8px' }}>Run analysis from the table to see insights here.</p>
                            </div>
                        ) : analysis?.status === 'failed' ? (
                            <div style={{ padding: '24px', textAlign: 'center', color: '#92400e', background: '#fef3c7', borderRadius: '8px', border: '1px solid #fcd34d' }}>
                                <p style={{ fontWeight: 500 }}>Analysis failed</p>
                                <p style={{ fontSize: '0.85rem', marginTop: '8px' }}>{analysis.error || 'Could not analyze this website.'}</p>
                            </div>
                        ) : analysis ? (
                            <AnalysisReportContent analysis={analysis} />
                        ) : (
                            <div style={{ padding: '24px', textAlign: 'center', color: '#9ca3af', background: '#f9fafb', borderRadius: '8px' }}>
                                No analysis available. Click &quot;Analyze&quot; in the table first.
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default EmailManagementModal;
