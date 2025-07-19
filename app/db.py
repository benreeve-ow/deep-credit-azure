from azure.cosmos import CosmosClient
import os, functools

@functools.lru_cache
def _container(name):
    # Handle missing environment variable for development
    conn_string = os.environ.get("COSMOS_CONN")
    if not conn_string or conn_string.startswith("AccountEndpoint=https://placeholder"):
        print(f"Warning: No valid Cosmos DB connection configured for container '{name}'. Using mock container.")
        return MockContainer()
    
    client = CosmosClient.from_connection_string(conn_string)
    db = client.get_database_client("cosmos-deepcredit")
    return db.get_container_client(name)

class MockContainer:
    """Mock container for development when Cosmos DB is not configured"""
    def create_item(self, item):
        print(f"Mock: Would create item {item}")
        return item
    
    def upsert_item(self, item):
        print(f"Mock: Would upsert item {item}")
        return item
    
    def read_item(self, item_id, partition_key):
        print(f"Mock: Would read item {item_id}")
        return {"id": item_id, "status": "done", "report": "Mock report for development"}
    
    def query_items(self, query, parameters=None, enable_cross_partition_query=True):
        print(f"Mock: Would query with {query}")
        return []

# Initialize containers (will use mock if Cosmos DB not configured)
current = _container("reports_current")
history = _container("reports_history")