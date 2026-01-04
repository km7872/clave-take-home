#get data from supabase
from src.db.dbConnect import db

def get_data(table_name: str):
    """Get data from a table in the database"""
    return db.table(table_name).select("*").execute()
