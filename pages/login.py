import streamlit as st
from auth.session import SessionManager

def show_login_page():
    # Hide sidebar and set minimal layout
    st.set_page_config(
        page_title="Sorø-Freja Login",
        layout="centered",
        initial_sidebar_state="collapsed"
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
                    st.rerun()
                else:
                    st.error("Ugyldigt brugernavn eller adgangskode")

def show_logout_button():
    session_manager = SessionManager()
    if st.sidebar.button("Log ud"):
        session_manager.logout_user()
        st.rerun()