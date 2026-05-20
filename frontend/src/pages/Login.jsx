import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const Login = () => {
  const { user, login } = useAuth();
  const navigate = useNavigate();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState({ text: '', type: '' });

  // Redirect to dashboard if user is already logged in
  useEffect(() => {
    if (user) {
      navigate('/dashboard');
    }
  }, [user, navigate]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage({ text: '', type: '' });

    try {
      const res = await login(email, password);
      
      if (res.success) {
        setMessage({ text: '✅ Acceso concedido.', type: 'success' });
        setTimeout(() => {
          navigate('/dashboard');
        }, 800);
      } else {
        setMessage({ text: `❌ ${res.message}`, type: 'danger' });
        setLoading(false);
      }
    } catch (err) {
      setMessage({ text: '⚠️ Error de conexión.', type: 'warning' });
      setLoading(false);
    }
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', width: '100%' }}>
      <div className="login-card">
        <div className="text-center mb-4">
          <div className="login-logo">
            <i className="bi bi-lightning-charge-fill"></i>
          </div>
          <h2 className="fw-bold m-0">GymAdmin</h2>
          <p className="text-muted small mt-2">Ingresa tus credenciales para continuar</p>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="mb-3">
            <label className="form-label small fw-bold text-muted text-uppercase">Email o Usuario</label>
            <input 
              type="text" 
              className="form-control form-control-premium" 
              required 
              placeholder="tu@email.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              disabled={loading}
            />
          </div>

          <div className="mb-4">
            <div className="d-flex justify-content-between mb-1">
              <label className="form-label small fw-bold text-muted text-uppercase m-0">Contraseña</label>
              <Link to="/forgot" className="auth-footer-link small">¿Olvidaste?</Link>
            </div>
            <input 
              type="password" 
              className="form-control form-control-premium" 
              required 
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              disabled={loading}
            />
          </div>

          <button 
            type="submit" 
            className="btn btn-premium w-100 text-white mb-4 d-flex align-items-center justify-content-center"
            disabled={loading}
          >
            {loading ? (
              <>
                <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                Entrando...
              </>
            ) : (
              'Iniciar Sesión'
            )}
          </button>
        </form>

        {message.text && (
          <div className={`text-center small mb-4 text-${message.type} fw-bold`}>
            {message.text}
          </div>
        )}

        <div className="text-center pt-3 border-top border-secondary border-opacity-25">
          <p className="text-muted small mb-2">¿Eres un miembro?</p>
          <Link 
            to="/myperfil" 
            className="btn btn-outline-light btn-sm w-100 py-2 border-opacity-25 fw-bold" 
            style={{ borderRadius: '10px' }}
          >
            Consultar mi perfil
          </Link>
        </div>
      </div>
    </div>
  );
};

export default Login;
