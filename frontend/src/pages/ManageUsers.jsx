import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const ManageUsers = () => {
  const { user, authFetch } = useAuth();
  const navigate = useNavigate();

  const [users, setUsers] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch users when component mounts or user details change
  useEffect(() => {
    const fetchUsers = async () => {
      if (!user || !user.gym_id) return;

      setLoading(true);
      setError(null);

      try {
        const res = await authFetch(`/api/users/gym/${user.gym_id}`);
        if (!res.ok) {
          throw new Error('Error al cargar la lista de miembros');
        }
        const data = await res.json();
        setUsers(data);
      } catch (err) {
        setError(err.message || 'Error de red o conexión.');
      } finally {
        setLoading(false);
      }
    };

    fetchUsers();
  }, [user]);

  // Helper to calculate expiration status and style
  const getStatus = (expDateString) => {
    if (!expDateString) return { label: 'Sin fecha', className: 'status-active' };

    const today = new Date();
    today.setHours(0, 0, 0, 0);
    const expDate = new Date(expDateString);

    if (expDate < today) {
      return { label: 'Expirado', className: 'status-expired' }; // Red pill
    }

    // Difference in days
    const diffTime = expDate - today;
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

    if (diffDays <= 7) {
      return { label: 'Próximo', className: 'status-warning' }; // Yellow pill
    }

    return { label: 'Activo', className: 'status-active' }; // Green pill
  };

  // Helper to format date cleanly
  const formatDate = (dateString) => {
    if (!dateString) return 'Sin fecha';
    return new Date(dateString).toLocaleDateString('es-ES', {
      day: 'numeric',
      month: 'short',
      year: 'numeric'
    });
  };

  // Filter users in real-time as the user types
  const filteredUsers = users.filter((u) => {
    const term = searchTerm.toLowerCase();
    return (
      u.name.toLowerCase().includes(term) ||
      String(u.id).includes(term)
    );
  });

  return (
    <div className="main-container">
      {/* Header section */}
      <div className="d-flex justify-content-between align-items-center mb-4 flex-wrap gap-3">
        <div>
          <h2 className="fw-bold text-white m-0">Miembros</h2>
          <p className="text-muted small m-0">Gestiona los usuarios de tu gimnasio</p>
        </div>
        <div className="d-flex gap-2">
          <Link to="/dashboard" className="btn btn-outline-light py-2 px-3 fw-bold" style={{ borderRadius: '12px' }}>
            <i className="bi bi-arrow-left me-2"></i>Volver
          </Link>
          <Link to="/add-user" className="btn btn-premium text-white py-2 px-3">
            <i className="bi bi-plus-lg me-2"></i>Nuevo Miembro
          </Link>
        </div>
      </div>

      {/* Search Input Box */}
      <div className="search-container mb-4" style={{ maxWidth: '400px' }}>
        <div className="input-group">
          <span className="input-group-text bg-dark border-secondary border-end-0 px-3 text-muted" style={{ borderTopLeftRadius: '12px', borderBottomLeftRadius: '12px' }}>
            <i className="bi bi-search"></i>
          </span>
          <input
            type="text"
            className="form-control form-control-premium border-start-0 py-2"
            placeholder="Buscar por nombre o ID..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            style={{ borderTopRightRadius: '12px', borderBottomRightRadius: '12px' }}
          />
        </div>
      </div>

      {/* Users Card Table */}
      <div className="glass-card p-0" style={{ overflow: 'hidden' }}>
        <div className="table-responsive">
          <table className="table table-hover mb-0 text-white" style={{ background: 'transparent' }}>
            <thead>
              <tr style={{ background: 'rgba(15, 23, 42, 0.5)' }}>
                <th className="text-muted px-4 py-3" style={{ fontSize: '0.75rem', fontWeight: 600, letterSpacing: '0.05em' }}>ID</th>
                <th className="text-muted px-4 py-3" style={{ fontSize: '0.75rem', fontWeight: 600, letterSpacing: '0.05em' }}>Miembro</th>
                <th className="text-muted px-4 py-3" style={{ fontSize: '0.75rem', fontWeight: 600, letterSpacing: '0.05em' }}>Estado</th>
                <th className="text-muted px-4 py-3" style={{ fontSize: '0.75rem', fontWeight: 600, letterSpacing: '0.05em' }}>Vencimiento</th>
                <th className="text-muted px-4 py-3 text-end" style={{ fontSize: '0.75rem', fontWeight: 600, letterSpacing: '0.05em' }}>Acciones</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                /* LOADING STATE */
                <tr>
                  <td colSpan="5" className="text-center py-5 text-muted">
                    <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                    Cargando miembros...
                  </td>
                </tr>
              ) : error ? (
                /* ERROR STATE */
                <tr>
                  <td colSpan="5" className="text-center py-5 text-danger fw-bold">
                    ❌ {error}
                  </td>
                </tr>
              ) : filteredUsers.length === 0 ? (
                /* EMPTY STATE */
                <tr>
                  <td colSpan="5" className="text-center py-5 text-muted">
                    No se encontraron miembros.
                  </td>
                </tr>
              ) : (
                /* DATA ITERATION */
                filteredUsers.map((u) => {
                  const status = getStatus(u.exp);
                  const avatarUrl = u.image
                    ? `data:image/jpeg;base64,${u.image}`
                    : `https://ui-avatars.com/api/?name=${encodeURIComponent(u.name)}&background=6366f1&color=fff&size=128`;

                  return (
                    <tr
                      key={u.id}
                      className="user-row align-middle"
                      onClick={() => navigate(`/user?user_id=${u.id}`)}
                      style={{ cursor: 'pointer', transition: 'all 0.2s' }}
                    >
                      <td className="px-4 py-3 text-secondary fw-semibold">#{u.id}</td>
                      <td className="px-4 py-3">
                        <div className="d-flex align-items-center gap-3">
                          <img
                            src={avatarUrl}
                            className="user-img"
                            alt="Avatar"
                            style={{
                              width: '44px',
                              height: '44px',
                              borderRadius: '12px',
                              objectFit: 'cover',
                              border: '1px solid rgba(255,255,255,0.05)'
                            }}
                          />
                          <span className="fw-bold">{u.name}</span>
                        </div>
                      </td>
                      <td className="px-4 py-3">
                        <span className={`status-pill ${status.className}`}>
                          {status.label}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-secondary small">
                        {formatDate(u.exp)}
                      </td>
                      <td className="px-4 py-3 text-end">
                        <i className="bi bi-chevron-right text-muted"></i>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default ManageUsers;
