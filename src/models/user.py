from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(15), nullable=True)
    
    # Student specific fields
    class_level = db.Column(db.String(20), nullable=True)  # 12th, Graduate, etc.
    stream = db.Column(db.String(50), nullable=True)  # Engineering, Medical, etc.
    target_exams = db.Column(db.Text, nullable=True)  # JSON string of exam preferences
    
    # Account status
    is_verified = db.Column(db.Boolean, default=False)
    is_premium = db.Column(db.Boolean, default=False)
    premium_expires = db.Column(db.DateTime, nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'phone': self.phone,
            'class_level': self.class_level,
            'stream': self.stream,
            'target_exams': self.target_exams,
            'is_verified': self.is_verified,
            'is_premium': self.is_premium,
            'premium_expires': self.premium_expires.isoformat() if self.premium_expires else None,
            'created_at': self.created_at.isoformat(),
            'last_login': self.last_login.isoformat() if self.last_login else None
        }

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Payment details
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(3), default='INR')
    payment_method = db.Column(db.String(50), nullable=False)  # razorpay, stripe, etc.
    
    # Payment status
    status = db.Column(db.String(20), default='pending')  # pending, completed, failed, refunded
    transaction_id = db.Column(db.String(100), unique=True, nullable=True)
    gateway_payment_id = db.Column(db.String(100), nullable=True)
    
    # Service details
    service_type = db.Column(db.String(50), nullable=False)  # premium, mentorship, etc.
    service_duration = db.Column(db.Integer, nullable=True)  # in days
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    # Relationship
    user = db.relationship('User', backref=db.backref('payments', lazy=True))

    def __repr__(self):
        return f'<Payment {self.id} - {self.amount} {self.currency}>'

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'amount': self.amount,
            'currency': self.currency,
            'payment_method': self.payment_method,
            'status': self.status,
            'transaction_id': self.transaction_id,
            'gateway_payment_id': self.gateway_payment_id,
            'service_type': self.service_type,
            'service_duration': self.service_duration,
            'created_at': self.created_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }

class UserProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Academic details
    current_class = db.Column(db.String(20), nullable=True)
    school_name = db.Column(db.String(200), nullable=True)
    board = db.Column(db.String(50), nullable=True)  # CBSE, ICSE, State Board
    
    # Exam preferences
    preferred_exams = db.Column(db.Text, nullable=True)  # JSON string
    target_colleges = db.Column(db.Text, nullable=True)  # JSON string
    preferred_streams = db.Column(db.Text, nullable=True)  # JSON string
    
    # Location preferences
    preferred_cities = db.Column(db.Text, nullable=True)  # JSON string
    budget_range = db.Column(db.String(50), nullable=True)  # low, medium, high
    
    # Progress tracking
    exam_scores = db.Column(db.Text, nullable=True)  # JSON string of exam scores
    shortlisted_colleges = db.Column(db.Text, nullable=True)  # JSON string
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    user = db.relationship('User', backref=db.backref('profile', uselist=False))

    def __repr__(self):
        return f'<UserProfile {self.user_id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'current_class': self.current_class,
            'school_name': self.school_name,
            'board': self.board,
            'preferred_exams': self.preferred_exams,
            'target_colleges': self.target_colleges,
            'preferred_streams': self.preferred_streams,
            'preferred_cities': self.preferred_cities,
            'budget_range': self.budget_range,
            'exam_scores': self.exam_scores,
            'shortlisted_colleges': self.shortlisted_colleges,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

