from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import User, ProviderProfile, FitnessClass, Booking, Review, Report, Discussion, Notification
from datetime import datetime, timedelta
from functools import wraps
from sqlalchemy import func

admin_bp = Blueprint('admin', __name__)


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash('Admin access only.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function


@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    stats = {
        'total_users': User.query.count(),
        'total_members': User.query.filter_by(role='member').count(),
        'total_providers': User.query.filter_by(role='provider').count(),
        'pending_providers': ProviderProfile.query.filter_by(is_approved=False).count(),
        'total_classes': FitnessClass.query.count(),
        'total_bookings': Booking.query.count(),
        'pending_reports': Report.query.filter_by(status='pending').count(),
        'flagged_reviews': Review.query.filter_by(is_flagged=True).count(),
    }
    recent_users = User.query.order_by(User.created_at.desc()).limit(8).all()
    pending_providers = ProviderProfile.query.filter_by(is_approved=False).all()
    pending_reports = Report.query.filter_by(status='pending').order_by(Report.created_at.desc()).limit(5).all()
    recent_bookings = Booking.query.order_by(Booking.booking_date.desc()).limit(8).all()
    return render_template('admin/dashboard.html', stats=stats, recent_users=recent_users,
                           pending_providers=pending_providers, pending_reports=pending_reports,
                           recent_bookings=recent_bookings, title='Admin Dashboard')


@admin_bp.route('/providers')
@login_required
@admin_required
def providers():
    filter_status = request.args.get('status', 'all')
    query = ProviderProfile.query
    if filter_status == 'pending':
        query = query.filter_by(is_approved=False)
    elif filter_status == 'approved':
        query = query.filter_by(is_approved=True)
    providers = query.order_by(ProviderProfile.id.desc()).paginate(
        page=request.args.get('page', 1, type=int), per_page=15, error_out=False)
    return render_template('admin/providers.html', providers=providers,
                           filter_status=filter_status, title='Manage Providers')


@admin_bp.route('/provider/<int:provider_id>/approve', methods=['POST'])
@login_required
@admin_required
def approve_provider(provider_id):
    provider = ProviderProfile.query.get_or_404(provider_id)
    provider.is_approved = True
    provider.approval_date = datetime.utcnow()
    notif = Notification(user_id=provider.user_id,
                         title='Your provider account has been approved! ✅',
                         message='You can now list classes on BloomWell.',
                         notif_type='system')
    db.session.add(notif)
    db.session.commit()
    flash(f'{provider.business_name} has been approved! ✅', 'success')
    return redirect(url_for('admin.providers'))


@admin_bp.route('/provider/<int:provider_id>/verify', methods=['POST'])
@login_required
@admin_required
def verify_provider(provider_id):
    provider = ProviderProfile.query.get_or_404(provider_id)
    provider.verified_badge = not provider.verified_badge
    db.session.commit()
    status = 'verified ✓' if provider.verified_badge else 'unverified'
    flash(f'{provider.business_name} is now {status}.', 'success')
    return redirect(url_for('admin.providers'))


@admin_bp.route('/provider/<int:provider_id>/reject', methods=['POST'])
@login_required
@admin_required
def reject_provider(provider_id):
    provider = ProviderProfile.query.get_or_404(provider_id)
    provider.user.is_active = False
    db.session.commit()
    flash(f'{provider.business_name} has been rejected.', 'warning')
    return redirect(url_for('admin.providers'))


@admin_bp.route('/users')
@login_required
@admin_required
def users():
    role_filter = request.args.get('role', '')
    search = request.args.get('q', '')
    query = User.query
    if role_filter:
        query = query.filter_by(role=role_filter)
    if search:
        query = query.filter(
            User.email.ilike(f'%{search}%') | User.full_name.ilike(f'%{search}%') |
            User.username.ilike(f'%{search}%')
        )
    users = query.order_by(User.created_at.desc()).paginate(
        page=request.args.get('page', 1, type=int), per_page=20, error_out=False)
    return render_template('admin/users.html', users=users, role_filter=role_filter,
                           search=search, title='Manage Users')


@admin_bp.route('/user/<int:user_id>/toggle', methods=['POST'])
@login_required
@admin_required
def toggle_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash('You cannot suspend yourself.', 'danger')
        return redirect(url_for('admin.users'))
    user.is_active = not user.is_active
    db.session.commit()
    status = 'activated' if user.is_active else 'suspended'
    flash(f'User {user.username} has been {status}.', 'info')
    return redirect(url_for('admin.users'))


@admin_bp.route('/reports')
@login_required
@admin_required
def reports():
    status_filter = request.args.get('status', 'pending')
    query = Report.query if status_filter == 'all' else Report.query.filter_by(status=status_filter)
    reports = query.order_by(Report.created_at.desc()).paginate(
        page=request.args.get('page', 1, type=int), per_page=15, error_out=False)
    return render_template('admin/reports.html', reports=reports,
                           status_filter=status_filter, title='Reports & Moderation')


@admin_bp.route('/report/<int:report_id>/<string:action>', methods=['POST'])
@login_required
@admin_required
def resolve_report(report_id, action):
    report = Report.query.get_or_404(report_id)
    if action in ['resolved', 'dismissed']:
        report.status = action
        report.resolved_at = datetime.utcnow()
        report.resolved_by = current_user.id
        db.session.commit()
        flash(f'Report marked as {action}.', 'success')
    return redirect(url_for('admin.reports'))


@admin_bp.route('/discussions')
@login_required
@admin_required
def discussions():
    discussions = Discussion.query.order_by(Discussion.created_at.desc()).paginate(
        page=request.args.get('page', 1, type=int), per_page=20, error_out=False)
    return render_template('admin/discussions.html', discussions=discussions, title='Moderate Discussions')


@admin_bp.route('/discussion/<int:discussion_id>/toggle', methods=['POST'])
@login_required
@admin_required
def toggle_discussion(discussion_id):
    d = Discussion.query.get_or_404(discussion_id)
    d.is_active = not d.is_active
    db.session.commit()
    flash(f'Discussion {"restored" if d.is_active else "hidden"}.', 'info')
    return redirect(url_for('admin.discussions'))


@admin_bp.route('/discussion/<int:discussion_id>/pin', methods=['POST'])
@login_required
@admin_required
def pin_discussion(discussion_id):
    d = Discussion.query.get_or_404(discussion_id)
    d.is_pinned = not d.is_pinned
    db.session.commit()
    flash(f'Discussion {"pinned 📌" if d.is_pinned else "unpinned"}.', 'success')
    return redirect(url_for('admin.discussions'))


@admin_bp.route('/reviews')
@login_required
@admin_required
def reviews():
    flagged_only = request.args.get('flagged', False)
    query = Review.query.filter_by(is_flagged=True) if flagged_only else Review.query
    reviews = query.order_by(Review.created_at.desc()).paginate(
        page=request.args.get('page', 1, type=int), per_page=15, error_out=False)
    return render_template('admin/reviews.html', reviews=reviews, title='Manage Reviews')


@admin_bp.route('/review/<int:review_id>/toggle', methods=['POST'])
@login_required
@admin_required
def toggle_review(review_id):
    review = Review.query.get_or_404(review_id)
    review.is_approved = not review.is_approved
    review.is_flagged = False
    db.session.commit()
    status = 'approved' if review.is_approved else 'hidden'
    flash(f'Review {status}.', 'info')
    return redirect(url_for('admin.reviews'))


@admin_bp.route('/announce', methods=['POST'])
@login_required
@admin_required
def announce():
    message = request.form.get('message', '').strip()
    if message:
        members = User.query.filter_by(is_active=True, role='member').all()
        for u in members:
            db.session.add(Notification(
                user_id=u.id,
                title='📢 Admin Announcement',
                message=message,
                notif_type='announcement'
            ))
        db.session.commit()
        flash(f'Announcement sent to {len(members)} members!', 'success')
    else:
        flash('Please enter a message.', 'warning')
    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/analytics')
@login_required
@admin_required
def analytics():
    activity_stats = db.session.query(
        FitnessClass.activity_type, func.count(FitnessClass.id).label('count')
    ).group_by(FitnessClass.activity_type).all()

    booking_stats = db.session.query(
        Booking.status, func.count(Booking.id).label('count')
    ).group_by(Booking.status).all()

    city_stats = db.session.query(
        FitnessClass.city, func.count(FitnessClass.id).label('count')
    ).filter(FitnessClass.city.isnot(None)).group_by(FitnessClass.city).all()

    top_classes = FitnessClass.query.order_by(FitnessClass.current_bookings.desc()).limit(5).all()

    top_providers = ProviderProfile.query.filter(
        ProviderProfile.total_reviews > 0
    ).order_by(ProviderProfile.average_rating.desc()).limit(5).all()

    six_ago = datetime.utcnow() - timedelta(days=180)
    monthly_signups = db.session.query(
        func.strftime('%Y-%m', User.created_at), func.count(User.id)
    ).filter(User.created_at >= six_ago).group_by(
        func.strftime('%Y-%m', User.created_at)
    ).order_by(func.strftime('%Y-%m', User.created_at)).all()

    kpis = {
        'total_users': User.query.count(),
        'total_bookings': Booking.query.count(),
        'total_classes': FitnessClass.query.count(),
        'total_providers': ProviderProfile.query.filter_by(is_approved=True).count(),
        'avg_rating': round(db.session.query(func.avg(Review.rating)).scalar() or 0, 1),
        'open_reports': Report.query.filter_by(status='pending').count(),
    }

    return render_template('admin/analytics.html',
                           kpis=kpis,
                           activity_stats=activity_stats,
                           booking_stats=booking_stats,
                           city_stats=city_stats,
                           top_classes=top_classes,
                           top_providers=top_providers,
                           monthly_signups=monthly_signups,
                           title='Platform Analytics')
