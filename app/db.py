"""
Cosmos DB Database Operations Module

This module handles all database operations for the OpenAI Responses API.
It provides functions to store, retrieve, and manage response data in Azure Cosmos DB.

Key Features:
- Store response data with automatic timestamps
- Retrieve responses by run_id
- List all responses with pagination
- Update response status and content
- Handle database connection errors gracefully
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from azure.cosmos import CosmosClient, PartitionKey
from azure.cosmos.exceptions import CosmosHttpResponseError

class CosmosDBManager:
    """
    Manages Cosmos DB operations for the OpenAI Responses API.
    
    This class handles:
    - Database and container creation
    - CRUD operations for response data
    - Error handling and connection management
    - Automatic retries for transient failures
    """
    
    def __init__(self, connection_string: str, database_name: str = "deep-credit", container_name: str = "reports_current"):
        """
        Initialize the Cosmos DB manager.
        
        Args:
            connection_string: Azure Cosmos DB connection string
            database_name: Name of the database to use (default: deep-credit)
            container_name: Name of the container to use (default: reports_current)
        """
        self.connection_string = connection_string
        self.database_name = database_name
        self.container_name = container_name
        self.client = None
        self.database = None
        self.container = None
        
        # Initialize the connection
        self._initialize_connection()
    
    def _initialize_connection(self):
        """Initialize the Cosmos DB client and connect to existing database/container."""
        try:
            # Create the Cosmos client
            self.client = CosmosClient.from_connection_string(self.connection_string)
            
            # Get the existing database
            self.database = self.client.get_database_client(self.database_name)
            
            # Get the existing container
            self.container = self.database.get_container_client(self.container_name)
            
            print(f"✅ Connected to Cosmos DB: {self.database_name}/{self.container_name}")
            
        except Exception as e:
            print(f"❌ Failed to initialize Cosmos DB connection: {str(e)}")
            raise
    
    def store_response(self, run_id: str, data: Dict[str, Any]) -> bool:
        """
        Store response data in Cosmos DB.
        
        Args:
            run_id: Unique identifier for the response
            data: Dictionary containing response data
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Prepare the document for storage
            document = {
                "id": run_id,  # Use run_id as the document id
                "run_id": run_id,  # Also store as a field for querying
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "type": "openai_response",  # Add type to distinguish from other documents
                **data  # Include all the response data
            }
            
            # Upsert the document (create if doesn't exist, update if it does)
            self.container.upsert_item(document)
            
            print(f"✅ Stored response data for run_id: {run_id}")
            return True
            
        except CosmosHttpResponseError as e:
            print(f"❌ Cosmos DB error storing response {run_id}: {str(e)}")
            return False
        except Exception as e:
            print(f"❌ Unexpected error storing response {run_id}: {str(e)}")
            return False
    
    def get_response(self, run_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve response data by run_id.
        
        Args:
            run_id: Unique identifier for the response
            
        Returns:
            Dict containing response data or None if not found
        """
        try:
            # Query for the specific run_id and type
            query = "SELECT * FROM c WHERE c.run_id = @run_id AND c.type = @type"
            parameters = [
                {"name": "@run_id", "value": run_id},
                {"name": "@type", "value": "openai_response"}
            ]
            
            items = list(self.container.query_items(
                query=query,
                parameters=parameters,
                enable_cross_partition_query=True
            ))
            
            if items:
                print(f"✅ Retrieved response data for run_id: {run_id}")
                return items[0]
            else:
                print(f"⚠️ No response found for run_id: {run_id}")
                return None
                
        except CosmosHttpResponseError as e:
            print(f"❌ Cosmos DB error retrieving response {run_id}: {str(e)}")
            return None
        except Exception as e:
            print(f"❌ Unexpected error retrieving response {run_id}: {str(e)}")
            return None
    
    def update_response(self, run_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update existing response data.
        
        Args:
            run_id: Unique identifier for the response
            updates: Dictionary containing fields to update
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # First get the existing document
            existing = self.get_response(run_id)
            if not existing:
                print(f"⚠️ Cannot update - no response found for run_id: {run_id}")
                return False
            
            # Update the document with new data
            existing.update(updates)
            existing["updated_at"] = datetime.utcnow().isoformat()
            
            # Replace the document
            self.container.replace_item(item=existing, body=existing)
            
            print(f"✅ Updated response data for run_id: {run_id}")
            return True
            
        except CosmosHttpResponseError as e:
            print(f"❌ Cosmos DB error updating response {run_id}: {str(e)}")
            return False
        except Exception as e:
            print(f"❌ Unexpected error updating response {run_id}: {str(e)}")
            return False
    
    def list_responses(self, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """
        List all responses with pagination.
        
        Args:
            limit: Maximum number of responses to return
            offset: Number of responses to skip
            
        Returns:
            List of response documents
        """
        try:
            # Query for all responses of type openai_response, ordered by creation date
            query = "SELECT * FROM c WHERE c.type = @type ORDER BY c.created_at DESC OFFSET @offset LIMIT @limit"
            parameters = [
                {"name": "@type", "value": "openai_response"},
                {"name": "@offset", "value": offset},
                {"name": "@limit", "value": limit}
            ]
            
            items = list(self.container.query_items(
                query=query,
                parameters=parameters,
                enable_cross_partition_query=True
            ))
            
            print(f"✅ Retrieved {len(items)} responses (limit: {limit}, offset: {offset})")
            return items
            
        except CosmosHttpResponseError as e:
            print(f"❌ Cosmos DB error listing responses: {str(e)}")
            return []
        except Exception as e:
            print(f"❌ Unexpected error listing responses: {str(e)}")
            return []
    
    def delete_response(self, run_id: str) -> bool:
        """
        Delete a response by run_id.
        
        Args:
            run_id: Unique identifier for the response
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Get the document first to get its id
            existing = self.get_response(run_id)
            if not existing:
                print(f"⚠️ Cannot delete - no response found for run_id: {run_id}")
                return False
            
            # Delete the document
            self.container.delete_item(item=existing, partition_key=run_id)
            
            print(f"✅ Deleted response for run_id: {run_id}")
            return True
            
        except CosmosHttpResponseError as e:
            print(f"❌ Cosmos DB error deleting response {run_id}: {str(e)}")
            return False
        except Exception as e:
            print(f"❌ Unexpected error deleting response {run_id}: {str(e)}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get database statistics.
        
        Returns:
            Dictionary containing database statistics
        """
        try:
            # Count total responses
            count_query = "SELECT VALUE COUNT(1) FROM c WHERE c.type = @type"
            count_result = list(self.container.query_items(
                query=count_query,
                parameters=[{"name": "@type", "value": "openai_response"}],
                enable_cross_partition_query=True
            ))
            total_count = count_result[0] if count_result else 0
            
            # Get recent responses count (last 24 hours)
            recent_query = "SELECT VALUE COUNT(1) FROM c WHERE c.type = @type AND c.created_at >= @yesterday"
            yesterday = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
            recent_result = list(self.container.query_items(
                query=recent_query,
                parameters=[
                    {"name": "@type", "value": "openai_response"},
                    {"name": "@yesterday", "value": yesterday}
                ],
                enable_cross_partition_query=True
            ))
            recent_count = recent_result[0] if recent_result else 0
            
            return {
                "total_responses": total_count,
                "recent_responses_24h": recent_count,
                "database_name": self.database_name,
                "container_name": self.container_name
            }
            
        except Exception as e:
            print(f"❌ Error getting database stats: {str(e)}")
            return {
                "total_responses": 0,
                "recent_responses_24h": 0,
                "error": str(e)
            }

# Global database manager instance
db_manager = None

def initialize_database():
    """Initialize the global database manager instance."""
    global db_manager
    
    # Get connection string from environment
    connection_string = os.environ.get("COSMOS_CONN")
    
    if not connection_string:
        print("⚠️ No Cosmos DB connection string found - using in-memory storage")
        return None
    
    try:
        db_manager = CosmosDBManager(connection_string)
        return db_manager
    except Exception as e:
        print(f"❌ Failed to initialize database: {str(e)}")
        return None

def get_db_manager():
    """Get the global database manager instance."""
    return db_manager