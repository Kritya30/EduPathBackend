import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS
from src.models.user import db
from src.routes.user import user_bp
from src.routes.auth import auth_bp
from src.routes.payments import payments_bp
from src.routes.exams import exams_bp
from src.routes.colleges import colleges_bp
from src.routes.mentorship import mentorship_bp
from src.routes.community import community_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'
# Enable CORS for all routes
CORS(app, supports_credentials=True)

# Register blueprints
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(payments_bp, url_prefix='/api/payments')
app.register_blueprint(exams_bp, url_prefix='/api')
app.register_blueprint(colleges_bp, url_prefix='/api')
app.register_blueprint(mentorship_bp, url_prefix='/api')
app.register_blueprint(community_bp, url_prefix='/api/community')

# Database configuration
app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"postgresql://{os.environ.get("PGUSER")}:{os.environ.get("PGPASSWORD")}@"
    f"{os.environ.get("PGHOST")}:{os.environ.get("PGPORT")}/{os.environ.get("PGDATABASE")}"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Create database tables
with app.app_context():
    db.create_all()

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
            return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404

# API health check endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    return {
        'status': 'healthy',
        'message': 'EduPath API is running',
        'version': '1.0.0'
    }, 200

# API documentation endpoint
@app.route('/api/docs', methods=['GET'])
def api_docs():
    return {
        'title': 'EduPath API Documentation',
        'version': '1.0.0',
        'endpoints': {
            'Authentication': {
                'POST /api/auth/signup': 'User registration',
                'POST /api/auth/login': 'User login',
                'POST /api/auth/logout': 'User logout',
                'GET /api/auth/me': 'Get current user',
                'GET /api/auth/profile': 'Get user profile',
                'PUT /api/auth/profile': 'Update user profile',
                'POST /api/auth/change-password': 'Change password'
            },
            'Exams': {
                'GET /api/exams': 'Get all exams with filtering',
                'GET /api/exams/{id}': 'Get exam details',
                'GET /api/exams/streams': 'Get exam streams',
                'GET /api/exams/upcoming': 'Get upcoming exams',
                'GET /api/exams/deadlines': 'Get exam deadlines',
                'POST /api/exams/bookmark': 'Bookmark an exam',
                'DELETE /api/exams/bookmark': 'Remove exam bookmark',
                'GET /api/exams/bookmarks': 'Get bookmarked exams',
                'GET /api/exams/recommendations': 'Get personalized exam recommendations'
            },
            'Colleges': {
                'GET /api/colleges': 'Get all colleges with filtering',
                'GET /api/colleges/{id}': 'Get college details',
                'POST /api/colleges/recommendations': 'Get college recommendations based on scores',
                'POST /api/colleges/compare': 'Compare multiple colleges',
                'GET /api/colleges/categories': 'Get college categories',
                'GET /api/colleges/states': 'Get college states',
                'POST /api/colleges/shortlist': 'Add college to shortlist',
                'GET /api/colleges/shortlist': 'Get shortlisted colleges',
                'DELETE /api/colleges/shortlist/{id}': 'Remove from shortlist'
            },
            'Mentorship': {
                'GET /api/mentors': 'Get all mentors with filtering',
                'GET /api/mentors/{id}': 'Get mentor details',
                'POST /api/mentors/search': 'Search mentors by criteria',
                'POST /api/mentors/{id}/book': 'Book mentor session',
                'GET /api/mentors/{id}/availability': 'Get mentor availability',
                'GET /api/bookings': 'Get user bookings',
                'POST /api/bookings/{id}/cancel': 'Cancel booking',
                'GET /api/mentors/{id}/reviews': 'Get mentor reviews',
                'POST /api/mentors/{id}/reviews': 'Add mentor review',
                'GET /api/mentors/categories': 'Get mentor categories',
                'GET /api/mentors/colleges': 'Get mentor colleges'
            },
            'Community': {
                'GET /api/community/questions': 'Get all questions',
                'GET /api/community/questions/{id}': 'Get question details',
                'POST /api/community/questions': 'Ask a question',
                'POST /api/community/questions/{id}/answers': 'Post an answer',
                'POST /api/community/questions/{id}/vote': 'Vote on question',
                'POST /api/community/answers/{id}/vote': 'Vote on answer',
                'POST /api/community/questions/{id}/best-answer/{answer_id}': 'Mark best answer',
                'GET /api/community/categories': 'Get question categories',
                'GET /api/community/tags': 'Get popular tags',
                'GET /api/community/my-questions': 'Get user questions',
                'GET /api/community/my-answers': 'Get user answers',
                'GET /api/community/stats': 'Get community statistics'
            },
            'Payments': {
                'GET /api/payments/plans': 'Get payment plans',
                'POST /api/payments/create-payment': 'Create payment intent',
                'POST /api/payments/simulate-gateway/{id}': 'Simulate payment (demo)',
                'POST /api/payments/verify-payment': 'Verify payment status',
                'GET /api/payments/history': 'Get payment history',
                'GET /api/payments/subscription-status': 'Get subscription status',
                'POST /api/payments/cancel-subscription': 'Cancel subscription',
                'POST /api/payments/refund': 'Request refund'
            },
            'User Management': {
                'GET /api/users': 'Get all users (admin)',
                'GET /api/users/{id}': 'Get user details',
                'PUT /api/users/{id}': 'Update user',
                'DELETE /api/users/{id}': 'Delete user account',
                'POST /api/shortlist': 'Add to shortlist',
                'DELETE /api/shortlist': 'Remove from shortlist',
                'GET /api/shortlist': 'Get shortlist',
                'POST /api/exam-scores': 'Save exam scores',
                'GET /api/exam-scores': 'Get exam scores'
            }
        }
    }, 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

