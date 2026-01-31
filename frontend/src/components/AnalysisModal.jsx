import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { X, Loader2, AlertTriangle, Bug, Zap, TrendingUp, Lightbulb, Search, Flag, Cpu, Briefcase, ShoppingCart, Globe, Mail, FileText, Shield } from 'lucide-react';
import ErrorBoundary from './ErrorBoundary';

// Safe helpers to prevent crashes from malformed data
const safeArray = (val) => Array.isArray(val) ? val : [];
const safeString = (val) => (val != null && typeof val === 'string') ? val : (typeof val === 'number' ? String(val) : '');
const safeObject = (val) => (val != null && typeof val === 'object' && !Array.isArray(val)) ? val : {};

const AnalysisModal = ({ isOpen, onClose, itemId }) => {
    const [loading, setLoading] = useState(true);
    const [analysis, setAnalysis] = useState(null);
    const [businessName, setBusinessName] = useState('');
    const [website, setWebsite] = useState('');
    const [error, setError] = useState(null);

    const fetchAnalysis = useCallback(async () => {
        setLoading(true);
        setError(null);
        try {
            const response = await axios.get(`/api/get_analysis/${itemId}`);
            if (response.data.success) {
                setAnalysis(response.data.analysis);
                setBusinessName(response.data.business_name || '');
                setWebsite(response.data.website || '');
            } else {
                setError(response.data.error || 'No analysis data');
            }
        } catch (err) {
            setError('Failed to load analysis');
        } finally {
            setLoading(false);
        }
    }, [itemId]);

    useEffect(() => {
        if (isOpen && itemId) {
            fetchAnalysis();
        } else {
            setAnalysis(null);
            setError(null);
        }
    }, [isOpen, itemId, fetchAnalysis]);

    if (!isOpen) return null;

    const isGeminiFormat = analysis && (analysis.source === 'gemini' || (analysis.keyword_analysis && analysis.overall_analysis) || (analysis.keywordAnalysis && analysis.overallAnalysis));

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
                width: '95%',
                maxWidth: '900px',
                maxHeight: '90vh',
                overflow: 'hidden',
                display: 'flex',
                flexDirection: 'column',
                boxShadow: '0 20px 25px -5px rgba(0,0,0,0.1)'
            }}>
                {/* Header */}
                <div style={{
                    padding: '20px 24px',
                    borderBottom: '1px solid #e5e7eb',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    background: '#f9fafb'
                }}>
                    <div>
                        <h2 style={{ fontSize: '1.25rem', fontWeight: 600, color: '#111827', margin: 0 }}>
                            {analysis?.url_type === 'facebook' ? 'Facebook Page Analysis Report' :
                             analysis?.url_type === 'instagram' ? 'Instagram Analysis Report' :
                             'Website Analysis Report'}
                        </h2>
                        {businessName && (
                            <p style={{ margin: '4px 0 0', fontSize: '0.9rem', color: '#6b7280' }}>
                                {businessName} {(analysis?.url || website) && `• ${analysis?.url || website}`}
                            </p>
                        )}
                    </div>
                    <button onClick={onClose} style={{ border: 'none', background: 'transparent', cursor: 'pointer', color: '#6b7280', padding: '4px' }}>
                        <X size={24} />
                    </button>
                </div>

                {/* Content */}
                <div style={{ flex: 1, overflowY: 'auto', padding: '24px' }}>
                    {loading ? (
                        <div style={{ display: 'flex', justifyContent: 'center', padding: '60px' }}>
                            <Loader2 className="animate-spin" size={40} color="#2563eb" />
                        </div>
                    ) : error ? (
                        <div style={{ padding: '40px', textAlign: 'center', color: '#dc2626' }}>
                            <AlertTriangle size={48} style={{ marginBottom: '16px' }} />
                            <p>{error}</p>
                        </div>
                    ) : analysis?.status === 'failed' ? (
                        <div style={{ padding: '40px', textAlign: 'center', color: '#374151' }}>
                            <AlertTriangle size={48} style={{ marginBottom: '16px', color: '#f59e0b' }} />
                            <h3 style={{ margin: '0 0 12px', fontSize: '1.1rem', color: '#111827' }}>Analysis Failed</h3>
                            <p style={{ margin: 0, color: '#6b7280', lineHeight: 1.6 }}>{analysis.error || 'The website could not be analyzed.'}</p>
                            <div style={{ marginTop: '20px', padding: '16px', background: '#fef3c7', borderRadius: '8px', textAlign: 'left', fontSize: '0.9rem', color: '#92400e' }}>
                                <strong>Why it failed:</strong>
                                <ul style={{ margin: '8px 0 0 20px', padding: 0 }}>
                                    <li><strong>Read/SSL timeout</strong> – The website server is slow or unresponsive (common with .np domains)</li>
                                    <li><strong>Blocked</strong> – The site may block automated requests</li>
                                    <li><strong>Down</strong> – The website may be temporarily offline</li>
                                </ul>
                                <p style={{ margin: '12px 0 0', fontSize: '0.85rem' }}>Try again later or use a different business with a faster website.</p>
                            </div>
                        </div>
                    ) : analysis ? (
                        <ErrorBoundary>
                            {isGeminiFormat ? (
                                <GeminiReport analysis={analysis} />
                            ) : (
                                <LegacyReport analysis={analysis} />
                            )}
                        </ErrorBoundary>
                    ) : (
                        <div style={{ padding: '40px', textAlign: 'center', color: '#6b7280' }}>No analysis data to display.</div>
                    )}
                </div>
            </div>
        </div>
    );
};

// Support both snake_case and camelCase from API
const getAnalysisData = (analysis) => ({
    businessSummary: safeObject(analysis.business_content_summary || analysis.businessContentSummary),
    overall: safeObject(analysis.overall_analysis || analysis.overallAnalysis),
    redFlags: safeArray(analysis.website_quality_red_flags || analysis.websiteQualityRedFlags),
    techStack: safeArray(analysis.tech_stack_signals || analysis.techStackSignals),
    growthIndicators: safeArray(analysis.business_growth_indicators || analysis.businessGrowthIndicators),
    conversionProblems: safeArray(analysis.conversion_problems || analysis.conversionProblems),
    seoIssues: safeArray(analysis.seo_visibility_issues || analysis.seoVisibilityIssues),
    bugs: safeArray(analysis.bugs_and_glitches || analysis.bugsAndGlitches),
    errors: safeArray(analysis.errors_and_loading_issues || analysis.errorsAndLoadingIssues),
    developerIssues: safeArray(analysis.developer_technical_issues || analysis.developerTechnicalIssues),
    recs: safeArray(analysis.improvement_recommendations || analysis.improvementRecommendations),
    keywords: safeArray(analysis.keyword_analysis || analysis.keywordAnalysis),
    featureSuggestions: safeArray(analysis.feature_and_growth_suggestions || analysis.featureAndGrowthSuggestions),
});

const ColdEmailCard = ({ item, labelKey }) => {
    if (!item || typeof item !== 'object') return null;
    const label = safeString(item[labelKey] || item.flag || item.signal || item.indicator || item.problem || item.issue);
    const present = item.present === true || item.present === 'true';
    const angle = safeString(item.cold_email_angle || item.coldEmailAngle);
    if (!label) return null;
    return (
        <div style={cardStyle}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: angle ? '8px' : 0 }}>
                <span style={{
                    padding: '2px 8px',
                    borderRadius: '4px',
                    fontSize: '0.7rem',
                    background: present ? '#dc2626' : '#059669',
                    color: 'white',
                    textTransform: 'uppercase'
                }}>{present ? 'Present' : 'OK'}</span>
                <strong>{label}</strong>
            </div>
            {angle && (
                <div style={{ fontSize: '0.9rem', color: '#4b5563', display: 'flex', alignItems: 'flex-start', gap: '8px' }}>
                    <Mail size={14} style={{ flexShrink: 0, marginTop: '2px', color: '#6b7280' }} />
                    <em>{angle}</em>
                </div>
            )}
        </div>
    );
};

const GeminiReport = ({ analysis, compact = false }) => {
    if (!analysis || typeof analysis !== 'object') return null;
    const { businessSummary, overall, redFlags, techStack, growthIndicators, conversionProblems, seoIssues, bugs, errors, developerIssues, recs, keywords, featureSuggestions } = getAnalysisData(analysis);
    const strengths = safeArray(overall.strengths);
    const criticalIssues = safeArray(overall.critical_issues || overall.criticalIssues);

    const hasBizSummary = businessSummary && (
        businessSummary.what_they_do || businessSummary.whatTheyDo ||
        (businessSummary.key_products_services || businessSummary.keyProductsServices || []).length > 0 ||
        businessSummary.target_audience || businessSummary.targetAudience ||
        businessSummary.value_proposition || businessSummary.valueProposition ||
        (businessSummary.crucial_details || businessSummary.crucialDetails || []).length > 0
    );

    const hasAnyContent = hasBizSummary || (overall && overall.summary) || strengths.length > 0 || criticalIssues.length > 0 ||
        redFlags.length > 0 || techStack.length > 0 || growthIndicators.length > 0 || conversionProblems.length > 0 || seoIssues.length > 0 ||
        bugs.length > 0 || errors.length > 0 || developerIssues.length > 0 || recs.length > 0 || keywords.length > 0 || featureSuggestions.length > 0;

    if (!hasAnyContent) {
        return (
            <div style={{ padding: '40px', textAlign: 'center', color: '#374151' }}>
                <p style={{ margin: 0, fontSize: '1rem' }}>Analysis completed but no structured data was returned.</p>
                <p style={{ fontSize: '0.9rem', marginTop: '12px', color: '#6b7280' }}>Try running the analysis again or check the website URL.</p>
            </div>
        );
    }

    const bs = businessSummary || {};
    const whatTheyDo = safeString(bs.what_they_do || bs.whatTheyDo);
    const keyProducts = safeArray(bs.key_products_services || bs.keyProductsServices);
    const targetAudience = safeString(bs.target_audience || bs.targetAudience);
    const valueProp = safeString(bs.value_proposition || bs.valueProposition);
    const keyContent = safeArray(bs.key_content_on_site || bs.keyContentOnSite);
    const locationMarket = safeString(bs.location_market || bs.locationMarket);
    const crucialDetails = safeArray(bs.crucial_details || bs.crucialDetails);

    return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: compact ? '16px' : '24px', minWidth: 0, maxWidth: '100%' }}>
        {/* Business Content Summary - Quick overview for consultant */}
        {hasBizSummary && (
            <Section title="Business Summary — Quick Overview" icon={<FileText size={20} />} compact={compact}>
                <div style={{ padding: '16px', background: '#f8fafc', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
                    {whatTheyDo && (
                        <div style={{ marginBottom: '14px' }}>
                            <strong style={{ fontSize: '0.8rem', color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.05em' }}>What they do</strong>
                            <p style={{ margin: '6px 0 0', lineHeight: 1.6, color: '#334155', fontSize: '0.95rem' }}>{whatTheyDo}</p>
                        </div>
                    )}
                    {keyProducts.length > 0 && (
                        <div style={{ marginBottom: '14px' }}>
                            <strong style={{ fontSize: '0.8rem', color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Key products & services</strong>
                            <ul style={{ margin: '6px 0 0', paddingLeft: '20px', lineHeight: 1.6, color: '#334155', fontSize: '0.9rem' }}>
                                {keyProducts.map((p, i) => <li key={i}>{safeString(p)}</li>)}
                            </ul>
                        </div>
                    )}
                    {targetAudience && (
                        <div style={{ marginBottom: '14px' }}>
                            <strong style={{ fontSize: '0.8rem', color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Target audience</strong>
                            <p style={{ margin: '6px 0 0', lineHeight: 1.6, color: '#334155', fontSize: '0.9rem' }}>{targetAudience}</p>
                        </div>
                    )}
                    {valueProp && (
                        <div style={{ marginBottom: '14px' }}>
                            <strong style={{ fontSize: '0.8rem', color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Value proposition</strong>
                            <p style={{ margin: '6px 0 0', lineHeight: 1.6, color: '#334155', fontSize: '0.9rem' }}>{valueProp}</p>
                        </div>
                    )}
                    {keyContent.length > 0 && (
                        <div style={{ marginBottom: '14px' }}>
                            <strong style={{ fontSize: '0.8rem', color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Key content on site</strong>
                            <ul style={{ margin: '6px 0 0', paddingLeft: '20px', lineHeight: 1.6, color: '#334155', fontSize: '0.9rem' }}>
                                {keyContent.map((c, i) => <li key={i}>{safeString(c)}</li>)}
                            </ul>
                        </div>
                    )}
                    {locationMarket && (
                        <div style={{ marginBottom: '14px' }}>
                            <strong style={{ fontSize: '0.8rem', color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Location / market</strong>
                            <p style={{ margin: '6px 0 0', lineHeight: 1.6, color: '#334155', fontSize: '0.9rem' }}>{locationMarket}</p>
                        </div>
                    )}
                    {crucialDetails.length > 0 && (
                        <div>
                            <strong style={{ fontSize: '0.8rem', color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Crucial details</strong>
                            <ul style={{ margin: '6px 0 0', paddingLeft: '20px', lineHeight: 1.6, color: '#334155', fontSize: '0.9rem' }}>
                                {crucialDetails.map((d, i) => <li key={i}>{safeString(d)}</li>)}
                            </ul>
                        </div>
                    )}
                </div>
            </Section>
        )}

        {/* Overall Analysis - always show when we have any content */}
        <Section title="Overall Assessment" icon={<Zap size={20} />} compact={compact}>
                <p style={{ margin: 0, lineHeight: 1.6, color: '#374151' }}>{safeString(overall.summary) || `Analysis of ${analysis.url || 'website'} completed.`}</p>
                {strengths.length > 0 && (
                    <div style={{ marginTop: '12px' }}>
                        <strong style={{ fontSize: '0.85rem', color: '#059669' }}>Strengths:</strong>
                        <ul style={{ margin: '4px 0 0', paddingLeft: '20px' }}>
                            {strengths.map((s, i) => (
                                <li key={i} style={{ marginBottom: '4px' }}>{safeString(s)}</li>
                            ))}
                        </ul>
                    </div>
                )}
                {criticalIssues.length > 0 && (
                    <div style={{ marginTop: '12px' }}>
                        <strong style={{ fontSize: '0.85rem', color: '#dc2626' }}>Critical Issues:</strong>
                        <ul style={{ margin: '4px 0 0', paddingLeft: '20px' }}>
                            {criticalIssues.map((s, i) => (
                                <li key={i} style={{ marginBottom: '4px' }}>{safeString(s)}</li>
                            ))}
                        </ul>
                    </div>
                )}
            </Section>

        {/* Website Quality Red Flags */}
        {redFlags.length > 0 && (
            <Section title="Website Quality Red Flags (Big Opportunity Signals)" icon={<Flag size={20} />} compact={compact}>
                <p style={{ margin: '0 0 12px', fontSize: '0.9rem', color: '#6b7280' }}>
                    These scream &quot;we need help&quot; — cold email angles included.
                </p>
                {redFlags.map((item, i) => (
                    <ColdEmailCard key={i} item={item} labelKey="flag" />
                ))}
            </Section>
        )}

        {/* Tech Stack Signals */}
        {techStack.length > 0 && (
            <Section title="Tech Stack Signals" icon={<Cpu size={20} />} compact={compact}>
                <p style={{ margin: '0 0 12px', fontSize: '0.9rem', color: '#6b7280' }}>
                    How mature their tech stack is — Wappalyzer/BuiltWith style insights.
                </p>
                {techStack.map((item, i) => (
                    <ColdEmailCard key={i} item={item} labelKey="signal" />
                ))}
            </Section>
        )}

        {/* Business Growth Indicators */}
        {growthIndicators.length > 0 && (
            <Section title="Business Growth Indicators" icon={<Briefcase size={20} />} compact={compact}>
                <p style={{ margin: '0 0 12px', fontSize: '0.9rem', color: '#6b7280' }}>
                    Perfect prospects are growing but messy — they have budget.
                </p>
                {growthIndicators.map((item, i) => (
                    <ColdEmailCard key={i} item={item} labelKey="indicator" />
                ))}
            </Section>
        )}

        {/* Conversion Problems */}
        {conversionProblems.length > 0 && (
            <Section title="Conversion Problems" icon={<ShoppingCart size={20} />} compact={compact}>
                <p style={{ margin: '0 0 12px', fontSize: '0.9rem', color: '#6b7280' }}>
                    Easy wins — small UX changes typically increase conversions 20–30%.
                </p>
                {conversionProblems.map((item, i) => (
                    <ColdEmailCard key={i} item={item} labelKey="problem" />
                ))}
            </Section>
        )}

        {/* SEO & Visibility Issues */}
        {seoIssues.length > 0 && (
            <Section title="SEO & Visibility Issues" icon={<Globe size={20} />} compact={compact}>
                <p style={{ margin: '0 0 12px', fontSize: '0.9rem', color: '#6b7280' }}>
                    Quick checks — meta titles, schema, local SEO, branded searches.
                </p>
                {seoIssues.map((item, i) => (
                    <ColdEmailCard key={i} item={item} labelKey="issue" />
                ))}
            </Section>
        )}

        {/* Bugs & Glitches */}
        {bugs.length > 0 && (
            <Section title="Bugs & Glitches" icon={<Bug size={20} />} compact={compact}>
                {bugs.map((item, i) => (
                    <IssueCard key={i} item={typeof item === 'object' ? item : { title: String(item), description: '', severity: 'medium' }} showAngle />
                ))}
            </Section>
        )}

        {/* Errors & Loading Issues */}
        {errors.length > 0 && (
            <Section title="Errors & Loading Issues" icon={<AlertTriangle size={20} />} compact={compact}>
                {errors.map((item, i) => {
                    const it = typeof item === 'object' ? item : { issue: String(item), likely_cause: '', cold_email_angle: '' };
                    return (
                    <div key={i} style={cardStyle}>
                        <p style={{ margin: 0, fontWeight: 500 }}>{safeString(it.issue)}</p>
                        {it.likely_cause && (
                            <p style={{ margin: '8px 0 0', fontSize: '0.9rem', color: '#6b7280' }}>
                                <em>Likely cause: {safeString(it.likely_cause)}</em>
                            </p>
                        )}
                        {(it.cold_email_angle || it.coldEmailAngle) && (
                            <div style={{ marginTop: '8px', fontSize: '0.9rem', color: '#4b5563', display: 'flex', alignItems: 'flex-start', gap: '8px' }}>
                                <Mail size={14} style={{ flexShrink: 0, marginTop: '2px', color: '#6b7280' }} />
                                <em>{safeString(it.cold_email_angle || it.coldEmailAngle)}</em>
                            </div>
                        )}
                    </div>
                );})}
            </Section>
        )}

        {/* Developer Technical Issues — vulnerabilities, security, functionality, glitches */}
        {developerIssues.length > 0 && (
            <Section title="Developer Technical Issues (Vulnerabilities, Security, Functions, Glitches)" icon={<Shield size={20} />} compact={compact}>
                <p style={{ margin: '0 0 12px', fontSize: '0.9rem', color: '#6b7280' }}>
                    Developer-focused findings: site vulnerabilities, security concerns, functions not working, and UI glitches.
                </p>
                {developerIssues.map((item, i) => (
                    <DeveloperIssueCard key={i} item={typeof item === 'object' ? item : { category: 'glitch', title: String(item), description: '', severity: 'medium' }} />
                ))}
            </Section>
        )}

        {/* Improvement Recommendations */}
        {recs.length > 0 && (
            <Section title="Improvement Recommendations" icon={<Lightbulb size={20} />} compact={compact}>
                {recs.map((item, i) => {
                    const it = typeof item === 'object' ? item : { category: 'General', recommendation: String(item), priority: 'medium' };
                    return (
                    <div key={i} style={cardStyle}>
                        <span style={{
                            fontSize: '0.75rem',
                            fontWeight: 600,
                            color: '#6b7280',
                            textTransform: 'uppercase',
                            marginRight: '8px'
                        }}>{safeString(it.category)}</span>
                        <span style={{
                            padding: '2px 8px',
                            borderRadius: '4px',
                            fontSize: '0.7rem',
                            background: priorityColor(it.priority),
                            color: 'white'
                        }}>{safeString(it.priority)}</span>
                        <p style={{ margin: '8px 0 0' }}>{safeString(it.recommendation)}</p>
                    </div>
                );})}
            </Section>
        )}

        {/* Keyword Analysis */}
        {featureSuggestions.length > 0 && (
            <Section title="Feature & Growth Suggestions (AI Agent, Features, Practical Growth)" icon={<TrendingUp size={20} />} compact={compact}>
                <p style={{ margin: '0 0 12px', fontSize: '0.9rem', color: '#6b7280' }}>
                    Tailored to this company — AI agents, features, and how to practically grow their business.
                </p>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                    {featureSuggestions.map((item, i) => {
                        const it = typeof item === 'object' ? item : {};
                        const type = safeString(it.type || '').toUpperCase();
                        const suggestion = safeString(it.suggestion);
                        const impact = safeString(it.practical_impact || it.practicalImpact);
                        const angle = safeString(it.cold_email_angle || it.coldEmailAngle);
                        if (!suggestion) return null;
                        return (
                            <div key={i} style={{ ...cardStyle, borderLeft: '4px solid #8b5cf6' }}>
                                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: (impact || angle) ? '8px' : 0 }}>
                                    <span style={{ padding: '2px 8px', borderRadius: '4px', fontSize: '0.7rem', background: '#8b5cf6', color: 'white', textTransform: 'uppercase' }}>
                                        {type || 'Feature'}
                                    </span>
                                    <strong>{suggestion}</strong>
                                </div>
                                {impact && <p style={{ margin: '0 0 6px', fontSize: '0.9rem', color: '#059669' }}>Practical impact: {impact}</p>}
                                {angle && (
                                    <div style={{ fontSize: '0.9rem', color: '#4b5563', display: 'flex', alignItems: 'flex-start', gap: '8px' }}>
                                        <Mail size={14} style={{ flexShrink: 0, marginTop: '2px', color: '#6b7280' }} />
                                        <em>{angle}</em>
                                    </div>
                                )}
                            </div>
                        );
                    })}
                </div>
            </Section>
        )}

        {keywords.length > 0 && (
            <Section title="Keyword Analysis & Exact Google Rankings" icon={<Search size={20} />} compact={compact}>
                {compact ? (
                    /* Compact card layout for Email Management */
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                        {keywords.map((kw, i) => {
                            const k = typeof kw === 'object' ? kw : {};
                            const score = k.relevance_score;
                            const scoreStr = (typeof score === 'number' && !isNaN(score)) ? score : (typeof score === 'string' && /^\d+$/.test(score) ? score : '-');
                            const rank = k.display_rank ?? k.google_rank ?? k.estimated_current_rank;
                            const isExact = typeof k.google_rank === 'number';
                            const rankStr = String(rank || '').toLowerCase();
                            const addEst = !isExact && rankStr && rankStr !== 'unknown';
                            const rankDisplay = rank != null && typeof rank === 'number' ? `#${rank}` : (rank != null ? `${String(rank)}${addEst ? ' (est.)' : ''}` : '—');
                            const tips = safeString(k.improvement_tips);
                            return (
                                <div key={i} style={{
                                    padding: '8px 12px',
                                    borderRadius: '6px',
                                    background: '#f8fafc',
                                    border: '1px solid #e2e8f0',
                                    fontSize: '0.75rem'
                                }}>
                                    <div style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'center', gap: '8px', marginBottom: tips ? '4px' : 0 }}>
                                        <strong style={{ color: '#1e293b', fontSize: '0.8rem' }}>{safeString(k.keyword) || '-'}</strong>
                                        <span style={{ color: '#64748b', fontWeight: 500 }}>{rankDisplay}</span>
                                        <span style={{ color: '#94a3b8' }}>{scoreStr}/10</span>
                                        <span style={{
                                            padding: '1px 6px',
                                            borderRadius: '4px',
                                            fontSize: '0.65rem',
                                            background: strengthColor(k.current_content_strength),
                                            color: 'white'
                                        }}>{safeString(k.current_content_strength) || '-'}</span>
                                    </div>
                                    {tips && (
                                        <div style={{ color: '#64748b', fontSize: '0.7rem', lineHeight: 1.4, overflow: 'hidden', textOverflow: 'ellipsis', display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical' }}>
                                            {tips}
                                        </div>
                                    )}
                                </div>
                            );
                        })}
                    </div>
                ) : (
                    <>
                        <p style={{ margin: '0 0 16px', fontSize: '0.9rem', color: '#6b7280' }}>
                            Relevance score (1-10), content strength, ranking potential, and <strong>Google rank</strong> — exact position (Serper API) when available, or Gemini-estimated range (est.) otherwise.
                        </p>
                        <div style={{ overflowX: 'auto', WebkitOverflowScrolling: 'touch', maxWidth: '100%' }}>
                            <table style={{ width: '100%', minWidth: '500px', borderCollapse: 'collapse', fontSize: '0.9rem', tableLayout: 'auto' }}>
                                <thead>
                                    <tr style={{ borderBottom: '2px solid #e5e7eb' }}>
                                        <th style={thStyle}>Keyword</th>
                                        <th style={thStyle}>Google Rank</th>
                                        <th style={thStyle}>Relevance</th>
                                        <th style={thStyle}>Content</th>
                                        <th style={thStyle}>Ranking Potential</th>
                                        <th style={thStyle}>Improvement Tips</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {keywords.map((kw, i) => {
                                        const k = typeof kw === 'object' ? kw : {};
                                        const score = k.relevance_score;
                                        const scoreStr = (typeof score === 'number' && !isNaN(score)) ? score : (typeof score === 'string' && /^\d+$/.test(score) ? score : '-');
                                        const rank = k.display_rank ?? k.google_rank ?? k.estimated_current_rank;
                                        const isExact = typeof k.google_rank === 'number';
                                        const rankStr = String(rank || '').toLowerCase();
                                        const addEst = !isExact && rankStr && rankStr !== 'unknown';
                                        const rankDisplay = rank != null && typeof rank === 'number' ? `#${rank}` : (rank != null ? `${String(rank)}${addEst ? ' (est.)' : ''}` : '—');
                                        return (
                                        <tr key={i} style={{ borderBottom: '1px solid #f3f4f6' }}>
                                            <td style={tdStyle}><strong>{safeString(k.keyword) || '-'}</strong></td>
                                            <td style={tdStyle}>
                                                <span style={{ fontSize: '0.9rem', fontWeight: 500, color: rank != null ? '#111827' : '#6b7280' }}>{rankDisplay}</span>
                                            </td>
                                            <td style={tdStyle}>{scoreStr}/10</td>
                                            <td style={tdStyle}>
                                                <span style={{ padding: '2px 8px', borderRadius: '4px', fontSize: '0.75rem', background: strengthColor(k.current_content_strength), color: 'white' }}>{safeString(k.current_content_strength) || '-'}</span>
                                            </td>
                                            <td style={tdStyle}>
                                                <span style={{ padding: '2px 8px', borderRadius: '4px', fontSize: '0.75rem', background: potentialColor(k.estimated_ranking_potential), color: 'white' }}>{safeString(k.estimated_ranking_potential) || '-'}</span>
                                            </td>
                                            <td style={tdStyle}>{safeString(k.improvement_tips) || '-'}</td>
                                        </tr>
                                    );})}
                                </tbody>
                            </table>
                        </div>
                    </>
                )}
            </Section>
        )}
    </div>
    );
};

const LegacyReport = ({ analysis }) => {
    if (!analysis || typeof analysis !== 'object') return null;
    const topPriorities = safeArray(analysis.top_priorities);
    const categories = safeObject(analysis.categories);
    const summary = safeString(analysis.summary);
    const score = (typeof analysis.overall_score === 'number' && !isNaN(analysis.overall_score)) ? analysis.overall_score : 0;
    const status = safeString(analysis.overall_status);
    return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
        {summary && (
            <Section title="Summary" icon={<Zap size={20} />}>
                <p style={{ margin: 0, lineHeight: 1.6 }}>{summary}</p>
                <div style={{ marginTop: '16px', display: 'flex', gap: '16px', alignItems: 'center' }}>
                    <span style={{
                        padding: '8px 16px',
                        borderRadius: '8px',
                        background: '#dbeafe',
                        color: '#1e40af',
                        fontWeight: 600
                    }}>Score: {score}/100</span>
                    {status && <span style={{ color: '#6b7280' }}>{status}</span>}
                </div>
            </Section>
        )}
        {topPriorities.length > 0 && (
            <Section title="Top Priorities" icon={<AlertTriangle size={20} />}>
                {topPriorities.map((item, i) => {
                    const it = typeof item === 'object' ? item : {};
                    return (
                    <div key={i} style={cardStyle}>
                        <strong>{safeString(it.title)}</strong>
                        <p style={{ margin: '4px 0 0', fontSize: '0.9rem' }}>{safeString(it.description)}</p>
                    </div>
                );})}
            </Section>
        )}
        {Object.keys(categories).length > 0 && (
            <Section title="Categories" icon={<TrendingUp size={20} />}>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: '12px' }}>
                    {Object.entries(categories).map(([name, data]) => {
                        const score = (data && typeof data === 'object' && typeof data.score === 'number') ? data.score : (typeof data === 'number' ? data : 0);
                        return (
                        <div key={String(name)} style={{
                            padding: '12px',
                            borderRadius: '8px',
                            background: '#f9fafb',
                            border: '1px solid #e5e7eb'
                        }}>
                            <div style={{ fontWeight: 600, textTransform: 'capitalize' }}>{String(name).replace(/_/g, ' ')}</div>
                            <div style={{ fontSize: '1.25rem', fontWeight: 700, color: '#2563eb' }}>{score}/100</div>
                        </div>
                    );})}
                </div>
            </Section>
        )}
    </div>
    );
};

const Section = ({ title, icon, children, compact = false }) => (
    <div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: compact ? '8px' : '12px' }}>
            <span style={{ color: '#2563eb' }}>{icon}</span>
            <h3 style={{ margin: 0, fontSize: compact ? '0.85rem' : '1rem', fontWeight: 600, color: '#111827' }}>{title}</h3>
        </div>
        {children}
    </div>
);

const IssueCard = ({ item, showAngle = false }) => {
    if (!item || typeof item !== 'object') return null;
    const severityColors = { critical: '#dc2626', high: '#ea580c', medium: '#ca8a04', low: '#6b7280' };
    const sev = (item.severity && typeof item.severity === 'string') ? item.severity.toLowerCase() : 'medium';
    const bg = severityColors[sev] || '#6b7280';
    const angle = safeString(item.cold_email_angle || item.coldEmailAngle);
    return (
        <div style={cardStyle}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                <strong>{safeString(item.title)}</strong>
                <span style={{
                    padding: '2px 8px',
                    borderRadius: '4px',
                    fontSize: '0.7rem',
                    background: bg,
                    color: 'white',
                    textTransform: 'uppercase'
                }}>{sev}</span>
            </div>
            <p style={{ margin: 0, fontSize: '0.9rem', color: '#4b5563' }}>{safeString(item.description)}</p>
            {showAngle && angle && (
                <div style={{ marginTop: '8px', fontSize: '0.9rem', color: '#4b5563', display: 'flex', alignItems: 'flex-start', gap: '8px' }}>
                    <Mail size={14} style={{ flexShrink: 0, marginTop: '2px', color: '#6b7280' }} />
                    <em>{angle}</em>
                </div>
            )}
        </div>
    );
};

const DeveloperIssueCard = ({ item }) => {
    if (!item || typeof item !== 'object') return null;
    const severityColors = { critical: '#dc2626', high: '#ea580c', medium: '#ca8a04', low: '#6b7280' };
    const sev = (item.severity && typeof item.severity === 'string') ? item.severity.toLowerCase() : 'medium';
    const bg = severityColors[sev] || '#6b7280';
    const cat = safeString(item.category || '').toUpperCase();
    const angle = safeString(item.cold_email_angle || item.coldEmailAngle);
    return (
        <div style={{ ...cardStyle, borderLeft: '4px solid #dc2626' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px', flexWrap: 'wrap' }}>
                <span style={{ padding: '2px 8px', borderRadius: '4px', fontSize: '0.65rem', background: '#374151', color: 'white', textTransform: 'uppercase' }}>{cat || 'GLITCH'}</span>
                <strong>{safeString(item.title)}</strong>
                <span style={{ padding: '2px 8px', borderRadius: '4px', fontSize: '0.7rem', background: bg, color: 'white', textTransform: 'uppercase' }}>{sev}</span>
            </div>
            <p style={{ margin: 0, fontSize: '0.9rem', color: '#4b5563' }}>{safeString(item.description)}</p>
            {angle && (
                <div style={{ marginTop: '8px', fontSize: '0.9rem', color: '#4b5563', display: 'flex', alignItems: 'flex-start', gap: '8px' }}>
                    <Mail size={14} style={{ flexShrink: 0, marginTop: '2px', color: '#6b7280' }} />
                    <em>{angle}</em>
                </div>
            )}
        </div>
    );
};

const cardStyle = {
    padding: '12px 16px',
    borderRadius: '8px',
    background: '#f9fafb',
    border: '1px solid #e5e7eb',
    marginBottom: '8px',
    wordBreak: 'break-word',
    overflowWrap: 'break-word',
    maxWidth: '100%'
};

const thStyle = { padding: '12px', textAlign: 'left', fontWeight: 600, color: '#6b7280', whiteSpace: 'nowrap' };
const tdStyle = { padding: '12px', verticalAlign: 'top', wordBreak: 'break-word' };

const priorityColor = (p) => {
    if (p == null || typeof p !== 'string') return '#6b7280';
    const m = String(p).toLowerCase();
    if (m === 'high') return '#dc2626';
    if (m === 'medium') return '#ca8a04';
    return '#6b7280';
};

const strengthColor = (s) => {
    if (s == null) return '#6b7280';
    const m = String(s).toLowerCase();
    if (m === 'strong') return '#059669';
    if (m === 'moderate') return '#ca8a04';
    return '#dc2626';
};

const potentialColor = (p) => {
    if (p == null) return '#6b7280';
    const m = String(p).toLowerCase();
    if (m === 'high') return '#059669';
    if (m === 'medium') return '#ca8a04';
    return '#6b7280';
};

// Export for use in EmailManagementModal and EmailManagement page
export const AnalysisReportContent = ({ analysis, compact = false }) => {
    if (!analysis || analysis.status === 'failed') return null;
    const isGemini = analysis.source === 'gemini' || (analysis.keyword_analysis && analysis.overall_analysis) || (analysis.keywordAnalysis && analysis.overallAnalysis);
    return isGemini ? <GeminiReport analysis={analysis} compact={compact} /> : <LegacyReport analysis={analysis} />;
};

export default AnalysisModal;
