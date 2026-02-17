"""MongoDB handler for feature store operations"""
import pandas as pd
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.server_api import ServerApi
from datetime import datetime, timedelta
from urllib.parse import quote_plus
from src.config import Config


class MongoDBHandler:
    """Handle MongoDB operations for feature store"""
    
    def __init__(self):
        
        username_encoded = quote_plus(Config.MONGODB_USERNAME)
        password_encoded = quote_plus(Config.MONGODB_PASSWORD)
        
        uri = f'mongodb+srv://{username_encoded}:{password_encoded}@{Config.MONGODB_CLUSTER}/?appName=AQIPredictor&retryWrites=true&w=majority'
        # print(f"   URI (masked): mongodb+srv://{username_encoded}:****@{Config.MONGODB_CLUSTER}/...")
        
        try:
            self.client = MongoClient(uri, server_api=ServerApi('1'))
            self.db = self.client[Config.MONGODB_DATABASE]
            self.historical_collection = self.db['historical_features']
            self.current_collection = self.db['current_features']
            self.metadata_collection = self.db['feature_metadata']
            
            # Test connection
            self.client.admin.command('ping')
            print("   ✅ MongoDB connection successful!")
            
            self._create_indexes()
        except Exception as e:
            print(f"   ❌ MongoDB connection failed: {str(e)}")
            raise
    
    def _create_indexes(self):
        """Create indexes for efficient querying"""
        self.historical_collection.create_index([('timestamp', DESCENDING)])
        self.historical_collection.create_index([('timestamp', DESCENDING), ('metadata.version', ASCENDING)])
        self.current_collection.create_index([('timestamp', DESCENDING)])
    
    def check_timestamp_exists(self, timestamp, collection_name='historical_features'):
        """Check if a timestamp already exists in the collection"""
        collection = self.db[collection_name]
        return collection.find_one({'timestamp': timestamp}) is not None
    
    def get_last_n_hours(self, n=24, collection_name='historical_features'):
        """Get last n hours of data for lag feature calculation"""
        collection = self.db[collection_name]
        
        cursor = collection.find().sort('timestamp', DESCENDING).limit(n)
        documents = list(cursor)
        
        if not documents:
            return None
        
        rows = []
        for doc in documents:
            row = {'timestamp': doc['timestamp'], 'aqi': doc['aqi']}
            row.update(doc['features'])
            rows.append(row)
        
        df = pd.DataFrame(rows)
        return df.sort_values('timestamp').reset_index(drop=True)
    
    def prepare_document(self, row, version='v1.0'):
        """Prepare a document for MongoDB from DataFrame row"""
        doc = row.to_dict()
        
        if isinstance(doc.get('timestamp'), str):
            doc['timestamp'] = pd.to_datetime(doc['timestamp'])
        
        aqi = doc.pop('aqi', None)
        timestamp = doc.pop('timestamp')
        
        return {
            'timestamp': timestamp,
            'aqi': aqi,
            'features': doc,
            'metadata': {
                'version': version,
                'created_at': datetime.utcnow(),
                'feature_count': len(doc)
            }
        }
    
    def upload_features(self, df, collection_name='historical_features', batch_size=1000, version='v1.0'):
        """Upload features in batches"""
        collection = self.db[collection_name]
        total_rows = len(df)
        uploaded = 0
        
        for i in range(0, total_rows, batch_size):
            batch = df.iloc[i:i+batch_size]
            documents = [self.prepare_document(row, version) for _, row in batch.iterrows()]
            result = collection.insert_many(documents, ordered=False)
            uploaded += len(result.inserted_ids)
        
        return uploaded
    
    def append_features(self, df, collection_name='historical_features', version='v1.0'):
        """Append new features, skip if timestamp exists"""
        collection = self.db[collection_name]
        added = 0
        skipped = 0
        
        for _, row in df.iterrows():
            timestamp = row['timestamp']
            
            if self.check_timestamp_exists(timestamp, collection_name):
                skipped += 1
                continue
            
            document = self.prepare_document(row, version)
            collection.insert_one(document)
            added += 1
        
        return added, skipped
    
    def query_features(self, collection_name='historical_features', limit=None, query=None):
        """Query features from MongoDB collection"""
        collection = self.db[collection_name]
        
        if query is None:
            query = {}
        
        cursor = collection.find(query).sort('timestamp', ASCENDING)
        
        if limit:
            cursor = cursor.limit(limit)
        
        documents = list(cursor)
        
        if not documents:
            return pd.DataFrame()
        
        rows = []
        for doc in documents:
            row = {'timestamp': doc['timestamp'], 'aqi': doc['aqi']}
            if '_id' in doc:
                row['_id'] = str(doc['_id'])
            row.update(doc['features'])
            rows.append(row)
        
        return pd.DataFrame(rows)
    
    def query_last_n_hours(self, hours=24, collection_name='historical_features'):
        """Query last n hours of data"""
        collection = self.db[collection_name]
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        cursor = collection.find({'timestamp': {'$gte': cutoff_time}}).sort('timestamp', ASCENDING)
        documents = list(cursor)
        
        if not documents:
            return pd.DataFrame()
        
        rows = []
        for doc in documents:
            row = {'timestamp': doc['timestamp'], 'aqi': doc['aqi']}
            if '_id' in doc:
                row['_id'] = str(doc['_id'])
            row.update(doc['features'])
            rows.append(row)
        
        return pd.DataFrame(rows)
    
    def close(self):
        """Close MongoDB connection"""
        self.client.close()
