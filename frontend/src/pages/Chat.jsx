import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { Send, MessageSquare, Loader2, Users } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import socketService from '../services/socketService';

const Chat = () => {
    const { user } = useAuth();
    const [messages, setMessages] = useState([]);
    const [admins, setAdmins] = useState([]);
    const [newMessage, setNewMessage] = useState('');
    const [loading, setLoading] = useState(true);
    const [loadingAdmins, setLoadingAdmins] = useState(true);
    const [typingUsers, setTypingUsers] = useState(new Set());
    const messagesEndRef = useRef(null);
    const typingTimeoutRef = useRef(null);

    useEffect(() => {
        // Fetch message history
        const fetchHistory = async () => {
            try {
                const response = await axios.get('/messages/history');
                setMessages(response.data.messages || []);
            } catch (error) {
                console.error('Error fetching messages:', error);
            } finally {
                setLoading(false);
            }
        };

        // Fetch all registered admins (even if no messages exchanged)
        const fetchAdmins = async () => {
            try {
                const response = await axios.get('/messages/admins');
                setAdmins(response.data.admins || []);
            } catch (error) {
                console.error('Error fetching admins:', error);
            } finally {
                setLoadingAdmins(false);
            }
        };

        fetchHistory();
        if (user?.is_admin) {
            fetchAdmins();
        } else {
            setAdmins([]);
            setLoadingAdmins(false);
        }

        // Connect to Socket.IO
        socketService.connect();
        socketService.joinChat();

        // Listen for new messages
        socketService.onNewMessage((message) => {
            setMessages(prev => [...prev, message]);
        });

        // Listen for typing indicators
        socketService.onUserTyping((data) => {
            setTypingUsers(prev => {
                const next = new Set(prev);
                if (data.is_typing) {
                    next.add(data.email);
                } else {
                    next.delete(data.email);
                }
                return next;
            });

            // Auto-clear typing indicator after 3 seconds
            setTimeout(() => {
                setTypingUsers(prev => {
                    const next = new Set(prev);
                    next.delete(data.email);
                    return next;
                });
            }, 3000);
        });

        // Cleanup on unmount
        return () => {
            socketService.removeAllListeners();
        };
    }, [user?.is_admin]);

    // Auto-scroll to bottom when new messages arrive
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    const handleSendMessage = (e) => {
        e.preventDefault();
        if (!newMessage.trim()) return;

        socketService.sendMessage(newMessage);
        setNewMessage('');
        
        // Clear typing indicator
        if (typingTimeoutRef.current) {
            clearTimeout(typingTimeoutRef.current);
        }
        socketService.sendTyping(false);
    };

    const handleTyping = (e) => {
        setNewMessage(e.target.value);

        // Send typing indicator
        socketService.sendTyping(true);

        // Clear previous timeout
        if (typingTimeoutRef.current) {
            clearTimeout(typingTimeoutRef.current);
        }

        // Stop typing indicator after 1 second of inactivity
        typingTimeoutRef.current = setTimeout(() => {
            socketService.sendTyping(false);
        }, 1000);
    };

    const formatTime = (timestamp) => {
        const date = new Date(timestamp);
        const now = new Date();
        const diffMs = now - date;
        const diffMins = Math.floor(diffMs / 60000);

        if (diffMins < 1) return 'Just now';
        if (diffMins < 60) return `${diffMins}m ago`;
        if (diffMins < 1440) return `${Math.floor(diffMins / 60)}h ago`;
        
        return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    };

    return (
        <>
            <div style={{ display: 'flex', height: 'calc(100vh - 100px)', background: 'white', borderRadius: '12px', boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)', border: '1px solid #e5e7eb', overflow: 'hidden' }}>
                
                {/* Left Sidebar - All Registered Admins */}
                <div style={{ width: '280px', borderRight: '1px solid #e5e7eb', display: 'flex', flexDirection: 'column', background: '#f9fafb' }}>
                    <div style={{ padding: '16px', borderBottom: '1px solid #e5e7eb' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                            <div style={{ padding: '8px', background: '#eff6ff', borderRadius: '8px', color: '#2563eb' }}>
                                <Users size={20} />
                            </div>
                            <div>
                                <h2 style={{ fontSize: '1rem', fontWeight: 600, color: '#1e293b', margin: 0 }}>Team Members</h2>
                                <p style={{ color: '#64748b', margin: 0, fontSize: '0.75rem' }}>All registered admins</p>
                            </div>
                        </div>
                    </div>
                    <div style={{ flex: 1, overflowY: 'auto' }}>
                        {loadingAdmins ? (
                            <div style={{ padding: '24px', display: 'flex', justifyContent: 'center' }}>
                                <Loader2 className="animate-spin" size={24} color="#2563eb" />
                            </div>
                        ) : (admins || []).length === 0 ? (
                            <div style={{ padding: '24px', textAlign: 'center', color: '#94a3b8', fontSize: '0.875rem' }}>
                                No other admins yet
                            </div>
                        ) : (
                            admins.map((admin) => (
                                <div
                                    key={admin.id}
                                    style={{
                                        padding: '12px 16px',
                                        borderBottom: '1px solid #f1f5f9',
                                        display: 'flex',
                                        alignItems: 'center',
                                        gap: '12px',
                                        background: admin.is_you ? '#eff6ff' : 'transparent'
                                    }}
                                >
                                    <div style={{ width: '36px', height: '36px', borderRadius: '50%', background: admin.is_you ? '#2563eb' : '#e2e8f0', display: 'flex', alignItems: 'center', justifyContent: 'center', color: admin.is_you ? 'white' : '#64748b', fontWeight: 600, fontSize: '0.9rem', flexShrink: 0 }}>
                                        {(admin.email || '?')[0].toUpperCase()}
                                    </div>
                                    <div style={{ flex: 1, minWidth: 0 }}>
                                        <div style={{ fontWeight: 500, color: '#1e293b', fontSize: '0.875rem', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                                            {admin.email || 'Unknown'}
                                            {admin.is_you && <span style={{ marginLeft: '6px', fontSize: '0.7rem', color: '#2563eb', fontWeight: 500 }}>(you)</span>}
                                        </div>
                                        <div style={{ fontSize: '0.7rem', color: '#64748b', textTransform: 'capitalize' }}>{admin.role}</div>
                                    </div>
                                </div>
                            ))
                        )}
                    </div>
                </div>

                {/* Main Chat Area */}
                <div style={{ flex: 1, display: 'flex', flexDirection: 'column', minWidth: 0 }}>
                    {/* Chat Header */}
                    <div style={{ padding: '20px 24px', borderBottom: '1px solid #e5e7eb', background: '#f9fafb' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                            <div style={{ padding: '10px', background: '#eff6ff', borderRadius: '10px', color: '#2563eb' }}>
                                <MessageSquare size={24} />
                            </div>
                            <div>
                                <h1 style={{ fontSize: '1.5rem', fontWeight: 700, color: '#1e293b', margin: 0 }}>Team Chat</h1>
                                <p style={{ color: '#64748b', margin: 0, fontSize: '0.875rem' }}>Real-time messaging for admins</p>
                            </div>
                        </div>
                    </div>

                        {/* Messages Area */}
                    <div style={{ flex: 1, overflowY: 'auto', padding: '24px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
                    {loading ? (
                        <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
                            <Loader2 className="animate-spin" size={40} color="#2563eb" />
                        </div>
                    ) : (messages || []).length === 0 ? (
                        <div style={{ display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', height: '100%', color: '#94a3b8' }}>
                            <MessageSquare size={48} style={{ marginBottom: '16px', opacity: 0.5 }} />
                            <p style={{ fontSize: '1.125rem', fontWeight: 500 }}>No messages yet</p>
                            <p style={{ fontSize: '0.875rem' }}>Start the conversation!</p>
                        </div>
                    ) : (
                        <>
                            {messages.map((msg, index) => {
                                const isOwnMessage = msg.sender_email === user.email;
                                return (
                                    <div key={msg._id || index} style={{ display: 'flex', justifyContent: isOwnMessage ? 'flex-end' : 'flex-start' }}>
                                        <div style={{ maxWidth: '70%' }}>
                                            {!isOwnMessage && (
                                                <div style={{ fontSize: '0.75rem', color: '#64748b', marginBottom: '4px', fontWeight: 500 }}>
                                                    {msg.sender_email}
                                                </div>
                                            )}
                                            <div style={{
                                                padding: '12px 16px',
                                                borderRadius: '12px',
                                                background: isOwnMessage ? '#2563eb' : '#f1f5f9',
                                                color: isOwnMessage ? 'white' : '#1e293b',
                                                wordBreak: 'break-word'
                                            }}>
                                                {msg.message}
                                            </div>
                                            <div style={{ fontSize: '0.7rem', color: '#94a3b8', marginTop: '4px', textAlign: isOwnMessage ? 'right' : 'left' }}>
                                                {formatTime(msg.timestamp)}
                                            </div>
                                        </div>
                                    </div>
                                );
                            })}
                            <div ref={messagesEndRef} />
                        </>
                    )}

                    {/* Typing Indicator */}
                    {typingUsers.size > 0 && (
                        <div style={{ fontSize: '0.875rem', color: '#64748b', fontStyle: 'italic', paddingLeft: '8px' }}>
                            {Array.from(typingUsers).join(', ')} {typingUsers.size === 1 ? 'is' : 'are'} typing...
                        </div>
                    )}
                    </div>

                    {/* Message Input */}
                    <div style={{ padding: '16px 24px', borderTop: '1px solid #e5e7eb', background: '#f9fafb' }}>
                    <form onSubmit={handleSendMessage} style={{ display: 'flex', gap: '12px' }}>
                        <input
                            type="text"
                            value={newMessage}
                            onChange={handleTyping}
                            placeholder="Type a message..."
                            style={{
                                flex: 1,
                                padding: '12px 16px',
                                borderRadius: '8px',
                                border: '1px solid #e2e8f0',
                                fontSize: '0.9rem',
                                outline: 'none',
                                background: 'white'
                            }}
                        />
                        <button
                            type="submit"
                            disabled={!newMessage.trim()}
                            style={{
                                padding: '12px 24px',
                                borderRadius: '8px',
                                background: newMessage.trim() ? '#2563eb' : '#cbd5e1',
                                color: 'white',
                                border: 'none',
                                fontWeight: 500,
                                cursor: newMessage.trim() ? 'pointer' : 'not-allowed',
                                display: 'flex',
                                alignItems: 'center',
                                gap: '8px',
                                transition: 'all 0.2s'
                            }}
                        >
                            <Send size={18} />
                            Send
                        </button>
                    </form>
                    </div>
                </div>
            </div>
        </>
    );
};

export default Chat;
