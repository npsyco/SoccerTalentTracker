import streamlit as st
from auth.session import SessionManager
from auth.database import AuthDB

def show_login_page():
    """Show login page with registration option"""
    # Only style the logout button
    st.markdown(
        """
        <style>
            button[kind="secondary"] {
                float: right;
                margin-right: 10px;
            }
        </style>
        """,
        unsafe_allow_html=True
    )

    session_manager = SessionManager()

    # Check if user is already logged in
    if session_manager.get_current_user():
        st.success("Du er allerede logget ind!")
        return

    # Center the login form
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        # App title
        st.title("Sorø-Freja")
        st.subheader("Spiller Udviklingsværktøj")
        st.markdown("---")

        # Login form
        with st.form("login_form"):
            username = st.text_input("Brugernavn")
            password = st.text_input("Adgangskode", type="password")

            if st.form_submit_button("Log ind"):
                if session_manager.login_user(username, password):
                    st.success("Log ind succesfuld!")
                    # Clear any existing impersonation data
                    if "impersonated_user" in st.session_state:
                        del st.session_state.impersonated_user
                    if "impersonated_user_id" in st.session_state:
                        del st.session_state.impersonated_user_id
                    st.rerun()
                else:
                    st.error("Ugyldigt brugernavn eller adgangskode")

        # Registration section with expander
        st.markdown("---")
        with st.expander("🆕 Ny bruger? Klik her for at registrere"):
            # Registration form
            with st.form("registration_form"):
                new_username = st.text_input("Vælg brugernavn")
                new_email = st.text_input("Email")
                new_password = st.text_input("Vælg adgangskode", type="password")
                role = st.selectbox(
                    "Vælg rolle",
                    ["Træner", "Assistent", "Tilskuer"]
                )

                # Map Danish roles to database roles
                role_map = {
                    "Træner": "coach",
                    "Assistent": "assistant_coach",
                    "Tilskuer": "observer"
                }

                if st.form_submit_button("Registrer"):
                    auth_db = AuthDB()
                    if auth_db.register_user(new_username, new_password, new_email, role_map[role]):
                        st.success("Registrering gennemført! Vent venligst på administrator godkendelse.")
                    else:
                        st.error("Kunne ikke oprette bruger. Brugernavn eller email er måske allerede i brug.")

def show_logout_button():
    session_manager = SessionManager()
    if st.button("Log ud", key="logout_button", type="secondary"):
        # Clear any existing impersonation data
        if "impersonated_user" in st.session_state:
            del st.session_state.impersonated_user
        if "impersonated_user_id" in st.session_state:
            del st.session_state.impersonated_user_id
        session_manager.logout_user()
        st.rerun()