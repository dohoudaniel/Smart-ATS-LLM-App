from datetime import datetime
from typing import Optional, Dict, Any, List
from bson import ObjectId


class Review:
    """Review model for MongoDB operations"""
    
    def __init__(self, db_collection):
        self.collection = db_collection
    
    def create_review(self, review_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new review"""
        # Validate required fields
        required_fields = ['userId', 'jobTitle', 'jobDescription', 'resumeFileName', 'matchScore']
        for field in required_fields:
            if field not in review_data:
                raise ValueError(f"Missing required field: {field}")
        
        # Create review document
        review_doc = {
            "userId": ObjectId(review_data['userId']),
            "jobTitle": review_data['jobTitle'],
            "jobDescription": review_data['jobDescription'],
            "resumeFileName": review_data['resumeFileName'],
            "matchScore": int(review_data['matchScore']),
            "missingKeywords": review_data.get('missingKeywords', []),
            "profileSummary": review_data.get('profileSummary', ''),
            "recommendations": review_data.get('recommendations', []),
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        }
        
        # Insert review
        result = self.collection.insert_one(review_doc)
        review_doc['_id'] = result.inserted_id
        
        return self._format_review_response(review_doc)
    
    def get_user_reviews(self, user_id: str, page: int = 1, limit: int = 10) -> Dict[str, Any]:
        """Get reviews for a specific user with pagination"""
        try:
            skip = (page - 1) * limit
            
            # Get total count
            total = self.collection.count_documents({"userId": ObjectId(user_id)})
            
            # Get reviews
            reviews = list(
                self.collection.find({"userId": ObjectId(user_id)})
                .sort("createdAt", -1)
                .skip(skip)
                .limit(limit)
            )
            
            return {
                "reviews": [self._format_review_response(review) for review in reviews],
                "total": total,
                "page": page,
                "totalPages": (total + limit - 1) // limit
            }
        except Exception:
            return {"reviews": [], "total": 0, "page": 1, "totalPages": 0}
    
    def get_review_by_id(self, review_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific review by ID (only if it belongs to the user)"""
        try:
            review = self.collection.find_one({
                "_id": ObjectId(review_id),
                "userId": ObjectId(user_id)
            })
            return self._format_review_response(review) if review else None
        except Exception:
            return None
    
    def update_review(self, review_id: str, user_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update a review (only if it belongs to the user)"""
        try:
            # Remove fields that shouldn't be updated directly
            forbidden_fields = ['_id', 'userId', 'createdAt']
            update_data = {k: v for k, v in update_data.items() if k not in forbidden_fields}
            
            if not update_data:
                return None
            
            update_data['updatedAt'] = datetime.utcnow()
            
            result = self.collection.update_one(
                {"_id": ObjectId(review_id), "userId": ObjectId(user_id)},
                {"$set": update_data}
            )
            
            if result.modified_count > 0:
                return self.get_review_by_id(review_id, user_id)
            return None
        except Exception:
            return None
    
    def delete_review(self, review_id: str, user_id: str) -> bool:
        """Delete a review (only if it belongs to the user)"""
        try:
            result = self.collection.delete_one({
                "_id": ObjectId(review_id),
                "userId": ObjectId(user_id)
            })
            return result.deleted_count > 0
        except Exception:
            return False
    
    def get_user_stats(self, user_id: str) -> Dict[str, Any]:
        """Get user's review statistics"""
        try:
            pipeline = [
                {"$match": {"userId": ObjectId(user_id)}},
                {
                    "$group": {
                        "_id": None,
                        "totalReviews": {"$sum": 1},
                        "averageScore": {"$avg": "$matchScore"},
                        "bestScore": {"$max": "$matchScore"},
                        "recentReviews": {"$push": "$$ROOT"}
                    }
                }
            ]
            
            result = list(self.collection.aggregate(pipeline))
            
            if not result:
                return {
                    "totalReviews": 0,
                    "averageScore": 0,
                    "bestScore": 0,
                    "recentReviews": []
                }
            
            stats = result[0]
            
            # Get recent reviews (last 5)
            recent_reviews = list(
                self.collection.find({"userId": ObjectId(user_id)})
                .sort("createdAt", -1)
                .limit(5)
            )
            
            return {
                "totalReviews": stats.get("totalReviews", 0),
                "averageScore": round(stats.get("averageScore", 0), 2),
                "bestScore": stats.get("bestScore", 0),
                "recentReviews": [self._format_review_response(review) for review in recent_reviews]
            }
        except Exception:
            return {
                "totalReviews": 0,
                "averageScore": 0,
                "bestScore": 0,
                "recentReviews": []
            }
    
    def search_reviews(self, user_id: str, query: str, page: int = 1, limit: int = 10) -> Dict[str, Any]:
        """Search user's reviews by job title or keywords"""
        try:
            skip = (page - 1) * limit
            
            # Create search filter
            search_filter = {
                "userId": ObjectId(user_id),
                "$or": [
                    {"jobTitle": {"$regex": query, "$options": "i"}},
                    {"missingKeywords": {"$regex": query, "$options": "i"}}
                ]
            }
            
            # Get total count
            total = self.collection.count_documents(search_filter)
            
            # Get reviews
            reviews = list(
                self.collection.find(search_filter)
                .sort("createdAt", -1)
                .skip(skip)
                .limit(limit)
            )
            
            return {
                "reviews": [self._format_review_response(review) for review in reviews],
                "total": total,
                "page": page,
                "totalPages": (total + limit - 1) // limit
            }
        except Exception:
            return {"reviews": [], "total": 0, "page": 1, "totalPages": 0}
    
    def get_trending_keywords(self, user_id: str) -> List[Dict[str, Any]]:
        """Get trending keywords from user's reviews"""
        try:
            pipeline = [
                {"$match": {"userId": ObjectId(user_id)}},
                {"$unwind": "$missingKeywords"},
                {
                    "$group": {
                        "_id": "$missingKeywords",
                        "frequency": {"$sum": 1},
                        "averageScore": {"$avg": "$matchScore"}
                    }
                },
                {"$sort": {"frequency": -1}},
                {"$limit": 20}
            ]
            
            result = list(self.collection.aggregate(pipeline))
            
            return [
                {
                    "keyword": item["_id"],
                    "frequency": item["frequency"],
                    "averageScore": round(item["averageScore"], 2)
                }
                for item in result
            ]
        except Exception:
            return []
    
    @staticmethod
    def _format_review_response(review: Dict[str, Any]) -> Dict[str, Any]:
        """Format review data for API response"""
        if not review:
            return None
        
        return {
            "id": str(review['_id']),
            "userId": str(review['userId']),
            "jobTitle": review['jobTitle'],
            "jobDescription": review['jobDescription'],
            "resumeFileName": review['resumeFileName'],
            "matchScore": review['matchScore'],
            "missingKeywords": review['missingKeywords'],
            "profileSummary": review['profileSummary'],
            "recommendations": review.get('recommendations', []),
            "createdAt": review['createdAt'].isoformat(),
            "updatedAt": review['updatedAt'].isoformat()
        }
