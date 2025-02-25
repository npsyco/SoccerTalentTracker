import streamlit as st
from .database import AuthDB
from .session import SessionManager
import psycopg2
from typing import List, Dict

def show_user_management():
    """Show user management interface for admins"""
    session_manager = SessionManager()

    # Only allow admins
    if not session_manager.require_role(['admin']):
        return

    st.title("Brugeradministration")

    # Initialize AuthDB
    auth_db = AuthDB()

    # Get list of all users
    users = get_all_users(auth_db)

    # Show existing users in a table
    if users:
        st.subheader("Eksisterende Brugere")

        # Convert users to DataFrame for display
        user_data = []
        for user in users:
            user_data.append({
                "Brugernavn": user["username"],
                "Email": user["email"],
                "Rolle": user["role_name"],
                "Oprettet": user["created_at"].strftime("%Y-%m-%d %H:%M") if user["created_at"] else "N/A"
            })

        st.dataframe(user_data)

    st.markdown("---")

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
            if auth_db.create_user(username, password, email, role):
                st.success("Bruger oprettet!")
                st.rerun()
            else:
                st.error("Kunne ikke oprette bruger. Prøv et andet brugernavn eller email.")

    st.markdown("---")

    # Update/Delete user section
    if users:
        st.subheader("Opdater eller Slet Bruger")

        # Select user to modify
        usernames = [user["username"] for user in users if user["role_name"] != "admin"]
        if usernames:
            selected_user = st.selectbox("Vælg bruger", usernames)

            col1, col2 = st.columns(2)

            with col1:
                # Update user form
                with st.form("update_user"):
                    st.subheader("Opdater Bruger")

                    new_email = st.text_input("Ny Email")
                    new_password = st.text_input("Ny Adgangskode", type="password")
                    new_role = st.selectbox(
                        "Ny Rolle",
                        ["coach", "assistant_coach", "observer"]
                    )

                    if st.form_submit_button("Opdater"):
                        if update_user(auth_db, selected_user, new_email, new_password, new_role):
                            st.success("Bruger opdateret!")
                            st.rerun()
                        else:
                            st.error("Kunne ikke opdatere bruger")

            with col2:
                # Delete user
                with st.form("delete_user"):
                    st.subheader("Slet Bruger")
                    st.warning(f"Er du sikker på, at du vil slette brugeren '{selected_user}'?")

                    if st.form_submit_button("Slet Bruger"):
                        if delete_user(auth_db, selected_user):
                            st.success("Bruger slettet!")
                            st.rerun()
                        else:
                            st.error("Kunne ikke slette bruger")

def get_all_users(auth_db: AuthDB) -> List[Dict]:
    """Get all users with their roles"""
    try:
        with psycopg2.connect(auth_db.conn_string) as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                cur.execute("""
                    SELECT u.username, u.email, u.created_at, r.name as role_name
                    FROM users u
                    JOIN roles r ON u.role_id = r.id
                    ORDER BY u.created_at DESC
                """)
                return [dict(row) for row in cur.fetchall()]
    except psycopg2.Error:
        st.error("Kunne ikke hente brugerliste")
        return []

def update_user(auth_db: AuthDB, username: str, email: str, password: str, role: str) -> bool:
    """Update user details"""
    try:
        with psycopg2.connect(auth_db.conn_string) as conn:
            with conn.cursor() as cur:
                # Get role ID
                cur.execute("SELECT id FROM roles WHERE name = %s", (role,))
                role_id = cur.fetchone()
                if not role_id:
                    return False

                # Update user
                if password:
                    password_hash = auth_db.pwd_context.hash(password)
                    cur.execute("""
                        UPDATE users 
                        SET email = %s, password_hash = %s, role_id = %s
                        WHERE username = %s
                    """, (email, password_hash, role_id[0], username))
                else:
                    cur.execute("""
                        UPDATE users 
                        SET email = %s, role_id = %s
                        WHERE username = %s
                    """, (email, role_id[0], username))

                conn.commit()
                return True
    except psycopg2.Error:
        return False

def delete_user(auth_db: AuthDB, username: str) -> bool:
    """Delete a user"""
    try:
        with psycopg2.connect(auth_db.conn_string) as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM users WHERE username = %s AND username != 'admin'", (username,))
                conn.commit()
                return True
    except psycopg2.Error:
        return False

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

                    # Create a test coach user
                    auth_db.create_user(
                        username="test_coach",
                        password="test123",
                        email="coach@test.com",
                        role="coach"
                    )
                else:
                    st.error("Failed to create initial admin user")
    except Exception as e:
        st.error(f"Error creating initial admin: {str(e)}")