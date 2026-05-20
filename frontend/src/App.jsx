import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import Login from './pages/Login';
import MyPerfil from './pages/MyPerfil';
import ManageUsers from './pages/ManageUsers';
import EditGym from './pages/EditGym';
import MobileNav from './components/MobileNav';
import SuperAdmin from './pages/SuperAdmin';
import Carousel from './components/Carousel';

// Protected Route Component to shield admin dashboards
const ProtectedRoute = ({ children }) => {
  const { user } = useAuth();
  if (!user) {
    return <Navigate to="/" replace />;
  }
  return children;
};

// Simple placeholder page component for demonstration
const PlaceholderPage = ({ title }) => {
  const { user } = useAuth();
  return (
    <div className="main-container text-center text-white" style={{ marginTop: '5rem' }}>
      <div className="login-card w-100" style={{ maxWidth: '600px' }}>
        <h1 className="fw-bold mb-4">{title}</h1>
        <p className="lead text-muted">Esta pantalla se encuentra lista para ser implementada en React.</p>
        <div className="mt-4 p-3 rounded bg-dark bg-opacity-50 border border-secondary border-opacity-25 text-start">
          <p className="small mb-1 text-uppercase text-secondary fw-bold">Usuario Autenticado:</p>
          <pre className="m-0 text-info small" style={{ whiteSpace: 'pre-wrap' }}>
            {JSON.stringify(user, null, 2)}
          </pre>
        </div>
      </div>
    </div>
  );
};

function AppContent() {
  return (
    <Router>
      <Routes>
        {/* Public Routes */}
        <Route path="/" element={<MyPerfil />} />
        <Route path="/myperfil" element={<MyPerfil />} />

        {/* Fallback redirection */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>

      {/* Dynamic authenticated navigation bar */}
      <MobileNav />
    </Router>
  );
}

function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}

export default App;
