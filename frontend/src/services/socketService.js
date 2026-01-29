import { io } from 'socket.io-client';

class SocketService {
    constructor() {
        this.socket = null;
        this.connected = false;
    }

    connect() {
        if (this.socket && this.connected) {
            return this.socket;
        }

        // Use VITE_API_URL if backend is on different origin; otherwise same origin (works with proxy in dev)
        const url = import.meta.env.VITE_API_URL || (typeof window !== 'undefined' ? window.location.origin : '');
        this.socket = io(url, {
            path: '/socket.io',
            transports: ['websocket', 'polling'],
            withCredentials: true
        });

        this.socket.on('connect', () => {
            this.connected = true;
        });

        this.socket.on('disconnect', () => {
            this.connected = false;
        });

        this.socket.on('connect_error', () => {
            // Silent in production - avoid exposing connection details
        });

        return this.socket;
    }

    disconnect() {
        if (this.socket) {
            this.socket.disconnect();
            this.socket = null;
            this.connected = false;
        }
    }

    // ===== TEAM CHAT METHODS =====

    joinChat() {
        if (this.socket) {
            this.socket.emit('join_chat', {});
        }
    }

    sendMessage(message) {
        if (this.socket) {
            this.socket.emit('send_message', { message });
        }
    }

    sendTyping(isTyping) {
        if (this.socket) {
            this.socket.emit('typing', { is_typing: isTyping });
        }
    }

    onNewMessage(callback) {
        if (this.socket) {
            this.socket.on('new_message', callback);
        }
    }

    onUserTyping(callback) {
        if (this.socket) {
            this.socket.on('user_typing', callback);
        }
    }

    onUserJoined(callback) {
        if (this.socket) {
            this.socket.on('user_joined', callback);
        }
    }

    onUserLeft(callback) {
        if (this.socket) {
            this.socket.on('user_left', callback);
        }
    }

    // ===== DIRECT MESSAGE METHODS =====

    joinDM(userId) {
        if (this.socket) {
            this.socket.emit('join_dm', { user_id: userId });
        }
    }

    leaveDM(userId) {
        if (this.socket) {
            this.socket.emit('leave_dm', { user_id: userId });
        }
    }

    sendDM(recipientId, message) {
        if (this.socket) {
            this.socket.emit('send_dm', { recipient_id: recipientId, message });
        }
    }

    sendDMTyping(recipientId, isTyping) {
        if (this.socket) {
            this.socket.emit('dm_typing', { recipient_id: recipientId, is_typing: isTyping });
        }
    }

    onNewDM(callback) {
        if (this.socket) {
            this.socket.on('new_dm', callback);
        }
    }

    onDMUserTyping(callback) {
        if (this.socket) {
            this.socket.on('dm_user_typing', callback);
        }
    }

    onDMUserJoined(callback) {
        if (this.socket) {
            this.socket.on('dm_user_joined', callback);
        }
    }

    removeAllListeners() {
        if (this.socket) {
            this.socket.removeAllListeners();
        }
    }
}

export default new SocketService();
