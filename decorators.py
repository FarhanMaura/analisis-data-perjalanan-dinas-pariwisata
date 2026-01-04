"""
Custom decorators for role-based access control
"""
from functools import wraps
from flask import redirect, url_for, flash
from flask_login import current_user


def role_required(*roles):
    """
    Decorator to require specific role(s) for a route
    Usage: @role_required('admin') or @role_required('admin', 'hotel')
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Silakan login terlebih dahulu', 'error')
                return redirect(url_for('login'))
            
            if current_user.role not in roles:
                flash('Anda tidak memiliki akses ke halaman ini', 'error')
                # Redirect based on role
                if current_user.role == 'admin':
                    return redirect(url_for('admin_home'))
                elif current_user.role == 'hotel':
                    return redirect(url_for('hotel_home'))
                elif current_user.role == 'tourism':
                    return redirect(url_for('tourism_home'))
                else:
                    return redirect(url_for('login'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator
