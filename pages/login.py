import streamlit as st
from auth.session import SessionManager

def show_login_page():
    session_manager = SessionManager()
    
    st.title("Log ind")
    
    # Check if user is already logged in
    if session_manager.get_current_user():
        st.success("Du er allerede logget ind!")
        return

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
