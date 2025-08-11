import os
from typing import Dict, Any, List, Optional
from .base_provider import DatabaseProvider
from .providers import SQLiteProvider, SupabaseProvider
from .providers.rds_provider import RDSProvider


class DatabaseManager:
    """Manages database providers and provides a unified interface."""
    
    def __init__(self, provider_name: str = None):
        """Initialize with specified provider or default to sqlite."""
        if provider_name is None:
            provider_name = os.getenv("DATABASE_PROVIDER", "sqlite")
        
        self.provider = self._create_provider(provider_name)
    
    def _create_provider(self, provider_name: str) -> DatabaseProvider:
        """Create and return the specified database provider."""
        if provider_name == "sqlite":
            return SQLiteProvider()
        elif provider_name == "supabase":
            return SupabaseProvider()
        elif provider_name == "rds":
            return RDSProvider()
        else:
            raise ValueError(f"Unknown database provider: {provider_name}")
    
    # Journal Entries
    def get_entries(self, user_id: str, not_in_timestamps: List = None, not_in_ids: List = None) -> List[Dict]:
        """Get journal entries for a user."""
        return self.provider.get_entries(user_id, not_in_timestamps, not_in_ids)
    
    def add_entry(self, what_happened: str, user_id: str, date: str) -> Dict:
        """Add a new journal entry."""
        return self.provider.add_entry(what_happened, user_id, date)
    
    def edit_entry(self, entry_id: str, what_happened: str) -> Dict:
        """Edit an existing journal entry."""
        return self.provider.edit_entry(entry_id, what_happened)
    
    # Activities
    def get_activities(self, user_id: str) -> List[Dict]:
        """Get activities for a user."""
        return self.provider.get_activities(user_id)
    
    def add_activity(self, activity_data: Any, entry_id: str, user_id: str) -> Optional[Dict]:
        """Add a new activity."""
        return self.provider.add_activity(activity_data, entry_id, user_id)
    
    def edit_activity(self, activity_id: str, update_payload: Dict) -> Dict:
        """Edit an existing activity."""
        return self.provider.edit_activity(activity_id, update_payload)
    
    def delete_activity(self, activity_id: str) -> Dict:
        """Delete an activity."""
        return self.provider.delete_activity(activity_id)
    
    # Messages and Threads
    def add_chat_message_DB(self, user_id: str, thread_id: str, role: str, content: str) -> Optional[str]:
        """Add a chat message to the database."""
        return self.provider.add_chat_message_DB(user_id, thread_id, role, content)
    
    def add_thread_DB(self, user_id: str, type: str, thread_data: Dict) -> Optional[str]:
        """Add a thread to the database."""
        return self.provider.add_thread_DB(user_id, type, thread_data)
    
    # Value Comparisons
    def get_value_comparison_instances(self, user_id: str) -> List[Dict]:
        """Get value comparison instances for a user."""
        return self.provider.get_value_comparison_instances(user_id)
    
    def get_human_values(self) -> List[Dict]:
        """Get all human values."""
        return self.provider.get_human_values()
    
    def add_value_comparison_instance(self, value_comp: Any, new_entry: Dict, superior_value_id: str, inferior_value_id: str) -> Optional[Dict]:
        """Add a value comparison instance."""
        return self.provider.add_value_comparison_instance(value_comp, new_entry, superior_value_id, inferior_value_id)
    
    def edit_value_comparison_instance(self, value_comparison_id: str, update_payload: Dict) -> Dict:
        """Edit a value comparison instance."""
        return self.provider.edit_value_comparison_instance(value_comparison_id, update_payload)
    
    # Utility Methods
    def merge_activities_and_entries(self, activities: List[Dict], entries: List[Dict]) -> List[tuple]:
        """Merge activities with their corresponding entries."""
        return self.provider.merge_activities_and_entries(activities, entries)
    
    def get_activities_and_entries(self, user_id: str) -> List[tuple]:
        """Get activities merged with their entries."""
        return self.provider.get_activities_and_entries(user_id)
    
    def get_pairwise_user_values(self, user_id: str) -> str:
        """Get pairwise user values as a formatted string."""
        return self.provider.get_pairwise_user_values(user_id)
    
    def get_value_comparison_from_entries(self, user_id: str) -> List[Dict]:
        """Get value comparisons associated with journal entries."""
        return self.provider.get_value_comparison_from_entries(user_id)
    
    def get_value_comparison_from_threads(self, user_id: str) -> List[Dict]:
        """Get value comparisons associated with threads (Supabase only)."""
        if hasattr(self.provider, 'get_value_comparison_from_threads'):
            return self.provider.get_value_comparison_from_threads(user_id)
        return []
    
    def encrypt_journal(self, user_id: str):
        """Encrypt journal entries (Supabase only)."""
        if hasattr(self.provider, 'encrypt_journal'):
            return self.provider.encrypt_journal(user_id)
        raise NotImplementedError("Encryption not supported by current provider")
    
    def delete_activities_by_entry(self, entry_id: str) -> int:
        """Delete all activities associated with a journal entry."""
        return self.provider.delete_activities_by_entry(entry_id)
    
    def delete_value_comparisons_by_entry(self, entry_id: str) -> int:
        """Delete all value comparisons associated with a journal entry."""
        return self.provider.delete_value_comparisons_by_entry(entry_id)