from flask import Blueprint, jsonify, request, session
from src.models.user import User, db
from datetime import datetime
import uuid
import json

community_bp = Blueprint('community', __name__)

# Sample community data (in real implementation, this would be in database)
QUESTIONS_DATA = [
    {
        "id": 1,
        "title": "Best strategy for JEE Main preparation in final 3 months?",
        "content": "I'm in 12th grade and have 3 months left for JEE Main. What should be my strategy to maximize my score? Currently scoring around 180/300 in mock tests.",
        "category": "JEE Main",
        "tags": ["jee-main", "preparation", "strategy", "mock-tests"],
        "author": {
            "id": 101,
            "username": "student_2025",
            "reputation": 45,
            "is_verified": False
        },
        "created_at": "2024-06-20T10:30:00Z",
        "updated_at": "2024-06-20T10:30:00Z",
        "votes": 15,
        "answers_count": 8,
        "views": 234,
        "is_answered": True,
        "best_answer_id": 101,
        "status": "open"
    },
    {
        "id": 2,
        "title": "IIT Delhi vs IIT Bombay for Computer Science - Which is better?",
        "content": "I have qualified JEE Advanced and can get CS in both IIT Delhi and IIT Bombay. Which one should I choose considering placements, research opportunities, and campus life?",
        "category": "College Selection",
        "tags": ["iit-delhi", "iit-bombay", "computer-science", "placements"],
        "author": {
            "id": 102,
            "username": "jee_qualified",
            "reputation": 78,
            "is_verified": True
        },
        "created_at": "2024-06-19T15:45:00Z",
        "updated_at": "2024-06-20T09:15:00Z",
        "votes": 32,
        "answers_count": 12,
        "views": 567,
        "is_answered": True,
        "best_answer_id": 205,
        "status": "open"
    },
    {
        "id": 3,
        "title": "NEET preparation while managing board exams - Need advice",
        "content": "How do I balance NEET preparation with 12th board exams? I'm finding it difficult to manage time between both. Any tips from successful candidates?",
        "category": "NEET",
        "tags": ["neet", "board-exams", "time-management", "preparation"],
        "author": {
            "id": 103,
            "username": "medical_aspirant",
            "reputation": 23,
            "is_verified": False
        },
        "created_at": "2024-06-18T12:20:00Z",
        "updated_at": "2024-06-19T16:30:00Z",
        "votes": 8,
        "answers_count": 5,
        "views": 189,
        "is_answered": False,
        "best_answer_id": None,
        "status": "open"
    }
]

ANSWERS_DATA = [
    {
        "id": 101,
        "question_id": 1,
        "content": "Focus on revision and mock tests. Don't try to learn new topics now. Solve previous year papers and identify weak areas. Practice time management. Take at least 2 mock tests per week.",
        "author": {
            "id": 201,
            "username": "iit_student_2023",
            "reputation": 156,
            "is_verified": True,
            "college": "IIT Delhi"
        },
        "created_at": "2024-06-20T11:15:00Z",
        "updated_at": "2024-06-20T11:15:00Z",
        "votes": 12,
        "is_best_answer": True,
        "is_helpful": True
    },
    {
        "id": 205,
        "question_id": 2,
        "content": "Both are excellent choices. IIT Bombay has slightly better industry connections in Mumbai, while IIT Delhi has proximity to government and policy circles. For CS, both have similar placement records. Choose based on your preference for city and campus culture.",
        "author": {
            "id": 202,
            "username": "cs_graduate",
            "reputation": 234,
            "is_verified": True,
            "college": "IIT Bombay"
        },
        "created_at": "2024-06-19T16:30:00Z",
        "updated_at": "2024-06-19T16:30:00Z",
        "votes": 18,
        "is_best_answer": True,
        "is_helpful": True
    }
]

@community_bp.route('/questions', methods=['GET'])
def get_questions():
    """Get all questions with optional filtering"""
    category = request.args.get('category')
    tag = request.args.get('tag')
    sort_by = request.args.get('sort_by', 'recent')  # recent, popular, unanswered
    search = request.args.get('search', '').lower()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    questions = QUESTIONS_DATA.copy()
    
    # Apply filters
    if category:
        questions = [q for q in questions if q['category'].lower() == category.lower()]
    
    if tag:
        questions = [q for q in questions if tag.lower() in [t.lower() for t in q['tags']]]
    
    if search:
        questions = [q for q in questions if 
                    search in q['title'].lower() or 
                    search in q['content'].lower()]
    
    # Apply sorting
    if sort_by == 'popular':
        questions.sort(key=lambda x: x['votes'], reverse=True)
    elif sort_by == 'unanswered':
        questions = [q for q in questions if not q['is_answered']]
        questions.sort(key=lambda x: x['created_at'], reverse=True)
    else:  # recent
        questions.sort(key=lambda x: x['created_at'], reverse=True)
    
    # Pagination
    start = (page - 1) * per_page
    end = start + per_page
    paginated_questions = questions[start:end]
    
    return jsonify({
        'questions': paginated_questions,
        'total': len(questions),
        'page': page,
        'per_page': per_page,
        'total_pages': (len(questions) + per_page - 1) // per_page
    }), 200

@community_bp.route('/questions/<int:question_id>', methods=['GET'])
def get_question_details(question_id):
    """Get detailed information about a specific question"""
    question = next((q for q in QUESTIONS_DATA if q['id'] == question_id), None)
    
    if not question:
        return jsonify({'error': 'Question not found'}), 404
    
    # Get answers for this question
    answers = [a for a in ANSWERS_DATA if a['question_id'] == question_id]
    answers.sort(key=lambda x: (x['is_best_answer'], x['votes']), reverse=True)
    
    # Increment view count (in real implementation)
    question_copy = question.copy()
    question_copy['views'] += 1
    
    return jsonify({
        'question': question_copy,
        'answers': answers
    }), 200

@community_bp.route('/questions', methods=['POST'])
def ask_question():
    """Post a new question"""
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    try:
        data = request.json
        title = data.get('title', '').strip()
        content = data.get('content', '').strip()
        category = data.get('category', '').strip()
        tags = data.get('tags', [])
        
        # Validation
        if not title or len(title) < 10:
            return jsonify({'error': 'Title must be at least 10 characters long'}), 400
        
        if not content or len(content) < 20:
            return jsonify({'error': 'Question content must be at least 20 characters long'}), 400
        
        if not category:
            return jsonify({'error': 'Category is required'}), 400
        
        # Get user info
        user = User.query.get(session['user_id'])
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Create question
        question = {
            'id': len(QUESTIONS_DATA) + 1,
            'title': title,
            'content': content,
            'category': category,
            'tags': tags,
            'author': {
                'id': user.id,
                'username': user.username,
                'reputation': 0,  # In real implementation, calculate from user activity
                'is_verified': user.is_verified
            },
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'votes': 0,
            'answers_count': 0,
            'views': 0,
            'is_answered': False,
            'best_answer_id': None,
            'status': 'open'
        }
        
        # In real implementation, save to database
        QUESTIONS_DATA.append(question)
        
        return jsonify({
            'message': 'Question posted successfully',
            'question': question
        }), 201
        
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@community_bp.route('/questions/<int:question_id>/answers', methods=['POST'])
def post_answer():
    """Post an answer to a question"""
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    try:
        data = request.json
        content = data.get('content', '').strip()
        
        if not content or len(content) < 10:
            return jsonify({'error': 'Answer must be at least 10 characters long'}), 400
        
        # Check if question exists
        question = next((q for q in QUESTIONS_DATA if q['id'] == question_id), None)
        if not question:
            return jsonify({'error': 'Question not found'}), 404
        
        # Get user info
        user = User.query.get(session['user_id'])
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Create answer
        answer = {
            'id': len(ANSWERS_DATA) + 1,
            'question_id': question_id,
            'content': content,
            'author': {
                'id': user.id,
                'username': user.username,
                'reputation': 0,
                'is_verified': user.is_verified,
                'college': getattr(user, 'college', None)
            },
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'votes': 0,
            'is_best_answer': False,
            'is_helpful': False
        }
        
        # In real implementation, save to database
        ANSWERS_DATA.append(answer)
        
        # Update question's answer count
        question['answers_count'] += 1
        
        return jsonify({
            'message': 'Answer posted successfully',
            'answer': answer
        }), 201
        
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@community_bp.route('/questions/<int:question_id>/vote', methods=['POST'])
def vote_question():
    """Vote on a question (upvote/downvote)"""
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    try:
        data = request.json
        vote_type = data.get('vote_type')  # 'up' or 'down'
        
        if vote_type not in ['up', 'down']:
            return jsonify({'error': 'Vote type must be "up" or "down"'}), 400
        
        question = next((q for q in QUESTIONS_DATA if q['id'] == question_id), None)
        if not question:
            return jsonify({'error': 'Question not found'}), 404
        
        # In real implementation, check if user already voted and update accordingly
        if vote_type == 'up':
            question['votes'] += 1
        else:
            question['votes'] -= 1
        
        return jsonify({
            'message': f'Question {vote_type}voted successfully',
            'votes': question['votes']
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@community_bp.route('/answers/<int:answer_id>/vote', methods=['POST'])
def vote_answer():
    """Vote on an answer (upvote/downvote)"""
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    try:
        data = request.json
        vote_type = data.get('vote_type')  # 'up' or 'down'
        
        if vote_type not in ['up', 'down']:
            return jsonify({'error': 'Vote type must be "up" or "down"'}), 400
        
        answer = next((a for a in ANSWERS_DATA if a['id'] == answer_id), None)
        if not answer:
            return jsonify({'error': 'Answer not found'}), 404
        
        # In real implementation, check if user already voted and update accordingly
        if vote_type == 'up':
            answer['votes'] += 1
        else:
            answer['votes'] -= 1
        
        return jsonify({
            'message': f'Answer {vote_type}voted successfully',
            'votes': answer['votes']
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@community_bp.route('/questions/<int:question_id>/best-answer/<int:answer_id>', methods=['POST'])
def mark_best_answer():
    """Mark an answer as the best answer"""
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    try:
        question = next((q for q in QUESTIONS_DATA if q['id'] == question_id), None)
        if not question:
            return jsonify({'error': 'Question not found'}), 404
        
        # Check if user is the question author
        if question['author']['id'] != session['user_id']:
            return jsonify({'error': 'Only question author can mark best answer'}), 403
        
        answer = next((a for a in ANSWERS_DATA if a['id'] == answer_id), None)
        if not answer or answer['question_id'] != question_id:
            return jsonify({'error': 'Answer not found'}), 404
        
        # Update question and answer
        question['best_answer_id'] = answer_id
        question['is_answered'] = True
        answer['is_best_answer'] = True
        
        return jsonify({
            'message': 'Answer marked as best answer successfully'
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@community_bp.route('/categories', methods=['GET'])
def get_categories():
    """Get all question categories"""
    categories = list(set(q['category'] for q in QUESTIONS_DATA))
    category_counts = {}
    
    for category in categories:
        category_counts[category] = len([q for q in QUESTIONS_DATA if q['category'] == category])
    
    return jsonify({
        'categories': sorted(categories),
        'counts': category_counts
    }), 200

@community_bp.route('/tags', methods=['GET'])
def get_popular_tags():
    """Get popular tags"""
    all_tags = []
    for question in QUESTIONS_DATA:
        all_tags.extend(question['tags'])
    
    # Count tag frequency
    tag_counts = {}
    for tag in all_tags:
        tag_counts[tag] = tag_counts.get(tag, 0) + 1
    
    # Sort by frequency
    popular_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)
    
    return jsonify({
        'popular_tags': popular_tags[:20]  # Top 20 tags
    }), 200

@community_bp.route('/my-questions', methods=['GET'])
def get_my_questions():
    """Get questions posted by the current user"""
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    user_questions = [q for q in QUESTIONS_DATA if q['author']['id'] == session['user_id']]
    user_questions.sort(key=lambda x: x['created_at'], reverse=True)
    
    return jsonify({
        'questions': user_questions,
        'total': len(user_questions)
    }), 200

@community_bp.route('/my-answers', methods=['GET'])
def get_my_answers():
    """Get answers posted by the current user"""
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    user_answers = [a for a in ANSWERS_DATA if a['author']['id'] == session['user_id']]
    user_answers.sort(key=lambda x: x['created_at'], reverse=True)
    
    # Get question titles for each answer
    for answer in user_answers:
        question = next((q for q in QUESTIONS_DATA if q['id'] == answer['question_id']), None)
        if question:
            answer['question_title'] = question['title']
    
    return jsonify({
        'answers': user_answers,
        'total': len(user_answers)
    }), 200

@community_bp.route('/stats', methods=['GET'])
def get_community_stats():
    """Get community statistics"""
    total_questions = len(QUESTIONS_DATA)
    total_answers = len(ANSWERS_DATA)
    answered_questions = len([q for q in QUESTIONS_DATA if q['is_answered']])
    
    # Calculate answer rate
    answer_rate = (answered_questions / total_questions * 100) if total_questions > 0 else 0
    
    # Get top contributors (simplified)
    contributors = {}
    for question in QUESTIONS_DATA:
        author_id = question['author']['id']
        contributors[author_id] = contributors.get(author_id, 0) + 1
    
    for answer in ANSWERS_DATA:
        author_id = answer['author']['id']
        contributors[author_id] = contributors.get(author_id, 0) + 1
    
    top_contributors = sorted(contributors.items(), key=lambda x: x[1], reverse=True)[:5]
    
    return jsonify({
        'total_questions': total_questions,
        'total_answers': total_answers,
        'answered_questions': answered_questions,
        'answer_rate': round(answer_rate, 1),
        'top_contributors': top_contributors
    }), 200

