"""
Firestore client for all agents
"""
import firebase_admin
from firebase_admin import credentials, firestore
from typing import Optional, List, Dict, Any
from google.cloud.firestore_v1 import DocumentSnapshot
from .config import config
from .logger import logger


class FirestoreClient:
    """Wrapper for Firestore operations"""

    def __init__(self):
        """Initialize Firestore client"""
        if not firebase_admin._apps:
            # Initialize Firebase Admin SDK
            cred = credentials.ApplicationDefault()
            firebase_admin.initialize_app(cred, {
                'projectId': config.PROJECT_ID,
            })

        self.db = firestore.client()
        logger.info("Firestore client initialized")

    def get_document(self, collection: str, doc_id: str) -> Optional[Dict[str, Any]]:
        """Get a single document"""
        try:
            doc_ref = self.db.collection(collection).document(doc_id)
            doc = doc_ref.get()

            if doc.exists:
                data = doc.to_dict()
                data['id'] = doc.id
                return data
            else:
                logger.warning(f"Document {doc_id} not found in {collection}")
                return None
        except Exception as e:
            logger.error(f"Error getting document: {e}")
            raise

    def update_document(self, collection: str, doc_id: str, data: Dict[str, Any]) -> None:
        """Update a document"""
        try:
            doc_ref = self.db.collection(collection).document(doc_id)
            doc_ref.update(data)
            logger.info(f"Updated document {doc_id} in {collection}")
        except Exception as e:
            logger.error(f"Error updating document: {e}")
            raise

    def create_document(self, collection: str, data: Dict[str, Any], doc_id: Optional[str] = None) -> str:
        """Create a new document"""
        try:
            if doc_id:
                doc_ref = self.db.collection(collection).document(doc_id)
                doc_ref.set(data)
                return doc_id
            else:
                doc_ref = self.db.collection(collection).add(data)
                return doc_ref[1].id
        except Exception as e:
            logger.error(f"Error creating document: {e}")
            raise

    def upsert_document(self, collection: str, doc_id: str, data: Dict[str, Any]) -> None:
        """Create or update a document (upsert operation)"""
        try:
            doc_ref = self.db.collection(collection).document(doc_id)
            doc_ref.set(data, merge=True)
            logger.info(f"Upserted document {doc_id} in {collection}")
        except Exception as e:
            logger.error(f"Error upserting document: {e}")
            raise

    def query_documents(
        self,
        collection: str,
        filters: Optional[List[tuple]] = None,
        order_by: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Query documents with filters"""
        try:
            query = self.db.collection(collection)

            # Apply filters
            if filters:
                for field, operator, value in filters:
                    query = query.where(field, operator, value)

            # Apply ordering
            if order_by:
                query = query.order_by(order_by)

            # Apply limit
            if limit:
                query = query.limit(limit)

            # Execute query
            docs = query.stream()

            results = []
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                results.append(data)

            return results
        except Exception as e:
            logger.error(f"Error querying documents: {e}")
            raise

    def log_agent_activity(self, agent_log: Dict[str, Any]) -> None:
        """Log agent activity to Firestore"""
        try:
            self.create_document(config.COLLECTION_AGENT_LOGS, agent_log)
            logger.info(f"Logged activity for agent: {agent_log.get('agent_name')}")
        except Exception as e:
            logger.error(f"Error logging agent activity: {e}")

    def query_documents_paginated(
        self,
        collection: str,
        page: int = 1,
        page_size: int = 12,
        filters: Optional[List[tuple]] = None,
        order_by: Optional[str] = None,
        order_direction: str = 'DESCENDING'
    ) -> Dict[str, Any]:
        """
        Query documents with pagination support

        Args:
            collection: Firestore collection name
            page: Page number (1-indexed)
            page_size: Number of items per page
            filters: List of filter tuples (field, operator, value)
            order_by: Field to order by
            order_direction: 'ASCENDING' or 'DESCENDING'

        Returns:
            Dict with 'data', 'total', 'page', 'page_size', 'total_pages'
        """
        try:
            query = self.db.collection(collection)

            # Apply filters
            if filters:
                for field, operator, value in filters:
                    query = query.where(field, operator, value)

            # Get total count (before pagination)
            total_docs = len(list(query.stream()))

            # Apply ordering
            if order_by:
                direction = firestore.Query.DESCENDING if order_direction == 'DESCENDING' else firestore.Query.ASCENDING
                query = query.order_by(order_by, direction=direction)

            # Calculate offset
            offset = (page - 1) * page_size

            # Apply pagination
            query = query.limit(page_size).offset(offset)

            # Execute query
            docs = query.stream()

            results = []
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                results.append(data)

            total_pages = (total_docs + page_size - 1) // page_size  # Ceiling division

            return {
                'data': results,
                'total': total_docs,
                'page': page,
                'page_size': page_size,
                'total_pages': total_pages,
                'has_next': page < total_pages,
                'has_prev': page > 1
            }
        except Exception as e:
            logger.error(f"Error in paginated query: {e}")
            raise


# Singleton instance
firestore_client = FirestoreClient()
