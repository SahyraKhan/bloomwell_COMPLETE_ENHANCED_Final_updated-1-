import os
import random
import string
from datetime import datetime
from PIL import Image
from flask import current_app


def save_image(file, folder='uploads', size=(400, 400)):
    """Save and resize an uploaded image, return filename."""
    ext = file.filename.rsplit('.', 1)[1].lower()
    random_name = ''.join(random.choices(string.ascii_lowercase + string.digits, k=12))
    filename = f"{random_name}.{ext}"

    upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], folder)
    os.makedirs(upload_path, exist_ok=True)
    filepath = os.path.join(upload_path, filename)

    img = Image.open(file)
    img.thumbnail(size)
    img.save(filepath)

    return f"uploads/{folder}/{filename}"


def generate_confirmation_code():
    """Generate a unique booking confirmation code."""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))


def get_activity_icon(activity_type):
    icons = {
        'yoga': '🧘',
        'pilates': '🤸',
        'strength': '💪',
        'cardio': '🏃',
        'hiit': '🔥',
        'dance': '💃',
        'swimming': '🏊',
        'walking_group': '🚶',
        'mental_wellbeing': '🧠',
        'meditation': '☯️',
        'nutrition': '🥗',
        'martial_arts': '🥋',
        'cycling': '🚴',
        'other': '⭐'
    }
    return icons.get(activity_type, '⭐')


def get_activity_color(activity_type):
    colors = {
        'yoga': '#8B7BA8',
        'pilates': '#C4A9C4',
        'strength': '#E8704A',
        'cardio': '#E85D75',
        'hiit': '#FF6B6B',
        'dance': '#F4C2C2',
        'swimming': '#76B7CC',
        'walking_group': '#88C9A1',
        'mental_wellbeing': '#B8A9C9',
        'meditation': '#9DBFB0',
        'nutrition': '#A8C5A0',
        'martial_arts': '#C9A08A',
        'cycling': '#A0B5C9',
        'other': '#C4B5A0'
    }
    return colors.get(activity_type, '#B8A9C9')
