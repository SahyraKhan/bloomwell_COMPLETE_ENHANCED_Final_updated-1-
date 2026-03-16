from flask import Blueprint, render_template, request
from flask_login import current_user
from app import db
from app.models import FitnessClass, ProviderProfile, Discussion, Review, Booking, User
from app.forms import SearchForm
from app.utils import get_activity_icon
from sqlalchemy import func

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    # Get 6 classes with distinct activity types so no duplicate images on homepage
    all_active = FitnessClass.query.filter_by(is_active=True).all()
    seen_types = set()
    featured_classes = []
    for fc in all_active:
        if fc.activity_type not in seen_types:
            featured_classes.append(fc)
            seen_types.add(fc.activity_type)
        if len(featured_classes) == 6:
            break
    verified_providers = ProviderProfile.query.filter_by(is_approved=True, verified_badge=True).limit(4).all()
    recent_discussions = Discussion.query.filter_by(is_active=True).order_by(Discussion.created_at.desc()).limit(3).all()
    stats = {
        'total_members': User.query.filter_by(role='member').count(),
        'total_classes': FitnessClass.query.filter_by(is_active=True).count(),
        'total_bookings': Booking.query.count(),
        'avg_rating': round(db.session.query(func.avg(Review.rating)).scalar() or 4.8, 1),
    }
    return render_template('main/index.html',
                           featured_classes=featured_classes,
                           verified_providers=verified_providers,
                           recent_discussions=recent_discussions,
                           platform_stats=stats,
                           title='Home')


@main_bp.route('/explore')
def explore():
    form = SearchForm(request.args)
    query = FitnessClass.query.filter_by(is_active=True)

    # Read all filters directly from URL args (most reliable)
    q        = request.args.get('query', '').strip()
    activity = request.args.get('activity_type', '').strip()
    city     = request.args.get('city', '').strip()
    diff     = request.args.get('difficulty', '').strip()
    lang     = request.args.get('language', '').strip()
    is_free  = request.args.get('is_free')
    is_online= request.args.get('is_online')
    women    = request.args.get('women_only')
    access   = request.args.get('accessible')
    min_rate = request.args.get('min_rating', '').strip()

    if q:
        s = f"%{q}%"
        query = query.filter(FitnessClass.title.ilike(s) | FitnessClass.description.ilike(s))
    if activity:
        query = query.filter_by(activity_type=activity)
    if city:
        query = query.filter(FitnessClass.city.ilike(f"%{city}%"))
    if diff:
        query = query.filter_by(difficulty_level=diff)
    if lang:
        query = query.filter_by(language=lang)
    if is_free:
        query = query.filter_by(is_free=True)
    if is_online:
        query = query.filter_by(is_online=True)
    if women:
        query = query.filter_by(is_women_only=True)
    if access:
        query = query.filter(FitnessClass.accessibility_info.isnot(None))
    if min_rate:
        try:
            mr = float(min_rate)
            rated_ids = db.session.query(ProviderProfile.id).filter(
                ProviderProfile.average_rating >= mr).all()
            ids = [r[0] for r in rated_ids]
            query = query.filter(FitnessClass.provider_id.in_(ids))
        except ValueError:
            pass

    classes = query.order_by(FitnessClass.created_at.desc()).paginate(
        page=request.args.get('page', 1, type=int), per_page=24, error_out=False)

    return render_template('main/explore.html', classes=classes, form=form,
                           get_activity_icon=get_activity_icon, title='Explore Classes')


@main_bp.route('/class/<int:class_id>')
def class_detail(class_id):
    fitness_class = FitnessClass.query.get_or_404(class_id)
    reviews = Review.query.filter_by(class_id=class_id, is_approved=True).order_by(Review.created_at.desc()).all()
    upcoming_schedules = fitness_class.schedules.filter_by(is_cancelled=False).all()
    avg_rating = sum(r.rating for r in reviews) / len(reviews) if reviews else 0
    return render_template('main/class_detail.html',
                           fitness_class=fitness_class,
                           reviews=reviews,
                           schedules=upcoming_schedules,
                           avg_rating=avg_rating,
                           get_activity_icon=get_activity_icon,
                           title=fitness_class.title)


@main_bp.route('/provider/<int:provider_id>')
def provider_detail(provider_id):
    provider = ProviderProfile.query.get_or_404(provider_id)
    classes = provider.classes.filter_by(is_active=True).all()
    reviews = Review.query.filter_by(provider_id=provider_id, is_approved=True).order_by(Review.created_at.desc()).all()
    return render_template('main/provider_detail.html', provider=provider,
                           classes=classes, reviews=reviews, title=provider.business_name)


@main_bp.route('/community')
def community():
    category = request.args.get('category', '')
    query = Discussion.query.filter_by(is_active=True)
    if category:
        query = query.filter_by(category=category)
    # Hide members-only threads from guests
    if not (current_user.is_authenticated and (current_user.is_member() or current_user.is_admin())):
        query = query.filter_by(is_members_only=False)
    discussions = query.order_by(Discussion.is_pinned.desc(), Discussion.created_at.desc()).paginate(
        page=request.args.get('page', 1, type=int), per_page=10, error_out=False)
    return render_template('main/community.html', discussions=discussions,
                           active_category=category, title='Community')


@main_bp.route('/about')
def about():
    return render_template('main/about.html', title='About Us')


@main_bp.route('/safety')
def safety():
    return render_template('main/safety.html', title='Safety & Inclusivity')


@main_bp.route('/calendar')
def calendar():
    import json
    from datetime import date
    from app.models import ClassSchedule
    schedules = (ClassSchedule.query
                 .filter_by(is_cancelled=False)
                 .filter(ClassSchedule.date >= date.today())
                 .join(FitnessClass)
                 .filter(FitnessClass.is_active == True)
                 .order_by(ClassSchedule.date.asc(), ClassSchedule.start_time.asc())
                 .all())
    data = json.dumps([{
        'schedule_id': s.id,
        'class_id': s.class_id,
        'title': s.fitness_class.title,
        'date': s.date.strftime('%Y-%m-%d'),
        'time': s.start_time.strftime('%H:%M'),
        'end_time': s.end_time.strftime('%H:%M'),
        'city': s.fitness_class.city or '',
        'provider': s.fitness_class.provider.business_name,
        'price': float(s.fitness_class.price),
        'free': s.fitness_class.is_free,
        'spots': max(0, (s.available_spots or s.fitness_class.max_capacity) - s.fitness_class.current_bookings),
        'capacity': s.fitness_class.max_capacity,
        'women_only': s.fitness_class.is_women_only,
        'detail_url': '/class/{}'.format(s.class_id),
    } for s in schedules])
    return render_template('main/calendar.html', schedule_json=data,
                           all_schedules=schedules, title='Booking Calendar')
