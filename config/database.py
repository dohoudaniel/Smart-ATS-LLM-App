import os
import logging
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from typing import Optional

logger = logging.getLogger(__name__)


class Database:
    """MongoDB database connection and management"""
    
    def __init__(self):
        self.client: Optional[MongoClient] = None
        self.db = None
        self.users_collection = None
        self.reviews_collection = None
    
    def connect(self) -> bool:
        """Connect to MongoDB"""
        try:
            # Get MongoDB URI from environment variables
            mongodb_uri = os.getenv('MONGODB_URI')
            if not mongodb_uri:
                logger.error("MONGODB_URI environment variable not set")
                return False
            
            # Get database name
            db_name = os.getenv('MONGODB_DB_NAME', 'smart_ats')
            
            # Create MongoDB client
            self.client = MongoClient(
                mongodb_uri,
                serverSelectionTimeoutMS=5000,  # 5 second timeout
                connectTimeoutMS=10000,         # 10 second connection timeout
                socketTimeoutMS=20000,          # 20 second socket timeout
                maxPoolSize=50,                 # Maximum number of connections
                retryWrites=True
            )
            
            # Test the connection
            self.client.admin.command('ping')
            
            # Get database and collections
            self.db = self.client[db_name]
            self.users_collection = self.db.users
            self.reviews_collection = self.db.reviews
            
            # Create indexes for better performance
            self._create_indexes()
            
            logger.info(f"Successfully connected to MongoDB database: {db_name}")
            return True
            
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.error(f"Failed to connect to MongoDB: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error connecting to MongoDB: {str(e)}")
            return False
    
    def _create_indexes(self):
        """Create database indexes for better performance"""
        try:
            # Users collection indexes
            self.users_collection.create_index("email", unique=True)
            self.users_collection.create_index("createdAt")
            self.users_collection.create_index("isActive")
            
            # Reviews collection indexes
            self.reviews_collection.create_index("userId")
            self.reviews_collection.create_index("createdAt")
            self.reviews_collection.create_index([("userId", 1), ("createdAt", -1)])
            self.reviews_collection.create_index([("jobTitle", "text"), ("missingKeywords", "text")])
            
            logger.info("Database indexes created successfully")
            
        except Exception as e:
            logger.warning(f"Failed to create some indexes: {str(e)}")
    
    def disconnect(self):
        """Disconnect from MongoDB"""
        if self.client:
            self.client.close()
            logger.info("Disconnected from MongoDB")
    
    def is_connected(self) -> bool:
        """Check if database is connected"""
        try:
            if self.client:
                self.client.admin.command('ping')
                return True
            return False
        except Exception:
            return False
    
    def get_users_collection(self):
        """Get users collection"""
        return self.users_collection
    
    def get_reviews_collection(self):
        """Get reviews collection"""
        return self.reviews_collection
    
    def get_database_stats(self) -> dict:
        """Get database statistics"""
        try:
            if not self.db:
                return {}
            
            stats = self.db.command("dbStats")
            
            return {
                "database": stats.get("db"),
                "collections": stats.get("collections", 0),
                "objects": stats.get("objects", 0),
                "dataSize": stats.get("dataSize", 0),
                "storageSize": stats.get("storageSize", 0),
                "indexes": stats.get("indexes", 0)
            }
        except Exception as e:
            logger.error(f"Failed to get database stats: {str(e)}")
            return {}
    
    def health_check(self) -> dict:
        """Perform database health check"""
        try:
            # Test connection
            if not self.is_connected():
                return {
                    "status": "unhealthy",
                    "message": "Database connection failed"
                }
            
            # Test basic operations
            self.users_collection.find_one({}, {"_id": 1})
            self.reviews_collection.find_one({}, {"_id": 1})
            
            return {
                "status": "healthy",
                "message": "Database is operational",
                "stats": self.get_database_stats()
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "message": f"Database health check failed: {str(e)}"
            }


# Global database instance
db_instance = Database()


def get_database():
    """Get the global database instance"""
    return db_instance


def init_database():
    """Initialize database connection"""
    return db_instance.connect()


def close_database():
    """Close database connection"""
    db_instance.disconnect()
