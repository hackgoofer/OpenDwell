from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Generator


class DatabaseProvider(ABC):
    """Abstract base class for database providers."""
    
    @abstractmethod
    def initialize(self):
        """Initialize the database connection and create tables if needed."""
        pass
    
    # Journal Entries
    @abstractmethod
    def get_entries(self, user_id: str, not_in_timestamps: List = None, not_in_ids: List = None) -> List[Dict]:
        """Get journal entries for a user."""
        pass
    
    @abstractmethod
    def add_entry(self, what_happened: str, user_id: str, date: str) -> Dict:
        """Add a new journal entry."""
        pass
    
    @abstractmethod
    def edit_entry(self, entry_id: str, what_happened: str) -> Dict:
        """Edit an existing journal entry."""
        pass
    
    @abstractmethod
    def delete_activities_by_entry(self, entry_id: str) -> int:
        """Delete all activities associated with a journal entry."""
        pass
    
    @abstractmethod
    def delete_value_comparisons_by_entry(self, entry_id: str) -> int:
        """Delete all value comparisons associated with a journal entry."""
        pass
    
    # Activities
    @abstractmethod
    def get_activities(self, user_id: str) -> List[Dict]:
        """Get activities for a user."""
        pass
    
    @abstractmethod
    def add_activity(self, activity_data: Any, entry_id: str, user_id: str) -> Optional[Dict]:
        """Add a new activity."""
        pass
    
    @abstractmethod
    def edit_activity(self, activity_id: str, update_payload: Dict) -> Dict:
        """Edit an existing activity."""
        pass
    
    @abstractmethod
    def delete_activity(self, activity_id: str) -> Dict:
        """Delete an activity."""
        pass
    
    # Messages and Threads
    @abstractmethod
    def add_chat_message_DB(self, user_id: str, thread_id: str, role: str, content: str) -> Optional[str]:
        """Add a chat message to the database."""
        pass
    
    @abstractmethod
    def add_thread_DB(self, user_id: str, type: str, thread_data: Dict) -> Optional[str]:
        """Add a thread to the database."""
        pass
    
    # Value Comparisons
    @abstractmethod
    def get_value_comparison_instances(self, user_id: str) -> List[Dict]:
        """Get value comparison instances for a user."""
        pass
    
    @abstractmethod
    def get_human_values(self) -> List[Dict]:
        """Get all human values."""
        pass
    
    @abstractmethod
    def add_value_comparison_instance(self, value_comp: Any, new_entry: Dict, superior_value_id: str, inferior_value_id: str) -> Optional[Dict]:
        """Add a value comparison instance."""
        pass
    
    @abstractmethod
    def edit_value_comparison_instance(self, value_comparison_id: str, update_payload: Dict) -> Dict:
        """Edit a value comparison instance."""
        pass
    
    # Utility Methods
    def merge_activities_and_entries(self, activities: List[Dict], entries: List[Dict]) -> List[tuple]:
        """Merge activities with their corresponding entries."""
        entries_dict = {entry['id']: entry for entry in entries}
        merged_data = []
        for activity in activities:
            entry = entries_dict.get(activity['entry_id'])
            if entry:
                merged_data.append((activity, entry['date']))
        return merged_data
    
    def get_activities_and_entries(self, user_id: str) -> List[tuple]:
        """Get activities merged with their entries."""
        activities = self.get_activities(user_id)
        entries = self.get_entries(user_id)
        return self.merge_activities_and_entries(activities, entries)
    
    def get_pairwise_user_values(self, user_id: str) -> str:
        """Get pairwise user values as a formatted string."""
        pairwise_comparisons = self.get_value_comparison_instances(user_id)
        comparisons_with_names = []
        human_values = self.get_human_values()
        human_values_dict = {value['id']: value['name'] for value in human_values}
        for comparison in pairwise_comparisons:
            superior_value_name = human_values_dict[comparison["superior_value_id"]]
            inferior_value_name = human_values_dict[comparison["inferior_value_id"]]
            comparisons_with_names.append((superior_value_name, inferior_value_name))
        return "; ".join([f"{a[0]} > {a[1]}" for a in comparisons_with_names])
    
    def get_value_comparison_from_entries(self, user_id: str) -> List[Dict]:
        """Get value comparisons associated with journal entries."""
        entries = self.get_entries(user_id)
        entries_dict = {entry['id']: entry["date"] for entry in entries}
        value_comparison_instances = self.get_value_comparison_instances(user_id)
        value_comparisons = []
        for instance in value_comparison_instances:
            if instance.get('type') == 'entry' and instance.get('entry_id') in entries_dict:
                instance['date'] = entries_dict[instance['entry_id']]
                value_comparisons.append(instance)
        
        value_comparisons.sort(key=lambda x: x['date'], reverse=True)
        return value_comparisons
    
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the name of this database provider."""
        pass