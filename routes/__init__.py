from .users import users_bp
from .entries import entries_bp
from .biometrics import biometrics_bp
from .gyms import gyms_bp
from .auth import auth_bp
from .api import api_bp
from .superadmin import superadmin_bp

all_blueprints = [users_bp, entries_bp, biometrics_bp, gyms_bp, auth_bp, api_bp, superadmin_bp]
