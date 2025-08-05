from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import logging
from models.review import Review
from models.user import User
from config.database import get_database

logger = logging.getLogger(__name__)

# Create blueprint
reviews_bp = Blueprint('reviews', __name__, url_prefix='/reviews')

# Get database instance
db = get_database()


@reviews_bp.route('', methods=['POST'])
@jwt_required()
def create_review():
    """Create a new review"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # Add user ID to the data
        data['userId'] = user_id
        
        # Create review model instance
        review_model = Review(db.get_reviews_collection())
        
        # Create review
        review = review_model.create_review(data)
        
        # Update user statistics
        user_model = User(db.get_users_collection())
        user_model.update_user_stats(user_id, data['matchScore'])
        
        logger.info(f"New review created for user: {user_id}")
        
        return jsonify({
            "message": "Review created successfully",
            "review": review
        }), 201
        
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Create review error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@reviews_bp.route('', methods=['GET'])
@jwt_required()
def get_reviews():
    """Get user's reviews with pagination"""
    try:
        user_id = get_jwt_identity()
        
        # Get pagination parameters
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        
        # Validate pagination parameters
        if page < 1:
            page = 1
        if limit < 1 or limit > 100:
            limit = 10
        
        # Create review model instance
        review_model = Review(db.get_reviews_collection())
        
        # Get reviews
        result = review_model.get_user_reviews(user_id, page, limit)
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Get reviews error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@reviews_bp.route('/<review_id>', methods=['GET'])
@jwt_required()
def get_review(review_id):
    """Get a specific review"""
    try:
        user_id = get_jwt_identity()
        
        # Create review model instance
        review_model = Review(db.get_reviews_collection())
        
        # Get review
        review = review_model.get_review_by_id(review_id, user_id)
        
        if not review:
            return jsonify({"error": "Review not found"}), 404
        
        return jsonify({
            "review": review
        }), 200
        
    except Exception as e:
        logger.error(f"Get review error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@reviews_bp.route('/<review_id>', methods=['PUT'])
@jwt_required()
def update_review(review_id):
    """Update a review"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # Create review model instance
        review_model = Review(db.get_reviews_collection())
        
        # Update review
        review = review_model.update_review(review_id, user_id, data)
        
        if not review:
            return jsonify({"error": "Review not found or update failed"}), 404
        
        logger.info(f"Review updated: {review_id} by user: {user_id}")
        
        return jsonify({
            "message": "Review updated successfully",
            "review": review
        }), 200
        
    except Exception as e:
        logger.error(f"Update review error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@reviews_bp.route('/<review_id>', methods=['DELETE'])
@jwt_required()
def delete_review(review_id):
    """Delete a review"""
    try:
        user_id = get_jwt_identity()
        
        # Create review model instance
        review_model = Review(db.get_reviews_collection())
        
        # Delete review
        success = review_model.delete_review(review_id, user_id)
        
        if not success:
            return jsonify({"error": "Review not found or delete failed"}), 404
        
        logger.info(f"Review deleted: {review_id} by user: {user_id}")
        
        return jsonify({
            "message": "Review deleted successfully"
        }), 200
        
    except Exception as e:
        logger.error(f"Delete review error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@reviews_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_review_stats():
    """Get user's review statistics"""
    try:
        user_id = get_jwt_identity()
        
        # Create review model instance
        review_model = Review(db.get_reviews_collection())
        
        # Get stats
        stats = review_model.get_user_stats(user_id)
        
        return jsonify(stats), 200
        
    except Exception as e:
        logger.error(f"Get review stats error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@reviews_bp.route('/search', methods=['GET'])
@jwt_required()
def search_reviews():
    """Search user's reviews"""
    try:
        user_id = get_jwt_identity()
        
        # Get search parameters
        query = request.args.get('q', '').strip()
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        
        if not query:
            return jsonify({"error": "Search query is required"}), 400
        
        # Validate pagination parameters
        if page < 1:
            page = 1
        if limit < 1 or limit > 100:
            limit = 10
        
        # Create review model instance
        review_model = Review(db.get_reviews_collection())
        
        # Search reviews
        result = review_model.search_reviews(user_id, query, page, limit)
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Search reviews error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@reviews_bp.route('/trending-keywords', methods=['GET'])
@jwt_required()
def get_trending_keywords():
    """Get trending keywords from user's reviews"""
    try:
        user_id = get_jwt_identity()
        
        # Create review model instance
        review_model = Review(db.get_reviews_collection())
        
        # Get trending keywords
        keywords = review_model.get_trending_keywords(user_id)
        
        return jsonify({
            "keywords": keywords
        }), 200
        
    except Exception as e:
        logger.error(f"Get trending keywords error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@reviews_bp.route('/export', methods=['GET'])
@jwt_required()
def export_user_data():
    """Export all user data"""
    try:
        user_id = get_jwt_identity()
        
        # Create model instances
        user_model = User(db.get_users_collection())
        review_model = Review(db.get_reviews_collection())
        
        # Get user data
        user = user_model.get_user_by_id(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        # Get all reviews
        all_reviews = review_model.get_user_reviews(user_id, 1, 1000)  # Get up to 1000 reviews
        
        # Get stats
        stats = review_model.get_user_stats(user_id)
        
        export_data = {
            "user": user,
            "reviews": all_reviews['reviews'],
            "stats": stats,
            "exportedAt": "2024-01-01T00:00:00Z"  # You can use datetime.utcnow().isoformat()
        }
        
        logger.info(f"Data exported for user: {user_id}")
        
        return jsonify(export_data), 200
        
    except Exception as e:
        logger.error(f"Export data error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500
