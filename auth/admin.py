import streamlit as st
from .database import AuthDB
from .session import SessionManager
import psycopg2

def show_user_management():
    """Show user management interface for admins"""
    session_manager = SessionManager()

    # Only allow admins
    if not session_manager.require_role(['admin']):
        return

    st.title("Brugeradministration")

    # Create new user form
    with st.form("create_user"):
        st.subheader("Opret ny bruger")

        username = st.text_input("Brugernavn")
        email = st.text_input("Email")
        password = st.text_input("Adgangskode", type="password")
        role = st.selectbox(
            "Rolle",
            ["coach", "assistant_coach", "observer"]
        )

        if st.form_submit_button("Opret bruger"):
            auth_db = AuthDB()
            if auth_db.create_user(username, password, email, role):
                st.success("Bruger oprettet!")
            else:
                st.error("Kunne ikke oprette bruger. Prøv et andet brugernavn eller email.")

def create_initial_admin():
    """Create initial admin user if no users exist"""
    auth_db = AuthDB()

    try:
        # Check if admin user exists
        with psycopg2.connect(auth_db.conn_string) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM users")
                user_count = cur.fetchone()[0]

                if user_count == 0:
                    # Create admin user
                    success = auth_db.create_user(
                        username="admin",
                        password="admin",
                        email="admin@example.com",
                        role="admin"
                    )

                    if success:
                        st.warning("""
                            Initial admin user created with these credentials:
                            Username: admin
                            Password: admin
                            Please log in and change the password immediately!
                        """)
                    else:
                        st.error("Failed to create initial admin user")
    except Exception as e:
        st.error(f"Error creating initial admin: {str(e)}")