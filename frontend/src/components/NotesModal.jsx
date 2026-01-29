import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { X, Save, Image as ImageIcon, Loader2 } from 'lucide-react';

const NotesModal = ({ isOpen, onClose, itemId }) => {
    const [note, setNote] = useState('');
    const [image, setImage] = useState(null);
    const [imagePreview, setImagePreview] = useState(null);
    const [loading, setLoading] = useState(false);
    const [saving, setSaving] = useState(false);

    useEffect(() => {
        if (isOpen && itemId) {
            fetchNote();
        } else {
            setNote('');
            setImage(null);
            setImagePreview(null);
        }
    }, [isOpen, itemId]);

    const fetchNote = async () => {
        setLoading(true);
        try {
            const response = await axios.get(`/api/get_note/${itemId}`);
            if (response.data.success && response.data.note) {
                setNote(response.data.note.text || '');
                if (response.data.note.image) {
                    setImagePreview(response.data.note.image);
                }
            }
        } catch (error) {
            console.error("Error fetching note:", error);
        } finally {
            setLoading(false);
        }
    };

    const handleImageChange = (e) => {
        const file = e.target.files[0];
        if (file) {
            setImage(file);
            const reader = new FileReader();
            reader.onloadend = () => {
                setImagePreview(reader.result);
            };
            reader.readAsDataURL(file);
        }
    };

    const handleSave = async () => {
        setSaving(true);
        const formData = new FormData();
        formData.append('text', note);
        if (image) {
            formData.append('image', image);
        }

        try {
            await axios.post(`/api/save_note/${itemId}`, formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });
            onClose();
        } catch (error) {
            alert('Failed to save note');
        } finally {
            setSaving(false);
        }
    };

    if (!isOpen) return null;

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
            backdropFilter: 'blur(4px)'
        }}>
            <div style={{
                backgroundColor: 'white',
                borderRadius: '12px',
                width: '90%',
                maxWidth: '600px',
                padding: '24px',
                boxShadow: '0 20px 25px -5px rgba(0,0,0,0.1)',
                maxHeight: '85vh',
                overflowY: 'auto'
            }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
                    <h2 style={{ fontSize: '1.25rem', fontWeight: 600, color: '#1f2937', margin: 0 }}>Business Notes</h2>
                    <button onClick={onClose} style={{ border: 'none', background: 'transparent', cursor: 'pointer', color: '#6b7280' }}>
                        <X size={24} />
                    </button>
                </div>

                {loading ? (
                    <div style={{ display: 'flex', justifyContent: 'center', padding: '40px' }}>
                        <Loader2 className="animate-spin" size={32} color="#2563eb" />
                    </div>
                ) : (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                        <textarea
                            value={note}
                            onChange={(e) => setNote(e.target.value)}
                            placeholder="Add your notes here..."
                            style={{
                                width: '100%',
                                minHeight: '150px',
                                padding: '12px',
                                borderRadius: '8px',
                                border: '1px solid #e5e7eb',
                                fontSize: '0.95rem',
                                resize: 'vertical'
                            }}
                        />

                        <div>
                            <label style={{ 
                                display: 'flex', 
                                alignItems: 'center', 
                                gap: '8px', 
                                padding: '8px 16px', 
                                background: '#f3f4f6', 
                                borderRadius: '6px', 
                                width: 'fit-content',
                                cursor: 'pointer',
                                fontSize: '0.9rem',
                                color: '#4b5563',
                                fontWeight: 500
                            }}>
                                <ImageIcon size={18} />
                                Upload Image
                                <input type="file" accept="image/*" onChange={handleImageChange} style={{ display: 'none' }} />
                            </label>
                            
                            {imagePreview && (
                                <div style={{ marginTop: '12px', border: '1px solid #e5e7eb', borderRadius: '8px', overflow: 'hidden' }}>
                                    <img src={imagePreview} alt="Preview" style={{ maxWidth: '100%', display: 'block' }} />
                                </div>
                            )}
                        </div>

                        <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '16px' }}>
                            <button
                                onClick={handleSave}
                                disabled={saving}
                                style={{
                                    display: 'flex',
                                    alignItems: 'center',
                                    gap: '8px',
                                    backgroundColor: '#2563eb',
                                    color: 'white',
                                    border: 'none',
                                    padding: '10px 24px',
                                    borderRadius: '8px',
                                    fontWeight: 500,
                                    cursor: saving ? 'not-allowed' : 'pointer',
                                    opacity: saving ? 0.7 : 1
                                }}
                            >
                                {saving ? <Loader2 className="animate-spin" size={18} /> : <Save size={18} />}
                                Save Note
                            </button>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default NotesModal;
