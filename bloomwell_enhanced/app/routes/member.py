from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import Booking, FitnessClass, ClassSchedule, Review, Discussion, DiscussionReply, Notification, Report
from app.forms import EditProfileForm, MemberPreferencesForm, ReviewForm, DiscussionForm, ReplyForm, ReportForm
from app.utils import save_image, generate_confirmation_code
from functools import wraps
from datetime import datetime

member_bp = Blueprint('member', __name__)


def member_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_member():
            flash('Access restricted to members.', 'warning')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function


@member_bp.route('/dashboard')
@login_required
@member_required
def dashboard():
    bookings = current_user.bookings.order_by(Booking.booking_date.desc()).limit(5).all()
    notifications = Notification.query.filter_by(user_id=current_user.id, is_read=False).order_by(
        Notification.created_at.desc()).limit(5).all()
    profile = current_user.member_profile
    return render_template('member/dashboard.html',
                           bookings=bookings,
                           notifications=notifications,
                           profile=profile,
                           title='My Dashboard')


@member_bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
@member_required
def edit_profile():
    form = EditProfileForm(obj=current_user)
    if form.validate_on_submit():
        current_user.full_name = form.full_name.data
        current_user.bio = form.bio.data
        current_user.location = form.location.data
        current_user.phone = form.phone.data
        if form.profile_image.data:
            current_user.profile_image = save_image(form.profile_image.data, 'avatars', (300, 300))
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('member.dashboard'))
    return render_template('member/edit_profile.html', form=form, title='Edit Profile')


@member_bp.route('/preferences', methods=['GET', 'POST'])
@login_required
@member_required
def preferences():
    profile = current_user.member_profile
    form = MemberPreferencesForm(obj=profile)
    if form.validate_on_submit():
        profile.preferred_activities = form.preferred_activities.data
        profile.fitness_goals = form.fitness_goals.data
        profile.age_group = form.age_group.data
        profile.language_preference = form.language_preference.data
        profile.cultural_preferences = form.cultural_preferences.data
        db.session.commit()
        flash('Preferences saved!', 'success')
        return redirect(url_for('member.dashboard'))
    return render_template('member/preferences.html', form=form, title='My Preferences')


@member_bp.route('/book/<int:class_id>', methods=['POST'])
@login_required
@member_required
def book_class(class_id):
    fitness_class = FitnessClass.query.get_or_404(class_id)
    schedule_id = request.form.get('schedule_id', type=int)

    existing = Booking.query.filter_by(user_id=current_user.id, class_id=class_id, status='confirmed').first()
    if existing:
        flash('You have already booked this class.', 'warning')
        return redirect(url_for('main.class_detail', class_id=class_id))

    if fitness_class.current_bookings >= fitness_class.max_capacity:
        flash('Sorry, this class is fully booked.', 'danger')
        return redirect(url_for('main.class_detail', class_id=class_id))

    booking = Booking(
        user_id=current_user.id,
        class_id=class_id,
        schedule_id=schedule_id,
        confirmation_code=generate_confirmation_code(),
        status='confirmed'
    )
    fitness_class.current_bookings += 1

    notif = Notification(
        user_id=current_user.id,
        title='Booking Confirmed! 🎉',
        message=f'Your spot in "{fitness_class.title}" is confirmed. Code: {booking.confirmation_code}',
        notif_type='booking'
    )
    db.session.add_all([booking, notif])
    db.session.commit()
    flash(f'Booking confirmed! Your code: {booking.confirmation_code} 🎉', 'success')
    return redirect(url_for('member.my_bookings'))


@member_bp.route('/bookings')
@login_required
@member_required
def my_bookings():
    status_filter = request.args.get('status', 'all')
    q = current_user.bookings
    if status_filter != 'all':
        q = q.filter_by(status=status_filter)
    bookings = q.order_by(Booking.booking_date.desc()).paginate(
        page=request.args.get('page', 1, type=int), per_page=10, error_out=False)
    return render_template('member/my_bookings.html', bookings=bookings,
                           status_filter=status_filter, title='My Bookings')


@member_bp.route('/booking/cancel/<int:booking_id>', methods=['POST'])
@login_required
@member_required
def cancel_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    if booking.user_id != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('member.my_bookings'))
    booking.status = 'cancelled'
    booking.fitness_class.current_bookings = max(0, booking.fitness_class.current_bookings - 1)
    notif = Notification(
        user_id=current_user.id,
        title='Booking Cancelled',
        message=f'Your booking for "{booking.fitness_class.title}" has been cancelled.',
        notif_type='booking'
    )
    db.session.add(notif)
    db.session.commit()
    flash('Booking cancelled successfully.', 'info')
    return redirect(url_for('member.my_bookings'))


@member_bp.route('/booking/reschedule/<int:booking_id>', methods=['GET', 'POST'])
@login_required
@member_required
def reschedule_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    if booking.user_id != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('member.my_bookings'))
    schedules = booking.fitness_class.schedules.filter_by(is_cancelled=False).all()
    if request.method == 'POST':
        new_schedule_id = request.form.get('schedule_id', type=int)
        if new_schedule_id:
            booking.schedule_id = new_schedule_id
            db.session.commit()
            flash('Booking rescheduled successfully!', 'success')
            return redirect(url_for('member.my_bookings'))
        flash('Please select a time slot.', 'warning')
    return render_template('member/reschedule.html', booking=booking,
                           schedules=schedules, title='Reschedule Booking')


@member_bp.route('/review/<int:class_id>', methods=['GET', 'POST'])
@login_required
@member_required
def leave_review(class_id):
    fitness_class = FitnessClass.query.get_or_404(class_id)
    booking = Booking.query.filter_by(user_id=current_user.id, class_id=class_id).first()
    if not booking:
        flash('You must book a class before reviewing it.', 'warning')
        return redirect(url_for('main.class_detail', class_id=class_id))
    existing = Review.query.filter_by(user_id=current_user.id, class_id=class_id).first()
    if existing:
        flash('You have already reviewed this class.', 'info')
        return redirect(url_for('main.class_detail', class_id=class_id))
    form = ReviewForm()
    if form.validate_on_submit():
        review = Review(
            user_id=current_user.id,
            class_id=class_id,
            provider_id=fitness_class.provider_id,
            rating=form.rating.data,
            title=form.title.data,
            body=form.body.data,
            is_verified_attendee=(booking.status == 'attended')
        )
        db.session.add(review)
        db.session.flush()
        provider = fitness_class.provider
        all_reviews = Review.query.filter_by(provider_id=provider.id).all()
        provider.total_reviews = len(all_reviews)
        provider.average_rating = sum(r.rating for r in all_reviews) / provider.total_reviews if provider.total_reviews else 0
        db.session.commit()
        flash('Thank you for your review! 💜', 'success')
        return redirect(url_for('main.class_detail', class_id=class_id))
    return render_template('member/leave_review.html', form=form,
                           fitness_class=fitness_class, title='Leave a Review')


@member_bp.route('/report', methods=['POST'])
@login_required
@member_required
def submit_report():
    form = ReportForm()
    if form.validate_on_submit():
        report = Report(
            reporter_id=current_user.id,
            report_type=request.form.get('report_type', 'review'),
            target_id=request.form.get('target_id', type=int),
            reason=form.reason.data,
            description=form.description.data
        )
        db.session.add(report)
        db.session.commit()
        flash('Report submitted. Our team will review it. 🛡️', 'info')
    return redirect(request.referrer or url_for('main.index'))


@member_bp.route('/discussions/new', methods=['GET', 'POST'])
@login_required
@member_required
def new_discussion():
    form = DiscussionForm()
    if form.validate_on_submit():
        discussion = Discussion(
            author_id=current_user.id,
            title=form.title.data,
            body=form.body.data,
            category=form.category.data
        )
        db.session.add(discussion)
        db.session.commit()
        flash('Discussion posted!', 'success')
        return redirect(url_for('main.community'))
    return render_template('member/new_discussion.html', form=form, title='New Discussion')


@member_bp.route('/discussion/<int:discussion_id>', methods=['GET', 'POST'])
@login_required
def view_discussion(discussion_id):
    discussion = Discussion.query.get_or_404(discussion_id)
    if discussion.is_members_only and not (current_user.is_authenticated and current_user.is_member()):
        flash('This discussion is for members only.', 'warning')
        return redirect(url_for('main.community'))
    discussion.view_count += 1
    db.session.commit()
    form = ReplyForm()
    if form.validate_on_submit() and current_user.is_authenticated:
        reply = DiscussionReply(
            discussion_id=discussion_id,
            author_id=current_user.id,
            body=form.body.data
        )
        db.session.add(reply)
        db.session.commit()
        flash('Reply posted!', 'success')
        return redirect(url_for('member.view_discussion', discussion_id=discussion_id))
    replies = discussion.replies.filter_by(is_active=True).order_by(DiscussionReply.created_at.asc()).all()
    return render_template('member/view_discussion.html', discussion=discussion,
                           replies=replies, form=form, title=discussion.title)


@member_bp.route('/notifications')
@login_required
@member_required
def notifications():
    active_filter = request.args.get('filter', 'all')
    q = Notification.query.filter_by(user_id=current_user.id)
    if active_filter == 'unread':
        q = q.filter_by(is_read=False)
    unread_count = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
    total_count = Notification.query.filter_by(user_id=current_user.id).count()
    notifs = q.order_by(Notification.created_at.desc()).paginate(
        page=request.args.get('page', 1, type=int), per_page=20, error_out=False)
    # Mark all as read after fetching counts
    Notification.query.filter_by(user_id=current_user.id, is_read=False).update({'is_read': True})
    db.session.commit()
    return render_template('member/notifications.html', notifications=notifs,
                           unread_count=unread_count, total_count=total_count,
                           active_filter=active_filter, title='Notifications')


@member_bp.route('/calendar.ics')
@login_required
@member_required
def calendar_ics():
    from flask import Response
    from app.models import Booking, ClassSchedule
    bookings = Booking.query.filter_by(
        user_id=current_user.id, status='confirmed'
    ).all()

    lines = [
        'BEGIN:VCALENDAR',
        'VERSION:2.0',
        'PRODID:-//BloomWell//Booking Calendar//EN',
        'CALSCALE:GREGORIAN',
        'METHOD:PUBLISH',
        'X-WR-CALNAME:BloomWell Bookings',
        'X-WR-TIMEZONE:Europe/London',
    ]

    for b in bookings:
        fc = b.fitness_class
        sched = b.schedule
        if not sched:
            continue
        dt_start = f"{sched.date.strftime('%Y%m%d')}T{sched.start_time.strftime('%H%M%S')}"
        dt_end   = f"{sched.date.strftime('%Y%m%d')}T{sched.end_time.strftime('%H%M%S')}"
        location = fc.provider.address or fc.city or ''
        description = (
            f"Provider: {fc.provider.business_name}\\n"
            f"Confirmation Code: {b.confirmation_code}\\n"
            f"Activity: {fc.activity_type.replace('_', ' ').title()}\\n"
            f"Duration: {fc.duration_minutes} minutes"
        )
        lines += [
            'BEGIN:VEVENT',
            f'DTSTART:{dt_start}',
            f'DTEND:{dt_end}',
            f'SUMMARY:{fc.title}',
            f'DESCRIPTION:{description}',
            f'LOCATION:{location}',
            f'UID:bloomwell-booking-{b.id}@bloomwell.co.uk',
            'STATUS:CONFIRMED',
            'END:VEVENT',
        ]

    lines.append('END:VCALENDAR')
    ics_content = '\r\n'.join(lines)

    return Response(
        ics_content,
        mimetype='text/calendar',
        headers={'Content-Disposition': 'attachment; filename=bloomwell_bookings.ics'}
    )
