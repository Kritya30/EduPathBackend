from flask import Blueprint, jsonify, request, session
from src.models.user import User, Payment, db
from datetime import datetime, timedelta
import uuid
import json

payments_bp = Blueprint('payments', __name__)

# Payment plans configuration
PAYMENT_PLANS = {
    'premium_monthly': {
        'name': 'Premium Monthly',
        'amount': 299.0,
        'currency': 'INR',
        'duration_days': 30,
        'features': [
            'Unlimited college recommendations',
            'Priority mentor access',
            'Advanced filtering options',
            'Exam score tracking',
            'Personalized study plans',
            'Ad-free experience'
        ]
    },
    'premium_yearly': {
        'name': 'Premium Yearly',
        'amount': 2999.0,
        'currency': 'INR',
        'duration_days': 365,
        'features': [
            'All monthly features',
            '2 months free',
            'Exclusive webinars',
            'Career counseling sessions',
            'Priority customer support'
        ]
    },
    'mentorship_session': {
        'name': 'One-on-One Mentorship',
        'amount': 499.0,
        'currency': 'INR',
        'duration_days': 1,
        'features': [
            '1-hour video call with mentor',
            'Personalized guidance',
            'College selection advice',
            'Exam preparation tips',
            'Career roadmap discussion'
        ]
    },
    'mentorship_package': {
        'name': 'Mentorship Package (5 sessions)',
        'amount': 2199.0,
        'currency': 'INR',
        'duration_days': 30,
        'features': [
            '5 one-hour sessions',
            'Dedicated mentor assignment',
            'Progress tracking',
            'Study material recommendations',
            'Mock interview sessions'
        ]
    }
}

@payments_bp.route('/plans', methods=['GET'])
def get_payment_plans():
    """Get all available payment plans"""
    return jsonify({
        'plans': PAYMENT_PLANS
    }), 200

@payments_bp.route('/create-payment', methods=['POST'])
def create_payment():
    """Create a new payment intent"""
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    try:
        data = request.json
        plan_id = data.get('plan_id')
        payment_method = data.get('payment_method', 'razorpay')
        
        if not plan_id or plan_id not in PAYMENT_PLANS:
            return jsonify({'error': 'Invalid payment plan'}), 400
        
        plan = PAYMENT_PLANS[plan_id]
        user = User.query.get(session['user_id'])
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Create payment record
        payment = Payment(
            user_id=user.id,
            amount=plan['amount'],
            currency=plan['currency'],
            payment_method=payment_method,
            service_type=plan_id,
            service_duration=plan['duration_days'],
            transaction_id=str(uuid.uuid4()),
            status='pending'
        )
        
        db.session.add(payment)
        db.session.commit()
        
        # In a real implementation, you would integrate with payment gateways like:
        # - Razorpay for Indian payments
        # - Stripe for international payments
        # - PayU, CCAvenue, etc.
        
        # For demo purposes, we'll simulate payment gateway response
        payment_intent = {
            'payment_id': payment.id,
            'transaction_id': payment.transaction_id,
            'amount': payment.amount,
            'currency': payment.currency,
            'plan': plan,
            'gateway_url': f'/api/payments/simulate-gateway/{payment.id}',
            'status': 'pending'
        }
        
        return jsonify({
            'message': 'Payment created successfully',
            'payment': payment_intent
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500

@payments_bp.route('/simulate-gateway/<int:payment_id>', methods=['POST'])
def simulate_payment_gateway(payment_id):
    """Simulate payment gateway processing (for demo purposes)"""
    try:
        data = request.json
        action = data.get('action', 'success')  # success, failure
        
        payment = Payment.query.get_or_404(payment_id)
        
        if payment.status != 'pending':
            return jsonify({'error': 'Payment already processed'}), 400
        
        if action == 'success':
            # Mark payment as completed
            payment.status = 'completed'
            payment.completed_at = datetime.utcnow()
            payment.gateway_payment_id = f"pay_{uuid.uuid4().hex[:16]}"
            
            # Update user premium status
            user = User.query.get(payment.user_id)
            if payment.service_type.startswith('premium'):
                user.is_premium = True
                if user.premium_expires:
                    # Extend existing premium
                    user.premium_expires = max(user.premium_expires, datetime.utcnow()) + timedelta(days=payment.service_duration)
                else:
                    # New premium subscription
                    user.premium_expires = datetime.utcnow() + timedelta(days=payment.service_duration)
            
            db.session.commit()
            
            return jsonify({
                'message': 'Payment completed successfully',
                'payment': payment.to_dict(),
                'user': user.to_dict()
            }), 200
            
        else:
            # Mark payment as failed
            payment.status = 'failed'
            db.session.commit()
            
            return jsonify({
                'message': 'Payment failed',
                'payment': payment.to_dict()
            }), 400
            
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500

@payments_bp.route('/verify-payment', methods=['POST'])
def verify_payment():
    """Verify payment status with gateway"""
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    try:
        data = request.json
        transaction_id = data.get('transaction_id')
        gateway_payment_id = data.get('gateway_payment_id')
        
        if not transaction_id:
            return jsonify({'error': 'Transaction ID is required'}), 400
        
        payment = Payment.query.filter_by(
            transaction_id=transaction_id,
            user_id=session['user_id']
        ).first()
        
        if not payment:
            return jsonify({'error': 'Payment not found'}), 404
        
        # In real implementation, verify with actual payment gateway
        # For demo, we'll check if gateway_payment_id is provided
        if gateway_payment_id and payment.status == 'pending':
            payment.status = 'completed'
            payment.completed_at = datetime.utcnow()
            payment.gateway_payment_id = gateway_payment_id
            
            # Update user premium status
            user = User.query.get(payment.user_id)
            if payment.service_type.startswith('premium'):
                user.is_premium = True
                if user.premium_expires:
                    user.premium_expires = max(user.premium_expires, datetime.utcnow()) + timedelta(days=payment.service_duration)
                else:
                    user.premium_expires = datetime.utcnow() + timedelta(days=payment.service_duration)
            
            db.session.commit()
        
        return jsonify({
            'payment': payment.to_dict(),
            'user': User.query.get(payment.user_id).to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500

@payments_bp.route('/history', methods=['GET'])
def get_payment_history():
    """Get user's payment history"""
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    payments = Payment.query.filter_by(user_id=session['user_id']).order_by(Payment.created_at.desc()).all()
    
    return jsonify({
        'payments': [payment.to_dict() for payment in payments]
    }), 200

@payments_bp.route('/subscription-status', methods=['GET'])
def get_subscription_status():
    """Get current subscription status"""
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    user = User.query.get(session['user_id'])
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Check if premium is still active
    is_premium_active = False
    days_remaining = 0
    
    if user.is_premium and user.premium_expires:
        if user.premium_expires > datetime.utcnow():
            is_premium_active = True
            days_remaining = (user.premium_expires - datetime.utcnow()).days
        else:
            # Premium expired, update user status
            user.is_premium = False
            db.session.commit()
    
    return jsonify({
        'is_premium': is_premium_active,
        'premium_expires': user.premium_expires.isoformat() if user.premium_expires else None,
        'days_remaining': days_remaining,
        'user': user.to_dict()
    }), 200

@payments_bp.route('/cancel-subscription', methods=['POST'])
def cancel_subscription():
    """Cancel premium subscription"""
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    try:
        user = User.query.get(session['user_id'])
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        if not user.is_premium:
            return jsonify({'error': 'No active subscription found'}), 400
        
        # In real implementation, you would:
        # 1. Cancel recurring payments with payment gateway
        # 2. Handle refunds if applicable
        # 3. Send confirmation emails
        
        # For demo, we'll just mark as cancelled but keep access until expiry
        user.is_premium = False
        db.session.commit()
        
        return jsonify({
            'message': 'Subscription cancelled successfully',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500

@payments_bp.route('/refund', methods=['POST'])
def request_refund():
    """Request refund for a payment"""
    if 'user_id' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    try:
        data = request.json
        payment_id = data.get('payment_id')
        reason = data.get('reason', '')
        
        if not payment_id:
            return jsonify({'error': 'Payment ID is required'}), 400
        
        payment = Payment.query.filter_by(
            id=payment_id,
            user_id=session['user_id']
        ).first()
        
        if not payment:
            return jsonify({'error': 'Payment not found'}), 404
        
        if payment.status != 'completed':
            return jsonify({'error': 'Only completed payments can be refunded'}), 400
        
        # Check refund eligibility (e.g., within 7 days)
        days_since_payment = (datetime.utcnow() - payment.completed_at).days
        if days_since_payment > 7:
            return jsonify({'error': 'Refund period has expired (7 days)'}), 400
        
        # In real implementation, process refund with payment gateway
        payment.status = 'refunded'
        
        # Revert premium status if applicable
        if payment.service_type.startswith('premium'):
            user = User.query.get(payment.user_id)
            user.is_premium = False
            user.premium_expires = None
        
        db.session.commit()
        
        return jsonify({
            'message': 'Refund processed successfully',
            'payment': payment.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500

