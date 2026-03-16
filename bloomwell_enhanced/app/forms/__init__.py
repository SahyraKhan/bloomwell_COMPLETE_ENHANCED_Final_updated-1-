from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, BooleanField, SelectField, TextAreaField, SubmitField, IntegerField, FloatField, DateField, TimeField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional, NumberRange, ValidationError
from app.models import User


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Keep me signed in')
    submit = SubmitField('Sign In')


class RegisterForm(FlaskForm):
    full_name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=120)])
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=80)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    role = SelectField('I am a...', choices=[
        ('member', 'Woman seeking fitness & wellbeing'),
        ('provider', 'Activity Provider / Trainer / Studio')
    ], validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Create Account')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already taken. Please choose another.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered. Please log in.')


class EditProfileForm(FlaskForm):
    full_name = StringField('Full Name', validators=[DataRequired(), Length(max=120)])
    bio = TextAreaField('About Me', validators=[Optional(), Length(max=500)])
    location = StringField('Location', validators=[Optional(), Length(max=120)])
    phone = StringField('Phone', validators=[Optional(), Length(max=20)])
    profile_image = FileField('Profile Photo', validators=[FileAllowed(['jpg', 'jpeg', 'png', 'webp'])])
    submit = SubmitField('Save Changes')


class MemberPreferencesForm(FlaskForm):
    preferred_activities = StringField('Preferred Activities (comma-separated)', validators=[Optional()])
    fitness_goals = TextAreaField('Fitness Goals', validators=[Optional(), Length(max=500)])
    age_group = SelectField('Age Group', choices=[
        ('', 'Prefer not to say'),
        ('18-25', '18-25'),
        ('26-35', '26-35'),
        ('36-45', '36-45'),
        ('46-55', '46-55'),
        ('55+', '55+')
    ], validators=[Optional()])
    language_preference = SelectField('Language Preference', choices=[
        ('English', 'English'),
        ('Urdu', 'Urdu'),
        ('Arabic', 'Arabic'),
        ('Bengali', 'Bengali'),
        ('Hindi', 'Hindi'),
        ('Punjabi', 'Punjabi'),
        ('Somali', 'Somali'),
        ('Other', 'Other')
    ])
    cultural_preferences = TextAreaField('Cultural / Accessibility Preferences', validators=[Optional(), Length(max=300)])
    submit = SubmitField('Save Preferences')


class ProviderProfileForm(FlaskForm):
    business_name = StringField('Business / Organisation Name', validators=[DataRequired(), Length(max=150)])
    business_type = SelectField('Type', choices=[
        ('studio', 'Fitness Studio'),
        ('trainer', 'Personal Trainer'),
        ('community_org', 'Community Organisation'),
        ('gym', 'Gym'),
        ('online', 'Online Provider'),
        ('other', 'Other')
    ])
    description = TextAreaField('About Your Services', validators=[Optional(), Length(max=1000)])
    address = StringField('Address', validators=[Optional(), Length(max=300)])
    city = StringField('City', validators=[Optional(), Length(max=100)])
    postcode = StringField('Postcode', validators=[Optional(), Length(max=20)])
    website = StringField('Website', validators=[Optional(), Length(max=200)])
    instagram = StringField('Instagram Handle', validators=[Optional(), Length(max=100)])
    is_women_only = BooleanField('Women-Only Space', default=True)
    logo_image = FileField('Logo', validators=[FileAllowed(['jpg', 'jpeg', 'png', 'webp'])])
    banner_image = FileField('Banner Image', validators=[FileAllowed(['jpg', 'jpeg', 'png', 'webp'])])
    submit = SubmitField('Save Profile')


class ClassForm(FlaskForm):
    title = StringField('Class Title', validators=[DataRequired(), Length(max=150)])
    description = TextAreaField('Description', validators=[Optional(), Length(max=1000)])
    activity_type = SelectField('Activity Type', choices=[
        ('yoga', 'Yoga'),
        ('pilates', 'Pilates'),
        ('strength', 'Strength Training'),
        ('cardio', 'Cardio'),
        ('hiit', 'HIIT'),
        ('dance', 'Dance'),
        ('swimming', 'Swimming'),
        ('walking_group', 'Walking Group'),
        ('mental_wellbeing', 'Mental Wellbeing'),
        ('meditation', 'Meditation'),
        ('nutrition', 'Nutrition Workshop'),
        ('boxing', 'Boxing'),
        ('martial_arts', 'Martial Arts'),
        ('cycling', 'Cycling'),
        ('other', 'Other')
    ], validators=[DataRequired()])
    difficulty_level = SelectField('Level', choices=[
        ('all_levels', 'All Levels'),
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced')
    ])
    duration_minutes = IntegerField('Duration (minutes)', validators=[DataRequired(), NumberRange(min=15, max=300)])
    max_capacity = IntegerField('Max Capacity', validators=[DataRequired(), NumberRange(min=1, max=200)])
    price = FloatField('Price (£)', validators=[Optional(), NumberRange(min=0)])
    is_free = BooleanField('Free Class')
    is_online = BooleanField('Online Class')
    is_women_only = BooleanField('Women-Only', default=True)
    location = StringField('Location / Venue', validators=[Optional(), Length(max=300)])
    city = StringField('City', validators=[Optional(), Length(max=100)])
    postcode = StringField('Postcode', validators=[Optional(), Length(max=20)])
    language = SelectField('Language', choices=[
        ('English', 'English'),
        ('Urdu', 'Urdu'),
        ('Arabic', 'Arabic'),
        ('Bengali', 'Bengali'),
        ('Hindi', 'Hindi'),
        ('Other', 'Other')
    ])
    accessibility_info = TextAreaField('Accessibility Information', validators=[Optional(), Length(max=500)])
    image = FileField('Class Image', validators=[FileAllowed(['jpg', 'jpeg', 'png', 'webp'])])
    cover_image_url = StringField('Or paste an Image URL (from Unsplash, etc.)', validators=[Optional(), Length(max=500)])
    submit = SubmitField('Save Class')


class ScheduleForm(FlaskForm):
    date = DateField('Date', validators=[DataRequired()])
    start_time = TimeField('Start Time', validators=[DataRequired()])
    end_time = TimeField('End Time', validators=[DataRequired()])
    available_spots = IntegerField('Available Spots', validators=[Optional(), NumberRange(min=1)])
    submit = SubmitField('Add Schedule')


class ReviewForm(FlaskForm):
    rating = SelectField('Rating', choices=[
        (5, '⭐⭐⭐⭐⭐ Excellent'),
        (4, '⭐⭐⭐⭐ Good'),
        (3, '⭐⭐⭐ Average'),
        (2, '⭐⭐ Poor'),
        (1, '⭐ Very Poor')
    ], coerce=int, validators=[DataRequired()])
    title = StringField('Review Title', validators=[Optional(), Length(max=150)])
    body = TextAreaField('Your Review', validators=[DataRequired(), Length(min=10, max=1000)])
    submit = SubmitField('Submit Review')


class DiscussionForm(FlaskForm):
    title = StringField('Topic Title', validators=[DataRequired(), Length(max=200)])
    body = TextAreaField('Your Message', validators=[DataRequired(), Length(min=10, max=5000)])
    category = SelectField('Category', choices=[
        ('general', 'General Chat'),
        ('fitness_tips', 'Fitness Tips'),
        ('mental_health', 'Mental Health & Wellbeing'),
        ('nutrition', 'Nutrition'),
        ('events', 'Events & Meetups'),
        ('support', 'Support & Advice')
    ])
    submit = SubmitField('Post Discussion')


class ReplyForm(FlaskForm):
    body = TextAreaField('Your Reply', validators=[DataRequired(), Length(min=2, max=2000)])
    submit = SubmitField('Post Reply')


class SearchForm(FlaskForm):
    query = StringField('Search', validators=[Optional()])
    activity_type = SelectField('Activity', choices=[
        ('', 'All Activities'),
        ('yoga', 'Yoga'),
        ('pilates', 'Pilates'),
        ('strength', 'Strength Training'),
        ('cardio', 'Cardio'),
        ('hiit', 'HIIT'),
        ('dance', 'Dance'),
        ('swimming', 'Swimming'),
        ('walking_group', 'Walking Group'),
        ('mental_wellbeing', 'Mental Wellbeing'),
        ('meditation', 'Meditation'),
        ('nutrition', 'Nutrition'),
        ('boxing', 'Boxing'),
        ('martial_arts', 'Martial Arts'),
        ('cycling', 'Cycling'),
        ('other', 'Other')
    ], validators=[Optional()])
    city = StringField('City / Location', validators=[Optional()])
    is_free = BooleanField('Free Only')
    is_online = BooleanField('Online Only')
    difficulty = SelectField('Level', choices=[
        ('', 'All Levels'),
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
        ('all_levels', 'All Levels')
    ], validators=[Optional()])
    submit = SubmitField('Search')


class ReportForm(FlaskForm):
    reason = SelectField('Reason', choices=[
        ('inappropriate', 'Inappropriate Content'),
        ('spam', 'Spam'),
        ('fake', 'Fake/Misleading Information'),
        ('harassment', 'Harassment'),
        ('safety', 'Safety Concern'),
        ('other', 'Other')
    ], validators=[DataRequired()])
    description = TextAreaField('Details', validators=[Optional(), Length(max=500)])
    submit = SubmitField('Submit Report')
