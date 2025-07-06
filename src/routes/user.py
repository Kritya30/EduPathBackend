from flask import Blueprint, jsonify, request, session
from src.models.user import User, UserProfile, db
import json

user_bp = Blueprint('user', __name__)

@user_bp.route('/users', methods=['GET'])
def get_users():
    # Only allow authenticated users to view user list (for admin purposes)
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])

@user_bp.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    # Allow users to view their own profile or require admin access
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    # Users can only view their own profile unless they're admin
    if session['user_id'] != user_id:
        return jsonify({'error': 'Access denied'}), 403
    
    user = User.query.get_or_404(user_id)
    profile = UserProfile.query.filter_by(user_id=user_id).first()
    
    return jsonify({
        'user': user.to_dict(),
        'profile': profile.to_dict() if profile else None
    })

@user_bp.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    # Users can only update their own profile
    if 'user_id' not in session or session['user_id'] != user_id:
        return jsonify({'error': 'Access denied'}), 403
    
    user = User.query.get_or_404(user_id)
    data = request.json
    
    # Update allowed fields
    if 'full_name' in data:
        user.full_name = data['full_name']
    if 'phone' in data:
        user.phone = data['phone']
    if 'class_level' in data:
        user.class_level = data['class_level']
    if 'stream' in data:
        user.stream = data['stream']
    if 'target_exams' in data:
        user.target_exams = json.dumps(data['target_exams'])
    
    db.session.commit()
    return jsonify(user.to_dict())

@user_bp.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    # Users can only delete their own account
    if 'user_id' not in session or session['user_id'] != user_id:
        return jsonify({'error': 'Access denied'}), 403
    
    user = User.query.get_or_404(user_id)
    
    # Delete associated profile first
    profile = UserProfile.query.filter_by(user_id=user_id).first()
    if profile:
        db.session.delete(profile)
    
    db.session.delete(user)
    db.session.commit()
    
    # Clear session
    session.clear()
    
    return jsonify({'message': 'Account deleted successfully'}), 200

@user_bp.route('/shortlist', methods=['POST'])
def add_to_shortlist():
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    try:
        data = request.json
        college_id = data.get('college_id')
        
        if not college_id:
            return jsonify({'error': 'College ID is required'}), 400
        
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

@user_bp.route('/shortlist', methods=['DELETE'])
def remove_from_shortlist():
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    try:
        data = request.json
        college_id = data.get('college_id')
        
        if not college_id:
            return jsonify({'error': 'College ID is required'}), 400
        
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

@user_bp.route('/shortlist', methods=['GET'])
def get_shortlist():
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    profile = UserProfile.query.filter_by(user_id=session['user_id']).first()
    if not profile or not profile.shortlisted_colleges:
        return jsonify({'shortlisted_colleges': []}), 200
    
    shortlisted = json.loads(profile.shortlisted_colleges)
    return jsonify({'shortlisted_colleges': shortlisted}), 200

@user_bp.route('/exam-scores', methods=['POST'])
def save_exam_scores():
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    try:
        data = request.json
        exam_name = data.get('exam_name')
        score_data = data.get('score_data')
        
        if not exam_name or not score_data:
            return jsonify({'error': 'Exam name and score data are required'}), 400
        
        profile = UserProfile.query.filter_by(user_id=session['user_id']).first()
        if not profile:
            profile = UserProfile(user_id=session['user_id'])
            db.session.add(profile)
        
        # Get current exam scores
        exam_scores = json.loads(profile.exam_scores) if profile.exam_scores else {}
        
        # Update scores for the exam
        exam_scores[exam_name] = score_data
        profile.exam_scores = json.dumps(exam_scores)
        db.session.commit()
        
        return jsonify({
            'message': 'Exam scores saved successfully',
            'exam_scores': exam_scores
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500

@user_bp.route('/exam-scores', methods=['GET'])
def get_exam_scores():
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    profile = UserProfile.query.filter_by(user_id=session['user_id']).first()
    if not profile or not profile.exam_scores:
        return jsonify({'exam_scores': {}}), 200
    
    exam_scores = json.loads(profile.exam_scores)
    return jsonify({'exam_scores': exam_scores}), 200

