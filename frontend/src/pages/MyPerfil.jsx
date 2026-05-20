import React, { useState } from 'react';
import { Link } from 'react-router-dom';

const MyPerfil = () => {
  const [userId, setUserId] = useState('');
  const [userInfo, setUserInfo] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!userId.trim()) return;

    setLoading(true);
    setError(null);
    setUserInfo(null);

    try {
      const res = await fetch(`/api/public/history/${userId}`);

      if (!res.ok) {
        throw new Error('Miembro no encontrado');
      }

      const data = await res.json();
      setUserInfo(data);
    } catch (err) {
      setError(err.message || 'Error al consultar el historial');
    } finally {
      setLoading(false);
    }
  };

  const handleNewSearch = () => {
    setUserInfo(null);
    setUserId('');
    setError(null);
  };

  // Helper to format date in Spanish/Local standard
  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString();
  };

  // Helper to format time
  const formatTime = (dateString) => {
    return new Date(dateString).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  // Check if membership is expired
  const isExpired = userInfo && new Date(userInfo.exp) < new Date();

  return (
    <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', width: '100%', padding: '2rem 1rem' }}>
      <div className="login-card" style={{ maxWidth: '500px' }}>

        {!userInfo ? (
          /* SEARCH VIEW */
          <div id="searchView">
            <div className="text-center mb-4">
              <div className="mb-3">
                <i className="bi bi-person-badge-fill text-primary" style={{ fontSize: '3rem' }}></i>
              </div>
              <h3 className="fw-bold">Mi Historial</h3>
              <p className="text-muted small">Ingresa tu ID de miembro para consultar tu estado</p>
            </div>

            <form onSubmit={handleSearch}>
              <div className="mb-4">
                <input
                  type="number"
                  className="form-control form-control-premium text-center fw-bold fs-5"
                  placeholder="ID de Miembro"
                  value={userId}
                  onChange={(e) => setUserId(e.target.value)}
                  required
                  disabled={loading}
                />
              </div>

              <button
                type="submit"
                className="btn btn-premium w-100 text-white mb-3 d-flex align-items-center justify-content-center"
                disabled={loading}
              >
                {loading ? (
                  <>
                    <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                    Buscando...
                  </>
                ) : (
                  <>
                    <i className="bi bi-search me-2"></i>Consultar Historial
                  </>
                )}
              </button>
            </form>

            <div className="text-center">
              <Link to="/" className="auth-footer-link small">
                <i className="bi bi-arrow-left me-1"></i>Volver al Login
              </Link>
            </div>

            {error && (
              <div className="mt-3 text-danger text-center small fw-bold">
                ❌ {error}
              </div>
            )}
          </div>
        ) : (
          /* RESULT VIEW */
          <div id="resultArea">
            <div className="text-center">
              <img
                src={userInfo.image
                  ? `data:image/jpeg;base64,${userInfo.image}`
                  : `https://ui-avatars.com/api/?name=${encodeURIComponent(userInfo.name)}&background=6366f1&color=fff&size=200`}
                className="user-avatar-public"
                alt="Perfil"
                style={{
                  width: '120px',
                  height: '120px',
                  borderRadius: '35px',
                  objectFit: 'cover',
                  border: '4px solid rgba(255,255,255,0.1)',
                  marginBottom: '1.5rem'
                }}
              />
              <h4 className="fw-bold mb-1">{userInfo.name}</h4>
              <h4 className="fw-bold mb-1">{userInfo.gym_name}</h4>
              <p className="text-muted small mb-2">{userInfo.gym_name || 'Sin gimnasio asignado'}</p>
              <div className="mb-4">
                <span className={`badge ${isExpired ? 'bg-danger' : 'bg-success'} px-3 py-2 fw-bold text-uppercase`} style={{ borderRadius: '8px', fontSize: '0.8rem' }}>
                  Expira: {formatDate(userInfo.exp)}
                </span>
              </div>
            </div>

            <div className="small fw-bold text-muted text-uppercase mb-3 pb-2 border-bottom border-secondary border-opacity-25" style={{ letterSpacing: '0.05em' }}>
              Últimas Entradas
            </div>

            <div style={{ maxHeight: '250px', overflowY: 'auto', paddingRight: '5px' }}>
              {userInfo.entries && userInfo.entries.length > 0 ? (
                userInfo.entries.map((entry, index) => (
                  <div
                    key={index}
                    className="d-flex justify-content-between align-items-center mb-2 p-3 rounded"
                    style={{
                      background: 'rgba(15, 23, 42, 0.4)',
                      border: '1px solid rgba(255, 255, 255, 0.05)'
                    }}
                  >
                    <span className="fw-semibold small">{formatDate(entry)}</span>
                    <span className="text-muted small">{formatTime(entry)}</span>
                  </div>
                ))
              ) : (
                <div className="text-center text-muted small py-4">Sin registros de entrada</div>
              )}
            </div>

            <button
              className="btn btn-outline-light w-100 mt-4 py-2"
              style={{ borderRadius: '12px', borderOpacity: '0.25' }}
              onClick={handleNewSearch}
            >
              <i className="bi bi-arrow-repeat me-2"></i>Nueva Consulta
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default MyPerfil;
