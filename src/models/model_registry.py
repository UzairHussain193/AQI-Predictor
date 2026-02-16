"""
Model Registry Module

Handles model storage and retrieval from MongoDB.
"""

import pickle
from datetime import datetime, timezone
from typing import Dict, Any, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class ModelRegistry:
    """Handles model storage and retrieval from MongoDB model_registry collection."""
    
    def __init__(self, db_handler):
        """
        Initialize ModelRegistry.
        
        Args:
            db_handler: MongoDBHandler instance
        """
        self.db_handler = db_handler
        self.collection = db_handler.db['model_registry']
        logger.info("ModelRegistry initialized")
    
    def save_model(self, model, scaler, model_name: str, version: str,
                   feature_names: list, performance: Dict[str, float],
                   training_info: Dict[str, Any]) -> str:
        """
        Save model to MongoDB registry.
        
        Args:
            model: Trained model object
            scaler: Fitted scaler object
            model_name: Name of the model
            version: Model version (e.g., 'v1')
            feature_names: List of feature names
            performance: Dictionary of performance metrics
            training_info: Dictionary of training information
            
        Returns:
            str: Inserted model ID
        """
        logger.info(f"Saving {model_name} {version} to MongoDB registry...")
        
        # Serialize model and scaler to binary
        model_binary = pickle.dumps(model)
        scaler_binary = pickle.dumps(scaler)
        
        # Prepare registry document
        registry_doc = {
            'model_name': model_name,
            'version': version,
            'model_binary': model_binary,
            'scaler_binary': scaler_binary,
            'feature_names': feature_names,
            'n_features': len(feature_names),
            'performance': performance,
            'training_info': training_info,
            'created_at': datetime.now(timezone.utc),
            'is_active': True  # Mark as active model for predictions
        }
        
        # Deactivate all previous models
        self.collection.update_many({}, {'$set': {'is_active': False}})
        
        # Insert new model
        result = self.collection.insert_one(registry_doc)
        
        logger.info(f"Model saved! ID: {result.inserted_id}")
        return str(result.inserted_id)
    
    def load_active_model(self) -> Optional[Tuple[Any, Any, list, Dict]]:
        """
        Load the active model from MongoDB registry.
        
        Returns:
            tuple: (model, scaler, feature_names, metadata) or None if not found
        """
        logger.info("Loading active model from MongoDB registry...")
        
        # Find active model
        doc = self.collection.find_one({'is_active': True})
        
        if not doc:
            logger.warning("No active model found in registry!")
            return None
        
        # Deserialize model and scaler
        model = pickle.loads(doc['model_binary'])
        scaler = pickle.loads(doc['scaler_binary'])
        feature_names = doc['feature_names']
        
        metadata = {
            'model_name': doc['model_name'],
            'version': doc['version'],
            'performance': doc['performance'],
            'training_info': doc['training_info'],
            'created_at': doc['created_at']
        }
        
        logger.info(f"Loaded {metadata['model_name']} {metadata['version']}")
        logger.info(f"   RMSE: {metadata['performance']['test_rmse']:.4f}")
        
        return model, scaler, feature_names, metadata
    
    def list_models(self, limit: int = 10) -> list:
        """
        List all models in registry (sorted by creation date, newest first).
        
        Args:
            limit: Maximum number of models to return
            
        Returns:
            list: List of model metadata dictionaries
        """
        cursor = self.collection.find(
            {},
            {'model_binary': 0, 'scaler_binary': 0}  # Exclude binary data
        ).sort('created_at', -1).limit(limit)
        
        models = []
        for doc in cursor:
            doc['_id'] = str(doc['_id'])
            models.append(doc)
        
        logger.info(f"Found {len(models)} models in registry")
        return models
    
    def get_model_by_id(self, model_id: str) -> Optional[Tuple[Any, Any, list, Dict]]:
        """
        Load a specific model by its ID.
        
        Args:
            model_id: MongoDB document ID
            
        Returns:
            tuple: (model, scaler, feature_names, metadata) or None if not found
        """
        from bson import ObjectId
        
        logger.info(f"Loading model {model_id}...")
        
        doc = self.collection.find_one({'_id': ObjectId(model_id)})
        
        if not doc:
            logger.warning(f"Model {model_id} not found!")
            return None
        
        # Deserialize model and scaler
        model = pickle.loads(doc['model_binary'])
        scaler = pickle.loads(doc['scaler_binary'])
        feature_names = doc['feature_names']
        
        metadata = {
            'model_name': doc['model_name'],
            'version': doc['version'],
            'performance': doc['performance'],
            'training_info': doc['training_info'],
            'created_at': doc['created_at']
        }
        
        logger.info(f"Loaded {metadata['model_name']} {metadata['version']}")
        
        return model, scaler, feature_names, metadata
    
    def set_active_model(self, model_id: str) -> bool:
        """
        Set a specific model as the active model.
        
        Args:
            model_id: MongoDB document ID
            
        Returns:
            bool: True if successful, False otherwise
        """
        from bson import ObjectId
        
        logger.info(f"Setting model {model_id} as active...")
        
        # Deactivate all models
        self.collection.update_many({}, {'$set': {'is_active': False}})
        
        # Activate specified model
        result = self.collection.update_one(
            {'_id': ObjectId(model_id)},
            {'$set': {'is_active': True}}
        )
        
        if result.modified_count > 0:
            logger.info(f"Model {model_id} is now active")
            return True
        else:
            logger.warning(f"Failed to activate model {model_id}")
            return False
