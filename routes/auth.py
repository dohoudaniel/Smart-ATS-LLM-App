from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token, 
    jwt_required, 
    get_jwt_identity,
    create_refresh_token,
    get_jwt
)
from datetime import timedelta
import logging
from models.user import User
from config.database import get_database

logger = logging.getLogger(__name__)

# Create blueprint
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# Get database instance
db = get_database()


@auth_bp.route('/signup', methods=['POST'])
def signup():
    """User registration endpoint"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # Validate required fields
        required_fields = ['email', 'password', 'firstName', 'lastName']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Create user model instance
        user_model = User(db.get_users_collection())
        
        # Create user
        user = user_model.create_user(data)
        
        # Create JWT tokens
        access_token = create_access_token(
            identity=user['id'],
            expires_delta=timedelta(hours=24)
        )
        refresh_token = create_refresh_token(
            identity=user['id'],
            expires_delta=timedelta(days=30)
        )
        
        logger.info(f"New user registered: {user['email']}")
        
        return jsonify({
            "message": "User created successfully",
            "user": user,
            "token": access_token,
            "refreshToken": refresh_token
        }), 201
        
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Signup error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """User login endpoint"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400
        
        # Create user model instance
        user_model = User(db.get_users_collection())
        
        # Authenticate user
        user = user_model.authenticate_user(email, password)
        
        if not user:
            return jsonify({"error": "Invalid email or password"}), 401
        
        # Create JWT tokens
        access_token = create_access_token(
            identity=user['id'],
            expires_delta=timedelta(hours=24)
        )
        refresh_token = create_refresh_token(
            identity=user['id'],
            expires_delta=timedelta(days=30)
        )
        
        logger.info(f"User logged in: {user['email']}")
        
        return jsonify({
            "message": "Login successful",
            "user": user,
            "token": access_token,
            "refreshToken": refresh_token
        }), 200
        
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@auth_bp.route('/verify', methods=['GET'])
@jwt_required()
def verify_token():
    """Verify JWT token and return user info"""
    try:
        user_id = get_jwt_identity()
        
        # Create user model instance
        user_model = User(db.get_users_collection())
        
        # Get user
        user = user_model.get_user_by_id(user_id)
        
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        return jsonify({
            "message": "Token is valid",
            "user": user
        }), 200
        
    except Exception as e:
        logger.error(f"Token verification error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token"""
    try:
        user_id = get_jwt_identity()
        
        # Create new access token
        access_token = create_access_token(
            identity=user_id,
            expires_delta=timedelta(hours=24)
        )
        
        return jsonify({
            "token": access_token
        }), 200
        
    except Exception as e:
        logger.error(f"Token refresh error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get user profile"""
    try:
        user_id = get_jwt_identity()
        
        # Create user model instance
        user_model = User(db.get_users_collection())
        
        # Get user
        user = user_model.get_user_by_id(user_id)
        
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        return jsonify({
            "user": user
        }), 200
        
    except Exception as e:
        logger.error(f"Get profile error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@auth_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Update user profile"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # Create user model instance
        user_model = User(db.get_users_collection())
        
        # Update user
        user = user_model.update_user(user_id, data)
        
        if not user:
            return jsonify({"error": "Failed to update profile"}), 400
        
        logger.info(f"User profile updated: {user_id}")
        
        return jsonify({
            "message": "Profile updated successfully",
            "user": user
        }), 200
        
    except Exception as e:
        logger.error(f"Update profile error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@auth_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_user_stats():
    """Get user statistics"""
    try:
        user_id = get_jwt_identity()
        
        # Import here to avoid circular imports
        from models.review import Review
        
        # Create review model instance
        review_model = Review(db.get_reviews_collection())
        
        # Get user stats
        stats = review_model.get_user_stats(user_id)
        
        return jsonify(stats), 200
        
    except Exception as e:
        logger.error(f"Get user stats error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """Logout user (invalidate token)"""
    try:
        # In a production environment, you would typically:
        # 1. Add the token to a blacklist
        # 2. Store blacklisted tokens in Redis or database
        # 3. Check blacklist in JWT verification
        
        # For now, we'll just return success
        # The frontend should remove the token from storage
        
        return jsonify({
            "message": "Logout successful"
        }), 200
        
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500
