"""
Azure Cosmos DB Helper Functions

This module contains functions to interact with Azure Cosmos DB:
- Database connection setup
- Data insertion and retrieval
- Query operations
- Error handling for database operations
"""

import os
from azure.cosmos import CosmosClient, PartitionKey, exceptions
from datetime import datetime
import json

# Get Cosmos DB connection details from environment variables
COSMOS_ENDPOINT = os.getenv('COSMOS_DB_ENDPOINT')
COSMOS_KEY = os.getenv('COSMOS_DB_KEY')
DATABASE_NAME = os.getenv('COSMOS_DB_NAME', 'deep-credit-db')
CONTAINER_NAME = os.getenv('COSMOS_CONTAINER_NAME', 'credit-analyses')

def get_cosmos_client():
    """
    Create and return a Cosmos DB client
    
    Returns:
        CosmosClient: Authenticated Cosmos DB client
        
    Raises:
        Exception: If connection credentials are missing
    """
    if not COSMOS_ENDPOINT or not COSMOS_KEY:
        raise Exception("Cosmos DB credentials not found in environment variables")
    
    try:
        # Create the Cosmos client
        client = CosmosClient(COSMOS_ENDPOINT, COSMOS_KEY)
        return client
    except Exception as e:
        raise Exception(f"Failed to create Cosmos DB client: {str(e)}")

def get_database_and_container():
    """
    Get or create the database and container
    
    Returns:
        tuple: (database, container) objects
    """
    client = get_cosmos_client()
    
    # Create database if it doesn't exist
    database = client.create_database_if_not_exists(id=DATABASE_NAME)
    
    # Create container if it doesn't exist
    # Partition key is used to distribute data across multiple partitions
    container = database.create_container_if_not_exists(
        id=CONTAINER_NAME,
        partition_key=PartitionKey(path="/user_id"),  # Partition by user_id
        offer_throughput=400  # Request Units (RUs) for performance
    )
    
    return database, container

def save_credit_analysis(user_id, credit_data, analysis_result):
    """
    Save a credit analysis to Cosmos DB
    
    Args:
        user_id (str): Unique identifier for the user
        credit_data (dict): Original credit data submitted
        analysis_result (dict): Analysis results from OpenAI
        
    Returns:
        dict: Created document with Cosmos DB metadata
        
    Raises:
        Exception: If save operation fails
    """
    try:
        database, container = get_database_and_container()
        
        # Create document to save
        document = {
            'id': f"{user_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            'user_id': user_id,
            'credit_data': credit_data,
            'analysis_result': analysis_result,
            'created_at': datetime.utcnow().isoformat(),
            'document_type': 'credit_analysis'
        }
        
        # Insert document into container
        created_document = container.create_item(body=document)
        
        print(f"Saved analysis for user {user_id} with ID: {created_document['id']}")
        return created_document
        
    except exceptions.CosmosHttpResponseError as e:
        raise Exception(f"Cosmos DB error: {e.message}")
    except Exception as e:
        raise Exception(f"Failed to save credit analysis: {str(e)}")

def get_user_analyses(user_id, limit=10):
    """
    Retrieve recent credit analyses for a specific user
    
    Args:
        user_id (str): User identifier to search for
        limit (int): Maximum number of analyses to return
        
    Returns:
        list: List of analysis documents for the user
    """
    try:
        database, container = get_database_and_container()
        
        # SQL query to get user's analyses, ordered by creation date
        query = """
        SELECT * FROM c 
        WHERE c.user_id = @user_id 
        AND c.document_type = 'credit_analysis'
        ORDER BY c.created_at DESC
        """
        
        # Execute query with parameters
        items = list(container.query_items(
            query=query,
            parameters=[{"name": "@user_id", "value": user_id}],
            enable_cross_partition_query=True,
            max_item_count=limit
        ))
        
        return items
        
    except exceptions.CosmosHttpResponseError as e:
        raise Exception(f"Cosmos DB query error: {e.message}")
    except Exception as e:
        raise Exception(f"Failed to retrieve user analyses: {str(e)}")

def delete_analysis(document_id, user_id):
    """
    Delete a specific credit analysis document
    
    Args:
        document_id (str): ID of the document to delete
        user_id (str): User ID (used as partition key)
        
    Returns:
        bool: True if deletion was successful
    """
    try:
        database, container = get_database_and_container()
        
        # Delete the document using ID and partition key
        container.delete_item(item=document_id, partition_key=user_id)
        
        print(f"Deleted analysis {document_id} for user {user_id}")
        return True
        
    except exceptions.CosmosHttpResponseError as e:
        if e.status_code == 404:
            print(f"Document {document_id} not found")
            return False
        else:
            raise Exception(f"Cosmos DB delete error: {e.message}")
    except Exception as e:
        raise Exception(f"Failed to delete analysis: {str(e)}")

# TODO: Add more helper functions as needed:
# - get_analysis_by_id()
# - update_analysis()
# - get_analytics_summary()
# - cleanup_old_analyses() 