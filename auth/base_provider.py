from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List


class AuthProvider(ABC):
    """Abstract base class for authentication providers."""
    
    @abstractmethod
    def show_login(self, st, **kwargs) -> Optional[Dict[str, Any]]:
        """Display login UI and return session data if authenticated."""
        pass
    
    @abstractmethod
    def show_logout(self, st, **kwargs) -> Optional[Dict[str, Any]]:
        """Display logout UI and return logout result."""
        pass
    
    @abstractmethod
    def is_user_logged_in(self, st) -> bool:
        """Check if user is currently logged in."""
        pass
    
    @abstractmethod
    def is_access_token_valid(self, st) -> bool:
        """Check if the access token is still valid."""
        pass
    
    @abstractmethod
    def get_user_email(self, st) -> Optional[str]:
        """Get the current user's email if logged in."""
        pass
    
    @abstractmethod
    def should_restrict_content(self, st, user_email: str) -> bool:
        """Check if content should be restricted for this user."""
        pass
    
    @abstractmethod
    def show_access_restriction(self, st, user_email: str):
        """Show access restriction message/UI when content is blocked."""
        pass
    
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the name of this auth provider."""
        pass