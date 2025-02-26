import streamlit as st
from typing import Optional
from .database import AuthDB

class SessionManager:
    def __init__(self):
        self.auth_db = AuthDB()

    def login_user(self, username: str, password: str) -> bool:
        """Log in a user and store their session"""
        user = self.auth_db.verify_user(username, password)
        if user:
            # Create access token
            token = self.auth_db.create_access_token({
                "sub": user["username"],
                "role": user["role_name"]
            })

            # Store in session state, including user ID
            st.session_state.user = {
                "id": user["id"],
                "username": user["username"],
                "role": user["role_name"],
                "token": token
            }
            return True
        return False

    def logout_user(self):
        """Log out the current user"""
        if "user" in st.session_state:
            del st.session_state.user

    def get_current_user(self) -> Optional[dict]:
        """Get the current logged-in user's information"""
        if "user" in st.session_state:
            token = st.session_state.user.get("token")
            if token:
                payload = self.auth_db.verify_token(token)
                if payload:
                    return st.session_state.user
                # Token expired, log out user
                self.logout_user()
        return None

    def require_login(self) -> bool:
        """Check if user is logged in, redirect to login if not"""
        user = self.get_current_user()
        if not user:
            st.warning("Please log in to access this page")
            return False
        return True

    def require_role(self, allowed_roles: list) -> bool:
        """Check if user has required role"""
        user = self.get_current_user()
        if not user:
            st.warning("Please log in to access this page")
            return False
        if user["role"] not in allowed_roles:
            st.error("You don't have permission to access this page")
            return False
        return True