import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { Send, Loader2, Mail, Search, ChevronDown, UserPlus, Shield } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import socketService from '../services/socketService';

const DirectMessages = () => {
    const { user } = useAuth();
    const [conversations, setConversations] = useState([]);
    const [admins, setAdmins] = useState([]);
    const [selectedConversation, setSelectedConversation] = useState(null);
    const [messages, setMessages] = useState([]);
    const [newMessage, setNewMessage] = useState('');
    const [loading, setLoading] = useState(true);
    const [loadingAdmins, setLoadingAdmins] = useState(false);
    const [loadingMessages, setLoadingMessages] = useState(false);
    const [typingUser, setTypingUser] = useState(null);
    const [searchQuery, setSearchQuery] = useState('');
    const [showRecipientDropdown, setShowRecipientDropdown] = useState(false);
    const [showAdminDropdown, setShowAdminDropdown] = useState(false);
    const messagesEndRef = useRef(null);
    const typingTimeoutRef = useRef(null);
    const selectedConvRef = useRef(null);
    const recipientDropdownRef = useRef(null);
    const adminDropdownRef = useRef(null);
    selectedConvRef.current = selectedConversation;

    useEffect(() => {
        const handleClickOutside = (e) => {
            if (recipientDropdownRef.current && !recipientDropdownRef.current.contains(e.target)) setShowRecipientDropdown(false);
            if (adminDropdownRef.current && !adminDropdownRef.current.contains(e.target)) setShowAdminDropdown(false);
        };
        document.addEventListener('mousedown', handleClickOutside);
        return () => document.removeEventListener('mousedown', handleClickOutside);
    }, []);

    // Fetch conversations and admins (for admins) on mount
    useEffect(() => {
        fetchConversations();
        
        // Connect to Socket.IO
        socketService.connect();

        // Listen for new DMs (use ref to avoid stale closure)
        socketService.onNewDM((message) => {
            const conv = selectedConvRef.current;
            if (conv && (message.sender_id === conv.user_id || message.recipient_id === conv.user_id)) {
                setMessages(prev => [...prev, message]);
            }
            fetchConversations();
        });

        // Listen for typing indicators
        socketService.onDMUserTyping((data) => {
            const conv = selectedConvRef.current;
            if (conv && data.user_id === conv.user_id) {
                setTypingUser(data.is_typing ? data.email : null);
                setTimeout(() => setTypingUser(null), 3000);
            }
        });

        return () => {
            if (selectedConvRef.current) {
                socketService.leaveDM(selectedConvRef.current.user_id);
            }
            socketService.removeAllListeners();
        };
    }, []);

    // Fetch admins when user loads (for admin/superadmin)
    useEffect(() => {
        if (user?.is_admin) {
            setLoadingAdmins(true);
            axios.get('/messages/admins')
                .then(res => setAdmins(res.data.admins || []))
                .catch(() => setAdmins([]))
                .finally(() => setLoadingAdmins(false));
        } else {
            setAdmins([]);
        }
    }, [user?.is_admin]);

    // Auto-scroll to bottom when new messages arrive
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    const fetchConversations = async () => {
        try {
            const response = await axios.get('/messages/conversations');
            setConversations(response.data.conversations || []);
        } catch (error) {
            console.error('Error fetching conversations:', error);
        } finally {
            setLoading(false);
        }
    };

    const openConversation = async (conversation) => {
        // Leave previous DM room
        if (selectedConversation) {
            socketService.leaveDM(selectedConversation.user_id);
        }

        setSelectedConversation(conversation);
        setLoadingMessages(true);
        
        try {
            const response = await axios.get(`/messages/dm/${conversation.user_id}`);
            setMessages(response.data.messages || []);
            
            // Join DM room
            socketService.joinDM(conversation.user_id);
        } catch (error) {
            console.error('Error fetching messages:', error);
        } finally {
            setLoadingMessages(false);
        }
    };

    const startNewConversation = async (userId, userEmail, userRole) => {
        // Check if conversation already exists in list
        const existing = conversations.find(c => c.user_id === userId);
        if (existing) {
            openConversation(existing);
            return;
        }

        // Create new conversation object
        const newConv = {
            user_id: userId,
            user_email: userEmail,
            user_role: userRole,
            last_message: { message: 'Start a conversation...', timestamp: new Date() },
            unread_count: 0
        };

        setSelectedConversation(newConv);
        setMessages([]);
        socketService.joinDM(userId);
    };

    const handleSendMessage = (e) => {
        e.preventDefault();
        if (!newMessage.trim() || !selectedConversation) return;

        socketService.sendDM(selectedConversation.user_id, newMessage);
        setNewMessage('');
        
        // Clear typing indicator
        if (typingTimeoutRef.current) {
            clearTimeout(typingTimeoutRef.current);
        }
        socketService.sendDMTyping(selectedConversation.user_id, false);
    };

    const handleTyping = (e) => {
        setNewMessage(e.target.value);

        if (!selectedConversation) return;

        // Send typing indicator
        socketService.sendDMTyping(selectedConversation.user_id, true);

        // Clear previous timeout
        if (typingTimeoutRef.current) {
            clearTimeout(typingTimeoutRef.current);
        }

        // Stop typing indicator after 1 second of inactivity
        typingTimeoutRef.current = setTimeout(() => {
            socketService.sendDMTyping(selectedConversation.user_id, false);
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

    const filteredConversations = (conversations || []).filter(conv =>
        conv.user_email.toLowerCase().includes(searchQuery.toLowerCase())
    );

    return (
        <>
            <div style={{ display: 'flex', height: 'calc(100vh - 100px)', background: 'white', borderRadius: '12px', boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)', border: '1px solid #e5e7eb', overflow: 'hidden' }}>
                
                {/* Left Panel - Conversations List */}
                <div style={{ width: '350px', borderRight: '1px solid #e5e7eb', display: 'flex', flexDirection: 'column' }}>
                    {/* Header */}
                    <div style={{ padding: '20px', borderBottom: '1px solid #e5e7eb', background: '#f9fafb' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
                            <div style={{ padding: '10px', background: '#eff6ff', borderRadius: '10px', color: '#2563eb' }}>
                                <Mail size={24} />
                            </div>
                            <h2 style={{ fontSize: '1.25rem', fontWeight: 700, color: '#1e293b', margin: 0 }}>Messages</h2>
                        </div>
                        {user?.is_admin && (
                            <div ref={adminDropdownRef} style={{ position: 'relative', marginBottom: '12px' }}>
                                <button
                                    type="button"
                                    onClick={() => setShowAdminDropdown(!showAdminDropdown)}
                                    style={{
                                        width: '100%',
                                        display: 'flex',
                                        alignItems: 'center',
                                        justifyContent: 'space-between',
                                        gap: '10px',
                                        padding: '12px 16px',
                                        borderRadius: '10px',
                                        border: '1px solid #c7d2fe',
                                        background: showAdminDropdown ? '#e0e7ff' : 'white',
                                        color: '#4338ca',
                                        fontSize: '0.875rem',
                                        fontWeight: 600,
                                        cursor: 'pointer',
                                        boxShadow: '0 1px 2px rgba(0,0,0,0.05)',
                                        transition: 'all 0.2s ease'
                                    }}
                                    onMouseEnter={(e) => { if (!showAdminDropdown) { e.currentTarget.style.background = '#f5f3ff'; e.currentTarget.style.borderColor = '#a5b4fc'; } }}
                                    onMouseLeave={(e) => { if (!showAdminDropdown) { e.currentTarget.style.background = 'white'; e.currentTarget.style.borderColor = '#c7d2fe'; } }}
                                >
                                    <span style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                                        <Shield size={18} style={{ flexShrink: 0 }} />
                                        New message to admin
                                    </span>
                                    <ChevronDown size={18} style={{ flexShrink: 0, transform: showAdminDropdown ? 'rotate(180deg)' : 'none', transition: 'transform 0.2s' }} />
                                </button>
                                {showAdminDropdown && (
                                    <div style={{
                                        position: 'absolute', top: '100%', left: 0, right: 0, marginTop: '8px',
                                        background: 'white',
                                        border: '1px solid #e5e7eb',
                                        borderRadius: '12px',
                                        boxShadow: '0 10px 40px -10px rgba(0,0,0,0.15), 0 0 0 1px rgba(0,0,0,0.03)',
                                        zIndex: 50, maxHeight: '260px', overflowY: 'auto',
                                        padding: '6px'
                                    }}>
                                        {loadingAdmins ? (
                                            <div style={{ padding: '24px', display: 'flex', justifyContent: 'center' }}><Loader2 className="animate-spin" size={24} color="#4338ca" /></div>
                                        ) : (admins || []).filter(a => !a.is_you).length === 0 ? (
                                            <div style={{ padding: '20px', color: '#64748b', fontSize: '0.875rem', textAlign: 'center' }}>No other admins or superadmins</div>
                                        ) : (
                                            (admins || []).filter(a => !a.is_you).map((admin) => (
                                                <div
                                                    key={admin.id}
                                                    onClick={() => { startNewConversation(admin.id, admin.email || 'Unknown', admin.role || 'user'); setShowAdminDropdown(false); }}
                                                    style={{
                                                        padding: '12px 14px',
                                                        cursor: 'pointer',
                                                        display: 'flex',
                                                        alignItems: 'center',
                                                        gap: '14px',
                                                        borderRadius: '8px',
                                                        transition: 'background 0.15s ease'
                                                    }}
                                                    onMouseEnter={(e) => { e.currentTarget.style.background = '#f8fafc'; }}
                                                    onMouseLeave={(e) => { e.currentTarget.style.background = 'transparent'; }}
                                                >
                                                    <div style={{ width: '40px', height: '40px', borderRadius: '50%', background: admin.role === 'superadmin' ? '#f3e8ff' : '#eff6ff', display: 'flex', alignItems: 'center', justifyContent: 'center', color: admin.role === 'superadmin' ? '#7c3aed' : '#2563eb', fontWeight: 600, fontSize: '0.95rem', flexShrink: 0 }}>
                                                        {(admin.email || '?')[0].toUpperCase()}
                                                    </div>
                                                    <div style={{ flex: 1, minWidth: 0 }}>
                                                        <div style={{ fontWeight: 600, color: '#1e293b', fontSize: '0.9rem', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{admin.email || 'Unknown'}</div>
                                                        <div style={{ fontSize: '0.75rem', color: admin.role === 'superadmin' ? '#7c3aed' : '#64748b', fontWeight: 500, textTransform: 'capitalize', marginTop: '2px' }}>{admin.role}</div>
                                                    </div>
                                                </div>
                                            ))
                                        )}
                                    </div>
                                )}
                            </div>
                        )}
                        <div style={{ position: 'relative' }}>
                            <Search style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: '#9ca3af' }} size={16} />
                            <input
                                type="text"
                                placeholder="Search people..."
                                value={searchQuery}
                                onChange={(e) => setSearchQuery(e.target.value)}
                                style={{ width: '100%', padding: '8px 12px 8px 40px', borderRadius: '8px', border: '1px solid #e2e8f0', fontSize: '0.875rem', outline: 'none' }}
                            />
                        </div>
                    </div>

                    {/* People List - shows all users by default */}
                    <div style={{ flex: 1, overflowY: 'auto' }}>
                        {loading ? (
                                <div style={{ padding: '40px', display: 'flex', justifyContent: 'center' }}>
                                    <Loader2 className="animate-spin" size={32} color="#2563eb" />
                                </div>
                            ) : filteredConversations.length === 0 ? (
                                <div style={{ padding: '40px', textAlign: 'center', color: '#94a3b8' }}>
                                    <Mail size={48} style={{ margin: '0 auto 16px', opacity: 0.5 }} />
                                    <p style={{ fontSize: '0.875rem' }}>No people to message</p>
                                </div>
                            ) : (
                                filteredConversations.map((conv) => (
                                    <div
                                        key={conv.user_id}
                                        onClick={() => openConversation(conv)}
                                        style={{
                                            padding: '16px',
                                            borderBottom: '1px solid #f1f5f9',
                                            cursor: 'pointer',
                                            background: selectedConversation?.user_id === conv.user_id ? '#f8fafc' : 'white',
                                            transition: 'background 0.2s',
                                            display: 'flex',
                                            alignItems: 'center',
                                            gap: '12px'
                                        }}
                                        onMouseEnter={(e) => e.currentTarget.style.background = '#f8fafc'}
                                        onMouseLeave={(e) => e.currentTarget.style.background = selectedConversation?.user_id === conv.user_id ? '#f8fafc' : 'white'}
                                    >
                                        <div style={{ width: '40px', height: '40px', borderRadius: '50%', background: '#eff6ff', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#2563eb', fontWeight: 600, fontSize: '1rem', flexShrink: 0 }}>
                                            {(conv.user_email || '?')[0].toUpperCase()}
                                        </div>
                                        <div style={{ flex: 1, minWidth: 0 }}>
                                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
                                                <span style={{ fontWeight: 600, color: '#1e293b', fontSize: '0.875rem', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                                                    {conv.user_email || 'Unknown'}
                                                </span>
                                                {conv.unread_count > 0 && (
                                                    <span style={{ background: '#2563eb', color: 'white', fontSize: '0.7rem', padding: '2px 6px', borderRadius: '10px', fontWeight: 600 }}>
                                                        {conv.unread_count}
                                                    </span>
                                                )}
                                            </div>
                                            <p style={{ color: '#64748b', fontSize: '0.8rem', margin: 0, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                                                {conv.last_message?.message || 'No messages yet'}
                                            </p>
                                        </div>
                                    </div>
                                ))
                            )}
                    </div>
                </div>

                {/* Right Panel - Chat Thread */}
                <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
                    {selectedConversation ? (
                        <>
                            {/* Chat Header */}
                            <div style={{ padding: '20px 24px', borderBottom: '1px solid #e5e7eb', background: '#f9fafb' }}>
                                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                                    <div style={{ width: '40px', height: '40px', borderRadius: '50%', background: '#eff6ff', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#2563eb', fontWeight: 600, fontSize: '1.1rem' }}>
                                        {(selectedConversation.user_email || '?')[0].toUpperCase()}
                                    </div>
                                    <div>
                                        <h3 style={{ fontSize: '1.125rem', fontWeight: 600, color: '#1e293b', margin: 0 }}>{selectedConversation.user_email || 'Unknown'}</h3>
                                        <p style={{ color: '#64748b', margin: 0, fontSize: '0.8rem', textTransform: 'capitalize' }}>{selectedConversation.user_role}</p>
                                    </div>
                                </div>
                            </div>

                            {/* Messages Area */}
                            <div style={{ flex: 1, overflowY: 'auto', padding: '24px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
                                {loadingMessages ? (
                                    <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
                                        <Loader2 className="animate-spin" size={40} color="#2563eb" />
                                    </div>
                                ) : (
                                    <>
                                        {messages.map((msg, index) => {
                                            const isOwnMessage = msg.sender_email === user?.email || msg.sender_id === user?.id;
                                            return (
                                                <div key={msg._id || index} style={{ display: 'flex', justifyContent: isOwnMessage ? 'flex-end' : 'flex-start' }}>
                                                    <div style={{ maxWidth: '70%' }}>
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
                                {typingUser && (
                                    <div style={{ fontSize: '0.875rem', color: '#64748b', fontStyle: 'italic', paddingLeft: '8px' }}>
                                        {typingUser} is typing...
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
                        </>
                    ) : (
                        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', color: '#94a3b8', padding: '24px' }}>
                            <Mail size={64} style={{ marginBottom: '16px', opacity: 0.5 }} />
                            <p style={{ fontSize: '1.125rem', fontWeight: 500, marginBottom: '8px' }}>Start a direct conversation</p>
                            <p style={{ fontSize: '0.875rem', marginBottom: '20px' }}>
                                {user?.is_admin ? 'Click "New message to admin" in the left sidebar, or choose from the list below' : 'Choose a recipient from the list on the left'}
                            </p>
                            <div ref={recipientDropdownRef} style={{ position: 'relative' }}>
                                <button
                                    type="button"
                                    onClick={() => setShowRecipientDropdown(!showRecipientDropdown)}
                                    style={{
                                        display: 'flex',
                                        alignItems: 'center',
                                        justifyContent: 'space-between',
                                        gap: '12px',
                                        padding: '14px 24px',
                                        borderRadius: '10px',
                                        border: '1px solid #c7d2fe',
                                        background: showRecipientDropdown ? '#e0e7ff' : 'white',
                                        fontSize: '0.9rem',
                                        color: '#4338ca',
                                        cursor: 'pointer',
                                        fontWeight: 600,
                                        boxShadow: '0 2px 4px rgba(0,0,0,0.06)',
                                        transition: 'all 0.2s ease',
                                        minWidth: '260px'
                                    }}
                                    onMouseEnter={(e) => { if (!showRecipientDropdown) { e.currentTarget.style.background = '#f5f3ff'; e.currentTarget.style.borderColor = '#a5b4fc'; } }}
                                    onMouseLeave={(e) => { if (!showRecipientDropdown) { e.currentTarget.style.background = 'white'; e.currentTarget.style.borderColor = '#c7d2fe'; } }}
                                >
                                    <span style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                                        <UserPlus size={20} style={{ flexShrink: 0 }} />
                                        Select recipient to message
                                    </span>
                                    <ChevronDown size={20} style={{ flexShrink: 0, transform: showRecipientDropdown ? 'rotate(180deg)' : 'none', transition: 'transform 0.2s' }} />
                                </button>
                                {showRecipientDropdown && (
                                    <div style={{
                                        position: 'absolute', top: '100%', left: '50%', transform: 'translateX(-50%)', marginTop: '10px',
                                        background: 'white',
                                        border: '1px solid #e5e7eb',
                                        borderRadius: '12px',
                                        boxShadow: '0 10px 40px -10px rgba(0,0,0,0.15), 0 0 0 1px rgba(0,0,0,0.03)',
                                        zIndex: 50, minWidth: '320px', maxHeight: '320px', overflowY: 'auto',
                                        padding: '8px'
                                    }}>
                                        {conversations.length === 0 ? (
                                            <div style={{ padding: '24px', color: '#64748b', fontSize: '0.875rem', textAlign: 'center' }}>No recipients available</div>
                                        ) : (
                                            (conversations || []).map((conv) => (
                                                <div
                                                    key={conv.user_id}
                                                    onClick={() => { startNewConversation(conv.user_id, conv.user_email || 'Unknown', conv.user_role || 'user'); setShowRecipientDropdown(false); }}
                                                    style={{
                                                        padding: '12px 16px',
                                                        cursor: 'pointer',
                                                        display: 'flex',
                                                        alignItems: 'center',
                                                        gap: '14px',
                                                        borderRadius: '8px',
                                                        transition: 'background 0.15s ease'
                                                    }}
                                                    onMouseEnter={(e) => { e.currentTarget.style.background = '#f8fafc'; }}
                                                    onMouseLeave={(e) => { e.currentTarget.style.background = 'transparent'; }}
                                                >
                                                    <div style={{ width: '40px', height: '40px', borderRadius: '50%', background: conv.user_role === 'superadmin' ? '#f3e8ff' : conv.user_role === 'admin' ? '#eff6ff' : '#f1f5f9', display: 'flex', alignItems: 'center', justifyContent: 'center', color: conv.user_role === 'superadmin' ? '#7c3aed' : conv.user_role === 'admin' ? '#2563eb' : '#64748b', fontWeight: 600, fontSize: '0.95rem', flexShrink: 0 }}>
                                                        {(conv.user_email || '?')[0].toUpperCase()}
                                                    </div>
                                                    <div style={{ flex: 1, minWidth: 0 }}>
                                                        <div style={{ fontWeight: 600, color: '#1e293b', fontSize: '0.9rem', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{conv.user_email || 'Unknown'}</div>
                                                        <div style={{ fontSize: '0.75rem', color: conv.user_role === 'superadmin' ? '#7c3aed' : conv.user_role === 'admin' ? '#2563eb' : '#64748b', fontWeight: 500, textTransform: 'capitalize', marginTop: '2px' }}>{conv.user_role}</div>
                                                    </div>
                                                </div>
                                            ))
                                        )}
                                    </div>
                                )}
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </>
    );
};

export default DirectMessages;
