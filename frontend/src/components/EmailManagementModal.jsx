import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { X, Loader2, Mail, Plus, Sparkles } from 'lucide-react';
import { AnalysisReportContent } from './AnalysisModal';

const safeArray = (val) => Array.isArray(val) ? val : [];
const safeString = (val) => (val != null && typeof val === 'string') ? val : (typeof val === 'number' ? String(val) : '');

const TONE_OPTIONS = [
    { id: 4, label: 'Best', desc: 'Optimal — every finding, makes them feel they need help' },
    { id: 1, label: 'Professional', desc: 'Formal, business value' },
    { id: 2, label: 'Friendly', desc: 'Warm, conversational' },
    { id: 3, label: 'Direct', desc: 'Short, clear CTA' },
];

const EmailManagementModal = ({ isOpen, onClose, place }) => {
    const [body, setBody] = useState('');
    const [analysis, setAnalysis] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [generating, setGenerating] = useState(false);
    const [selectedTone, setSelectedTone] = useState(4);
    const [genError, setGenError] = useState(null);

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
            setBody('');
            setGenError(null);
            fetchAnalysis();
        } else {
            setAnalysis(null);
            setError(null);
            setGenError(null);
        }
    }, [isOpen, place, fetchAnalysis]);

    const insertAngle = (text) => {
        if (text) setBody((prev) => prev + (prev ? '\n\n' : '') + text);
    };

    const generateEmail = async () => {
        if (!place?._id) return;
        setGenerating(true);
        setGenError(null);
        try {
            const res = await axios.post('/api/generate_email', {
                item_id: place._id,
                template_type: selectedTone,
            }, { timeout: 120000 });
            if (res.data?.success) {
                setBody(res.data.body || '');
            } else {
                setGenError(res.data?.error || 'Generation failed');
            }
        } catch (err) {
            setGenError(err.response?.data?.error || err.message || 'Failed to generate email');
        } finally {
            setGenerating(false);
        }
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
            width: '100vw',
            height: '100vh',
            backgroundColor: 'white',
            display: 'flex',
            flexDirection: 'column',
            zIndex: 1000,
            overflow: 'hidden'
        }}>
            <div style={{
                flex: 1,
                display: 'flex',
                flexDirection: 'column',
                overflow: 'hidden',
                minHeight: 0
            }}>
                {/* Header */}
                <div style={{
                    padding: '20px 24px',
                    borderBottom: '1px solid #e5e7eb',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    background: '#f9fafb',
                    flexShrink: 0,
                }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
                        <div style={{ padding: '10px', background: '#eff6ff', borderRadius: '10px', color: '#2563eb' }}>
                            <Mail size={24} />
                        </div>
                        <div>
                            <h2 style={{ fontSize: '1.125rem', fontWeight: 600, color: '#111827', margin: 0 }}>
                                Prepare Cold Email
                            </h2>
                            <p style={{ margin: '4px 0 0', fontSize: '0.85rem', color: '#6b7280' }}>
                                {place?.name || 'Compose email'} — Edit on left, analysis result on right
                            </p>
                        </div>
                    </div>
                    <button onClick={onClose} style={{ border: 'none', background: 'transparent', cursor: 'pointer', color: '#6b7280', padding: '8px' }}>
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
                        background: '#fafafa',
                        overflowY: 'auto',
                    }}>
                        <div style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '20px' }}>
                            {/* Prepare cold email — 3 tone options, comprehensive */}
                            <div style={{
                                padding: '24px',
                                background: 'linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%)',
                                borderRadius: '12px',
                                border: '1px solid #bae6fd',
                            }}>
                                <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px', fontSize: '1rem', fontWeight: 600, color: '#0369a1' }}>
                                    <Sparkles size={22} /> Prepare cold email
                                </div>
                                <p style={{ margin: '0 0 20px', fontSize: '0.9rem', color: '#0c4a6e', lineHeight: 1.5 }}>
                                    Creates a summarized cold email including each and every minor detail from the analysis.
                                </p>
                                <div style={{ marginBottom: '20px' }}>
                                    <span style={{ display: 'block', fontSize: '0.75rem', fontWeight: 600, color: '#0369a1', marginBottom: '10px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Tone</span>
                                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '10px' }}>
                                        {TONE_OPTIONS.map((t) => (
                                            <button
                                                key={t.id}
                                                onClick={() => setSelectedTone(t.id)}
                                                style={{
                                                    padding: '12px 20px',
                                                    borderRadius: '10px',
                                                    border: selectedTone === t.id ? '2px solid #0284c7' : '1px solid #7dd3fc',
                                                    background: selectedTone === t.id ? '#0ea5e9' : 'white',
                                                    color: selectedTone === t.id ? 'white' : '#0369a1',
                                                    fontSize: '0.9rem',
                                                    fontWeight: 500,
                                                    cursor: 'pointer',
                                                    transition: 'all 0.2s',
                                                }}
                                            >
                                                {t.label}{t.id === 4 ? ' ★' : ''}
                                            </button>
                                        ))}
                                    </div>
                                </div>
                                <button
                                    onClick={generateEmail}
                                    disabled={generating || !analysis}
                                    style={{
                                        display: 'inline-flex',
                                        alignItems: 'center',
                                        gap: '10px',
                                        padding: '14px 24px',
                                        borderRadius: '10px',
                                        background: '#0284c7',
                                        color: 'white',
                                        border: 'none',
                                        fontWeight: 600,
                                        cursor: generating || !analysis ? 'not-allowed' : 'pointer',
                                        opacity: generating || !analysis ? 0.7 : 1,
                                        fontSize: '0.95rem',
                                    }}
                                >
                                    {generating ? <Loader2 className="animate-spin" size={20} /> : <Sparkles size={20} />}
                                    {generating ? 'Preparing...' : 'Prepare summarized mail'}
                                </button>
                                {genError && (
                                    <div style={{ marginTop: '14px', padding: '12px 16px', background: '#fef2f2', color: '#b91c1c', borderRadius: '8px', fontSize: '0.85rem' }}>
                                        {genError}
                                    </div>
                                )}
                            </div>

                            <div>
                                <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 600, color: '#6b7280', marginBottom: '8px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Edit cold email (like MS Word)</label>
                                <textarea
                                    value={body}
                                    onChange={(e) => setBody(e.target.value)}
                                    placeholder="Type your cold email here. Use Generate Email or Insert buttons below to add content from the analysis on the right."
                                    style={{
                                        width: '100%',
                                        minHeight: '400px',
                                        padding: '24px',
                                        borderRadius: '8px',
                                        border: '1px solid #d1d5db',
                                        fontSize: '0.95rem',
                                        outline: 'none',
                                        background: '#ffffff',
                                        resize: 'none',
                                        fontFamily: 'Georgia, "Times New Roman", serif',
                                        lineHeight: 1.7,
                                        boxShadow: 'inset 0 1px 2px rgba(0,0,0,0.05)',
                                    }}
                                />
                                {coldAngles.length > 0 && (
                                    <div style={{ marginTop: '12px' }}>
                                        <span style={{ display: 'block', fontSize: '0.75rem', fontWeight: 600, color: '#6b7280', marginBottom: '8px' }}>Insert cold email angle</span>
                                        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                                            {coldAngles.slice(0, 5).map((angle, i) => (
                                                <button
                                                    key={i}
                                                    onClick={() => insertAngle(angle)}
                                                    style={{
                                                        display: 'inline-flex',
                                                        alignItems: 'center',
                                                        gap: '6px',
                                                        padding: '8px 14px',
                                                        borderRadius: '8px',
                                                        border: '1px solid #e2e8f0',
                                                        background: 'white',
                                                        fontSize: '0.85rem',
                                                        color: '#374151',
                                                        cursor: 'pointer',
                                                    }}
                                                >
                                                    <Plus size={14} /> Add #{i + 1}
                                                </button>
                                            ))}
                                        </div>
                                    </div>
                                )}
                            </div>
                            <div style={{ marginTop: '12px' }}>
                                <button
                                    onClick={() => {
                                        navigator.clipboard?.writeText(body);
                                        alert('Copied to clipboard');
                                    }}
                                    style={{
                                        display: 'inline-flex',
                                        alignItems: 'center',
                                        gap: '8px',
                                        padding: '10px 18px',
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
                        background: 'white',
                    }}>
                        <div style={{
                            fontSize: '0.75rem',
                            fontWeight: 600,
                            color: '#6b7280',
                            marginBottom: '20px',
                            paddingBottom: '12px',
                            borderBottom: '1px solid #e5e7eb',
                            textTransform: 'uppercase',
                            letterSpacing: '0.05em',
                        }}>
                            Analysis Result (right panel)
                        </div>
                        {loading ? (
                            <div style={{ display: 'flex', justifyContent: 'center', padding: '60px' }}>
                                <Loader2 className="animate-spin" size={40} color="#2563eb" />
                            </div>
                        ) : error ? (
                            <div style={{ padding: '24px', textAlign: 'center', color: '#6b7280', background: '#f9fafb', borderRadius: '12px', border: '1px solid #e5e7eb' }}>
                                <p style={{ margin: 0 }}>{error}</p>
                                <p style={{ fontSize: '0.85rem', marginTop: '12px', marginBottom: 0 }}>Run analysis from the table to see insights here.</p>
                            </div>
                        ) : analysis?.status === 'failed' ? (
                            <div style={{ padding: '24px', textAlign: 'center', color: '#92400e', background: '#fef3c7', borderRadius: '12px', border: '1px solid #fcd34d' }}>
                                <p style={{ fontWeight: 500, margin: 0 }}>Analysis failed</p>
                                <p style={{ fontSize: '0.85rem', marginTop: '12px', marginBottom: 0 }}>{analysis.error || 'Could not analyze this website.'}</p>
                            </div>
                        ) : analysis ? (
                            <AnalysisReportContent analysis={analysis} />
                        ) : (
                            <div style={{ padding: '24px', textAlign: 'center', color: '#9ca3af', background: '#f9fafb', borderRadius: '12px', border: '1px solid #e5e7eb' }}>
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
