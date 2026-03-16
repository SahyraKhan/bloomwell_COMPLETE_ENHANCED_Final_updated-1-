import os, sys

# Always run from the directory containing this file
os.chdir(os.path.dirname(os.path.abspath(__file__)))
if os.path.dirname(os.path.abspath(__file__)) not in sys.path:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import User

app = create_app()

def auto_seed():
    """Automatically seed the database if it is empty."""
    with app.app_context():
        db.create_all()
        if User.query.first() is None:
            print("📦 No data found — auto-seeding database...")
            import subprocess
            seed_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'seed_db.py')
            result = subprocess.run([sys.executable, seed_path])
            if result.returncode == 0:
                print("✅ Database seeded successfully!")
            else:
                print("❌ Seeding failed — please run: python seed_db.py manually")
        else:
            count = User.query.count()
            print(f"✅ Database ready ({count} users found)")

if __name__ == '__main__':
    auto_seed()
    print("\n🌸 BloomWell running at: http://127.0.0.1:5000\n")
    app.run(debug=True, host='127.0.0.1', port=5000)
