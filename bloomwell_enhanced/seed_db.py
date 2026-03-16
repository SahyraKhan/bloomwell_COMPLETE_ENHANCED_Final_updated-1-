# BloomWell – Full Seed Script  /  Run: python seed_db.py
import os, sys
os.chdir(os.path.dirname(os.path.abspath(__file__)))
if os.path.dirname(os.path.abspath(__file__)) not in sys.path:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import (User, MemberProfile, ProviderProfile, FitnessClass,
                         ClassSchedule, Booking, Review, Discussion, DiscussionReply,
                         Notification, Report)
from datetime import datetime, date, time, timedelta
import random, string

app = create_app()

def gen_code():
    return 'BW' + ''.join(random.choices(string.digits, k=6))

with app.app_context():
    db.drop_all(); db.create_all()
    print("✅ Tables created.")

    # ADMIN
    admin = User(email='admin@bloomwell.com', username='sahyra_admin',
                 full_name='Sahyra Khan', role='admin', is_verified=True, is_active=True)
    admin.set_password('Admin@123')
    db.session.add(admin)

    # MEMBERS
    members = []
    for email, uname, fname, loc in [
        ('member@bloomwell.com','sarah_jane','Sarah Jane','Redditch'),
        ('fatima@bloomwell.com','fatima_ali','Fatima Ali','Birmingham'),
        ('priya@bloomwell.com','priya_sharma','Priya Sharma','Worcester'),
        ('amira@bloomwell.com','amira_hassan','Amira Hassan','Bromsgrove'),
        ('claire@bloomwell.com','claire_wales','Claire Wales','Redditch'),
    ]:
        u = User(email=email, username=uname, full_name=fname, role='member',
                 location=loc, is_verified=True, is_active=True)
        u.set_password('Member@123')
        db.session.add(u); db.session.flush()
        db.session.add(MemberProfile(user_id=u.id,
            preferred_activities='yoga,meditation,walking_group',
            fitness_goals='Improve flexibility and mental wellbeing',
            age_group='26-35', language_preference='English',
            total_sessions_attended=random.randint(4,20)))
        members.append(u)

    # PROVIDERS
    prov_data = [
        dict(email='amara@bloomwell.com', username='blossomstudio', full_name='Amara Khan',
             bname='Blossom Wellness Studio', city='Redditch', postcode='B97 4AA',
             address='15 Unicorn Hill, Redditch, B97 4AA',
             phone='01527 123456', contact_email='hello@blossomwellness.co.uk',
             website='https://blossomwellness.co.uk',
             desc='A welcoming women-only space in Redditch offering yoga, pilates and holistic wellbeing.',
             lat=52.3063, lng=-1.9449),
        dict(email='lisa@bloomwell.com', username='lisastrength', full_name='Lisa Thompson',
             bname='FemFit Bromsgrove', city='Bromsgrove', postcode='B60 1AB',
             address='22 High Street, Bromsgrove, B60 1AB',
             phone='01527 654321', contact_email='info@femfitbromsgrove.co.uk',
             website='https://femfitbromsgrove.co.uk',
             desc='Strength, HIIT and confidence classes designed for women in Bromsgrove.',
             lat=52.3352, lng=-2.0594),
        dict(email='sophie@bloomwell.com', username='sophiemind', full_name='Sophie Williams',
             bname='Serenity Mind & Body', city='Worcester', postcode='WR1 2JH',
             address='8 Foregate Street, Worcester, WR1 2JH',
             phone='01905 789012', contact_email='contact@serenitymindandbody.co.uk',
             website='https://serenitymindandbody.co.uk',
             desc='Meditation, mindfulness and wellbeing workshops in the heart of Worcester.',
             lat=52.1927, lng=-2.2200),
        dict(email='nadia@bloomwell.com', username='nadiafit', full_name='Nadia Patel',
             bname='ActiveWomen Birmingham', city='Birmingham', postcode='B1 1BB',
             address='45 Broad Street, Birmingham, B1 1BB',
             phone='0121 456 7890', contact_email='hello@activewomen.co.uk',
             website='https://activewomen.co.uk',
             desc='High-energy fitness studio for women of all backgrounds in Birmingham city centre.',
             lat=52.4796, lng=-1.9026),
    ]
    provider_profiles = []
    for pd in prov_data:
        pu = User(email=pd['email'], username=pd['username'], full_name=pd['full_name'],
                  role='provider', is_verified=True, is_active=True)
        pu.set_password('Provider@123')
        db.session.add(pu); db.session.flush()
        pp = ProviderProfile(
            user_id=pu.id, business_name=pd['bname'], business_type='studio',
            description=pd['desc'], address=pd['address'], city=pd['city'],
            postcode=pd['postcode'], phone=pd['phone'], contact_email=pd['contact_email'],
            website=pd.get('website',''), is_women_only=True, is_approved=True,
            verified_badge=True, approval_date=datetime.utcnow(),
            average_rating=round(random.uniform(4.5,5.0),1), total_reviews=random.randint(15,40))
        db.session.add(pp); db.session.flush()
        provider_profiles.append(pp)

    IMGS = {
        'yoga':            'https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?w=700&q=80',
        'meditation':      'https://images.unsplash.com/photo-1602192509154-0b900ee1f851?w=700&q=80',
        'pilates':         'https://images.unsplash.com/photo-1518611012118-696072aa579a?w=700&q=80',
        'strength':        'https://images.unsplash.com/photo-1534258936925-c58bed479fcb?w=700&q=80',
        'hiit':            'https://images.unsplash.com/photo-1518310383802-640c2de311b2?w=700&q=80',
        'walking_group':   'https://images.unsplash.com/photo-1476480862126-209bfaa8edc8?w=700&q=80',
        'mental_wellbeing':'https://images.unsplash.com/photo-1522075469751-3a6694fb2f61?w=700&q=80',
        'dance':           'https://images.unsplash.com/photo-1504609813442-a8924e83f76e?w=700&q=80',
        'nutrition':       'https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=700&q=80',
        'boxing':          'https://images.unsplash.com/photo-1591940742878-13aba4b7a34e?w=700&q=80',
        'swimming':        'https://images.unsplash.com/photo-1560090995-01632a28895b?w=700&q=80',
        'cycling':         'https://media.istockphoto.com/id/507108546/photo/working-out-on-stationary-bikes.jpg?s=612x612&w=0&k=20&c=pqotatX5O_yRHof-uxsFmJiJ2J-1IGTyabO2w6Hhw_Q=',
        'barre':           'https://images.unsplash.com/photo-1516526995003-435ccce2be97?w=700&q=80',
        'zumba':           'https://images.unsplash.com/photo-1504609773096-104ff2c73ba4?w=700&q=80',
        'martial_arts':    'https://images.unsplash.com/photo-1555597673-b21d5c935865?w=700&q=80',
        'stretching':      'https://images.unsplash.com/photo-1566241142559-40e1dab266c6?w=700&q=80',
        'other':           'https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=700&q=80',
    }

    CR = [
        # Blossom Wellness Studio – Redditch (pid=0)
        dict(pid=0,title='Morning Yoga Flow',activity_type='yoga',img='https://images.unsplash.com/photo-1588286840104-8957b019727f?w=700&q=80',
             desc='Gentle morning yoga for all levels. Start your day with intention, breath, and movement in our calm studio. No experience needed.',
             level='all_levels',mins=60,cap=15,price=10.0,city='Redditch',
             address='15 Unicorn Hill, Redditch, B97 4AA',postcode='B97 4AA',
             lang='English',access='Step-free access available',lat=52.3063,lng=-1.9449),
        dict(pid=0,title='Mindfulness & Meditation',activity_type='meditation',img='https://images.unsplash.com/photo-1602192509154-0b900ee1f851?w=700&q=80',
             desc='Guided meditation for stress relief and inner calm using breathing techniques, body scan and visualisation. Perfect for beginners.',
             level='beginner',mins=45,cap=12,price=0.0,free=True,city='Redditch',
             address='15 Unicorn Hill, Redditch, B97 4AA',postcode='B97 4AA',
             lang='English',lat=52.3063,lng=-1.9449),
        dict(pid=0,title='Pilates Flow',activity_type='pilates',img='https://images.unsplash.com/photo-1518611012118-696072aa579a?w=700&q=80',
             desc='Core-focused Pilates to improve posture, flexibility and strength. Small classes mean personalised attention from your instructor.',
             level='all_levels',mins=55,cap=14,price=9.0,city='Redditch',
             address='15 Unicorn Hill, Redditch, B97 4AA',postcode='B97 4AA',
             lang='Urdu',lat=52.3063,lng=-1.9449),
        dict(pid=0,title='Barre Fitness',activity_type='barre',img='https://images.unsplash.com/photo-1516526995003-435ccce2be97?w=700&q=80',
             desc='Ballet-inspired barre workout combining elements of dance, yoga and pilates. Sculpt and tone your body while having fun.',
             level='beginner',mins=50,cap=12,price=11.0,city='Redditch',
             address='15 Unicorn Hill, Redditch, B97 4AA',postcode='B97 4AA',
             lang='English',lat=52.3063,lng=-1.9449),
        dict(pid=0,title='Gentle Stretching',activity_type='stretching',img='https://images.unsplash.com/photo-1566241142559-40e1dab266c6?w=700&q=80',
             desc='Slow restorative stretching focused on flexibility, easing muscle tension and relaxation. Ideal for recovery or as a wind-down.',
             level='beginner',mins=45,cap=16,price=8.0,city='Redditch',
             address='15 Unicorn Hill, Redditch, B97 4AA',postcode='B97 4AA',
             lang='English',access='Fully accessible, seated options available',lat=52.3063,lng=-1.9449),
        dict(pid=0,title="Women's Self-Defence",activity_type='martial_arts',img='https://images.unsplash.com/photo-1555597673-b21d5c935865?w=700&q=80',
             desc='Practical self-defence taught in a safe, empowering environment. No martial arts experience needed — learn awareness, confidence and how to protect yourself.',
             level='all_levels',mins=60,cap=14,price=12.0,city='Redditch',
             address='15 Unicorn Hill, Redditch, B97 4AA',postcode='B97 4AA',
             lang='English',lat=52.3063,lng=-1.9449),
        # FemFit Bromsgrove (pid=1)
        dict(pid=1,title='Strength & Confidence',activity_type='strength',img='https://images.unsplash.com/photo-1534258936925-c58bed479fcb?w=700&q=80',
             desc='Fun strength training for women of all sizes. Build real-world strength using weights, resistance bands and bodyweight in an encouraging female-only space.',
             level='beginner',mins=50,cap=10,price=12.0,city='Bromsgrove',
             address='22 High Street, Bromsgrove, B60 1AB',postcode='B60 1AB',
             lang='English',lat=52.3352,lng=-2.0594),
        dict(pid=1,title='HIIT Burn',activity_type='hiit',img='https://images.unsplash.com/photo-1518310383802-640c2de311b2?w=700&q=80',
             desc='High-intensity interval training to boost fitness and feel powerful. Short bursts of effort followed by rest — suitable for all fitness levels.',
             level='intermediate',mins=45,cap=16,price=11.0,city='Bromsgrove',
             address='22 High Street, Bromsgrove, B60 1AB',postcode='B60 1AB',
             lang='English',lat=52.3352,lng=-2.0594),
        dict(pid=1,title="Women's Walking Group",activity_type='walking_group',img='https://images.unsplash.com/photo-1476480862126-209bfaa8edc8?w=700&q=80',
             desc='Friendly outdoor walking group exploring beautiful local routes around Bromsgrove. Fresh air, exercise, and genuine connections with like-minded women.',
             level='all_levels',mins=90,cap=20,price=0.0,free=True,city='Bromsgrove',
             address='Bromsgrove Library, Stratford Road, Bromsgrove, B61 8DN',postcode='B61 8DN',
             lang='English',access='All-terrain accessible',lat=52.3352,lng=-2.0594),
        dict(pid=1,title='Indoor Cycling',activity_type='cycling',img='https://hips.hearstapps.com/hmg-prod/images/woman-working-out-on-her-indoors-cycling-turbo-royalty-free-image-1702313926.jpg',
             desc='High-energy indoor cycling to build cardiovascular fitness and leg strength. All bikes adjustable for any height and fitness level. Beginners very welcome!',
             level='all_levels',mins=45,cap=12,price=10.0,city='Bromsgrove',
             address='22 High Street, Bromsgrove, B60 1AB',postcode='B60 1AB',
             lang='English',lat=52.3352,lng=-2.0594),
        dict(pid=1,title='Boxing Fitness',activity_type='boxing',img='https://www.boxnburn.com/wp-content/uploads/2020/08/outdoor-fitness-gym-class-boxing-santa-monica-1-1280x1024.jpg',
             desc='Empowering boxing fitness class using pads, bags and drills. No sparring — pure fitness fun. Build confidence, coordination and strength.',
             level='all_levels',mins=55,cap=10,price=13.0,city='Bromsgrove',
             address='22 High Street, Bromsgrove, B60 1AB',postcode='B60 1AB',
             lang='English',lat=52.3352,lng=-2.0594),
        dict(pid=1,title='Aqua Aerobics',activity_type='swimming',img='https://images.healthshots.com/healthshots/en/uploads/2023/07/11123418/water-aerobics.jpg',
             desc='Low-impact water aerobics easy on joints but highly effective for cardio and strength. Perfect for all ages and abilities.',
             level='all_levels',mins=45,cap=18,price=8.0,city='Bromsgrove',
             address='Bromsgrove Leisure Centre, Slideslow Drive, Bromsgrove, B60 3PL',postcode='B60 3PL',
             lang='English',access='Pool lift available',lat=52.3210,lng=-2.0489),
        # Serenity Mind & Body – Worcester (pid=2)
        dict(pid=2,title='Wellbeing Workshop',activity_type='mental_wellbeing',img='https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?w=700&q=80',
             desc='Breathwork, journalling and self-care in a safe space. Evidence-based tools to manage stress, anxiety and burnout. Facilitated by a qualified female therapist.',
             level='beginner',mins=60,cap=12,price=15.0,city='Worcester',
             address='8 Foregate Street, Worcester, WR1 2JH',postcode='WR1 2JH',
             lang='Arabic',lat=52.1927,lng=-2.2200),
        dict(pid=2,title='Dance Cardio',activity_type='dance',img='https://www.jazzercise.com/_next/image?url=https:%2F%2Fjazzercise.wpenginepowered.com%2Fwp-content%2Fuploads%2F2024%2F03%2F03-15_Top10DanceFitness_MN.webp.webp&w=3840&q=100',
             desc='Joyful dance-based cardio — no experience needed! Celebrate your body, build confidence and connect with your community through music and movement.',
             level='all_levels',mins=50,cap=18,price=10.0,city='Worcester',
             address='8 Foregate Street, Worcester, WR1 2JH',postcode='WR1 2JH',
             lang='English',lat=52.1927,lng=-2.2200),
        dict(pid=2,title='Nutrition & Wellness Talk',activity_type='nutrition',img='https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=700&q=80',
             desc='Practical nutrition advice for busy women — meal prep, hormonal health, emotional eating and building a positive relationship with food.',
             level='all_levels',mins=75,cap=25,price=0.0,free=True,city='Worcester',
             address='8 Foregate Street, Worcester, WR1 2JH',postcode='WR1 2JH',
             lang='English',lat=52.1927,lng=-2.2200),
        dict(pid=2,title='Zumba Party',activity_type='zumba',img='https://images.unsplash.com/photo-1504609773096-104ff2c73ba4?w=700&q=80',
             desc='High-energy Zumba combining Latin dance and fitness. The most fun you can have exercising! Suitable for all levels.',
             level='all_levels',mins=55,cap=20,price=9.0,city='Worcester',
             address='8 Foregate Street, Worcester, WR1 2JH',postcode='WR1 2JH',
             lang='English',lat=52.1927,lng=-2.2200),
        dict(pid=2,title='Relaxation Yoga',activity_type='yoga',img='https://images.unsplash.com/photo-1506126613408-eca07ce68773?w=700&q=80',
             desc='Evening yoga focused entirely on deep relaxation, gentle stretching and stress relief. End your day in stillness. Bolsters and blankets provided.',
             level='beginner',mins=60,cap=14,price=10.0,city='Worcester',
             address='8 Foregate Street, Worcester, WR1 2JH',postcode='WR1 2JH',
             lang='English',access='Step-free entrance',lat=52.1927,lng=-2.2200),
        dict(pid=2,title='Mindful Swimming',activity_type='swimming',img='https://media.istockphoto.com/id/166935181/photo/portrait-of-smiling-women-with-arms-raised-in-swimming-pool.jpg?s=612x612&w=0&k=20&c=XGAtXsf8nNOIbhGSBXVqFVyllPOY84gC3TjwFZ5MmWY=',
             desc='Women-only mindful swimming combining gentle swimming techniques with breathwork and mindfulness. All abilities welcome.',
             level='all_levels',mins=60,cap=8,price=14.0,city='Worcester',
             address='Worcester Leisure Centre, Perdiswell Park, Worcester, WR3 7EX',postcode='WR3 7EX',
             lang='English',access='Accessible pool facilities',lat=52.2120,lng=-2.2073),
        # ActiveWomen Birmingham (pid=3)
        dict(pid=3,title='Power Yoga',activity_type='yoga',img='https://images.unsplash.com/photo-1575052814086-f385e2e2ad1b?w=700&q=80',
             desc='Dynamic and challenging yoga combining strength, flexibility and breathwork. Build a powerful body and a calm mind in our energising Birmingham studio.',
             level='intermediate',mins=60,cap=16,price=14.0,city='Birmingham',
             address='45 Broad Street, Birmingham, B1 1BB',postcode='B1 1BB',
             lang='English',lat=52.4796,lng=-1.9026),
        dict(pid=3,title="Women's Boxing Club",activity_type='boxing',img='https://imgcdn.stablediffusionweb.com/2025/5/21/cafb9c6b-7300-491c-b205-8b9eef73e169.jpg',
             desc='Serious boxing training for women — technique, bag work, sparring drills and fitness. Female coaches create a challenging yet supportive environment.',
             level='all_levels',mins=60,cap=12,price=15.0,city='Birmingham',
             address='45 Broad Street, Birmingham, B1 1BB',postcode='B1 1BB',
             lang='English',lat=52.4796,lng=-1.9026),
        dict(pid=3,title='Body Pump',activity_type='strength',img='https://degymplatinum.com/wp-content/uploads/2023/07/FUJI5854-scaled.jpg',
             desc='The original barbell class for women. Build strength, increase core stability and improve bone density in a motivating group setting.',
             level='all_levels',mins=55,cap=20,price=12.0,city='Birmingham',
             address='45 Broad Street, Birmingham, B1 1BB',postcode='B1 1BB',
             lang='English',lat=52.4796,lng=-1.9026),
        dict(pid=3,title='Latin Dance Fitness',activity_type='dance',img='https://images.unsplash.com/photo-1518834107812-67b0b7c58434?w=700&q=80',
             desc='Salsa, merengue and cumbia combined into an explosive cardio dance workout. Burn calories, boost your mood and learn amazing dance moves. No partner needed!',
             level='all_levels',mins=50,cap=22,price=10.0,city='Birmingham',
             address='45 Broad Street, Birmingham, B1 1BB',postcode='B1 1BB',
             lang='English',lat=52.4796,lng=-1.9026),
        dict(pid=3,title='Anxiety & Stress Management',activity_type='mental_wellbeing',img='https://images.pexels.com/photos/5717262/pexels-photo-5717262.jpeg?auto=compress&cs=tinysrgb&w=1600',
             desc='CBT techniques, mindfulness and peer support in a women-only group. Facilitated by a qualified counsellor. A safe space to talk, breathe and heal.',
             level='all_levels',mins=75,cap=10,price=0.0,free=True,city='Birmingham',
             address='45 Broad Street, Birmingham, B1 1BB',postcode='B1 1BB',
             lang='Urdu',access='Quiet room, low sensory',lat=52.4796,lng=-1.9026),
        dict(pid=3,title='Spin & Core',activity_type='cycling',img='https://media.istockphoto.com/id/507108546/photo/working-out-on-stationary-bikes.jpg?s=612x612&w=0&k=20&c=pqotatX5O_yRHof-uxsFmJiJ2J-1IGTyabO2w6Hhw_Q=',
             desc='30 minutes of intense indoor cycling followed by 20 minutes of core strengthening. The ultimate combo for cardiovascular fitness and a strong core.',
             level='intermediate',mins=50,cap=14,price=13.0,city='Birmingham',
             address='45 Broad Street, Birmingham, B1 1BB',postcode='B1 1BB',
             lang='English',lat=52.4796,lng=-1.9026),
    ]

    fitness_classes = []
    for cd in CR:
        fc = FitnessClass(
            provider_id=provider_profiles[cd['pid']].id,
            title=cd['title'], description=cd['desc'],
            activity_type=cd['activity_type'],
            difficulty_level=cd.get('level','all_levels'),
            duration_minutes=cd['mins'], max_capacity=cd['cap'],
            price=cd['price'], is_free=cd.get('free',False),
            is_women_only=True, is_active=True,
            city=cd['city'], postcode=cd.get('postcode',''),
            location=cd.get('address',''),
            language=cd.get('lang','English'),
            accessibility_info=cd.get('access',None),
            cover_image_url=cd.get('img') or IMGS.get(cd['activity_type'], IMGS['other']),
            latitude=cd.get('lat'), longitude=cd.get('lng'))
        db.session.add(fc); db.session.flush()
        fitness_classes.append(fc)

    # SCHEDULES – 2 per class per week for 6 weeks
    base = date.today()
    slot_times = [time(7,0),time(9,0),time(10,30),time(12,0),
                  time(17,30),time(18,0),time(18,30),time(19,0)]
    schedules = []
    for week in range(6):
        for i, fc in enumerate(fitness_classes):
            for slot in range(2):
                dow = (i*3+slot*2)%7
                days_ahead = (dow - base.weekday())%7 + week*7
                sdate = base + timedelta(days=days_ahead)
                ts = slot_times[(i+slot)%len(slot_times)]
                end_mins = ts.hour*60 + ts.minute + fc.duration_minutes
                te = time(min(end_mins//60,23), end_mins%60)
                s = ClassSchedule(class_id=fc.id, date=sdate,
                    start_time=ts, end_time=te, available_spots=fc.max_capacity)
                db.session.add(s); schedules.append(s)
    db.session.flush()

    # BOOKINGS
    for m in members:
        for _ in range(5):
            fc = random.choice(fitness_classes)
            fc_scheds = [s for s in schedules if s.class_id==fc.id]
            if not fc_scheds: continue
            s = random.choice(fc_scheds)
            b = Booking(user_id=m.id, class_id=fc.id, schedule_id=s.id,
                status=random.choice(['confirmed','confirmed','confirmed','attended','cancelled']),
                confirmation_code=gen_code(),
                booking_date=datetime.utcnow()-timedelta(days=random.randint(1,30)))
            db.session.add(b)
            fc.current_bookings = min(fc.max_capacity,(fc.current_bookings or 0)+1)
    db.session.flush()

    # REVIEWS
    rtexts = [
        "Absolutely loved this class! The instructor was so encouraging and the atmosphere incredibly welcoming. Felt comfortable from the moment I walked in.",
        "Such a safe and supportive space. As someone always nervous about group fitness, this changed everything for me.",
        "The perfect women-only environment. No judgement, just pure support and positive energy from everyone.",
        "Really enjoyed the pace and energy. The instructor adapts to everyone's level which is so refreshing. Booking again next week!",
        "Wonderful instructor who really listens. I left feeling so positive and energised — exactly what I needed after a stressful week.",
        "Nervous as a complete beginner but everyone was so kind. The instructor made modifications for me throughout. Highly recommend!",
        "A genuinely transformative experience. Two months in and the difference in my confidence is remarkable. Worth every penny.",
        "Love the community feel. You really get to know the other women — it becomes so much more than just a workout.",
        "The instructor has a real gift for making everyone feel included. Sessions fly by because you're having so much fun.",
        "I started coming after a difficult period in my life and these classes helped me so much — physically and mentally.",
        "Excellent facilities and a knowledgeable, passionate instructor. I always leave feeling stronger and happier.",
        "Perfect for women returning to fitness after children. No pressure, great support, and genuinely fun from start to finish.",
    ]
    rtitles = ["Life-changing experience!","Best women's class in the area",
               "Finally found my community","Highly recommend to all women",
               "Brilliant instructor","Exactly what I needed",
               "Welcoming and professional","My weekly highlight!",
               "Worth every penny","Changed my relationship with fitness",
               "Incredible supportive space","Wish I'd found this sooner!"]
    for m in members:
        for fc in random.sample(fitness_classes, min(5,len(fitness_classes))):
            db.session.add(Review(
                user_id=m.id, class_id=fc.id, provider_id=fc.provider_id,
                rating=random.choice([4,4,5,5,5]),
                title=random.choice(rtitles), body=random.choice(rtexts),
                is_approved=True, is_verified_attendee=True,
                created_at=datetime.utcnow()-timedelta(days=random.randint(1,60))))
    db.session.flush()

    from sqlalchemy import func
    for pp in provider_profiles:
        res = db.session.query(func.avg(Review.rating),func.count(Review.id))\
                .filter_by(provider_id=pp.id,is_approved=True).first()
        if res and res[0]:
            pp.average_rating=round(float(res[0]),1); pp.total_reviews=res[1]

    # DISCUSSIONS
    for author,title,body,cat,views in [
        (members[0],'Best beginner yoga tips? 🧘','Hi everyone! Just started yoga and would love tips. What helped you most in the first few weeks?','fitness_tips',42),
        (members[1],'Healthy meal prep ideas for busy mums?',"Working mum of two struggling to eat well. Any quick healthy meal prep ideas?",'nutrition',31),
        (members[2],'Managing anxiety before a new class?',"I want to try dance cardio but always get anxious in new group settings. Any advice?",'mental_health',58),
        (members[0],"Walking group Bromsgrove — joining Saturday?",'Planning to come this Saturday! The route through Waseley Hills is beautiful this time of year.','general_chat',19),
        (members[3],'Arabic-speaking members — Worcester Workshop',"Just a reminder the Wellbeing Workshop at Serenity Mind & Body is available in Arabic!",'events',27),
        (members[4],'Tips for staying motivated through winter?',"With darker evenings it is so hard to keep up with fitness. What keeps you all going?",'fitness_tips',35),
    ]:
        d = Discussion(author_id=author.id,title=title,body=body,category=cat,
                       is_active=True,view_count=views,
                       created_at=datetime.utcnow()-timedelta(days=random.randint(1,14)))
        db.session.add(d); db.session.flush()
        for _ in range(random.randint(1,3)):
            db.session.add(DiscussionReply(
                discussion_id=d.id, author_id=random.choice(members).id,
                body=random.choice(["Thanks for sharing! Really helpful 💜","I had the exact same experience. You've got this!","Such a great point — this community is amazing.","Totally agree! The instructors here make such a difference."]),
                created_at=datetime.utcnow()-timedelta(days=random.randint(0,3))))

    # REPORTS
    db.session.add_all([
        Report(reporter_id=members[0].id,report_type='review',reason='inappropriate_content',
               status='pending',description='Review contains inappropriate language.',
               created_at=datetime.utcnow()-timedelta(hours=5)),
        Report(reporter_id=members[1].id,report_type='discussion',reason='spam',
               status='pending',description='Post appears to be promotional spam.',
               created_at=datetime.utcnow()-timedelta(hours=12)),
        Report(reporter_id=members[2].id,report_type='review',reason='fake_review',
               status='resolved',description='Suspected fake review — no booking found.',
               created_at=datetime.utcnow()-timedelta(days=3),
               resolved_at=datetime.utcnow()-timedelta(days=2)),
    ])

    # NOTIFICATIONS
    for m in members:
        db.session.add(Notification(user_id=m.id,title='Welcome to BloomWell! 🌸',
            message='Your account is set up. Start exploring women-only classes near you!',notif_type='system'))
        db.session.add(Notification(user_id=m.id,title='📅 Class Reminder',
            message='You have a class coming up tomorrow. Check your bookings!',notif_type='reminder'))

    db.session.commit()
    print("\n✅ BloomWell database seeded successfully!\n")
    print("═══════════════════════════════════════════════")
    print("  Admin:    admin@bloomwell.com  /  Admin@123")
    print("  Member:   member@bloomwell.com /  Member@123")
    print("  Provider: amara@bloomwell.com  /  Provider@123")
    print("═══════════════════════════════════════════════")
    print(f"  {len(fitness_classes)} classes | {len(schedules)} schedules | {len(members)*5} bookings")
    print("═══════════════════════════════════════════════\n")
