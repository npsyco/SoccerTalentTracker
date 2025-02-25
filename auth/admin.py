import streamlit as st
from .database import AuthDB
from .session import SessionManager
import psycopg2
from psycopg2.extras import DictCursor
from typing import List, Dict
from passlib.context import CryptContext
import os

# Password hashing configuration
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_initial_admin():
    """Create or update admin user with environment credentials"""
    auth_db = AuthDB()

    try:
        with psycopg2.connect(auth_db.conn_string) as conn:
            with conn.cursor() as cur:
                # Get admin credentials from environment variables
                admin_username = os.environ.get('ADMIN_USERNAME')
                admin_password = os.environ.get('ADMIN_PASSWORD')
                admin_email = os.environ.get('ADMIN_EMAIL')

                if not all([admin_username, admin_password, admin_email]):
                    return

                # Get admin role ID
                cur.execute("SELECT id FROM roles WHERE name = 'admin'")
                admin_role = cur.fetchone()
                if not admin_role:
                    return
                admin_role_id = admin_role[0]

                # Create password hash
                password_hash = pwd_context.hash(admin_password)

                # Check if admin user exists
                cur.execute("""
                    SELECT u.id FROM users u
                    JOIN roles r ON u.role_id = r.id
                    WHERE r.name = 'admin'
                """)
                admin_exists = cur.fetchone()

                if admin_exists:
                    # Update existing admin
                    cur.execute("""
                        UPDATE users 
                        SET username = %s, 
                            password_hash = %s, 
                            email = %s, 
                            status = 'active'
                        WHERE id = %s
                    """, (admin_username, password_hash, admin_email, admin_exists[0]))
                else:
                    # Create new admin user
                    cur.execute("""
                        INSERT INTO users 
                        (username, password_hash, email, role_id, status)
                        VALUES (%s, %s, %s, %s, 'active')
                    """, (admin_username, password_hash, admin_email, admin_role_id))

                conn.commit()

    except Exception as e:
        print(f"Error setting up admin user: {str(e)}")

def show_user_management():
    """Show user management interface for admins"""
    session_manager = SessionManager()

    # Only allow admins
    if not session_manager.require_role(['admin']):
        return

    st.title("Brugeradministration")

    # Initialize AuthDB
    auth_db = AuthDB()

    # Tabs for different admin functions
    tab1, tab2, tab3 = st.tabs(["Brugere", "Godkendelser", "Brugeradgang"])

    with tab1:
        # Get list of all active users
        users = get_all_users(auth_db)

        # Show existing users in a table
        if users:
            st.subheader("Eksisterende Brugere")

            # Convert users to DataFrame for display
            user_data = []
            for user in users:
                # Convert role names to Danish
                role_name = {
                    'coach': 'Træner',
                    'assistant_coach': 'Assistent',
                    'observer': 'Tilskuer',
                    'admin': 'Administrator'
                }.get(user["role_name"], user["role_name"])

                user_data.append({
                    "Brugernavn": user["username"],
                    "Email": user["email"],
                    "Rolle": role_name,
                    "Oprettet": user["created_at"].strftime("%Y-%m-%d %H:%M") if user["created_at"] else "N/A"
                })

            st.dataframe(user_data)

        st.markdown("---")

        # Create new user form
        with st.form("create_user", clear_on_submit=True):
            st.subheader("Opret ny bruger")

            username = st.text_input("Brugernavn")
            email = st.text_input("Email")
            password = st.text_input("Adgangskode", type="password")
            role = st.selectbox(
                "Rolle",
                ["Træner", "Assistent", "Tilskuer"],
                format_func=lambda x: x
            )

            # Convert Danish role names back to database values
            role_map = {
                "Træner": "coach",
                "Assistent": "assistant_coach",
                "Tilskuer": "observer"
            }

            if st.form_submit_button("Opret bruger"):
                if auth_db.create_user(username, password, email, role_map[role]):
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
                            ["Træner", "Assistent", "Tilskuer"]
                        )

                        if st.form_submit_button("Opdater"):
                            if update_user(auth_db, selected_user, new_email, new_password, role_map[new_role]):
                                st.success("Bruger opdateret!")
                                st.rerun()
                            else:
                                st.error("Kunne ikke opdatere bruger")

                with col2:
                    # Delete user section
                    st.subheader("Slet Bruger")
                    delete_btn = st.button("Slet Bruger")

                    if delete_btn:
                        confirm_col1, confirm_col2 = st.columns(2)
                        with confirm_col1:
                            st.warning(f"Er du sikker på, at du vil slette brugeren '{selected_user}'?")
                        with confirm_col2:
                            if st.button("Ja, slet bruger"):
                                if delete_user(auth_db, selected_user):
                                    st.success("Bruger slettet!")
                                    st.rerun()
                                else:
                                    st.error("Kunne ikke slette bruger")

    with tab2:
        # Pending Users Approval
        st.subheader("Ventende Godkendelser")
        pending_users = auth_db.get_pending_users()

        if pending_users:
            for user in pending_users:
                with st.container():
                    col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
                    with col1:
                        st.write(f"**{user['username']}**")
                        st.write(f"Email: {user['email']}")
                    with col2:
                        st.write(f"Rolle: {role_map.get(user['role_name'], user['role_name'])}")
                        st.write(f"Registreret: {user['created_at'].strftime('%Y-%m-%d %H:%M')}")
                    with col3:
                        if st.button("Godkend", key=f"approve_{user['username']}"):
                            if auth_db.approve_user(user['username']):
                                st.success("Bruger godkendt!")
                                st.rerun()
                    with col4:
                        if st.button("Afvis", key=f"reject_{user['username']}"):
                            if auth_db.reject_user(user['username']):
                                st.success("Bruger afvist!")
                                st.rerun()
                    st.markdown("---")
        else:
            st.info("Ingen ventende godkendelser")

    with tab3:
        # User Impersonation
        st.subheader("Brugeradgang")
        st.write("Vælg en bruger for at se og administrere deres data:")

        non_admin_users = [user for user in users if user["role_name"] != "admin"]
        if non_admin_users:
            selected_user = st.selectbox(
                "Vælg bruger at administrere",
                options=[user["username"] for user in non_admin_users]
            )

            col1, col2 = st.columns(2)
            with col1:
                if st.button("Skift til bruger"):
                    # Store the impersonated user in session state
                    st.session_state.impersonated_user = selected_user
                    st.success(f"Du administrerer nu {selected_user}'s data")
                    st.rerun()

            with col2:
                if st.button("Generer testdata"):
                    from data_manager import DataManager
                    dm = DataManager()
                    dm.reset_data()  # Clear existing data
                    dm.generate_test_data(selected_user)  # Generate new test data
                    st.success(f"Testdata genereret for {selected_user}")
                    st.rerun()

        else:
            st.info("Ingen brugere at administrere")

        # Show current impersonation status
        if "impersonated_user" in st.session_state:
            st.write(f"Du administrerer: **{st.session_state.impersonated_user}**")
            if st.button("Afslut administration"):
                del st.session_state.impersonated_user
                st.rerun()

def get_all_users(auth_db: AuthDB) -> List[Dict]:
    """Get all users with their roles"""
    try:
        with psycopg2.connect(auth_db.conn_string) as conn:
            with conn.cursor(cursor_factory=DictCursor) as cur:
                cur.execute("""
                    SELECT u.username, u.email, u.created_at, r.name as role_name
                    FROM users u
                    JOIN roles r ON u.role_id = r.id
                    WHERE u.status = 'active'
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
                    password_hash = pwd_context.hash(password)
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