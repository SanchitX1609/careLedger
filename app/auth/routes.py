from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from app.auth import auth_bp
from app.auth.forms import LoginForm, RegistrationForm, ChangePasswordForm, UserProfileForm, UserManagementForm
from app.models import User, Role, Orphanage
from app import db
from datetime import datetime
import logging

# Set up logging
logger = logging.getLogger(__name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        
        if user and user.check_password(form.password.data):
            if not user.is_active:
                flash('Your account has been deactivated. Please contact an administrator.', 'error')
                return render_template('auth/login.html', form=form)
            
            # Update last login time
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            login_user(user, remember=form.remember_me.data)
            
            # Redirect to next page or dashboard
            next_page = request.args.get('next')
            if not next_page or not next_page.startswith('/'):
                if user.orphanage_id:
                    next_page = url_for('main.api_dashboard', orphanage_id=user.orphanage_id)
                elif user.has_role('admin'):  # Admin user without a specific orphanage
                    next_page = url_for('auth.users') # Redirect to user management page
                else:
                    # Non-admin user without an orphanage_id
                    flash('Your user profile is not associated with an orphanage. Please contact an administrator or update your profile if applicable.', 'warning')
                    next_page = url_for('auth.profile') # Redirect to profile page
            
            flash(f'Welcome back, {user.get_full_name()}!', 'success')
            logger.info(f'User {user.username} logged in successfully')
            return redirect(next_page)
        else:
            flash('Invalid username or password.', 'error')
            logger.warning(f'Failed login attempt for username: {form.username.data}')
    
    return render_template('auth/login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    username = current_user.username
    logout_user()
    flash('You have been logged out.', 'info')
    logger.info(f'User {username} logged out')
    return redirect(url_for('auth.login'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    # Only allow registration if user is admin or no users exist
    if User.query.count() > 0 and (not current_user.is_authenticated or not current_user.has_role('admin')):
        flash('Registration is restricted to administrators.', 'error')
        return redirect(url_for('auth.login'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        # Create new user
        user = User(
            username=form.username.data,
            email=form.email.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            role_id=form.role_id.data,
            orphanage_id=form.orphanage_id.data if form.orphanage_id.data != 0 else None
        )
        user.set_password(form.password.data)
        
        db.session.add(user)
        db.session.commit()
        
        flash(f'User {user.username} has been registered successfully!', 'success')
        logger.info(f'New user registered: {user.username} by {current_user.username if current_user.is_authenticated else "system"}')
        
        # If this is the first user, redirect to login
        if User.query.count() == 1:
            flash('First user created! Please log in.', 'info')
            return redirect(url_for('auth.login'))
        
        return redirect(url_for('main.dashboard'))
    
    return render_template('auth/register.html', form=form)

@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = UserProfileForm(current_user.email)
    password_form = ChangePasswordForm()
    
    # Handle profile form submission
    if form.validate_on_submit() and 'profile_submit' in request.form:
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        current_user.email = form.email.data
        db.session.commit()
        
        flash('Your profile has been updated!', 'success')
        return redirect(url_for('auth.profile'))
    
    # Handle password change form submission
    elif password_form.validate_on_submit() and 'password_submit' in request.form:
        if current_user.check_password(password_form.current_password.data):
            current_user.set_password(password_form.new_password.data)
            db.session.commit()
            flash('Your password has been updated!', 'success')
            logger.info(f'User {current_user.username} changed password from profile page')
            return redirect(url_for('auth.profile'))
        else:
            flash('Invalid current password.', 'error')
    
    elif request.method == 'GET':
        form.first_name.data = current_user.first_name
        form.last_name.data = current_user.last_name
        form.email.data = current_user.email
    
    return render_template('auth/profile.html', form=form, password_form=password_form)

@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    
    if form.validate_on_submit():
        if current_user.check_password(form.current_password.data):
            current_user.set_password(form.new_password.data)
            db.session.commit()
            flash('Your password has been updated!', 'success')
            logger.info(f'User {current_user.username} changed password')
            return redirect(url_for('auth.profile'))
        else:
            flash('Invalid current password.', 'error')
    
    return render_template('auth/change_password.html', form=form)

@auth_bp.route('/users', methods=['GET', 'POST'])
@login_required
def users():
    if not current_user.has_role('admin'):
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('main.dashboard'))
    
    form = UserManagementForm()
    
    if form.validate_on_submit():
        # Create new user from form data
        user = User(
            username=form.username.data,
            email=form.email.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            is_active=form.is_active.data
        )
        user.set_password(form.password.data)
        
        # Set role
        role = Role.query.get(form.role_id.data)
        if role:
            user.add_role(role)
        
        # Set orphanage if selected
        if form.orphanage_id.data and form.orphanage_id.data != 0:
            orphanage = Orphanage.query.get(form.orphanage_id.data)
            if orphanage:
                user.orphanage = orphanage
        
        db.session.add(user)
        db.session.commit()
        
        flash('User created successfully!', 'success')
        return redirect(url_for('auth.users'))
    
    users = User.query.all()
    return render_template('auth/users.html', users=users, form=form)

@auth_bp.route('/users/<int:user_id>/toggle-active')
@login_required
def toggle_user_active(user_id):
    if not current_user.has_role('admin'):
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('main.dashboard'))
    
    user = User.query.get_or_404(user_id)
    
    if user.id == current_user.id:
        flash('You cannot deactivate your own account.', 'error')
        return redirect(url_for('auth.users'))
    
    user.is_active = not user.is_active
    db.session.commit()
    
    status = 'activated' if user.is_active else 'deactivated'
    flash(f'User {user.username} has been {status}.', 'success')
    logger.info(f'User {user.username} {status} by {current_user.username}')
    
    return redirect(url_for('auth.users'))
