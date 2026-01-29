import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, Outlet } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import Layout from './components/Layout';
import LoginPage from './pages/LoginPage';
import Dashboard from './pages/Dashboard';
import AdminPanel from './pages/AdminPanel';
import Chat from './pages/Chat';
import DirectMessages from './pages/DirectMessages';
import EmailManagement from './pages/EmailManagement';

const ProtectedLayout = ({ adminOnly = false, superadminOnly = false }) => {
  const { user, loading } = useAuth();

  if (loading) return <div>Loading...</div>;
  if (!user) return <Navigate to="/login" />;
  if (adminOnly && !user.is_admin) return <Navigate to="/" />;
  if (superadminOnly && !user.is_superadmin) return <Navigate to="/" />;

  return (
    <Layout>
      <Outlet />
    </Layout>
  );
};

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route element={<ProtectedLayout />}>
            <Route path="/" element={<Dashboard />} />
            <Route path="/email" element={<EmailManagement />} />
            <Route path="/messages" element={<DirectMessages />} />
          </Route>
          <Route element={<ProtectedLayout adminOnly />}>
            <Route path="/admin" element={<AdminPanel />} />
            <Route path="/chat" element={<Chat />} />
          </Route>
          <Route path="*" element={<Navigate to="/" />} />
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;
