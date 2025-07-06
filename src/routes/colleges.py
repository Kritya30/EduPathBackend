from flask import Blueprint, jsonify, request, session
from src.models.user import User, UserProfile, db
import json

colleges_bp = Blueprint('colleges', __name__)

# College data (in real implementation, this would be in database)
COLLEGES_DATA = [
    {
        "id": 1,
        "name": "IIT Delhi",
        "full_name": "Indian Institute of Technology Delhi",
        "location": "New Delhi, Delhi",
        "state": "Delhi",
        "type": "Government",
        "category": "Engineering",
        "nirf_ranking": 2,
        "established": 1961,
        "website": "https://home.iitd.ac.in/",
        "fees": {
            "annual": 250000,
            "currency": "INR",
            "category": "Tuition + Hostel"
        },
        "courses": [
            "B.Tech Computer Science",
            "B.Tech Electrical Engineering", 
            "B.Tech Mechanical Engineering",
            "B.Tech Civil Engineering",
            "M.Tech", "PhD"
        ],
        "accepted_exams": ["JEE Advanced"],
        "cutoffs": {
            "JEE Advanced": {
                "general": {"rank": 500, "percentile": 99.8},
                "obc": {"rank": 800, "percentile": 99.7},
                "sc": {"rank": 1500, "percentile": 99.5},
                "st": {"rank": 2000, "percentile": 99.3}
            }
        },
        "placement": {
            "average_package": 1800000,
            "highest_package": 5000000,
            "placement_rate": 95
        },
        "facilities": [
            "World-class laboratories",
            "Modern hostels",
            "Sports complex",
            "Library with vast collection",
            "Research centers"
        ],
        "description": "Premier engineering institute known for excellence in technology and research.",
        "icon": "🏛️",
        "images": [
            "/images/iit-delhi-campus.jpg",
            "/images/iit-delhi-lab.jpg"
        ]
    },
    {
        "id": 2,
        "name": "IIT Bombay",
        "full_name": "Indian Institute of Technology Bombay",
        "location": "Mumbai, Maharashtra",
        "state": "Maharashtra",
        "type": "Government",
        "category": "Engineering",
        "nirf_ranking": 3,
        "established": 1958,
        "website": "https://www.iitb.ac.in/",
        "fees": {
            "annual": 250000,
            "currency": "INR",
            "category": "Tuition + Hostel"
        },
        "courses": [
            "B.Tech Computer Science",
            "B.Tech Electrical Engineering",
            "B.Tech Aerospace Engineering",
            "B.Tech Chemical Engineering",
            "M.Tech", "PhD"
        ],
        "accepted_exams": ["JEE Advanced"],
        "cutoffs": {
            "JEE Advanced": {
                "general": {"rank": 400, "percentile": 99.85},
                "obc": {"rank": 700, "percentile": 99.75},
                "sc": {"rank": 1200, "percentile": 99.6},
                "st": {"rank": 1800, "percentile": 99.4}
            }
        },
        "placement": {
            "average_package": 2000000,
            "highest_package": 5500000,
            "placement_rate": 96
        },
        "facilities": [
            "State-of-the-art infrastructure",
            "Research parks",
            "Innovation labs",
            "Cultural centers",
            "Medical facilities"
        ],
        "description": "Top-ranked IIT known for computer science and engineering excellence.",
        "icon": "🏛️",
        "images": [
            "/images/iit-bombay-campus.jpg"
        ]
    },
    {
        "id": 3,
        "name": "IIT Madras",
        "full_name": "Indian Institute of Technology Madras",
        "location": "Chennai, Tamil Nadu",
        "state": "Tamil Nadu",
        "type": "Government",
        "category": "Engineering",
        "nirf_ranking": 1,
        "established": 1959,
        "website": "https://www.iitm.ac.in/",
        "fees": {
            "annual": 250000,
            "currency": "INR",
            "category": "Tuition + Hostel"
        },
        "courses": [
            "B.Tech Computer Science",
            "B.Tech Electrical Engineering",
            "B.Tech Ocean Engineering",
            "B.Tech Metallurgical Engineering",
            "M.Tech", "PhD"
        ],
        "accepted_exams": ["JEE Advanced"],
        "cutoffs": {
            "JEE Advanced": {
                "general": {"rank": 300, "percentile": 99.9},
                "obc": {"rank": 600, "percentile": 99.8},
                "sc": {"rank": 1000, "percentile": 99.65},
                "st": {"rank": 1500, "percentile": 99.5}
            }
        },
        "placement": {
            "average_package": 2200000,
            "highest_package": 6000000,
            "placement_rate": 97
        },
        "facilities": [
            "Sprawling green campus",
            "Advanced research facilities",
            "Incubation centers",
            "Sports facilities",
            "Cultural venues"
        ],
        "description": "India's top engineering institute with world-class research facilities.",
        "icon": "🏛️",
        "images": []
    },
    {
        "id": 4,
        "name": "NIT Trichy",
        "full_name": "National Institute of Technology Tiruchirappalli",
        "location": "Tiruchirappalli, Tamil Nadu",
        "state": "Tamil Nadu",
        "type": "Government",
        "category": "Engineering",
        "nirf_ranking": 9,
        "established": 1964,
        "website": "https://www.nitt.edu/",
        "fees": {
            "annual": 150000,
            "currency": "INR",
            "category": "Tuition + Hostel"
        },
        "courses": [
            "B.Tech Computer Science",
            "B.Tech Electronics and Communication",
            "B.Tech Mechanical Engineering",
            "B.Tech Civil Engineering",
            "M.Tech", "MBA"
        ],
        "accepted_exams": ["JEE Main"],
        "cutoffs": {
            "JEE Main": {
                "general": {"rank": 2000, "percentile": 99.5},
                "obc": {"rank": 3500, "percentile": 99.2},
                "sc": {"rank": 8000, "percentile": 98.5},
                "st": {"rank": 12000, "percentile": 97.8}
            }
        },
        "placement": {
            "average_package": 1200000,
            "highest_package": 4000000,
            "placement_rate": 92
        },
        "facilities": [
            "Modern laboratories",
            "Central library",
            "Sports complex",
            "Hostels",
            "Medical center"
        ],
        "description": "Premier NIT known for excellent engineering education and placements.",
        "icon": "🏫",
        "images": []
    },
    {
        "id": 5,
        "name": "AIIMS Delhi",
        "full_name": "All India Institute of Medical Sciences Delhi",
        "location": "New Delhi, Delhi",
        "state": "Delhi",
        "type": "Government",
        "category": "Medical",
        "nirf_ranking": 1,
        "established": 1956,
        "website": "https://www.aiims.edu/",
        "fees": {
            "annual": 1500,
            "currency": "INR",
            "category": "Tuition only"
        },
        "courses": [
            "MBBS",
            "MD/MS",
            "DM/MCh",
            "PhD",
            "Nursing",
            "Paramedical"
        ],
        "accepted_exams": ["NEET UG"],
        "cutoffs": {
            "NEET UG": {
                "general": {"rank": 50, "percentile": 99.99},
                "obc": {"rank": 150, "percentile": 99.95},
                "sc": {"rank": 500, "percentile": 99.8},
                "st": {"rank": 800, "percentile": 99.7}
            }
        },
        "placement": {
            "average_package": "Government Service",
            "highest_package": "Government Service",
            "placement_rate": 100
        },
        "facilities": [
            "Super specialty hospital",
            "Research centers",
            "Modern hostels",
            "Library",
            "Sports facilities"
        ],
        "description": "India's premier medical institute with world-class healthcare education.",
        "icon": "🏥",
        "images": []
    },
    {
        "id": 6,
        "name": "IIM Ahmedabad",
        "full_name": "Indian Institute of Management Ahmedabad",
        "location": "Ahmedabad, Gujarat",
        "state": "Gujarat",
        "type": "Government",
        "category": "Management",
        "nirf_ranking": 1,
        "established": 1961,
        "website": "https://www.iima.ac.in/",
        "fees": {
            "annual": 2500000,
            "currency": "INR",
            "category": "2-year program total"
        },
        "courses": [
            "MBA",
            "Executive MBA",
            "PhD",
            "Fellow Programme"
        ],
        "accepted_exams": ["CAT"],
        "cutoffs": {
            "CAT": {
                "general": {"rank": 50, "percentile": 99.5},
                "obc": {"rank": 100, "percentile": 99.2},
                "sc": {"rank": 200, "percentile": 98.5},
                "st": {"rank": 300, "percentile": 98.0}
            }
        },
        "placement": {
            "average_package": 3400000,
            "highest_package": 7000000,
            "placement_rate": 100
        },
        "facilities": [
            "Modern classrooms",
            "Case study rooms",
            "Library",
            "Hostels",
            "Sports facilities"
        ],
        "description": "India's top business school with global recognition.",
        "icon": "🏢",
        "images": []
    }
]

@colleges_bp.route('/colleges', methods=['GET'])
def get_all_colleges():
    """Get all colleges with optional filtering"""
    category = request.args.get('category')
    state = request.args.get('state')
    college_type = request.args.get('type')
    search = request.args.get('search', '').lower()
    min_ranking = request.args.get('min_ranking', type=int)
    max_ranking = request.args.get('max_ranking', type=int)
    
    colleges = COLLEGES_DATA.copy()
    
    # Apply filters
    if category:
        colleges = [college for college in colleges if college['category'].lower() == category.lower()]
    
    if state:
        colleges = [college for college in colleges if college['state'].lower() == state.lower()]
    
    if college_type:
        colleges = [college for college in colleges if college['type'].lower() == college_type.lower()]
    
    if search:
        colleges = [college for college in colleges if 
                   search in college['name'].lower() or 
                   search in college['full_name'].lower() or
                   search in college['location'].lower()]
    
    if min_ranking:
        colleges = [college for college in colleges if college['nirf_ranking'] >= min_ranking]
    
    if max_ranking:
        colleges = [college for college in colleges if college['nirf_ranking'] <= max_ranking]
    
    return jsonify({
        'colleges': colleges,
        'total': len(colleges)
    }), 200

@colleges_bp.route('/colleges/<int:college_id>', methods=['GET'])
def get_college_details(college_id):
    """Get detailed information about a specific college"""
    college = next((college for college in COLLEGES_DATA if college['id'] == college_id), None)
    
    if not college:
        return jsonify({'error': 'College not found'}), 404
    
    return jsonify({'college': college}), 200

@colleges_bp.route('/colleges/recommendations', methods=['POST'])
def get_college_recommendations():
    """Get personalized college recommendations based on exam scores"""
    data = request.json
    exam_name = data.get('exam_name')
    rank = data.get('rank', type=int)
    percentile = data.get('percentile', type=float)
    category = data.get('category', 'general').lower()
    preferred_states = data.get('preferred_states', [])
    preferred_categories = data.get('preferred_categories', [])
    
    if not exam_name or (not rank and not percentile):
        return jsonify({'error': 'Exam name and rank/percentile are required'}), 400
    
    recommendations = []
    
    for college in COLLEGES_DATA:
        if exam_name in college['accepted_exams']:
            cutoff_data = college['cutoffs'].get(exam_name, {}).get(category, {})
            
            if cutoff_data:
                eligible = False
                
                # Check eligibility based on rank or percentile
                if rank and 'rank' in cutoff_data:
                    eligible = rank <= cutoff_data['rank']
                elif percentile and 'percentile' in cutoff_data:
                    eligible = percentile >= cutoff_data['percentile']
                
                if eligible:
                    college_copy = college.copy()
                    college_copy['eligibility_status'] = 'eligible'
                    college_copy['cutoff_info'] = cutoff_data
                    recommendations.append(college_copy)
                else:
                    # Include colleges slightly above cutoff as "reach" options
                    if rank and 'rank' in cutoff_data and rank <= cutoff_data['rank'] * 1.2:
                        college_copy = college.copy()
                        college_copy['eligibility_status'] = 'reach'
                        college_copy['cutoff_info'] = cutoff_data
                        recommendations.append(college_copy)
    
    # Apply preference filters
    if preferred_states:
        recommendations = [college for college in recommendations 
                         if college['state'] in preferred_states]
    
    if preferred_categories:
        recommendations = [college for college in recommendations 
                         if college['category'] in preferred_categories]
    
    # Sort by NIRF ranking (lower is better)
    recommendations.sort(key=lambda x: x['nirf_ranking'])
    
    return jsonify({
        'recommendations': recommendations,
        'total': len(recommendations),
        'criteria': {
            'exam': exam_name,
            'rank': rank,
            'percentile': percentile,
            'category': category
        }
    }), 200

@colleges_bp.route('/colleges/compare', methods=['POST'])
def compare_colleges():
    """Compare multiple colleges"""
    data = request.json
    college_ids = data.get('college_ids', [])
    
    if not college_ids or len(college_ids) < 2:
        return jsonify({'error': 'At least 2 college IDs are required for comparison'}), 400
    
    colleges_to_compare = []
    for college_id in college_ids:
        college = next((college for college in COLLEGES_DATA if college['id'] == college_id), None)
        if college:
            colleges_to_compare.append(college)
    
    if len(colleges_to_compare) < 2:
        return jsonify({'error': 'Not enough valid colleges found for comparison'}), 400
    
    # Create comparison matrix
    comparison = {
        'colleges': colleges_to_compare,
        'comparison_points': [
            'NIRF Ranking',
            'Annual Fees',
            'Average Placement Package',
            'Placement Rate',
            'Established Year',
            'Location'
        ]
    }
    
    return jsonify(comparison), 200

@colleges_bp.route('/colleges/categories', methods=['GET'])
def get_college_categories():
    """Get all available college categories"""
    categories = list(set(college['category'] for college in COLLEGES_DATA))
    category_counts = {}
    
    for category in categories:
        category_counts[category] = len([college for college in COLLEGES_DATA if college['category'] == category])
    
    return jsonify({
        'categories': categories,
        'counts': category_counts
    }), 200

@colleges_bp.route('/colleges/states', methods=['GET'])
def get_college_states():
    """Get all states with colleges"""
    states = list(set(college['state'] for college in COLLEGES_DATA))
    state_counts = {}
    
    for state in states:
        state_counts[state] = len([college for college in COLLEGES_DATA if college['state'] == state])
    
    return jsonify({
        'states': sorted(states),
        'counts': state_counts
    }), 200

@colleges_bp.route('/colleges/shortlist', methods=['POST'])
def add_to_shortlist():
    """Add college to user's shortlist"""
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    try:
        data = request.json
        college_id = data.get('college_id')
        
        if not college_id:
            return jsonify({'error': 'College ID is required'}), 400
        
        # Check if college exists
        college = next((college for college in COLLEGES_DATA if college['id'] == college_id), None)
        if not college:
            return jsonify({'error': 'College not found'}), 404
        
        profile = UserProfile.query.filter_by(user_id=session['user_id']).first()
        if not profile:
            profile = UserProfile(user_id=session['user_id'])
            db.session.add(profile)
        
        # Get current shortlisted colleges
        shortlisted = json.loads(profile.shortlisted_colleges) if profile.shortlisted_colleges else []
        
        # Add college if not already shortlisted
        if college_id not in shortlisted:
            shortlisted.append(college_id)
            profile.shortlisted_colleges = json.dumps(shortlisted)
            db.session.commit()
        
        return jsonify({
            'message': 'College added to shortlist',
            'shortlisted_colleges': shortlisted
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500

@colleges_bp.route('/colleges/shortlist', methods=['GET'])
def get_shortlisted_colleges():
    """Get user's shortlisted colleges"""
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    profile = UserProfile.query.filter_by(user_id=session['user_id']).first()
    if not profile or not profile.shortlisted_colleges:
        return jsonify({'shortlisted_colleges': []}), 200
    
    shortlisted_ids = json.loads(profile.shortlisted_colleges)
    shortlisted_colleges = [college for college in COLLEGES_DATA if college['id'] in shortlisted_ids]
    
    return jsonify({
        'shortlisted_colleges': shortlisted_colleges,
        'total': len(shortlisted_colleges)
    }), 200

@colleges_bp.route('/colleges/shortlist/<int:college_id>', methods=['DELETE'])
def remove_from_shortlist(college_id):
    """Remove college from shortlist"""
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    try:
        profile = UserProfile.query.filter_by(user_id=session['user_id']).first()
        if not profile or not profile.shortlisted_colleges:
            return jsonify({'error': 'No shortlisted colleges found'}), 404
        
        # Get current shortlisted colleges
        shortlisted = json.loads(profile.shortlisted_colleges)
        
        # Remove college if shortlisted
        if college_id in shortlisted:
            shortlisted.remove(college_id)
            profile.shortlisted_colleges = json.dumps(shortlisted)
            db.session.commit()
        
        return jsonify({
            'message': 'College removed from shortlist',
            'shortlisted_colleges': shortlisted
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500

