import calendar
from datetime import datetime
import random
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# ============ DATA (STORED IN MEMORY) ============

users = [
    {
        'id': 1,
        'name': 'Alex Johnson',
        'username': 'alex',
        'department': 'Engineering',
        'tenure': 3,
        'interests': 'Football, Board games, Coffee',
        'profile_pic_emoji': '👨‍💻',
        'bio': 'Loves coding and hiking'
    },
    {
        'id': 2,
        'name': 'Maria Garcia',
        'username': 'maria',
        'department': 'Marketing',
        'tenure': 2,
        'interests': 'Photography, Hiking, Reading',
        'profile_pic_emoji': '👩‍🎨',
        'bio': 'Creative mind with a passion for design'
    },
    {
        'id': 3,
        'name': 'David Kim',
        'username': 'david',
        'department': 'Sales',
        'tenure': 5,
        'interests': 'Guitar, Cooking, Tennis',
        'profile_pic_emoji': '👨‍🍳',
        'bio': 'Foodie and music lover'
    }
]

# Pastel colors for events
COLORS = ['#FFB3BA', '#C1E1C1', '#A7C7E7', '#FFD580', '#D4A5A5', '#E0BBE4', '#B5EAD7']

events = [
    {
        'id': 1,
        'title': 'Team Lunch',
        'date': '2026-03-15',
        'time': '12:30',
        'location': 'Cafe Central',
        'description': 'Casual team lunch - Italian food!',
        'emoji': '🍕',
        'created_by': 1,
        'participants': [1, 2],
        'color': '#FFB3BA'
    },
    {
        'id': 2,
        'title': 'Yoga Class',
        'date': '2026-03-15',
        'time': '18:00',
        'location': 'Online (Zoom)',
        'description': 'Relaxing yoga session for beginners',
        'emoji': '🧘',
        'created_by': 2,
        'participants': [1, 3],
        'color': '#C1E1C1'
    },
    {
        'id': 3,
        'title': 'Birthday Party',
        'date': '2026-03-18',
        'time': '16:00',
        'location': 'Office Rooftop',
        'description': 'Celebrating Maria\'s birthday! Cake and drinks',
        'emoji': '🎂',
        'created_by': 3,
        'participants': [2],
        'color': '#A7C7E7'
    },
    {
        'id': 4,
        'title': 'Coffee Chat',
        'date': '2026-03-20',
        'time': '10:00',
        'location': 'Coffee Shop',
        'description': 'Casual coffee and networking',
        'emoji': '☕',
        'created_by': 1,
        'participants': [1],
        'color': '#FFD580'
    }
]

# ============ HELPER FUNCTIONS ============

def get_user_by_id(user_id):
    """Get user by ID, return None if not found"""
    for user in users:
        if user['id'] == user_id:
            return user
    return None

def get_event_by_id(event_id):
    """Get event by ID"""
    for event in events:
        if event['id'] == event_id:
            return event
    return None

def get_user_events(user_id):
    """Get all events where user is a participant"""
    user_events = []
    for event in events:
        if user_id in event['participants']:
            user_events.append(event)
    return user_events

def build_calendar_days(year, month):
    """Build a 6-week calendar grid with events"""
    # Get first day of month (0=Monday, 6=Sunday)
    first_day, num_days = calendar.monthrange(year, month)
    
    # Create empty grid of 42 cells (6 weeks * 7 days)
    calendar_days = []
    
    # Add empty cells for days before month starts
    for _ in range(first_day):
        calendar_days.append({'day': None, 'events': []})
    
    # Add days of the month
    for day in range(1, num_days + 1):
        date_str = f"{year}-{month:02d}-{day:02d}"
        # Find events on this date
        day_events = []
        for event in events:
            if event['date'] == date_str:
                day_events.append(event)
        calendar_days.append({'day': day, 'events': day_events})
    
    # Add empty cells for remaining days to reach 42
    while len(calendar_days) < 42:
        calendar_days.append({'day': None, 'events': []})
    
    return calendar_days

# ============ ROUTES ============

@app.route('/')
def index():
    """Main page with calendar and event feed"""
    now = datetime.now()
    year = now.year
    month = now.month
    month_name = now.strftime('%B %Y')

    calendar_days = build_calendar_days(year, month)

    # Get upcoming events (next 30 days for feed)
    upcoming_events = []
    for event in events:
        event_date = datetime.strptime(event['date'], '%Y-%m-%d')
        if event_date >= now:
            upcoming_events.append(event)
    # Sort by date
    upcoming_events.sort(key=lambda x: x['date'])

    # Get current user (default to user 1)
    current_user = get_user_by_id(1)

    return render_template('index.html',
                           calendar_days=calendar_days,
                           month_name=month_name,
                           events=upcoming_events[:10],  # Show only 10 latest
                           users=users,
                           current_user=current_user)  # ← ЭТО ВАЖНО!
@app.route('/create', methods=['GET', 'POST'])
def create_event():
    """Create new event page"""
    if request.method == 'POST':
        # Get form data
        new_event = {
            'id': len(events) + 1,
            'title': request.form['title'],
            'date': request.form['date'],
            'time': request.form['time'],
            'location': request.form['location'],
            'description': request.form['description'],
            'emoji': request.form.get('emoji', '📅'),
            'created_by': 1,  # Default user
            'participants': [1],  # Creator automatically joins
            'color': random.choice(COLORS)
        }
        events.append(new_event)
        return redirect(url_for('index'))
    
    return render_template('create_event.html')

@app.route('/join/<int:event_id>')
def join_event(event_id):
    """Join an event (default user ID=1)"""
    event = get_event_by_id(event_id)
    if event and 1 not in event['participants']:
        event['participants'].append(1)
    return redirect(url_for('index'))

@app.route('/profile/<int:user_id>')
def profile(user_id):
    """User profile page"""
    user = get_user_by_id(user_id)
    if not user:
        # If user not found, show default user
        user = users[0]
        user_id = user['id']
    
    user_events = get_user_events(user_id)
    return render_template('profile.html', user=user, events=user_events)

@app.route('/profile/')
def profile_default():
    """Redirect to default profile"""
    return redirect(url_for('profile', user_id=1))

if __name__ == '__main__':
    app.run(debug=True,port=8080)
