import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class PineconeService:
    def __init__(self):
        self.model = None
        self.index = None
        self.initialize_model()
        self.initialize_pinecone()
    
    def initialize_model(self):
        """Initialize the sentence transformer model"""
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("SentenceTransformer model loaded successfully")
        except ImportError:
            logger.warning("SentenceTransformer not available, using mock mode")
        except Exception as e:
            logger.error(f"Failed to load SentenceTransformer model: {e}")
    
    def initialize_pinecone(self):
        """Initialize Pinecone connection"""
        try:
            from ..config import settings
            
            if hasattr(settings, 'PINECONE_API_KEY') and settings.PINECONE_API_KEY:
                try:
                    from pinecone import Pinecone
                    pc = Pinecone(api_key=settings.PINECONE_API_KEY)
                    
                    # Simple approach - try to connect to index directly
                    if hasattr(settings, 'PINECONE_INDEX_NAME'):
                        try:
                            self.index = pc.Index(settings.PINECONE_INDEX_NAME)
                            logger.info("Connected to existing Pinecone index")
                        except Exception:
                            logger.info(f"Index {settings.PINECONE_INDEX_NAME} not found, creating...")
                            # Create index with serverless spec (new API)
                            pc.create_index(
                                name=settings.PINECONE_INDEX_NAME,
                                dimension=384,  # Dimension for all-MiniLM-L6-v2
                                metric="cosine",
                                spec={
                                    "serverless": {
                                        "cloud": "aws",
                                        "region": "us-east-1"
                                    }
                                }
                            )
                            self.index = pc.Index(settings.PINECONE_INDEX_NAME)
                            logger.info("Pinecone index created and connected successfully")
                    else:
                        logger.warning("PINECONE_INDEX_NAME not configured")
                        
                except ImportError:
                    logger.warning("Pinecone library not available, using mock mode")
                except Exception as pinecone_error:
                    logger.error(f"Pinecone initialization failed: {pinecone_error}")
            else:
                logger.warning("Pinecone credentials not found, using mock mode")
        except Exception as e:
            logger.error(f"Failed to initialize Pinecone: {e}")
    
    def vectorize_creator_data(self, creator_data: Dict[str, Any]) -> List[float]:
        """Convert creator data to vector embedding"""
        if not self.model:
            logger.warning("SentenceTransformer model not available, returning empty vector")
            return [0.0] * 384  # Return zero vector if model not available
            
        # Combine relevant text fields for vectorization
        text_data = []
        
        if creator_data.get('full_name'):
            text_data.append(creator_data['full_name'])
        if creator_data.get('bio'):
            text_data.append(creator_data['bio'])
        if creator_data.get('location'):
            text_data.append(creator_data['location'])
        if creator_data.get('category'):
            text_data.append(creator_data['category'])
        if creator_data.get('languages'):
            text_data.extend(creator_data['languages'])
        if creator_data.get('content_types'):
            text_data.extend(creator_data['content_types'])
        
        combined_text = " ".join(text_data)
        
        try:
            # Generate embedding
            embedding = self.model.encode(combined_text)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            return [0.0] * 384
    
    async def upsert_creator(self, creator_id: int, creator_data: Dict[str, Any]):
        """Add or update creator in Pinecone"""
        try:
            if not self.index:
                logger.warning("Pinecone not initialized, skipping upsert")
                return
            
            vector = self.vectorize_creator_data(creator_data)
            
            # Prepare metadata
            metadata = {
                'creator_id': creator_id,
                'full_name': creator_data.get('full_name', ''),
                'category': creator_data.get('category', ''),
                'location': creator_data.get('location', ''),
                'instagram_followers': creator_data.get('instagram_followers', 0),
                'base_rate': creator_data.get('base_rate', 0),
                'engagement_rate': creator_data.get('engagement_rate', 0)
            }
            
            self.index.upsert([
                (str(creator_id), vector, metadata)
            ])
            
            logger.info(f"Creator {creator_id} upserted to Pinecone successfully")
        except Exception as e:
            logger.error(f"Failed to upsert creator {creator_id} to Pinecone: {e}")
    
    async def search_creators(self, query: str, filters: Dict[str, Any] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Search for similar creators using vector similarity"""
        try:
            if not self.index or not self.model:
                logger.warning("Pinecone or model not initialized, returning empty results")
                return []
            
            # Vectorize query
            query_vector = self.model.encode(query).tolist()
            
            # Prepare filters
            pinecone_filter = {}
            if filters:
                if filters.get('category'):
                    pinecone_filter['category'] = {'$eq': filters['category']}
                if filters.get('min_followers'):
                    pinecone_filter['instagram_followers'] = {'$gte': filters['min_followers']}
                if filters.get('max_rate'):
                    pinecone_filter['base_rate'] = {'$lte': filters['max_rate']}
            
            # Search in Pinecone
            results = self.index.query(
                vector=query_vector,
                top_k=limit,
                include_metadata=True,
                filter=pinecone_filter if pinecone_filter else None
            )
            
            return results.matches
        except Exception as e:
            logger.error(f"Failed to search creators: {e}")
            return []
    
    async def delete_creator(self, creator_id: int):
        """Remove creator from Pinecone"""
        try:
            if not self.index:
                logger.warning("Pinecone not initialized, skipping delete")
                return
            
            self.index.delete(ids=[str(creator_id)])
            logger.info(f"Creator {creator_id} deleted from Pinecone")
        except Exception as e:
            logger.error(f"Failed to delete creator {creator_id}: {e}")

