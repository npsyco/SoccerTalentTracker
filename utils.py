import streamlit as st

def initialize_session_state():
    """Initialize session state variables"""
    if 'players' not in st.session_state:
        st.session_state.players = []
    
    if 'matches' not in st.session_state:
        st.session_state.matches = []
