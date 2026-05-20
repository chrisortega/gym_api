import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const EditGym = () => {
  const { user, authFetch } = useAuth();

  // General state whiteboards
  const [gymName, setGymName] = useState('');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState({ text: '', type: '' });

  // Image file states
  const [logoFile, setLogoFile] = useState(null);
  const [backFile, setBackFile] = useState(null);

  // Previews urls (can be base64 strings from API, or temp blob URLs from local file uploads)
  const [logoPreview, setLogoPreview] = useState('/static/default-gym.png');
  const [backPreview, setBackPreview] = useState('/static/default-background.jpg');

  // Load gym details from Flask when page loads
  useEffect(() => {
    const loadGymData = async () => {
      if (!user || !user.gym_id) return;
      
      setLoading(true);
      setMessage({ text: '', type: '' });

      try {
        const res = await authFetch(`/api/gym/${user.gym_id}`);
        if (!res.ok) {
          throw new Error('Error al descargar los datos del gimnasio');
        }
        const data = await res.json();
        
        setGymName(data.name || '');
        if (data.image) setLogoPreview(`data:image/jpeg;base64,${data.image}`);
        if (data.back) setBackPreview(`data:image/jpeg;base64,${data.back}`);
      } catch (err) {
        setMessage({ text: '❌ ' + err.message, type: 'danger' });
      } finally {
        setLoading(false);
      }
    };

    loadGymData();
  }, [user]);

  // Handle local logo upload & generate instant preview
  const handleLogoChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setLogoFile(file);
      // Modern method: create a temporary URL representing the local file
      setLogoPreview(URL.createObjectURL(file));
    }
  };

  // Handle local background upload & generate instant preview
  const handleBackChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setBackFile(file);
      // Modern method: create a temporary URL representing the local file
      setBackPreview(URL.createObjectURL(file));
    }
  };

  // Submit edits as FormData (multipart/form-data)
  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!gymName.trim()) return;

    setSaving(true);
    setMessage({ text: '', type: '' });

    // 1. Initialize FormData container
    const formData = new FormData();
    formData.append('name', gymName);

    // 2. Append files if the user uploaded new ones
    if (logoFile) formData.append('image', logoFile);
    if (backFile) formData.append('back', backFile);

    try {
      // 3. Make fetch request. Note: We use authFetch but WITHOUT custom 'Content-Type' header!
      // authFetch handles authorization token insertion.
      const res = await authFetch(`/api/gym/${user.gym_id}`, {
        method: 'PUT',
        body: formData // Body is a FormData object
      });

      if (res.ok) {
        setMessage({ text: '✅ Cambios guardados correctamente.', type: 'success' });
        setTimeout(() => setMessage({ text: '', type: '' }), 3000);
      } else {
        throw new Error('Error al guardar cambios.');
      }
    } catch (err) {
      setMessage({ text: '❌ ' + err.message, type: 'danger' });
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="main-container">
      {/* Header section */}
      <div className="d-flex justify-content-between align-items-center mb-4 flex-wrap gap-3">
        <div>
          <h2 className="fw-bold text-white m-0">Mi Gimnasio</h2>
          <p className="text-muted small m-0">Personaliza la apariencia y nombre de tu gimnasio</p>
        </div>
        <Link to="/dashboard" className="btn btn-outline-light py-2 px-3 fw-bold" style={{ borderRadius: '12px' }}>
          <i className="bi bi-arrow-left me-2"></i>Volver
        </Link>
      </div>

      {/* Alert Banners */}
      {message.text && (
        <div className={`alert alert-${message.type} rounded-4 border-0 shadow mb-4`} role="alert">
          {message.text}
        </div>
      )}

      {loading ? (
        /* LOADING VIEW */
        <div className="glass-card text-center py-5">
          <span className="spinner-border text-primary me-2" role="status" aria-hidden="true"></span>
          Cargando configuración...
        </div>
      ) : (
        /* EDIT FORM */
        <form onSubmit={handleSubmit}>
          <div className="row g-4">
            
            {/* LEFT COLUMN: Visual Identity */}
            <div className="col-lg-6">
              <div className="glass-card h-100 d-flex flex-column gap-4">
                <h5 className="fw-bold m-0" style={{ color: '#818cf8' }}>
                  <i className="bi bi-palette me-2"></i>Identidad Visual
                </h5>
                
                {/* Logo section */}
                <div>
                  <label className="form-label text-muted small fw-bold text-uppercase mb-2">Logo del Gimnasio</label>
                  <div 
                    className="p-4 rounded-4 text-center d-flex flex-column align-items-center justify-content-center"
                    style={{ background: 'rgba(15, 23, 42, 0.4)', border: '2px dashed rgba(255,255,255,0.1)' }}
                  >
                    <img 
                      src={logoPreview} 
                      className="mb-3"
                      alt="Logo Preview" 
                      style={{
                        width: '100px',
                        height: '100px',
                        borderRadius: '20px',
                        objectFit: 'cover',
                        border: '2px solid rgba(255,255,255,0.1)',
                        background: 'white'
                      }}
                    />
                    <input 
                      type="file" 
                      className="form-control form-control-premium text-muted" 
                      accept="image/*"
                      onChange={handleLogoChange}
                    />
                  </div>
                </div>

                {/* Hero section */}
                <div>
                  <label className="form-label text-muted small fw-bold text-uppercase mb-2">Imagen de Portada (Hero)</label>
                  <div 
                    className="p-4 rounded-4 text-center d-flex flex-column align-items-center justify-content-center"
                    style={{ background: 'rgba(15, 23, 42, 0.4)', border: '2px dashed rgba(255,255,255,0.1)' }}
                  >
                    <img 
                      src={backPreview} 
                      className="mb-3 w-100"
                      alt="Hero Preview" 
                      style={{
                        maxHeight: '150px',
                        borderRadius: '12px',
                        objectFit: 'cover',
                        border: '2px solid rgba(255,255,255,0.1)',
                        background: 'white'
                      }}
                    />
                    <input 
                      type="file" 
                      className="form-control form-control-premium text-muted" 
                      accept="image/*"
                      onChange={handleBackChange}
                    />
                  </div>
                </div>

              </div>
            </div>

            {/* RIGHT COLUMN: Settings & Submit */}
            <div className="col-lg-6">
              <div className="glass-card h-100 d-flex flex-column justify-content-between gap-4">
                
                <div>
                  <h5 className="fw-bold mb-4" style={{ color: '#818cf8' }}>
                    <i className="bi bi-gear me-2"></i>Configuración General
                  </h5>
                  
                  <div className="mb-4">
                    <label className="form-label text-muted small fw-bold text-uppercase mb-2">Nombre del Gimnasio</label>
                    <input 
                      type="text" 
                      className="form-control form-control-premium fw-bold" 
                      value={gymName} 
                      onChange={(e) => setGymName(e.target.value)}
                      placeholder="Ej. Sparta Fitness"
                      required
                      disabled={saving}
                    />
                  </div>

                  <div className="p-4 rounded-4 d-flex gap-3" style={{ background: 'rgba(99, 102, 241, 0.1)', border: '1px solid rgba(99, 102, 241, 0.2)' }}>
                    <i className="bi bi-info-circle-fill" style={{ fontSize: '1.5rem', color: '#818cf8' }}></i>
                    <div>
                      <h6 className="fw-bold m-0 text-white">Información de Perfil</h6>
                      <p className="small text-muted mb-0 mt-1">
                        Esta información será visible para tus administradores y en el dashboard de entradas público.
                      </p>
                    </div>
                  </div>
                </div>

                <div className="pt-4">
                  <button 
                    type="submit" 
                    className="btn btn-premium text-white w-100 d-flex align-items-center justify-content-center py-3"
                    disabled={saving}
                  >
                    {saving ? (
                      <>
                        <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                        Guardando Cambios...
                      </>
                    ) : (
                      <>
                        <i className="bi bi-cloud-arrow-up me-2"></i>Guardar Cambios
                      </>
                    )}
                  </button>
                </div>

              </div>
            </div>

          </div>
        </form>
      )}
    </div>
  );
};

export default EditGym;
