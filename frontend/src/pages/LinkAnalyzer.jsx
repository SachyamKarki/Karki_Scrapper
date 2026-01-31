import React, { useState } from 'react';
import axios from 'axios';
import { Search, Loader2, Globe, Facebook, AlertTriangle, Sparkles } from 'lucide-react';
import { AnalysisReportContent } from '../components/AnalysisModal';

const TONE_OPTIONS = [
    { id: 4, label: 'Best' },
    { id: 1, label: 'Professional' },
    { id: 2, label: 'Friendly' },
    { id: 3, label: 'Direct' },
];

const LinkAnalyzer = () => {
    const [url, setUrl] = useState('');
    const [urlType, setUrlType] = useState('website');
    const [loading, setLoading] = useState(false);
    const [analysis, setAnalysis] = useState(null);
    const [error, setError] = useState(null);
    const [letterBody, setLetterBody] = useState('');
    const [selectedTone, setSelectedTone] = useState(4);
    const [generating, setGenerating] = useState(false);
    const [genError, setGenError] = useState(null);

    const handleAnalyze = async (e) => {
        e.preventDefault();
        const trimmed = url.trim();
        if (!trimmed) {
            setError('Enter a URL');
            return;
        }
        setLoading(true);
        setError(null);
        setAnalysis(null);
        setLetterBody('');
        try {
            const res = await axios.post('/api/analyze_link', {
                url: trimmed,
                url_type: urlType
            }, { timeout: 120000 });
            if (res.data.success) {
                setAnalysis(res.data.analysis);
            } else {
                setError(res.data.error || 'Analysis failed');
            }
        } catch (err) {
            setError(err.response?.data?.error || err.message || 'Analysis failed');
        } finally {
            setLoading(false);
        }
    };

    const handlePrepareSummary = async () => {
        if (!analysis) return;
        setGenerating(true);
        setGenError(null);
        try {
            const res = await axios.post('/api/generate_email_from_analysis', {
                analysis,
                url: url.trim(),
                template_type: selectedTone
            }, { timeout: 120000 });
            if (res.data.success) {
                setLetterBody(res.data.body || '');
            } else {
                setGenError(res.data.error || 'Generation failed');
            }
        } catch (err) {
            setGenError(err.response?.data?.error || err.message || 'Generation failed');
        } finally {
            setGenerating(false);
        }
    };

    return (
        <div style={{ padding: '32px', maxWidth: '1200px', margin: '0 auto' }}>
            <div style={{ marginBottom: '32px' }}>
                <h1 style={{ fontSize: '1.5rem', fontWeight: 600, color: '#111827', margin: '0 0 8px' }}>
                    Link Analyzer
                </h1>
                <p style={{ margin: 0, fontSize: '0.95rem', color: '#6b7280' }}>
                    Paste any website or Facebook URL to get a full analysis report.
                </p>
            </div>

            <form onSubmit={handleAnalyze} style={{
                background: 'white',
                borderRadius: '12px',
                padding: '24px',
                boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
                border: '1px solid #e5e7eb',
                marginBottom: '24px'
            }}>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                    <div>
                        <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: '#374151', marginBottom: '8px' }}>URL</label>
                        <input
                            type="url"
                            value={url}
                            onChange={(e) => setUrl(e.target.value)}
                            placeholder="https://example.com or https://facebook.com/page"
                            style={{
                                width: '100%',
                                padding: '14px 16px',
                                borderRadius: '8px',
                                border: '1px solid #e2e8f0',
                                fontSize: '0.95rem',
                                outline: 'none'
                            }}
                        />
                    </div>
                    <div>
                        <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: '#374151', marginBottom: '8px' }}>Type</label>
                        <div style={{ display: 'flex', gap: '12px' }}>
                            <button
                                type="button"
                                onClick={() => setUrlType('website')}
                                style={{
                                    display: 'flex',
                                    alignItems: 'center',
                                    gap: '8px',
                                    padding: '12px 20px',
                                    borderRadius: '8px',
                                    border: urlType === 'website' ? '2px solid #2563eb' : '1px solid #e2e8f0',
                                    background: urlType === 'website' ? '#eff6ff' : 'white',
                                    color: urlType === 'website' ? '#2563eb' : '#374151',
                                    fontWeight: 500,
                                    cursor: 'pointer'
                                }}
                            >
                                <Globe size={18} /> Website
                            </button>
                            <button
                                type="button"
                                onClick={() => setUrlType('facebook')}
                                style={{
                                    display: 'flex',
                                    alignItems: 'center',
                                    gap: '8px',
                                    padding: '12px 20px',
                                    borderRadius: '8px',
                                    border: urlType === 'facebook' ? '2px solid #1877f2' : '1px solid #e2e8f0',
                                    background: urlType === 'facebook' ? '#eff6ff' : 'white',
                                    color: urlType === 'facebook' ? '#1877f2' : '#374151',
                                    fontWeight: 500,
                                    cursor: 'pointer'
                                }}
                            >
                                <Facebook size={18} /> Facebook
                            </button>
                        </div>
                    </div>
                    <button
                        type="submit"
                        disabled={loading || !url.trim()}
                        style={{
                            display: 'inline-flex',
                            alignItems: 'center',
                            gap: '10px',
                            padding: '14px 24px',
                            borderRadius: '8px',
                            background: '#2563eb',
                            color: 'white',
                            border: 'none',
                            fontWeight: 600,
                            cursor: loading || !url.trim() ? 'not-allowed' : 'pointer',
                            opacity: loading || !url.trim() ? 0.7 : 1,
                            fontSize: '0.95rem'
                        }}
                    >
                        {loading ? <Loader2 className="animate-spin" size={20} /> : <Search size={20} />}
                        {loading ? 'Analyzing...' : 'Analyze Link'}
                    </button>
                </div>
            </form>

            {error && (
                <div style={{
                    padding: '20px',
                    background: '#fef2f2',
                    borderRadius: '12px',
                    border: '1px solid #fecaca',
                    color: '#b91c1c',
                    marginBottom: '24px',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '12px'
                }}>
                    <AlertTriangle size={24} />
                    {error}
                </div>
            )}

            {analysis && (
                <div style={{
                    display: 'flex',
                    gap: 0,
                    background: 'white',
                    borderRadius: '12px',
                    boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
                    border: '1px solid #e5e7eb',
                    overflow: 'hidden',
                    minHeight: '600px'
                }}>
                    {/* Left: Prepare summary + Write letter (like MS Word) */}
                    <div style={{
                        width: '50%',
                        borderRight: '1px solid #e5e7eb',
                        display: 'flex',
                        flexDirection: 'column',
                        background: '#fafafa',
                        padding: '24px',
                        overflowY: 'auto'
                    }}>
                        {/* Prepare cold email — same as other management */}
                        <div style={{
                            padding: '20px',
                            background: 'linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%)',
                            borderRadius: '12px',
                            border: '1px solid #bae6fd',
                            marginBottom: '20px'
                        }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px', fontSize: '1rem', fontWeight: 600, color: '#0369a1' }}>
                                <Sparkles size={22} /> Prepare cold email
                            </div>
                            <p style={{ margin: '0 0 16px', fontSize: '0.9rem', color: '#0c4a6e', lineHeight: 1.5 }}>
                                Creates a summarized cold email including each and every minor detail from the analysis.
                            </p>
                            <div style={{ marginBottom: '16px' }}>
                                <span style={{ display: 'block', fontSize: '0.75rem', fontWeight: 600, color: '#0369a1', marginBottom: '8px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Tone</span>
                                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                                    {TONE_OPTIONS.map((t) => (
                                        <button
                                            key={t.id}
                                            type="button"
                                            onClick={() => setSelectedTone(t.id)}
                                            style={{
                                                padding: '10px 18px',
                                                borderRadius: '8px',
                                                border: selectedTone === t.id ? '2px solid #0284c7' : '1px solid #7dd3fc',
                                                background: selectedTone === t.id ? '#0ea5e9' : 'white',
                                                color: selectedTone === t.id ? 'white' : '#0369a1',
                                                fontSize: '0.9rem',
                                                fontWeight: 500,
                                                cursor: 'pointer'
                                            }}
                                        >
                                            {t.label}{t.id === 4 ? ' ★' : ''}
                                        </button>
                                    ))}
                                </div>
                            </div>
                            <button
                                type="button"
                                onClick={handlePrepareSummary}
                                disabled={generating}
                                style={{
                                    display: 'inline-flex',
                                    alignItems: 'center',
                                    gap: '10px',
                                    padding: '12px 20px',
                                    borderRadius: '10px',
                                    background: '#0284c7',
                                    color: 'white',
                                    border: 'none',
                                    fontWeight: 600,
                                    cursor: generating ? 'not-allowed' : 'pointer',
                                    opacity: generating ? 0.7 : 1,
                                    fontSize: '0.9rem'
                                }}
                            >
                                {generating ? <Loader2 className="animate-spin" size={18} /> : <Sparkles size={18} />}
                                {generating ? 'Preparing...' : 'Prepare summarized mail'}
                            </button>
                            {genError && (
                                <div style={{ marginTop: '12px', padding: '10px 14px', background: '#fef2f2', color: '#b91c1c', borderRadius: '8px', fontSize: '0.85rem' }}>
                                    {genError}
                                </div>
                            )}
                        </div>
                        <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 600, color: '#6b7280', marginBottom: '8px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                            Write letter (like MS Word)
                        </label>
                        <textarea
                            value={letterBody}
                            onChange={(e) => setLetterBody(e.target.value)}
                            placeholder="Type your letter here. Use the analysis on the right for reference."
                            style={{
                                flex: 1,
                                minHeight: '500px',
                                padding: '24px',
                                borderRadius: '8px',
                                border: '1px solid #d1d5db',
                                fontSize: '0.95rem',
                                outline: 'none',
                                background: '#ffffff',
                                resize: 'none',
                                fontFamily: 'Georgia, "Times New Roman", serif',
                                lineHeight: 1.7,
                                boxShadow: 'inset 0 1px 2px rgba(0,0,0,0.05)'
                            }}
                        />
                        <button
                            onClick={() => {
                                navigator.clipboard?.writeText(letterBody);
                                alert('Copied to clipboard');
                            }}
                            style={{
                                marginTop: '12px',
                                alignSelf: 'flex-start',
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
                    {/* Right: Analysis report */}
                    <div style={{
                        width: '50%',
                        display: 'flex',
                        flexDirection: 'column',
                        overflow: 'hidden'
                    }}>
                        <div style={{
                            padding: '20px 24px',
                            borderBottom: '1px solid #e5e7eb',
                            background: '#f9fafb',
                            flexShrink: 0
                        }}>
                            <h2 style={{ fontSize: '1.1rem', fontWeight: 600, color: '#111827', margin: 0 }}>
                                {analysis.url_type === 'facebook' ? 'Facebook Page Analysis Report' : 'Website Analysis Report'}
                            </h2>
                            <p style={{ margin: '4px 0 0', fontSize: '0.9rem', color: '#6b7280' }}>
                                {analysis.url || url}
                            </p>
                        </div>
                        <div style={{ flex: 1, overflowY: 'auto', padding: '24px' }}>
                            <AnalysisReportContent analysis={analysis} />
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default LinkAnalyzer;
