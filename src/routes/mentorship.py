from flask import Blueprint, jsonify, request, session
from src.models.user import User, UserProfile, db
from datetime import datetime, timedelta
import json
import uuid

mentorship_bp = Blueprint('mentorship', __name__)

# Mentor data (in real implementation, this would be in database)
MENTORS_DATA = [
    {
        "id": 1,
        "name": "Arjun Sharma",
        "college": "IIT Delhi",
        "course": "B.Tech Computer Science",
        "year": "4th Year",
        "expertise": ["JEE Preparation", "Computer Science", "Campus Life", "Placements"],
        "rating": 4.9,
        "reviews_count": 127,
        "sessions_completed": 245,
        "bio": "Final year CS student at IIT Delhi with internship experience at Google. Passionate about helping JEE aspirants achieve their dreams.",
        "achievements": [
            "JEE Advanced AIR 156",
            "Google Summer Intern 2024",
            "ACM ICPC Regionalist",
            "Dean's List for 3 consecutive semesters"
        ],
        "availability": {
            "days": ["Monday", "Wednesday", "Friday", "Sunday"],
            "time_slots": ["10:00-12:00", "14:00-16:00", "19:00-21:00"]
        },
        "pricing": {
            "per_session": 499,
            "package_5": 2199,
            "package_10": 3999
        },
        "languages": ["English", "Hindi"],
        "location": "Delhi",
        "profile_image": "/images/mentors/arjun.jpg",
        "specializations": ["JEE Main", "JEE Advanced", "BITSAT"],
        "response_time": "Within 2 hours",
        "success_stories": 45,
        "is_verified": True,
        "is_available": True
    },
    {
        "id": 2,
        "name": "Priya Patel",
        "college": "AIIMS Delhi",
        "course": "MBBS",
        "year": "3rd Year",
        "expertise": ["NEET Preparation", "Medical Studies", "Study Techniques", "Time Management"],
        "rating": 4.8,
        "reviews_count": 89,
        "sessions_completed": 156,
        "bio": "MBBS student at AIIMS Delhi. Cleared NEET with AIR 23. Love helping medical aspirants with preparation strategies and motivation.",
        "achievements": [
            "NEET AIR 23",
            "State Topper in 12th Boards",
            "Medical Quiz Champion",
            "Research publication in medical journal"
        ],
        "availability": {
            "days": ["Tuesday", "Thursday", "Saturday", "Sunday"],
            "time_slots": ["09:00-11:00", "15:00-17:00", "20:00-22:00"]
        },
        "pricing": {
            "per_session": 599,
            "package_5": 2699,
            "package_10": 4999
        },
        "languages": ["English", "Hindi", "Gujarati"],
        "location": "Delhi",
        "profile_image": "/images/mentors/priya.jpg",
        "specializations": ["NEET UG", "AIIMS", "Medical Career Guidance"],
        "response_time": "Within 3 hours",
        "success_stories": 32,
        "is_verified": True,
        "is_available": True
    },
    {
        "id": 3,
        "name": "Rahul Kumar",
        "college": "IIM Bangalore",
        "course": "MBA",
        "year": "2nd Year",
        "expertise": ["CAT Preparation", "MBA Admissions", "Interview Preparation", "Career Guidance"],
        "rating": 4.7,
        "reviews_count": 64,
        "sessions_completed": 98,
        "bio": "MBA student at IIM Bangalore. CAT 99.8 percentiler. Former software engineer with 3 years experience. Helping CAT aspirants crack the exam.",
        "achievements": [
            "CAT 99.8 percentile",
            "IIM Bangalore MBA",
            "3 years software engineering experience",
            "Summer internship at McKinsey"
        ],
        "availability": {
            "days": ["Monday", "Wednesday", "Friday", "Saturday"],
            "time_slots": ["11:00-13:00", "16:00-18:00", "21:00-23:00"]
        },
        "pricing": {
            "per_session": 699,
            "package_5": 3199,
            "package_10": 5999
        },
        "languages": ["English", "Hindi"],
        "location": "Bangalore",
        "profile_image": "/images/mentors/rahul.jpg",
        "specializations": ["CAT", "MBA Admissions", "Career Switch"],
        "response_time": "Within 4 hours",
        "success_stories": 28,
        "is_verified": True,
        "is_available": True
    },
    {
        "id": 4,
        "name": "Sneha Reddy",
        "college": "NLSIU Bangalore",
        "course": "BA LLB",
        "year": "4th Year",
        "expertise": ["CLAT Preparation", "Law Studies", "Legal Career", "Moot Courts"],
        "rating": 4.6,
        "reviews_count": 42,
        "sessions_completed": 67,
        "bio": "Final year law student at NLSIU Bangalore. CLAT AIR 45. Active in moot courts and legal research. Passionate about legal education.",
        "achievements": [
            "CLAT AIR 45",
            "National Moot Court Winner",
            "Legal Research Publications",
            "Internship at Supreme Court"
        ],
        "availability": {
            "days": ["Tuesday", "Thursday", "Saturday"],
            "time_slots": ["10:00-12:00", "17:00-19:00"]
        },
        "pricing": {
            "per_session": 449,
            "package_5": 1999,
            "package_10": 3699
        },
        "languages": ["English", "Hindi", "Telugu"],
        "location": "Bangalore",
        "profile_image": "/images/mentors/sneha.jpg",
        "specializations": ["CLAT", "Law Career Guidance", "Legal Studies"],
        "response_time": "Within 6 hours",
        "success_stories": 18,
        "is_verified": True,
        "is_available": True
    },
    {
        "id": 5,
        "name": "Vikash Singh",
        "college": "NIT Trichy",
        "course": "B.Tech Mechanical",
        "year": "Alumni (2023)",
        "expertise": ["JEE Main", "NIT Admissions", "Mechanical Engineering", "Placements"],
        "rating": 4.5,
        "reviews_count": 78,
        "sessions_completed": 134,
        "bio": "NIT Trichy alumnus working at Tata Motors. JEE Main AIR 1200. Helping students with JEE preparation and engineering career guidance.",
        "achievements": [
            "JEE Main AIR 1200",
            "NIT Trichy Mechanical Engineering",
            "Placed at Tata Motors",
            "Technical Society President"
        ],
        "availability": {
            "days": ["Saturday", "Sunday"],
            "time_slots": ["09:00-11:00", "14:00-16:00", "19:00-21:00"]
        },
        "pricing": {
            "per_session": 399,
            "package_5": 1799,
            "package_10": 3299
        },
        "languages": ["English", "Hindi"],
        "location": "Chennai",
        "profile_image": "/images/mentors/vikash.jpg",
        "specializations": ["JEE Main", "NIT Admissions", "Mechanical Engineering"],
        "response_time": "Within 8 hours",
        "success_stories": 25,
        "is_verified": True,
        "is_available": True
    }
]

@mentorship_bp.route('/mentors', methods=['GET'])
def get_all_mentors():
    """Get all mentors with optional filtering"""
    college = request.args.get('college')
    expertise = request.args.get('expertise')
    location = request.args.get('location')
    min_rating = request.args.get('min_rating', type=float)
    max_price = request.args.get('max_price', type=int)
    available_only = request.args.get('available_only', 'true').lower() == 'true'
    
    mentors = MENTORS_DATA.copy()
    
    # Apply filters
    if college:
        mentors = [mentor for mentor in mentors if college.lower() in mentor['college'].lower()]
    
    if expertise:
        mentors = [mentor for mentor in mentors if 
                  any(expertise.lower() in exp.lower() for exp in mentor['expertise'])]
    
    if location:
        mentors = [mentor for mentor in mentors if location.lower() in mentor['location'].lower()]
    
    if min_rating:
        mentors = [mentor for mentor in mentors if mentor['rating'] >= min_rating]
    
    if max_price:
        mentors = [mentor for mentor in mentors if mentor['pricing']['per_session'] <= max_price]
    
    if available_only:
        mentors = [mentor for mentor in mentors if mentor['is_available']]
    
    # Sort by rating (descending)
    mentors.sort(key=lambda x: x['rating'], reverse=True)
    
    return jsonify({
        'mentors': mentors,
        'total': len(mentors)
    }), 200

@mentorship_bp.route('/mentors/<int:mentor_id>', methods=['GET'])
def get_mentor_details(mentor_id):
    """Get detailed information about a specific mentor"""
    mentor = next((mentor for mentor in MENTORS_DATA if mentor['id'] == mentor_id), None)
    
    if not mentor:
        return jsonify({'error': 'Mentor not found'}), 404
    
    return jsonify({'mentor': mentor}), 200

@mentorship_bp.route('/mentors/search', methods=['POST'])
def search_mentors():
    """Search mentors based on specific criteria"""
    data = request.json
    target_exam = data.get('target_exam')
    preferred_college = data.get('preferred_college')
    budget_range = data.get('budget_range')  # low, medium, high
    expertise_areas = data.get('expertise_areas', [])
    
    mentors = MENTORS_DATA.copy()
    
    # Filter by target exam
    if target_exam:
        mentors = [mentor for mentor in mentors if 
                  any(target_exam.lower() in spec.lower() for spec in mentor['specializations'])]
    
    # Filter by preferred college
    if preferred_college:
        mentors = [mentor for mentor in mentors if 
                  preferred_college.lower() in mentor['college'].lower()]
    
    # Filter by budget range
    if budget_range:
        if budget_range == 'low':
            mentors = [mentor for mentor in mentors if mentor['pricing']['per_session'] <= 400]
        elif budget_range == 'medium':
            mentors = [mentor for mentor in mentors if 400 < mentor['pricing']['per_session'] <= 600]
        elif budget_range == 'high':
            mentors = [mentor for mentor in mentors if mentor['pricing']['per_session'] > 600]
    
    # Filter by expertise areas
    if expertise_areas:
        mentors = [mentor for mentor in mentors if 
                  any(area.lower() in exp.lower() for area in expertise_areas for exp in mentor['expertise'])]
    
    # Sort by rating and success stories
    mentors.sort(key=lambda x: (x['rating'], x['success_stories']), reverse=True)
    
    return jsonify({
        'mentors': mentors,
        'total': len(mentors),
        'search_criteria': data
    }), 200

@mentorship_bp.route('/mentors/<int:mentor_id>/book', methods=['POST'])
def book_mentor_session():
    """Book a session with a mentor"""
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    try:
        data = request.json
        mentor_id = data.get('mentor_id')
        session_date = data.get('session_date')
        session_time = data.get('session_time')
        session_type = data.get('session_type', 'single')  # single, package_5, package_10
        message = data.get('message', '')
        
        if not all([mentor_id, session_date, session_time]):
            return jsonify({'error': 'Mentor ID, date, and time are required'}), 400
        
        # Check if mentor exists
        mentor = next((mentor for mentor in MENTORS_DATA if mentor['id'] == mentor_id), None)
        if not mentor:
            return jsonify({'error': 'Mentor not found'}), 404
        
        if not mentor['is_available']:
            return jsonify({'error': 'Mentor is currently unavailable'}), 400
        
        # Validate session date and time
        try:
            session_datetime = datetime.strptime(f"{session_date} {session_time}", "%Y-%m-%d %H:%M")
            if session_datetime <= datetime.now():
                return jsonify({'error': 'Session must be scheduled for future date/time'}), 400
        except ValueError:
            return jsonify({'error': 'Invalid date/time format'}), 400
        
        # Calculate pricing
        pricing = mentor['pricing']
        if session_type == 'package_5':
            amount = pricing['package_5']
            sessions_count = 5
        elif session_type == 'package_10':
            amount = pricing['package_10']
            sessions_count = 10
        else:
            amount = pricing['per_session']
            sessions_count = 1
        
        # Create booking record (in real implementation, this would be stored in database)
        booking = {
            'id': str(uuid.uuid4()),
            'user_id': session['user_id'],
            'mentor_id': mentor_id,
            'session_date': session_date,
            'session_time': session_time,
            'session_type': session_type,
            'sessions_count': sessions_count,
            'amount': amount,
            'status': 'pending_payment',
            'message': message,
            'created_at': datetime.now().isoformat(),
            'mentor_info': {
                'name': mentor['name'],
                'college': mentor['college'],
                'expertise': mentor['expertise']
            }
        }
        
        return jsonify({
            'message': 'Session booking created successfully',
            'booking': booking,
            'payment_required': True
        }), 201
        
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@mentorship_bp.route('/mentors/<int:mentor_id>/availability', methods=['GET'])
def get_mentor_availability(mentor_id):
    """Get mentor's availability for next 30 days"""
    mentor = next((mentor for mentor in MENTORS_DATA if mentor['id'] == mentor_id), None)
    
    if not mentor:
        return jsonify({'error': 'Mentor not found'}), 404
    
    # Generate availability for next 30 days
    availability = []
    current_date = datetime.now().date()
    
    for i in range(30):
        date = current_date + timedelta(days=i)
        day_name = date.strftime('%A')
        
        if day_name in mentor['availability']['days']:
            available_slots = []
            for time_slot in mentor['availability']['time_slots']:
                # In real implementation, check against existing bookings
                available_slots.append({
                    'time': time_slot,
                    'available': True  # Simplified - would check actual bookings
                })
            
            availability.append({
                'date': date.isoformat(),
                'day': day_name,
                'slots': available_slots
            })
    
    return jsonify({
        'mentor_id': mentor_id,
        'availability': availability
    }), 200

@mentorship_bp.route('/bookings', methods=['GET'])
def get_user_bookings():
    """Get user's mentor session bookings"""
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    # In real implementation, fetch from database
    # For demo, return empty list
    bookings = []
    
    return jsonify({
        'bookings': bookings,
        'total': len(bookings)
    }), 200

@mentorship_bp.route('/bookings/<booking_id>/cancel', methods=['POST'])
def cancel_booking(booking_id):
    """Cancel a mentor session booking"""
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    try:
        # In real implementation, find and update booking in database
        # Check cancellation policy, process refunds if applicable
        
        return jsonify({
            'message': 'Booking cancelled successfully',
            'refund_info': 'Refund will be processed within 5-7 business days'
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@mentorship_bp.route('/mentors/<int:mentor_id>/reviews', methods=['GET'])
def get_mentor_reviews(mentor_id):
    """Get reviews for a specific mentor"""
    mentor = next((mentor for mentor in MENTORS_DATA if mentor['id'] == mentor_id), None)
    
    if not mentor:
        return jsonify({'error': 'Mentor not found'}), 404
    
    # Sample reviews (in real implementation, fetch from database)
    reviews = [
        {
            'id': 1,
            'user_name': 'Anonymous Student',
            'rating': 5,
            'comment': 'Excellent guidance for JEE preparation. Very helpful and patient.',
            'date': '2024-06-15',
            'verified': True
        },
        {
            'id': 2,
            'user_name': 'Anonymous Student',
            'rating': 4,
            'comment': 'Good session, learned a lot about college life and placements.',
            'date': '2024-06-10',
            'verified': True
        }
    ]
    
    return jsonify({
        'mentor_id': mentor_id,
        'reviews': reviews,
        'total_reviews': len(reviews),
        'average_rating': mentor['rating']
    }), 200

@mentorship_bp.route('/mentors/<int:mentor_id>/reviews', methods=['POST'])
def add_mentor_review():
    """Add a review for a mentor"""
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    try:
        data = request.json
        rating = data.get('rating')
        comment = data.get('comment', '')
        
        if not rating or rating < 1 or rating > 5:
            return jsonify({'error': 'Rating must be between 1 and 5'}), 400
        
        # In real implementation, check if user has completed session with mentor
        # Store review in database
        
        review = {
            'id': str(uuid.uuid4()),
            'user_id': session['user_id'],
            'rating': rating,
            'comment': comment,
            'date': datetime.now().isoformat(),
            'verified': True
        }
        
        return jsonify({
            'message': 'Review added successfully',
            'review': review
        }), 201
        
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@mentorship_bp.route('/mentors/categories', methods=['GET'])
def get_mentor_categories():
    """Get all mentor expertise categories"""
    all_expertise = []
    for mentor in MENTORS_DATA:
        all_expertise.extend(mentor['expertise'])
    
    unique_expertise = list(set(all_expertise))
    
    return jsonify({
        'categories': sorted(unique_expertise)
    }), 200

@mentorship_bp.route('/mentors/colleges', methods=['GET'])
def get_mentor_colleges():
    """Get all colleges represented by mentors"""
    colleges = list(set(mentor['college'] for mentor in MENTORS_DATA))
    
    return jsonify({
        'colleges': sorted(colleges)
    }), 200

