import React from 'react';
import { NavLink, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const MobileNav = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  if (!user) return null;

  const currentPath = location.pathname;

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  return (
    <nav className="mobile-nav">


      <NavLink
        to="/myperfil"
        className={`mobile-nav-item ${currentPath === '/myperfil' ? 'active' : ''}`}
      >
        <i className="bi bi-person-badge-fill"></i>
        <span>Perfil</span>
      </NavLink>


    </nav>
  );
};

export default MobileNav;
