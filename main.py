import streamlit as st
import pandas as pd
from data_manager import DataManager
from visualizations import Visualizer
from utils import initialize_session_state
from auth.session import SessionManager
from auth.database import AuthDB
from auth.admin import create_initial_admin, show_user_management
from auth.login import show_login_page, show_logout_button
from datetime import datetime

# Must be the first Streamlit command
st.set_page_config(
    page_title="Sorø-Freja Spiller Udviklingsværktøj",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Keep only essential navigation hiding
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        footer {visibility: hidden;}
        section[data-testid="stSidebarNav"] {display: none;}
        div[data-testid="stSidebarNavItems"] {display: none;}
        div[data-testid="stToolbar"] {display: none;}

        /* Only keep warning styling */
        .impersonation-warning {
            background-color: #ff4444;
            color: white;
            border-radius: 4px;
            padding: 8px;
            margin-bottom: 10px;
            text-align: center;
        }
    </style>
""", unsafe_allow_html=True)

def get_current_user_id():
    """Helper function to safely get current user ID"""
    if "impersonated_user_id" in st.session_state:
        return st.session_state.impersonated_user_id
    elif "user" in st.session_state and st.session_state.user and "id" in st.session_state.user:
        return st.session_state.user["id"]
    return None

def get_player_best_stat(player_name, user_id):
    """Get the best recent performance stat for a player"""
    dm = DataManager()
    performance = dm.get_player_performance(player_name, user_id=user_id)
    if performance.empty:
        return None, None

    # Get most recent performance
    latest = performance.iloc[-1]
    categories = ['Boldholder', 'Medspiller', 'Presspiller', 'Støttespiller']
    best_stat = max(categories, key=lambda x: latest[x])
    return best_stat, latest[best_stat]

def main():
    try:
        initialize_session_state()
        session_manager = SessionManager()
        create_initial_admin()
    except Exception:
        handle_streamlit_error()
        st.stop()

    # Get current user ID safely
    current_user_id = get_current_user_id()

    # Show login page if user is not logged in
    if not session_manager.get_current_user():
        show_login_page()
        return

    # Initialize data manager
    dm = DataManager()

    # Create top navigation bar with account info
    _, _, account_col = st.columns([1, 2, 1])
    with account_col:
        # Show impersonation warning if applicable
        if ("impersonated_user" in st.session_state and 
            st.session_state.user['role'] == 'admin' and 
            st.session_state.user['username'] != st.session_state.impersonated_user):
            st.markdown(
                f"""
                <div class="impersonation-warning">
                    ⚠️ Administrerer bruger: {st.session_state.impersonated_user}
                </div>
                """,
                unsafe_allow_html=True
            )
        st.markdown(
            f"""
            <div style="text-align: right;">
                <span style="margin-right: 10px;">Logget ind som: {st.session_state.user['username']}</span>
            </div>
            """,
            unsafe_allow_html=True
        )
        show_logout_button()

    st.title("Sorø-Freja Spiller Udviklingsværktøj")

    # Show navigation and content based on page state
    if st.session_state.page == "Spillere":
        st.header("Spillere")

        # Create two columns with custom widths
        col1, col2 = st.columns([1, 2])

        with col1:
            with st.form("add_player", clear_on_submit=True):
                st.subheader("Tilføj spiller")
                player_name = st.text_input("Spiller navn")

                if st.form_submit_button("Tilføj Spiller"):
                    if player_name:
                        current_players = dm.get_players(current_user_id)
                        if not current_players.empty and player_name in current_players['Name'].values:
                            st.error(f"Spiller '{player_name}' findes allerede")
                        else:
                            if dm.add_player(player_name, "Not specified", current_user_id):
                                st.success(f"Spiller tilføjet: {player_name}")
                                st.rerun()
                            else:
                                st.error(f"Spiller '{player_name}' findes allerede")
                    else:
                        st.error("Indtast venligst et spillernavn")

        with col2:
            st.subheader("Aktive Spillere")
            players_df = dm.get_players(current_user_id)

            if not players_df.empty:
                for _, player in players_df.iterrows():
                    best_stat, stat_value = get_player_best_stat(player['Name'], current_user_id)
                    cols = st.columns([3, 1])
                    with cols[0]:
                        if best_stat:
                            st.write(f"**{player['Name']}** - Bedste rolle: {best_stat}")
                        else:
                            st.write(f"**{player['Name']}**")
                    with cols[1]:
                        if st.button("🗑️", key=f"delete_{player['Name']}", help="Slet spiller"):
                            if dm.delete_player(player['Name'], current_user_id):
                                st.success(f"Spiller slettet: {player['Name']}")
                                st.rerun()
            else:
                st.info("Ingen spillere fundet")

if __name__ == "__main__":
    main()