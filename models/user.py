from datetime import datetime
from typing import Optional, Dict, Any
from bson import ObjectId
import bcrypt
from email_validator import validate_email, EmailNotValidError


class User:
    """User model for MongoDB operations"""
    
    def __init__(self, db_collection):
        self.collection = db_collection
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using bcrypt"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """Verify a password against its hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    @staticmethod
    def validate_email_format(email: str) -> bool:
        """Validate email format"""
        try:
            validate_email(email)
            return True
        except EmailNotValidError:
            return False
    
    def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new user"""
        # Validate required fields
        required_fields = ['email', 'password', 'firstName', 'lastName']
        for field in required_fields:
            if field not in user_data or not user_data[field]:
                raise ValueError(f"Missing required field: {field}")
        
        # Validate email format
        if not self.validate_email_format(user_data['email']):
            raise ValueError("Invalid email format")
        
        # Check if user already exists
        if self.collection.find_one({"email": user_data['email'].lower()}):
            raise ValueError("User with this email already exists")
        
        # Validate password strength
        if len(user_data['password']) < 8:
            raise ValueError("Password must be at least 8 characters long")
        
        # Create user document
        user_doc = {
            "email": user_data['email'].lower(),
            "password": self.hash_password(user_data['password']),
            "firstName": user_data['firstName'].strip(),
            "lastName": user_data['lastName'].strip(),
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow(),
            "isActive": True,
            "profile": {
                "totalReviews": 0,
                "averageScore": 0,
                "lastLoginAt": None
            }
        }
        
        # Insert user
        result = self.collection.insert_one(user_doc)
        
        # Return user without password
        user_doc['_id'] = result.inserted_id
        return self._format_user_response(user_doc)
    
    def authenticate_user(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate user with email and password"""
        user = self.collection.find_one({"email": email.lower(), "isActive": True})
        
        if not user:
            return None
        
        if not self.verify_password(password, user['password']):
            return None
        
        # Update last login
        self.collection.update_one(
            {"_id": user['_id']},
            {"$set": {"profile.lastLoginAt": datetime.utcnow()}}
        )
        
        return self._format_user_response(user)
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        try:
            user = self.collection.find_one({"_id": ObjectId(user_id), "isActive": True})
            return self._format_user_response(user) if user else None
        except Exception:
            return None
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email"""
        user = self.collection.find_one({"email": email.lower(), "isActive": True})
        return self._format_user_response(user) if user else None
    
    def update_user(self, user_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update user information"""
        try:
            # Remove fields that shouldn't be updated directly
            forbidden_fields = ['_id', 'password', 'createdAt', 'email']
            update_data = {k: v for k, v in update_data.items() if k not in forbidden_fields}
            
            if not update_data:
                return None
            
            update_data['updatedAt'] = datetime.utcnow()
            
            result = self.collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": update_data}
            )
            
            if result.modified_count > 0:
                return self.get_user_by_id(user_id)
            return None
        except Exception:
            return None
    
    def update_user_stats(self, user_id: str, review_score: int) -> bool:
        """Update user's review statistics"""
        try:
            user = self.collection.find_one({"_id": ObjectId(user_id)})
            if not user:
                return False
            
            current_total = user.get('profile', {}).get('totalReviews', 0)
            current_avg = user.get('profile', {}).get('averageScore', 0)
            
            new_total = current_total + 1
            new_avg = ((current_avg * current_total) + review_score) / new_total
            
            self.collection.update_one(
                {"_id": ObjectId(user_id)},
                {
                    "$set": {
                        "profile.totalReviews": new_total,
                        "profile.averageScore": round(new_avg, 2),
                        "updatedAt": datetime.utcnow()
                    }
                }
            )
            return True
        except Exception:
            return False
    
    def delete_user(self, user_id: str) -> bool:
        """Soft delete user (mark as inactive)"""
        try:
            result = self.collection.update_one(
                {"_id": ObjectId(user_id)},
                {
                    "$set": {
                        "isActive": False,
                        "updatedAt": datetime.utcnow()
                    }
                }
            )
            return result.modified_count > 0
        except Exception:
            return False
    
    @staticmethod
    def _format_user_response(user: Dict[str, Any]) -> Dict[str, Any]:
        """Format user data for API response (remove sensitive data)"""
        if not user:
            return None
        
        return {
            "id": str(user['_id']),
            "email": user['email'],
            "firstName": user['firstName'],
            "lastName": user['lastName'],
            "createdAt": user['createdAt'].isoformat(),
            "profile": user.get('profile', {})
        }
