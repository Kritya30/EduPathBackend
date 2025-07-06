from flask import Blueprint, jsonify, request, session
from src.models.user import User, UserProfile, db
import json
from datetime import datetime

exams_bp = Blueprint('exams', __name__)

# Exam data (in real implementation, this would be in database)
EXAMS_DATA = [
    {
        "id": 1,
        "name": "JEE Main",
        "full_name": "Joint Entrance Examination Main",
        "stream": "Engineering",
        "level": "Undergraduate",
        "conducting_body": "National Testing Agency (NTA)",
        "official_website": "https://jeemain.nta.nic.in/",
        "application_deadline": "2025-02-25",
        "exam_date": "2025-04-02",
        "result_date": "2025-04-30",
        "eligibility": "12th Pass with PCM",
        "age_limit": "No age limit",
        "attempts": "Unlimited",
        "exam_mode": "Computer Based Test (CBT)",
        "duration": "3 hours",
        "subjects": ["Physics", "Chemistry", "Mathematics"],
        "total_marks": 300,
        "difficulty": "High",
        "applicants": "13.8 Lakh",
        "application_fee": {
            "general": 650,
            "obc": 650,
            "sc": 325,
            "st": 325
        },
        "exam_centers": ["All major cities in India"],
        "syllabus_topics": [
            "Physics: Mechanics, Thermodynamics, Waves, Electromagnetism",
            "Chemistry: Physical, Organic, Inorganic Chemistry",
            "Mathematics: Algebra, Calculus, Coordinate Geometry, Trigonometry"
        ],
        "preparation_tips": [
            "Focus on NCERT textbooks",
            "Practice previous year questions",
            "Take regular mock tests",
            "Maintain a study schedule"
        ],
        "colleges_accepting": ["NITs", "IIITs", "GFTIs", "State Engineering Colleges"],
        "status": "expired",
        "icon": "🔧"
    },
    {
        "id": 2,
        "name": "JEE Advanced",
        "full_name": "Joint Entrance Examination Advanced",
        "stream": "Engineering",
        "level": "Undergraduate",
        "conducting_body": "IIT (Rotating)",
        "official_website": "https://jeeadv.ac.in/",
        "application_deadline": "2025-05-02",
        "exam_date": "2025-05-18",
        "result_date": "2025-06-15",
        "eligibility": "Qualify JEE Main",
        "age_limit": "25 years (30 for SC/ST)",
        "attempts": "2 attempts in consecutive years",
        "exam_mode": "Computer Based Test (CBT)",
        "duration": "3 hours per paper",
        "subjects": ["Physics", "Chemistry", "Mathematics"],
        "total_marks": 372,
        "difficulty": "Very High",
        "applicants": "1.87 Lakh",
        "application_fee": {
            "general": 2800,
            "obc": 2800,
            "sc": 1400,
            "st": 1400
        },
        "exam_centers": ["Limited centers across India"],
        "syllabus_topics": [
            "Advanced Physics concepts",
            "Advanced Chemistry problems",
            "Higher Mathematics"
        ],
        "preparation_tips": [
            "Master JEE Main syllabus first",
            "Focus on conceptual understanding",
            "Practice advanced level problems",
            "Time management is crucial"
        ],
        "colleges_accepting": ["IITs", "ISM Dhanbad"],
        "status": "expired",
        "icon": "🏛️"
    },
    {
        "id": 3,
        "name": "NEET UG",
        "full_name": "National Eligibility cum Entrance Test (Undergraduate)",
        "stream": "Medical",
        "level": "Undergraduate",
        "conducting_body": "National Testing Agency (NTA)",
        "official_website": "https://neet.nta.nic.in/",
        "application_deadline": "2025-03-07",
        "exam_date": "2025-05-04",
        "result_date": "2025-06-04",
        "eligibility": "12th Pass with PCB",
        "age_limit": "17-25 years (30 for SC/ST/OBC)",
        "attempts": "Unlimited",
        "exam_mode": "Pen and Paper (Offline)",
        "duration": "3 hours 20 minutes",
        "subjects": ["Physics", "Chemistry", "Biology"],
        "total_marks": 720,
        "difficulty": "Very High",
        "applicants": "22.76 Lakh",
        "application_fee": {
            "general": 1700,
            "obc": 1700,
            "sc": 1000,
            "st": 1000
        },
        "exam_centers": ["All states and UTs"],
        "syllabus_topics": [
            "Physics: Mechanics, Thermodynamics, Optics",
            "Chemistry: Physical, Organic, Inorganic",
            "Biology: Botany and Zoology"
        ],
        "preparation_tips": [
            "NCERT is the bible for NEET",
            "Focus on Biology - highest weightage",
            "Practice MCQs regularly",
            "Revise frequently"
        ],
        "colleges_accepting": ["AIIMS", "Government Medical Colleges", "Private Medical Colleges"],
        "status": "expired",
        "icon": "🩺"
    },
    {
        "id": 4,
        "name": "CUET UG",
        "full_name": "Common University Entrance Test (Undergraduate)",
        "stream": "University Admissions",
        "level": "Undergraduate",
        "conducting_body": "National Testing Agency (NTA)",
        "official_website": "https://cuet.samarth.ac.in/",
        "application_deadline": "2025-03-24",
        "exam_date": "2025-05-13",
        "result_date": "2025-06-30",
        "eligibility": "12th Pass",
        "age_limit": "No age limit",
        "attempts": "Unlimited",
        "exam_mode": "Computer Based Test (CBT)",
        "duration": "Varies by subjects chosen",
        "subjects": ["Languages", "Domain Subjects", "General Test"],
        "total_marks": "Varies",
        "difficulty": "Medium",
        "applicants": "14.9 Lakh",
        "application_fee": {
            "general": 650,
            "obc": 650,
            "sc": 325,
            "st": 325
        },
        "exam_centers": ["All major cities"],
        "syllabus_topics": [
            "Based on NCERT curriculum",
            "Subject-specific topics",
            "General awareness"
        ],
        "preparation_tips": [
            "Choose subjects wisely",
            "Focus on NCERT textbooks",
            "Practice mock tests",
            "Stay updated with current affairs"
        ],
        "colleges_accepting": ["Central Universities", "State Universities", "Deemed Universities"],
        "status": "expired",
        "icon": "🎓"
    },
    {
        "id": 5,
        "name": "BITSAT",
        "full_name": "BITS Admission Test",
        "stream": "Engineering",
        "level": "Undergraduate",
        "conducting_body": "BITS Pilani",
        "official_website": "https://www.bitsadmission.com/",
        "application_deadline": "2025-06-30",
        "exam_date": "2025-05-26",
        "result_date": "2025-07-15",
        "eligibility": "12th Pass with PCM",
        "age_limit": "No age limit",
        "attempts": "Once per year",
        "exam_mode": "Computer Based Test (CBT)",
        "duration": "3 hours",
        "subjects": ["Physics", "Chemistry", "Mathematics", "English", "Logical Reasoning"],
        "total_marks": 450,
        "difficulty": "High",
        "applicants": "3 Lakh",
        "application_fee": {
            "general": 3400,
            "obc": 3400,
            "sc": 3400,
            "st": 3400
        },
        "exam_centers": ["Multiple cities in India and abroad"],
        "syllabus_topics": [
            "NCERT + advanced topics",
            "English proficiency",
            "Logical reasoning"
        ],
        "preparation_tips": [
            "Speed and accuracy are key",
            "Practice English and logical reasoning",
            "No negative marking advantage",
            "Time management crucial"
        ],
        "colleges_accepting": ["BITS Pilani", "BITS Goa", "BITS Hyderabad"],
        "status": "urgent",
        "icon": "⚙️"
    },
    {
        "id": 6,
        "name": "CAT",
        "full_name": "Common Admission Test",
        "stream": "Management",
        "level": "Postgraduate",
        "conducting_body": "IIMs (Rotating)",
        "official_website": "https://iimcat.ac.in/",
        "application_deadline": "2025-09-21",
        "exam_date": "2025-11-30",
        "result_date": "2026-01-15",
        "eligibility": "Bachelor's Degree",
        "age_limit": "No age limit",
        "attempts": "Unlimited",
        "exam_mode": "Computer Based Test (CBT)",
        "duration": "2 hours",
        "subjects": ["Verbal Ability", "Data Interpretation", "Quantitative Ability"],
        "total_marks": "Percentile based",
        "difficulty": "Very High",
        "applicants": "3.29 Lakh",
        "application_fee": {
            "general": 2300,
            "obc": 2300,
            "sc": 1150,
            "st": 1150
        },
        "exam_centers": ["Major cities across India"],
        "syllabus_topics": [
            "Reading comprehension",
            "Data interpretation and analysis",
            "Quantitative aptitude"
        ],
        "preparation_tips": [
            "Focus on fundamentals",
            "Practice time management",
            "Read extensively",
            "Take sectional tests"
        ],
        "colleges_accepting": ["IIMs", "Top B-Schools", "Management Institutes"],
        "status": "open",
        "icon": "💼"
    }
]

@exams_bp.route('/exams', methods=['GET'])
def get_all_exams():
    """Get all exams with optional filtering"""
    stream = request.args.get('stream')
    level = request.args.get('level')
    status = request.args.get('status')
    search = request.args.get('search', '').lower()
    
    exams = EXAMS_DATA.copy()
    
    # Apply filters
    if stream:
        exams = [exam for exam in exams if exam['stream'].lower() == stream.lower()]
    
    if level:
        exams = [exam for exam in exams if exam['level'].lower() == level.lower()]
    
    if status:
        exams = [exam for exam in exams if exam['status'].lower() == status.lower()]
    
    if search:
        exams = [exam for exam in exams if 
                search in exam['name'].lower() or 
                search in exam['full_name'].lower() or
                search in exam['stream'].lower()]
    
    return jsonify({
        'exams': exams,
        'total': len(exams)
    }), 200

@exams_bp.route('/exams/<int:exam_id>', methods=['GET'])
def get_exam_details(exam_id):
    """Get detailed information about a specific exam"""
    exam = next((exam for exam in EXAMS_DATA if exam['id'] == exam_id), None)
    
    if not exam:
        return jsonify({'error': 'Exam not found'}), 404
    
    return jsonify({'exam': exam}), 200

@exams_bp.route('/exams/streams', methods=['GET'])
def get_exam_streams():
    """Get all available exam streams"""
    streams = list(set(exam['stream'] for exam in EXAMS_DATA))
    stream_counts = {}
    
    for stream in streams:
        stream_counts[stream] = len([exam for exam in EXAMS_DATA if exam['stream'] == stream])
    
    return jsonify({
        'streams': streams,
        'counts': stream_counts
    }), 200

@exams_bp.route('/exams/upcoming', methods=['GET'])
def get_upcoming_exams():
    """Get upcoming exams based on current date"""
    current_date = datetime.now().date()
    upcoming_exams = []
    
    for exam in EXAMS_DATA:
        try:
            exam_date = datetime.strptime(exam['exam_date'], '%Y-%m-%d').date()
            if exam_date >= current_date:
                days_remaining = (exam_date - current_date).days
                exam_copy = exam.copy()
                exam_copy['days_remaining'] = days_remaining
                upcoming_exams.append(exam_copy)
        except:
            continue
    
    # Sort by exam date
    upcoming_exams.sort(key=lambda x: x['exam_date'])
    
    return jsonify({
        'upcoming_exams': upcoming_exams,
        'total': len(upcoming_exams)
    }), 200

@exams_bp.route('/exams/deadlines', methods=['GET'])
def get_exam_deadlines():
    """Get exams with approaching deadlines"""
    current_date = datetime.now().date()
    deadline_exams = []
    
    for exam in EXAMS_DATA:
        try:
            deadline_date = datetime.strptime(exam['application_deadline'], '%Y-%m-%d').date()
            if deadline_date >= current_date:
                days_remaining = (deadline_date - current_date).days
                if days_remaining <= 30:  # Deadlines within 30 days
                    exam_copy = exam.copy()
                    exam_copy['deadline_days_remaining'] = days_remaining
                    if days_remaining <= 7:
                        exam_copy['urgency'] = 'urgent'
                    elif days_remaining <= 15:
                        exam_copy['urgency'] = 'moderate'
                    else:
                        exam_copy['urgency'] = 'normal'
                    deadline_exams.append(exam_copy)
        except:
            continue
    
    # Sort by deadline
    deadline_exams.sort(key=lambda x: x['application_deadline'])
    
    return jsonify({
        'deadline_exams': deadline_exams,
        'total': len(deadline_exams)
    }), 200

@exams_bp.route('/exams/bookmark', methods=['POST'])
def bookmark_exam():
    """Bookmark an exam for a user"""
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    try:
        data = request.json
        exam_id = data.get('exam_id')
        
        if not exam_id:
            return jsonify({'error': 'Exam ID is required'}), 400
        
        # Check if exam exists
        exam = next((exam for exam in EXAMS_DATA if exam['id'] == exam_id), None)
        if not exam:
            return jsonify({'error': 'Exam not found'}), 404
        
        profile = UserProfile.query.filter_by(user_id=session['user_id']).first()
        if not profile:
            profile = UserProfile(user_id=session['user_id'])
            db.session.add(profile)
        
        # Get current bookmarked exams
        bookmarked = json.loads(profile.preferred_exams) if profile.preferred_exams else []
        
        # Add exam if not already bookmarked
        if exam_id not in bookmarked:
            bookmarked.append(exam_id)
            profile.preferred_exams = json.dumps(bookmarked)
            db.session.commit()
        
        return jsonify({
            'message': 'Exam bookmarked successfully',
            'bookmarked_exams': bookmarked
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500

@exams_bp.route('/exams/bookmark', methods=['DELETE'])
def remove_bookmark():
    """Remove exam bookmark"""
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    try:
        data = request.json
        exam_id = data.get('exam_id')
        
        if not exam_id:
            return jsonify({'error': 'Exam ID is required'}), 400
        
        profile = UserProfile.query.filter_by(user_id=session['user_id']).first()
        if not profile or not profile.preferred_exams:
            return jsonify({'error': 'No bookmarked exams found'}), 404
        
        # Get current bookmarked exams
        bookmarked = json.loads(profile.preferred_exams)
        
        # Remove exam if bookmarked
        if exam_id in bookmarked:
            bookmarked.remove(exam_id)
            profile.preferred_exams = json.dumps(bookmarked)
            db.session.commit()
        
        return jsonify({
            'message': 'Exam bookmark removed',
            'bookmarked_exams': bookmarked
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500

@exams_bp.route('/exams/bookmarks', methods=['GET'])
def get_bookmarked_exams():
    """Get user's bookmarked exams"""
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    profile = UserProfile.query.filter_by(user_id=session['user_id']).first()
    if not profile or not profile.preferred_exams:
        return jsonify({'bookmarked_exams': []}), 200
    
    bookmarked_ids = json.loads(profile.preferred_exams)
    bookmarked_exams = [exam for exam in EXAMS_DATA if exam['id'] in bookmarked_ids]
    
    return jsonify({
        'bookmarked_exams': bookmarked_exams,
        'total': len(bookmarked_exams)
    }), 200

@exams_bp.route('/exams/recommendations', methods=['GET'])
def get_exam_recommendations():
    """Get personalized exam recommendations for user"""
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    user = User.query.get(session['user_id'])
    profile = UserProfile.query.filter_by(user_id=session['user_id']).first()
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    recommendations = []
    
    # Filter exams based on user's stream preference
    if user.stream:
        stream_exams = [exam for exam in EXAMS_DATA if exam['stream'].lower() == user.stream.lower()]
        recommendations.extend(stream_exams)
    
    # Add exams based on class level
    if user.class_level:
        if user.class_level in ['12th', 'Class 12']:
            undergraduate_exams = [exam for exam in EXAMS_DATA if exam['level'] == 'Undergraduate']
            recommendations.extend(undergraduate_exams)
        elif 'graduate' in user.class_level.lower():
            postgraduate_exams = [exam for exam in EXAMS_DATA if exam['level'] == 'Postgraduate']
            recommendations.extend(postgraduate_exams)
    
    # Remove duplicates
    seen_ids = set()
    unique_recommendations = []
    for exam in recommendations:
        if exam['id'] not in seen_ids:
            unique_recommendations.append(exam)
            seen_ids.add(exam['id'])
    
    # If no specific recommendations, show popular exams
    if not unique_recommendations:
        unique_recommendations = EXAMS_DATA[:5]  # Top 5 exams
    
    return jsonify({
        'recommended_exams': unique_recommendations,
        'total': len(unique_recommendations),
        'reason': 'Based on your profile preferences'
    }), 200

