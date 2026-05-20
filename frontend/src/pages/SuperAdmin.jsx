import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useEffect } from 'react';

const SuperAdmin = () => {
    const [userId, setUserId] = useState('');
    const { user, authFetch } = useAuth();
    const is_super_admin = user.is_super_admin;
    const [adminMessage, setAdminMessage] = useState('Acceso denegado');
    const [gyms, setAdmins] = useState([]);
    const [adminEmail, setAdminEmail] = useState('');
    const navigate = useNavigate();
    const [isSaving, setIsSaving] = useState(false);
    if (is_super_admin == false) {
        navigate('/');
    }

    const handleEmailChange = (gymId, newEmail) => {

        setAdmins(prevGyms =>
            prevGyms.map(gym =>
                gym.gym_id === gymId ? { ...gym, admin_email: newEmail } : gym
            )
        );
    };
    const handleSaveEmail = async (gymId, email) => {
        setIsSaving(true);
        try {
            const res = await authFetch(`/api/superadmin/admins/${gymId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ email: email })
            });
            if (!res.ok) {
                throw new Error('Error al guardar el correo');
            }
        } catch (err) {
            console.error(err);
        } finally {
            setIsSaving(false);
        }
    };
    useEffect(() => {
        const fetchAdmins = async () => {

            try {
                const res = await authFetch(`/api/superadmin/gyms`);
                if (!res.ok) {
                    throw new Error('Error al cargar la lista de gyms');
                }
                const data = await res.json();
                setAdmins(data);
            } catch (err) {
                setAdminMessage(err.message || 'Error de red o conexión.');
            }
        };

        fetchAdmins();
    }, []);

    const adminGyms = gyms.map((u) => {
        return (
            <div key={u.gym_id} id={u.gym_id} className="glass-card w-100 mb-3" >
                <p>Gym: {u.gym_name}</p>
                <input
                    className='glass-card w-100'
                    value={u.admin_email || ''}
                    onChange={(e) => handleEmailChange(u.gym_id, e.target.value)}
                />
                <button onClick={() => handleSaveEmail(u.gym_id, u.admin_email)} className='glass-card w-100'>Guardar</button>        </div>
        )
    });

    return (
        <div style={{ display: is_super_admin ? 'block' : 'none' }} className="main-container" >
            <div className="glass-card w-100 mb-4" >
                {is_super_admin ? 'Super Admin' : adminMessage}
                {isSaving ? 'Guardando...' : ''}
            </div >
            {adminGyms}
        </div >
    )


}



export default SuperAdmin;