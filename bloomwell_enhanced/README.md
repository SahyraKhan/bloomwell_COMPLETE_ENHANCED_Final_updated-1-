# BloomWell – Women's Wellness Platform

A Flask-based platform connecting women with verified fitness classes, studios, and wellbeing activities.

---

## HOW TO RUN (3 steps)

### Prerequisites
- Python 3.9 or higher installed
- pip (comes with Python)

### Step 1: Install dependencies
Open your terminal/command prompt, navigate to the project folder, and run:

```bash
cd womens_wellness
pip install -r requirements.txt
```

If you get a permission error on Mac/Linux, try:
```bash
pip install --user -r requirements.txt
```

### Step 2: Create the database and seed sample data
```bash
python seed_db.py
```

You should see:
```
Database tables created.
Sample data created successfully!
```

### Step 3: Run the application
```bash
python run.py
```

Then open your browser and go to: **http://127.0.0.1:5000**

---

## Login Credentials (sample accounts)

| Role     | Email                     | Password      |
|----------|---------------------------|---------------|
| Admin    | admin@bloomwell.com       | Admin@123     |
| Member   | member@bloomwell.com      | Member@123    |
| Provider | provider@bloomwell.com    | Provider@123  |

---

## Project Structure

```
womens_wellness/
├── run.py                  # Entry point - run this to start the app
├── config.py               # Configuration (database, uploads, etc.)
├── seed_db.py              # Database seeder with sample data
├── requirements.txt        # Python dependencies
├── app/
│   ├── __init__.py         # App factory (create_app)
│   ├── utils.py            # Helper functions (image upload, etc.)
│   ├── models/
│   │   └── __init__.py     # All database models (User, Booking, etc.)
│   ├── forms/
│   │   └── __init__.py     # All WTForms (Login, Register, Search, etc.)
│   ├── routes/
│   │   ├── auth.py         # Login, Register, Logout
│   │   ├── main.py         # Home, Explore, Class Detail, Community
│   │   ├── member.py       # Member dashboard, bookings, reviews
│   │   ├── provider.py     # Provider dashboard, classes, schedule
│   │   ├── admin.py        # Admin panel, user management, reports
│   │   └── errors.py       # 404, 403, 500 error handlers
│   ├── templates/          # Jinja2 HTML templates
│   │   ├── base.html       # Main layout (navbar, footer, flash messages)
│   │   ├── auth/           # Login and Register pages
│   │   ├── main/           # Public pages (home, explore, about)
│   │   ├── member/         # Member area pages
│   │   ├── provider/       # Provider area pages
│   │   ├── admin/          # Admin panel pages
│   │   └── errors/         # Error pages
│   └── static/
│       ├── css/style.css   # Full design system
│       └── js/main.js      # Interactive features
└── wellness.db             # SQLite database (created after seed_db.py)
```

---

## Bugs Fixed in This Version

1. **Session count was wrong** - total_sessions_attended was incrementing when a user booked a class instead of when the provider marked them as attended. Fixed so it only counts when the provider confirms attendance.

2. **Missing access control on discussions** - new_discussion route was missing the @member_required decorator, allowing providers/admins to create member discussions. view_discussion was missing @login_required, so unauthenticated users could post replies.

3. **Rating calculation off-by-one** - The provider average rating calculation was counting the new review twice (once in the query, once manually added). Fixed by using db.session.flush() first so the new review is included in the query results.

4. **Junk directories removed** - The original zip contained broken directory entries that have been cleaned up.

---

## Common Issues and Fixes

**"ModuleNotFoundError: No module named 'flask'"**
You haven't installed dependencies. Run: pip install -r requirements.txt

**"OperationalError: no such table: users"**
You haven't created the database. Run: python seed_db.py

**"Address already in use" error**
Another app is using port 5000. Either close it or change the port in run.py to app.run(debug=True, port=5001)

**Images not loading**
The app/static/images/uploads/ folder is created automatically when you first upload an image. Sample data uses placeholder icons.
