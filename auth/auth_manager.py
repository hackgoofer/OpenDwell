import os
from typing import Dict, Any, Optional
from .base_provider import AuthProvider
from .providers import VanillaAuthProvider


class AuthManager:
    """Manages authentication providers and provides a unified interface."""

    def __init__(self, provider_name: str = None):
        """Initialize with specified provider or default to vanilla."""
        if provider_name is None:
            provider_name = os.getenv("AUTH_PROVIDER", "vanilla")

        self.provider = self._create_provider(provider_name)

    def _create_provider(self, provider_name: str) -> AuthProvider:
        """Create and return the specified auth provider."""
        if provider_name == "vanilla":
            return VanillaAuthProvider()
        elif provider_name == "streamlit_auth_ui":
            from .providers.streamlit_auth_provider import StreamlitAuthProvider
            return StreamlitAuthProvider()
        else:
            raise ValueError(f"Unknown auth provider: {provider_name}")

    def show_login(self, st, **kwargs) -> Optional[Dict[str, Any]]:
        """Display login UI using the configured provider."""
        return self.provider.show_login(st, **kwargs)

    def show_logout(self, st, **kwargs) -> Optional[Dict[str, Any]]:
        """Display logout UI using the configured provider."""
        return self.provider.show_logout(st, **kwargs)

    def is_user_logged_in(self, st) -> bool:
        """Check if user is logged in using the configured provider."""
        return self.provider.is_user_logged_in(st)

    def is_access_token_valid(self, st) -> bool:
        """Check if access token is valid using the configured provider."""
        return self.provider.is_access_token_valid(st)

    def get_user_email(self, st) -> Optional[str]:
        """Get user email using the configured provider."""
        return self.provider.get_user_email(st)

    def is_user_valid(self, st) -> tuple[bool, Optional[str]]:
        """Check if user is valid and return email."""
        # For vanilla auth, auto-login if no session exists
        if self.provider.provider_name == "vanilla" and not st.session_state.get('session_data'):
            session_data = self.provider.show_login(st)
            if session_data:
                st.session_state["session_data"] = session_data
        
        valid_user = self.is_user_logged_in(st) and self.is_access_token_valid(st)
        email = None
        if valid_user:
            email = self.get_user_email(st)
        return valid_user, email
    
    def should_restrict_content(self, st, user_email: str) -> bool:
        """Check if content should be restricted for this user."""
        return self.provider.should_restrict_content(st, user_email)
    
    def show_access_restriction(self, st, user_email: str):
        """Show access restriction message/UI when content is blocked."""
        return self.provider.show_access_restriction(st, user_email)
    
    def is_user_subscriber(self, st, user_email: str) -> bool:
        """Check if user has access (not restricted) - legacy method name."""
        return not self.should_restrict_content(st, user_email)
