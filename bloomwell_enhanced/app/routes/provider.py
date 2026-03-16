from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import FitnessClass, ClassSchedule, Booking, Review, ProviderProfile, Notification
from app.forms import ProviderProfileForm, ClassForm, ScheduleForm
from app.utils import save_image
from functools import wraps
from datetime import datetime

provider_bp = Blueprint('provider', __name__)


def provider_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_provider():
            flash('Access restricted to providers.', 'warning')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function


@provider_bp.route('/dashboard')
@login_required
@provider_required
def dashboard():
    profile = current_user.provider_profile
    classes = []
    recent_bookings = []
    total_bookings = 0
    if profile:
        classes = profile.classes.filter_by(is_active=True).all()
        for cls in classes:
            total_bookings += cls.current_bookings
        recent_bookings = Booking.query.join(FitnessClass).filter(
            FitnessClass.provider_id == profile.id).order_by(
            Booking.booking_date.desc()).limit(8).all()
    pending_reviews = Review.query.filter_by(provider_id=profile.id if profile else 0,
                                              provider_response=None).count() if profile else 0
    return render_template('provider/dashboard.html', profile=profile, classes=classes,
                           recent_bookings=recent_bookings, total_bookings=total_bookings,
                           pending_reviews=pending_reviews, title='Provider Dashboard')


@provider_bp.route('/profile', methods=['GET', 'POST'])
@login_required
@provider_required
def edit_profile():
    profile = current_user.provider_profile
    form = ProviderProfileForm(obj=profile)
    if form.validate_on_submit():
        if not profile:
            profile = ProviderProfile(user_id=current_user.id)
            db.session.add(profile)
        profile.business_name = form.business_name.data
        profile.business_type = form.business_type.data
        profile.description = form.description.data
        profile.address = form.address.data
        profile.city = form.city.data
        profile.postcode = form.postcode.data
        profile.website = form.website.data
        profile.instagram = form.instagram.data
        profile.is_women_only = form.is_women_only.data
        if form.logo_image.data:
            profile.logo_image = save_image(form.logo_image.data, 'logos', (300, 300))
        if form.banner_image.data:
            profile.banner_image = save_image(form.banner_image.data, 'banners', (1200, 400))
        db.session.commit()
        flash('Profile updated! Pending admin approval for verification badge.', 'success')
        return redirect(url_for('provider.dashboard'))
    return render_template('provider/edit_profile.html', form=form, title='Edit Provider Profile')


@provider_bp.route('/classes')
@login_required
@provider_required
def my_classes():
    profile = current_user.provider_profile
    classes = profile.classes.all() if profile else []
    return render_template('provider/my_classes.html', classes=classes, title='My Classes')


@provider_bp.route('/class/new', methods=['GET', 'POST'])
@login_required
@provider_required
def new_class():
    profile = current_user.provider_profile
    if not profile or not profile.is_approved:
        flash('Your provider profile must be approved before listing classes.', 'warning')
        return redirect(url_for('provider.dashboard'))
    form = ClassForm()
    if form.validate_on_submit():
        fitness_class = FitnessClass(provider_id=profile.id)
        _populate_class(fitness_class, form)
        db.session.add(fitness_class)
        db.session.commit()
        flash('Class listed successfully! 🎉', 'success')
        return redirect(url_for('provider.my_classes'))
    return render_template('provider/class_form.html', form=form, title='Add New Class', action='new')


@provider_bp.route('/class/<int:class_id>/edit', methods=['GET', 'POST'])
@login_required
@provider_required
def edit_class(class_id):
    fitness_class = FitnessClass.query.get_or_404(class_id)
    if fitness_class.provider.user_id != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('provider.my_classes'))
    form = ClassForm(obj=fitness_class)
    if form.validate_on_submit():
        _populate_class(fitness_class, form)
        db.session.commit()
        # Notify confirmed bookers of the update
        for b in fitness_class.bookings.filter_by(status='confirmed').all():
            db.session.add(Notification(
                user_id=b.user_id,
                title=f'Class Updated: {fitness_class.title}',
                message='Details for a class you booked have been updated. Please check.',
                notif_type='update'
            ))
        db.session.commit()
        flash('Class updated! Bookers have been notified.', 'success')
        return redirect(url_for('provider.my_classes'))
    return render_template('provider/class_form.html', form=form, title='Edit Class', action='edit',
                           fitness_class=fitness_class)


@provider_bp.route('/class/<int:class_id>/delete', methods=['POST'])
@login_required
@provider_required
def delete_class(class_id):
    fitness_class = FitnessClass.query.get_or_404(class_id)
    if fitness_class.provider.user_id != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('provider.my_classes'))
    fitness_class.is_active = False
    db.session.commit()
    flash('Class removed.', 'info')
    return redirect(url_for('provider.my_classes'))


@provider_bp.route('/class/<int:class_id>/schedule', methods=['GET', 'POST'])
@login_required
@provider_required
def manage_schedule(class_id):
    fitness_class = FitnessClass.query.get_or_404(class_id)
    if fitness_class.provider.user_id != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('provider.my_classes'))
    form = ScheduleForm()
    if form.validate_on_submit():
        schedule = ClassSchedule(
            class_id=class_id,
            date=form.date.data,
            start_time=form.start_time.data,
            end_time=form.end_time.data,
            available_spots=form.available_spots.data or fitness_class.max_capacity
        )
        db.session.add(schedule)
        db.session.commit()
        flash('Session scheduled!', 'success')
        return redirect(url_for('provider.manage_schedule', class_id=class_id))
    schedules = fitness_class.schedules.order_by(ClassSchedule.date.desc()).all()
    return render_template('provider/schedule.html', form=form, fitness_class=fitness_class,
                           schedules=schedules, title='Manage Schedule')


@provider_bp.route('/schedule/<int:schedule_id>/cancel', methods=['POST'])
@login_required
@provider_required
def cancel_schedule(schedule_id):
    schedule = ClassSchedule.query.get_or_404(schedule_id)
    if schedule.fitness_class.provider.user_id != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('provider.my_classes'))
    schedule.is_cancelled = True
    schedule.cancellation_reason = request.form.get('reason', 'Cancelled by provider')
    for b in schedule.bookings.filter_by(status='confirmed').all():
        b.status = 'cancelled'
        db.session.add(Notification(
            user_id=b.user_id,
            title=f'Class Cancelled: {schedule.fitness_class.title}',
            message=f'The session on {schedule.date.strftime("%d %b %Y")} has been cancelled.',
            notif_type='update'
        ))
    db.session.commit()
    flash('Session cancelled and members notified.', 'info')
    return redirect(url_for('provider.manage_schedule', class_id=schedule.class_id))


@provider_bp.route('/bookings')
@login_required
@provider_required
def bookings():
    profile = current_user.provider_profile
    if not profile:
        return redirect(url_for('provider.dashboard'))
    status_filter = request.args.get('status', 'all')
    q = Booking.query.join(FitnessClass).filter(FitnessClass.provider_id == profile.id)
    if status_filter != 'all':
        q = q.filter(Booking.status == status_filter)
    all_bookings = q.order_by(Booking.booking_date.desc()).paginate(
        page=request.args.get('page', 1, type=int), per_page=20, error_out=False)
    return render_template('provider/bookings.html', bookings=all_bookings,
                           status_filter=status_filter, title='Bookings')


@provider_bp.route('/attendance/<int:booking_id>/<string:status>', methods=['POST'])
@login_required
@provider_required
def mark_attendance(booking_id, status):
    booking = Booking.query.get_or_404(booking_id)
    if status in ['attended', 'no_show']:
        booking.status = status
        if status == 'attended' and booking.user.member_profile:
            booking.user.member_profile.total_sessions_attended += 1
        db.session.commit()
        flash(f'Attendance marked as {status.replace("_", " ")}.', 'success')
    return redirect(url_for('provider.bookings'))


@provider_bp.route('/reviews')
@login_required
@provider_required
def my_reviews():
    profile = current_user.provider_profile
    reviews = Review.query.filter_by(provider_id=profile.id).order_by(
        Review.created_at.desc()).paginate(
        page=request.args.get('page', 1, type=int), per_page=10, error_out=False) if profile else None
    return render_template('provider/reviews.html', reviews=reviews, title='Reviews')


@provider_bp.route('/review/<int:review_id>/respond', methods=['POST'])
@login_required
@provider_required
def respond_review(review_id):
    review = Review.query.get_or_404(review_id)
    if review.provider_id != current_user.provider_profile.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('provider.my_reviews'))
    response_text = request.form.get('response', '').strip()
    if response_text:
        review.provider_response = response_text
        review.provider_response_date = datetime.utcnow()
        db.session.commit()
        flash('Response posted successfully!', 'success')
    else:
        flash('Response cannot be empty.', 'warning')
    return redirect(url_for('provider.my_reviews'))


def _populate_class(fitness_class, form):
    fitness_class.title = form.title.data
    fitness_class.description = form.description.data
    fitness_class.activity_type = form.activity_type.data
    fitness_class.difficulty_level = form.difficulty_level.data
    fitness_class.duration_minutes = form.duration_minutes.data
    fitness_class.max_capacity = form.max_capacity.data
    fitness_class.price = 0 if form.is_free.data else form.price.data
    fitness_class.is_free = form.is_free.data
    fitness_class.is_online = form.is_online.data
    fitness_class.is_women_only = form.is_women_only.data
    fitness_class.location = form.location.data
    fitness_class.city = form.city.data
    fitness_class.postcode = form.postcode.data
    fitness_class.language = form.language.data
    fitness_class.accessibility_info = form.accessibility_info.data
    if form.image.data:
        fitness_class.image = save_image(form.image.data, 'classes', (800, 500))
    # Save cover image URL if provided
    if form.cover_image_url.data and form.cover_image_url.data.startswith('http'):
        fitness_class.cover_image_url = form.cover_image_url.data
    elif not form.cover_image_url.data and not fitness_class.cover_image_url:
        # Auto-assign default image based on activity type
        defaults = {
            'yoga': 'https://images.unsplash.com/photo-1588286840104-8957b019727f?w=700&q=80',
            'meditation': 'https://images.unsplash.com/photo-1591228127791-8e2eaef098d3?w=700&q=80',
            'pilates': 'https://images.unsplash.com/photo-1518611012118-696072aa579a?w=700&q=80',
            'strength': 'https://images.unsplash.com/photo-1554284126-aa88f22d8b74?w=700&q=80',
            'hiit': 'https://images.unsplash.com/photo-1518310383802-640c2de311b2?w=700&q=80',
            'walking_group': 'https://images.unsplash.com/photo-1476480862126-209bfaa8edc8?w=700&q=80',
            'mental_wellbeing': 'https://images.unsplash.com/photo-1547592166-23ac45744acd?w=700&q=80',
            'dance': 'https://images.unsplash.com/photo-1545959570-a94084071b5d?w=700&q=80',
            'nutrition': 'https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=700&q=80',
            'boxing': 'https://images.unsplash.com/photo-1549719386-74dfcbf7dbed?w=700&q=80',
            'other': 'https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=700&q=80',
        }
        fitness_class.cover_image_url = defaults.get(form.activity_type.data, '')
