# BloomWell ✦ Women's Wellbeing and Fitness Community Platform

> A centralised digital platform connecting women to safe, inclusive, and local fitness and wellbeing opportunities.

---

## 📌 About the Project

BloomWell is a full-stack web application developed as part of a BSc (Hons) Applied Computing independent project at UWTSD Birmingham. It addresses the lack of safe, women-only fitness spaces by providing a verified, community-driven platform where women can discover, book, and review local wellbeing classes.

---

## 🌸 Key Features

- **Member Dashboard** — Book classes, track sessions, manage notifications and preferences
- **Provider Dashboard** — List and manage classes, view bookings, analytics and earnings
- **Admin Panel** — Approve providers, moderate content, manage users and view platform analytics
- **Women-Only Verification** — Providers can be verified and classes marked women-only
- **Class Booking System** — Real-time booking with confirmation codes and cancellation handling
- **Community Forum** — Members can post discussions, share experiences and leave reviews
- **Explore & Filter** — Search classes by activity type, location, difficulty, price and more
- **Booking Calendar** — Visual calendar of all upcoming classes
- **Real-Time Notifications** — In-app alerts for bookings, messages and updates
- **Safety & Inclusivity Page** — Platform guidelines and community standards

---

## 🛠️ Technology Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python, Flask |
| Database | SQLite, Flask |
| Frontend | HTML, CSS, JavaScript, Jinja2 |
| Authentication | Flask-Login, Flask-WTF |
| Architecture | Three-Tier MVC (Presentation, Application, Data) |

---

## 🚀 Getting Started

### Prerequisites
- Python 3.12+
- pip

### Installation

1. **Clone the repository**
```bash
   git clone https://github.com/SahyraKhan/bloomwell_COMPLETE_ENHANCED_Final_updated-1-.git
   cd bloomwell_COMPLETE_ENHANCED_Final_updated-1-/bloomwell_enhanced
```

2. **Create a virtual environment**
```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
```

3. **Install dependencies**
```bash
   pip install -r requirements.txt
```

4. **Seed the database**
```bash
   python seed_db.py
```

5. **Run the application**
```bash
   python run.py
```

6. **Open in browser**
```
   http://localhost:5000
```

---

## 👤 Demo Accounts

| Role | Email | Password |
|------|-------|----------|
| Member | member@demo.com | password123 |
| Provider | provider@demo.com | password123 |
| Admin | admin@demo.com | password123 |

---

## 📁 Project Structure
```
bloomwell_enhanced/
├── app/
│   ├── models/          # Database models
│   ├── routes/          # Blueprint routes (auth, member, provider, admin)
│   ├── templates/       # Jinja2 HTML templates
│   ├── static/          # CSS, JS, images
│   └── forms/           # WTForms form definitions
├── config.py            # App configuration
├── run.py               # Entry point
├── seed_db.py           # Database seeding
└── requirements.txt     # Dependencies
```

---

## 📊 Project Info

- **Student:** Sahyra Khan
- **Student ID:** 2237641
- **Degree:** BSc (Hons) Applied Computing
- **Institution:** UWTSD Birmingham (IICL)
- **Supervisor:** MD Shantanu Islam
- **Year:** 2026

---

## 📄 Licence

This project was created for academic purposes as part of an independent study module at UWTSD Birmingham.
