from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User, MemberProfile, ProviderProfile
from app.forms import LoginForm, RegisterForm

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user and user.check_password(form.password.data):
            if not user.is_active:
                flash('Your account has been suspended. Please contact support.', 'danger')
                return redirect(url_for('auth.login'))
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            flash(f'Welcome back, {user.full_name or user.username}! 💜', 'success')
            if next_page:
                return redirect(next_page)
            if user.is_admin():
                return redirect(url_for('admin.dashboard'))
            elif user.is_provider():
                return redirect(url_for('provider.dashboard'))
            else:
                return redirect(url_for('member.dashboard'))
        flash('Incorrect email or password. Please try again.', 'danger')
    return render_template('auth/login.html', form=form, title='Sign In')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(
            email=form.email.data.lower(),
            username=form.username.data,
            full_name=form.full_name.data,
            role=form.role.data
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.flush()

        if form.role.data == 'member':
            profile = MemberProfile(user_id=user.id)
            db.session.add(profile)
        elif form.role.data == 'provider':
            profile = ProviderProfile(user_id=user.id, business_name=form.full_name.data)
            db.session.add(profile)

        db.session.commit()
        flash('Account created successfully! Please sign in.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form, title='Create Account')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been signed out safely.', 'info')
    return redirect(url_for('main.index'))
