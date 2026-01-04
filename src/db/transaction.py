"""
Transaction wrapper for database operations.
Since Supabase uses PostgREST (HTTP), we implement rollback by tracking inserts
and deleting them in reverse order on error.
"""
from typing import Dict, List, Callable, Tuple, Any
from src.db.dbConnect import db


class Transaction:
    """
    Transaction wrapper that tracks inserts and provides rollback functionality.
    On error, deletes all inserted records in reverse order.
    """
    
    def __init__(self):
        self.inserted_ids: Dict[str, List[str]] = {}  # table_name -> list of inserted IDs
        self.committed = False
    
    def track_insert(self, table_name: str, inserted_data: List[Dict]) -> None:
        """Track inserted records for potential rollback."""
        if table_name not in self.inserted_ids:
            self.inserted_ids[table_name] = []
        
        # Extract IDs from inserted data (assumes 'id' field exists)
        for record in inserted_data:
            if 'id' in record:
                self.inserted_ids[table_name].append(record['id'])
    
    def rollback(self) -> bool:
        """
        Rollback all inserts by deleting tracked records in reverse order.
        Returns True if rollback was successful, False otherwise.
        """
        if self.committed:
            return False
        
        success = True
        # Delete in reverse order of inserts (reverse the dict order)
        tables = list(self.inserted_ids.keys())
        for table_name in reversed(tables):
            ids = self.inserted_ids[table_name]
            if ids:
                try:
                    # Delete all tracked IDs from this table
                    db.table(table_name).delete().in_('id', ids).execute()
                except Exception as e:
                    print(f"Error rolling back table {table_name}: {str(e)}")
                    success = False
        
        self.inserted_ids = {}
        return success
    
    def commit(self) -> None:
        """Mark transaction as committed (no rollback possible after this)."""
        self.committed = True
        self.inserted_ids = {}
    
    def execute_insert(self, table_name: str, insert_func: Callable, data: List[Any]) -> Tuple[Dict, int]:
        """
        Execute an insert function and track results for rollback.
        
        Args:
            table_name: Name of the table being inserted into
            insert_func: The insert function to call
            data: Data to insert
            
        Returns:
            Tuple of (response dict, status code)
        """
        response, status = insert_func(data)
        
        if status == 200 and 'data' in response:
            # Track inserted records
            if response['data']:
                self.track_insert(table_name, response['data'])
        
        return response, status


# Global transaction instance
_current_transaction: Transaction = None


def begin_transaction() -> Transaction:
    """Begin a new transaction."""
    global _current_transaction
    _current_transaction = Transaction()
    return _current_transaction


def get_transaction() -> Transaction:
    """Get the current transaction, or create a new one if none exists."""
    global _current_transaction
    if _current_transaction is None:
        _current_transaction = Transaction()
    return _current_transaction


def commit_transaction() -> None:
    """Commit the current transaction."""
    global _current_transaction
    if _current_transaction:
        _current_transaction.commit()
        _current_transaction = None


def rollback_transaction() -> bool:
    """Rollback the current transaction."""
    global _current_transaction
    if _current_transaction:
        success = _current_transaction.rollback()
        _current_transaction = None
        return success
    return False

