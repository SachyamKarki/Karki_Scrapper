import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Lock, Mail, Loader2 } from 'lucide-react';

const LoginPage = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const { login } = useAuth();
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);
        try {
            const result = await login(email, password);
            if (result.success) {
                navigate('/');
            } else {
                setError(result.message || 'Invalid email or password');
            }
        } catch (err) {
            const msg = err.response?.data?.message || err.message || 'An error occurred during login';
            setError(msg);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div style={{ 
            minHeight: '100vh', 
            display: 'flex', 
            alignItems: 'center', 
            justifyContent: 'center', 
            background: '#f8fafc',
            fontFamily: 'Inter, sans-serif'
        }}>
            <div style={{ 
                width: '100%', 
                maxWidth: '400px', 
                background: 'white', 
                padding: '40px', 
                borderRadius: '16px', 
                boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)'
            }}>
                <div style={{ textAlign: 'center', marginBottom: '32px' }}>
                    <h1 style={{ fontSize: '1.875rem', fontWeight: 700, color: '#1e293b' }}>Welcome Back</h1>
                    <p style={{ color: '#64748b', marginTop: '8px' }}>Please enter your details to sign in</p>
                </div>

                {error && (
                    <div style={{ 
                        background: '#fef2f2', 
                        color: '#ef4444', 
                        padding: '12px', 
                        borderRadius: '8px', 
                        marginBottom: '24px',
                        fontSize: '0.875rem',
                        textAlign: 'center'
                    }}>
                        {error}
                    </div>
                )}

                <form onSubmit={handleSubmit}>
                    <div style={{ marginBottom: '20px' }}>
                        <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 500, marginBottom: '8px' }}>Email</label>
                        <div style={{ position: 'relative' }}>
                            <Mail size={18} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: '#94a3b8' }} />
                            <input 
                                type="email" 
                                required
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                placeholder="name@company.com"
                                style={{ 
                                    width: '100%', 
                                    padding: '12px 12px 12px 42px', 
                                    borderRadius: '8px', 
                                    border: '1px solid #e2e8f0',
                                    fontSize: '1rem',
                                    outline: 'none'
                                }}
                            />
                        </div>
                    </div>

                    <div style={{ marginBottom: '24px' }}>
                        <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 500, marginBottom: '8px' }}>Password</label>
                        <div style={{ position: 'relative' }}>
                            <Lock size={18} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: '#94a3b8' }} />
                            <input 
                                type="password" 
                                required
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                placeholder="••••••••"
                                style={{ 
                                    width: '100%', 
                                    padding: '12px 12px 12px 42px', 
                                    borderRadius: '8px', 
                                    border: '1px solid #e2e8f0',
                                    fontSize: '1rem',
                                    outline: 'none'
                                }}
                            />
                        </div>
                    </div>

                    <button 
                        type="submit" 
                        disabled={loading}
                        style={{ 
                            width: '100%', 
                            padding: '12px', 
                            background: '#3b82f6', 
                            color: 'white', 
                            borderRadius: '8px', 
                            border: 'none', 
                            fontWeight: 600, 
                            fontSize: '1rem',
                            cursor: 'pointer',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            gap: '8px',
                            transition: 'background 0.2s'
                        }}
                    >
                        {loading ? <Loader2 className="animate-spin" /> : 'Sign In'}
                    </button>
                </form>
            </div>
        </div>
    );
};

export default LoginPage;
