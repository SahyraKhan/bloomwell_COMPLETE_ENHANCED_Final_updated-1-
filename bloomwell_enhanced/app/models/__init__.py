from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='member')
    full_name = db.Column(db.String(120))
    profile_image = db.Column(db.String(200), default='default_avatar.png')
    bio = db.Column(db.Text)
    location = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)

    member_profile = db.relationship('MemberProfile', backref='user', uselist=False, cascade='all, delete-orphan')
    provider_profile = db.relationship('ProviderProfile', backref='user', uselist=False, cascade='all, delete-orphan')
    bookings = db.relationship('Booking', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    reviews = db.relationship('Review', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    reports = db.relationship('Report', backref='reporter', lazy='dynamic', cascade='all, delete-orphan', foreign_keys='Report.reporter_id')
    discussions = db.relationship('Discussion', backref='author', lazy='dynamic', cascade='all, delete-orphan')
    discussion_replies = db.relationship('DiscussionReply', backref='author', lazy='dynamic', cascade='all, delete-orphan')

    def set_password(self, password): self.password_hash = generate_password_hash(password)
    def check_password(self, password): return check_password_hash(self.password_hash, password)
    def is_admin(self): return self.role == 'admin'
    def is_provider(self): return self.role == 'provider'
    def is_member(self): return self.role == 'member'
    def __repr__(self): return f'<User {self.username}>'


class MemberProfile(db.Model):
    __tablename__ = 'member_profiles'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    preferred_activities = db.Column(db.String(300))
    fitness_goals = db.Column(db.Text)
    age_group = db.Column(db.String(20))
    language_preference = db.Column(db.String(50), default='English')
    cultural_preferences = db.Column(db.Text)
    accessibility_needs = db.Column(db.Text)
    notification_preferences = db.Column(db.String(100), default='email')
    total_sessions_attended = db.Column(db.Integer, default=0)
    joined_date = db.Column(db.DateTime, default=datetime.utcnow)


class ProviderProfile(db.Model):
    __tablename__ = 'provider_profiles'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    business_name = db.Column(db.String(150), nullable=False)
    business_type = db.Column(db.String(50))
    description = db.Column(db.Text)
    address = db.Column(db.String(300))
    city = db.Column(db.String(100))
    postcode = db.Column(db.String(20))
    phone = db.Column(db.String(30))
    contact_email = db.Column(db.String(150))
    website = db.Column(db.String(200))
    instagram = db.Column(db.String(100))
    is_women_only = db.Column(db.Boolean, default=True)
    is_approved = db.Column(db.Boolean, default=False)
    approval_date = db.Column(db.DateTime)
    verified_badge = db.Column(db.Boolean, default=False)
    banner_image = db.Column(db.String(200))
    logo_image = db.Column(db.String(200))
    average_rating = db.Column(db.Float, default=0.0)
    total_reviews = db.Column(db.Integer, default=0)
    classes = db.relationship('FitnessClass', backref='provider', lazy='dynamic', cascade='all, delete-orphan')


class FitnessClass(db.Model):
    __tablename__ = 'fitness_classes'
    id = db.Column(db.Integer, primary_key=True)
    provider_id = db.Column(db.Integer, db.ForeignKey('provider_profiles.id'), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    activity_type = db.Column(db.String(50), nullable=False)
    difficulty_level = db.Column(db.String(20))
    duration_minutes = db.Column(db.Integer)
    max_capacity = db.Column(db.Integer, default=20)
    current_bookings = db.Column(db.Integer, default=0)
    price = db.Column(db.Float, default=0.0)
    is_free = db.Column(db.Boolean, default=False)
    is_online = db.Column(db.Boolean, default=False)
    is_women_only = db.Column(db.Boolean, default=True)
    is_active = db.Column(db.Boolean, default=True)
    image = db.Column(db.String(200))
    location = db.Column(db.String(300))
    city = db.Column(db.String(100))
    postcode = db.Column(db.String(20))
    language = db.Column(db.String(50), default='English')
    accessibility_info = db.Column(db.Text)
    cover_image_url = db.Column(db.String(500))  # External image URL for display
    latitude = db.Column(db.Float)   # For map display
    longitude = db.Column(db.Float)  # For map display
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    schedules = db.relationship('ClassSchedule', backref='fitness_class', lazy='dynamic', cascade='all, delete-orphan')
    bookings = db.relationship('Booking', backref='fitness_class', lazy='dynamic', cascade='all, delete-orphan')
    reviews = db.relationship('Review', backref='fitness_class', lazy='dynamic', cascade='all, delete-orphan')


class ClassSchedule(db.Model):
    __tablename__ = 'class_schedules'
    id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.Integer, db.ForeignKey('fitness_classes.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    is_cancelled = db.Column(db.Boolean, default=False)
    cancellation_reason = db.Column(db.Text)
    available_spots = db.Column(db.Integer)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    bookings = db.relationship('Booking', backref='schedule', lazy='dynamic')


class Booking(db.Model):
    __tablename__ = 'bookings'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('fitness_classes.id'), nullable=False)
    schedule_id = db.Column(db.Integer, db.ForeignKey('class_schedules.id'), nullable=True)
    status = db.Column(db.String(20), default='confirmed')
    booking_date = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text)
    confirmation_code = db.Column(db.String(20))
    reminder_sent = db.Column(db.Boolean, default=False)


class Review(db.Model):
    __tablename__ = 'reviews'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('fitness_classes.id'), nullable=False)
    provider_id = db.Column(db.Integer, db.ForeignKey('provider_profiles.id'), nullable=True)
    rating = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(150))
    body = db.Column(db.Text, nullable=False)
    is_approved = db.Column(db.Boolean, default=True)
    is_flagged = db.Column(db.Boolean, default=False)
    provider_response = db.Column(db.Text)
    provider_response_date = db.Column(db.DateTime)
    is_verified_attendee = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Discussion(db.Model):
    __tablename__ = 'discussions'
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    body = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50))
    is_pinned = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    is_members_only = db.Column(db.Boolean, default=False)
    view_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    replies = db.relationship('DiscussionReply', backref='discussion', lazy='dynamic', cascade='all, delete-orphan')


class DiscussionReply(db.Model):
    __tablename__ = 'discussion_replies'
    id = db.Column(db.Integer, primary_key=True)
    discussion_id = db.Column(db.Integer, db.ForeignKey('discussions.id'), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    body = db.Column(db.Text, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Report(db.Model):
    __tablename__ = 'reports'
    id = db.Column(db.Integer, primary_key=True)
    reporter_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    report_type = db.Column(db.String(50))
    target_id = db.Column(db.Integer)
    reason = db.Column(db.String(100))
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    resolved_at = db.Column(db.DateTime)
    resolved_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)


class Notification(db.Model):
    __tablename__ = 'notifications'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(150))
    message = db.Column(db.Text)
    link = db.Column(db.String(300))
    notif_type = db.Column(db.String(30), default='system')  # booking, reminder, update, announcement, system
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='notifications')


class ChatMessage(db.Model):
    __tablename__ = 'chat_messages'
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    sender = db.relationship('User', foreign_keys=[sender_id], backref='sent_messages')
    receiver = db.relationship('User', foreign_keys=[receiver_id], backref='received_messages')
