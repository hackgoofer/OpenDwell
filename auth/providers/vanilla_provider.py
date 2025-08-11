import json
import os
from typing import Dict, Any, Optional
from ..base_provider import AuthProvider


class VanillaAuthProvider(AuthProvider):
    """A simple vanilla auth provider that reads user config from a file."""
    
    def __init__(self, config_file: str = "user_config.json"):
        self.config_file = config_file
    
    @property
    def provider_name(self) -> str:
        return "vanilla"
    
    def _load_user_config(self) -> Dict[str, Any]:
        """Load user configuration from file."""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                return json.load(f)
        return {
            "user_id": "vanilla_user",
            "first_name": "Anonymous",
            "last_name": "User",
            "email": "user@example.com",
            "bio": "I am a user of Dwell interested in personal development and journaling."
        }
    
    def get_user_bio(self) -> str:
        """Get user's bio from config."""
        config = self._load_user_config()
        return config.get("bio", "I am a user of Dwell.")
    
    def get_user_profile(self) -> str:
        """Get user's detailed profile from config."""
        config = self._load_user_config()
        
        # Try to read from user_profile_path if specified
        user_profile_path = config.get("user_profile_path")
        if user_profile_path and os.path.exists(user_profile_path):
            try:
                with open(user_profile_path, 'r') as f:
                    return f.read().strip()
            except Exception:
                pass
        
        # Fallback to bio
        return config.get("bio", "A user interested in personal development and journaling.")
    
    def show_login(self, st, **kwargs) -> Optional[Dict[str, Any]]:
        """Auto-login for vanilla mode - no UI needed."""
        user_config = self._load_user_config()
        session_data = {
            "user": {
                "id": user_config.get("user_id", "vanilla_user"),
                "email": user_config.get("email", "user@example.com"),
                "user_metadata": {
                    "first_name": user_config.get("first_name", "Anonymous"),
                    "last_name": user_config.get("last_name", "User")
                }
            },
            "expires_at": 9999999999  # Far future timestamp
        }
        return session_data
    
    def show_logout(self, st, **kwargs) -> Optional[Dict[str, Any]]:
        """Display a simple logout button."""
        if st.button("Logout", key="vanilla_logout"):
            return {"loggedOut": True}
        return None
    
    def is_user_logged_in(self, st) -> bool:
        """Check if user is logged in."""
        session_data = st.session_state.get('session_data', {})
        if session_data is None:
            return False
        return 'user' in session_data and 'id' in session_data['user']
    
    def is_access_token_valid(self, st) -> bool:
        """Check if access token is valid (always true for vanilla mode)."""
        return True
    
    def get_user_email(self, st) -> Optional[str]:
        """Get user email from session."""
        session_data = st.session_state.get('session_data', {})
        if session_data and 'user' in session_data:
            return session_data['user'].get('email')
        return None
    
    def should_restrict_content(self, st, user_email: str) -> bool:
        """Vanilla users never have content restricted."""
        return False
    
    def show_access_restriction(self, st, user_email: str):
        """This should never be called for vanilla users."""
        pass