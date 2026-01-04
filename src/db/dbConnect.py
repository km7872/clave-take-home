"""
Database connection class using singleton pattern.
Ensures only one Supabase client instance is created and shared.
"""
from supabase import create_client
from dotenv import load_dotenv
import os


class DBConnection:
    """
    Singleton class for Supabase database connection.
    Only one instance is created and reused across the application.
    """
    _instance = None
    _client = None
    _initialized = False
    
    def __new__(cls):
        """Ensure only one instance is created (singleton pattern)"""
        if cls._instance is None:
            cls._instance = super(DBConnection, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize the connection only once"""
        if DBConnection._initialized:
            return
        
        load_dotenv()
        
        SUPABASE_URL = "https://bagwhaycbcbyccygeleo.supabase.co"
        # Use service role key to bypass RLS for backend operations
        SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        #  or os.getenv("SUPABASE_KEY"
        
        DBConnection._client = create_client(SUPABASE_URL, SUPABASE_KEY)
        DBConnection._initialized = True
    
    @property
    def client(self):
        """Get the Supabase client instance"""
        if DBConnection._client is None:
            raise RuntimeError("Database client not initialized")
        return DBConnection._client
    
    def table(self, table_name: str):
        """Access a table from the Supabase client"""
        return self.client.table(table_name)


# Create a singleton instance that can be imported
db = DBConnection()
