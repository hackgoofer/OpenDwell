import os
from typing import Dict, Any, List, Optional
from ..base_provider import DatabaseProvider
from supabase import create_client, Client


class SupabaseProvider(DatabaseProvider):
    """Supabase database provider wrapping existing functionality."""
    
    def __init__(self):
        self.initialize()
    
    @property
    def provider_name(self) -> str:
        return "supabase"
    
    def initialize(self):
        """Initialize Supabase client."""
        self.client: Client = create_client(
            os.getenv("SUPABASE_URL"), 
            os.getenv("SUPABASE_KEY")
        )
    
    def get_entries(self, user_id: str, not_in_timestamps: List = None, not_in_ids: List = None) -> List[Dict]:
        """Get journal entries for a user."""
        not_in_timestamps = not_in_timestamps or []
        not_in_ids = not_in_ids or []
        
        response = self.client.table("journal_entries")\
            .select("*")\
            .eq("user_id", user_id)\
            .order("created_at.desc").execute()
        
        returned_entries = []
        for entry in response.data:
            if entry["date"] in not_in_timestamps:
                break
            if entry["id"] in not_in_ids:
                break
            returned_entries.append(entry)
        return returned_entries
    
    def add_entry(self, what_happened: str, user_id: str, date: str) -> Dict:
        """Add a new journal entry."""
        import hashlib
        content_hash = hashlib.sha256(what_happened.encode()).hexdigest()
        
        entry_data = {
            "user_id": user_id,
            "date": date,
            "what_happened": what_happened,
            "content_hash": content_hash,
            "data": {}
        }
        
        response = self.client.table("journal_entries").insert(entry_data).execute()
        print("New journal entry added successfully.")
        return response.data[0] if response.data else {}
    
    def edit_entry(self, entry_id: str, what_happened: str) -> Dict:
        """Edit an existing journal entry and invalidate dependent data if content changed."""
        import hashlib
        new_content_hash = hashlib.sha256(what_happened.encode()).hexdigest()
        
        # Get current entry to check if content changed
        current_entry_response = self.client.table("journal_entries").select("*").eq("id", entry_id).execute()
        if not current_entry_response.data:
            return {}
        
        current_entry = current_entry_response.data[0]
        content_changed = current_entry.get('content_hash') != new_content_hash
        
        if content_changed:
            print(f"Content changed for entry {entry_id}, invalidating dependent data...")
            self.delete_activities_by_entry(entry_id)
            self.delete_value_comparisons_by_entry(entry_id)
        
        entry_data = {"what_happened": what_happened, "content_hash": new_content_hash}
        
        response = self.client.table("journal_entries").update(entry_data).eq("id", entry_id).execute()
        print("Journal entry updated successfully.")
        return response.data[0] if response.data else {}
    
    def get_activities(self, user_id: str) -> List[Dict]:
        """Get activities for a user."""
        response = self.client.table("activities").select("*").eq("user_id", user_id).execute()
        return response.data
    
    def add_activity(self, activity_data: Any, entry_id: str, user_id: str) -> Optional[Dict]:
        """Add a new activity."""
        activity_record = {
            "user_id": user_id,
            "activity": activity_data.activity,
            "activity_raw": activity_data.activity_raw,
            "emotions": activity_data.emotion.name,
            "entry_id": entry_id,
            "data": {"reviewed": False}
        }
        
        response = self.client.table("activities").insert(activity_record).execute()
        if len(response.data) > 0:
            return response.data[0]
        return None
    
    def edit_activity(self, activity_id: str, update_payload: Dict) -> Dict:
        """Edit an existing activity."""
        response = self.client.table("activities").update(update_payload).eq('id', activity_id).execute()
        print("Activity updated successfully.")
        return response.data[0] if response.data else {}
    
    def delete_activity(self, activity_id: str) -> Dict:
        """Delete an activity."""
        response = self.client.table("activities").delete().eq('id', activity_id).execute()
        print("Activity deleted successfully.")
        return response.data[0] if response.data else {}
    
    def add_chat_message_DB(self, user_id: str, thread_id: str, role: str, content: str) -> Optional[str]:
        """Add a chat message to the database."""
        response = self.client.table("messages").insert({
            "user_id": user_id, 
            "thread_id": thread_id, 
            "role": role, 
            "message_text": content
        }).execute()
        
        if len(response.data) > 0 and "id" in response.data[0]:
            return str(response.data[0]["id"])
        return None
    
    def add_thread_DB(self, user_id: str, type: str, thread_data: Dict) -> Optional[str]:
        """Add a thread to the database."""
        response = self.client.table("threads").insert({
            "user_id": user_id, 
            "type": type, 
            "data": thread_data
        }).execute()
        
        if len(response.data) > 0 and "id" in response.data[0]:
            return str(response.data[0]["id"])
        return None
    
    def get_value_comparison_instances(self, user_id: str) -> List[Dict]:
        """Get value comparison instances for a user."""
        response = self.client.table("value_comparison_instances").select("*").eq("user_id", user_id).execute()
        return response.data
    
    def get_human_values(self) -> List[Dict]:
        """Get all human values."""
        response = self.client.table("human_values").select("*").execute()
        return response.data
    
    def add_value_comparison_instance(self, value_comp: Any, new_entry: Dict, superior_value_id: str, inferior_value_id: str) -> Optional[Dict]:
        """Add a value comparison instance."""
        new_value_comparison = {
            "user_id": new_entry["user_id"],
            "type": "entry",
            "superior_value_id": superior_value_id,
            "inferior_value_id": inferior_value_id,
            "reason": value_comp.reason,
            "entry_id": new_entry["id"],
            "data": {"entry_extract": value_comp.ref},
            "user_sentiment": 'undecided'
        }
        
        response = self.client.table("value_comparison_instances").insert(new_value_comparison).execute()
        if len(response.data) > 0:
            return response.data[0]
        return None
    
    def edit_value_comparison_instance(self, value_comparison_id: str, update_payload: Dict) -> Dict:
        """Edit a value comparison instance."""
        response = self.client.table("value_comparison_instances").update(update_payload).eq('id', value_comparison_id).execute()
        print("Value comparison updated successfully.")
        return response.data[0] if response.data else {}
    
    def get_value_comparison_from_entries(self, user_id: str) -> List[Dict]:
        """Get value comparisons associated with journal entries."""
        entries = self.client.table("journal_entries").select("id, date").eq("user_id", user_id).execute()
        entries_dict = {entry['id']: entry["date"] for entry in entries.data}
        value_comparison_instances = self.client.table("value_comparison_instances").select("*").eq('type', 'entry').execute()
        value_comparisons = []
        for instance in value_comparison_instances.data:
            entry_ids = list(entries_dict.keys())
            if instance['entry_id'] in entry_ids:
                instance['date'] = entries_dict[instance['entry_id']]
                value_comparisons.append(instance)
        
        value_comparisons.sort(key=lambda x: x['date'], reverse=True)
        return value_comparisons
    
    def get_value_comparison_from_threads(self, user_id: str) -> List[Dict]:
        """Get value comparisons associated with threads."""
        threads = self.client.table("threads").select("id, created_at").eq("user_id", user_id).execute()
        threads_dict = {thread['id']: thread["created_at"] for thread in threads.data}
        value_comparison_instances = self.client.table("value_comparison_instances").select("*").eq('type', 'thread').execute()
        value_comparisons = []
        for instance in value_comparison_instances.data:
            thread_ids = list(threads_dict.keys())
            if instance['thread_id'] in thread_ids:
                instance['created_at'] = threads_dict[instance['thread_id']]
                value_comparisons.append(instance)
        
        value_comparisons.sort(key=lambda x: x['created_at'], reverse=True)
        return value_comparisons
    
    def encrypt_journal(self, user_id: str):
        """Encrypt journal entries (generator for progress tracking)."""
        from cryptography.fernet import Fernet
        
        key = os.getenv("FERNET_KEY")
        if isinstance(key, str):
            key = key.encode()
        
        fernet = Fernet(key)
        journal_entries = self.get_entries(user_id)
        count = 0
        for journal_entry in journal_entries:
            self._encrypt_journal_entry(fernet, journal_entry)
            count += 1
            yield count / len(journal_entries)
    
    def _encrypt_journal_entry(self, fernet, journal_entry: Dict) -> Dict:
        """Encrypt a single journal entry."""
        entry_data = {
            "what_happened": fernet.encrypt(journal_entry["what_happened"].encode()),
        }
        
        response = self.client.table("journal_entries").update(entry_data).eq("id", journal_entry["id"]).execute()
        print("Journal entry updated successfully.")
        return response.data[0] if response.data else {}
    
    def delete_activities_by_entry(self, entry_id: str) -> int:
        """Delete all activities associated with a journal entry."""
        response = self.client.table("activities").delete().eq("entry_id", entry_id).execute()
        deleted_count = len(response.data) if response.data else 0
        print(f"Deleted {deleted_count} activities for entry {entry_id}")
        return deleted_count
    
    def delete_value_comparisons_by_entry(self, entry_id: str) -> int:
        """Delete all value comparisons associated with a journal entry."""
        response = self.client.table("value_comparison_instances").delete().eq("entry_id", entry_id).execute()
        deleted_count = len(response.data) if response.data else 0
        print(f"Deleted {deleted_count} value comparisons for entry {entry_id}")
        return deleted_count