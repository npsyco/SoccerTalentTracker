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

def handle_streamlit_error():
    """Global error handler for unhandled exceptions"""
    import sys
    import traceback

    exc_type, exc_value, exc_tb = sys.exc_info()

    if exc_type is not None:
        error_details = ''.join(traceback.format_exception(exc_type, exc_value, exc_tb))
        st.error("Der opstod en fejl. Kontakt venligst systemadministrator.")

        if st.session_state.user and st.session_state.user.get('role') == 'admin':
            with st.expander("Tekniske detaljer"):
                st.code(error_details)

# Must be the first Streamlit command
st.set_page_config(
    page_title="Sorø-Freja Spiller Udviklingsværktøj",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Performance optimizations and styling
st.markdown("""
    <style>
        /* Hide main menu and navigation */
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        footer {visibility: hidden;}

        /* Hide navigation bar */
        section[data-testid="stSidebarNav"] {display: none;}
        div[data-testid="stSidebarNavItems"] {display: none;}
        .css-1d391kg {display: none;}

        /* Hide toolbar */
        div[data-testid="stToolbar"] {display: none;}

        /* Sorø-Freja Theme Colors */
        :root {
            --primary-color: #003087;
            --secondary-color: #0046c7;
            --text-color: #333333;
            --background-light: #f5f7fa;
            --border-color: #e1e4e8;
        }

        /* Base styles */
        .stButton > button {
            background-color: var(--primary-color) !important;
            color: white !important;
            border: none !important;
            border-radius: 4px !important;
            transition: all 0.1s ease-in-out !important;
        }

        .stButton > button:hover {
            background-color: var(--secondary-color) !important;
        }

        /* Player Card Styles */
        .player-card {
            background: white;
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 16px;
            margin: 8px 0;
            display: flex;
            justify-content: space-between;
            align-items: center;
            transition: all 0.1s ease-in-out;
        }

        .player-card:hover {
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }

        .player-name {
            font-size: 16px;
            color: var(--text-color);
            margin: 0;
        }

        .delete-button {
            color: #dc3545;
            background: none;
            border: none;
            cursor: pointer;
            padding: 4px 8px;
            font-size: 14px;
            transition: all 0.1s ease-in-out;
        }

        .delete-button:hover {
            color: #bd2130;
        }

        /* Form Styling */
        .stTextInput > div > div > input {
            border-radius: 4px !important;
            border-color: var(--border-color) !important;
        }

        /* Existing optimizations remain unchanged */
        div.stButton > button:first-child {
            transition: all 0.1s ease-in-out !important;
        }

        .element-container {
            transition: height 0.1s ease-in-out !important;
        }

        .stSpinner > div {
            animation-duration: 0.5s !important;
        }

        * {
            transition-duration: 0.1s !important;
        }

        /* Admin impersonation warning */
        .impersonation-warning {
            background-color: #ffebee;
            border: 1px solid #ef5350;
            border-radius: 4px;
            padding: 8px;
            margin-bottom: 10px;
            color: #c62828;
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

def main():
    # Initialize session state
    try:
        initialize_session_state()
        session_manager = SessionManager()
        create_initial_admin()
    except Exception:
        handle_streamlit_error()
        st.stop()

    # Show login page if user is not logged in
    if not session_manager.get_current_user():
        show_login_page()
        return

    # Initialize data manager and visualizer
    dm = DataManager()
    viz = Visualizer()

    # Get current user ID safely
    current_user_id = get_current_user_id()
    if not current_user_id:
        st.error("Bruger ID ikke fundet. Log venligst ud og ind igen.")
        show_logout_button()
        return

    # Create top navigation bar with account info
    _, _, account_col = st.columns([1, 2, 1])
    with account_col:
        # Show impersonation warning only when admin is actually impersonating
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

    # Show navigation and content
    with st.sidebar:
        # For admin users, show admin panel option
        if st.session_state.user['role'] == 'admin':
            if st.button("🔧 Administration", use_container_width=True):
                st.session_state.page = "Admin"
                st.rerun()

        st.markdown("---")

        # Simplified navigation - buttons with equal width
        if st.button("👥 Spillere", key="nav_players", use_container_width=True):
            st.session_state.page = "Spillere"
            st.rerun()
        if st.button("📊 Kampdata", key="nav_matches", use_container_width=True):
            st.session_state.page = "Kampdata"
            st.rerun()
        if st.button("📈 Udviklingsanalyse", key="nav_analysis", use_container_width=True):
            st.session_state.page = "Udviklingsanalyse"
            st.rerun()

    # Initialize page state if not set
    if 'page' not in st.session_state:
        st.session_state.page = "Spillere"

    # Show selected page content
    if st.session_state.page == "Admin" and st.session_state.user['role'] == 'admin':
        show_user_management()
    elif st.session_state.page == "Spillere":
        # Require coach or admin role
        if not session_manager.require_role(['admin', 'coach']):
            return

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
                # Display players as cards
                for _, player in players_df.iterrows():
                    # Create a container for each player card
                    with st.container():
                        st.markdown(f"""
                            <div class="player-card">
                                <span class="player-name">{player['Name']}</span>
                                <button class="delete-button" onclick="handle_delete('{player['Name']}')">
                                    🗑️ Slet
                                </button>
                            </div>
                        """, unsafe_allow_html=True)

                        # Hidden delete confirmation
                        if st.button(f"Slet {player['Name']}", key=f"delete_{player['Name']}", type="secondary"):
                            st.warning(f"Er du sikker på at du vil slette spilleren '{player['Name']}'?")
                            col1, col2 = st.columns(2)
                            with col1:
                                if st.button("Ja, slet spiller", key=f"confirm_{player['Name']}"):
                                    if dm.delete_player(player['Name'], current_user_id):
                                        st.success(f"Spiller slettet: {player['Name']}")
                                        st.rerun()
                            with col2:
                                if st.button("Nej, behold spiller", key=f"cancel_{player['Name']}"):
                                    st.rerun()
            else:
                st.info("Ingen spillere fundet")

    elif st.session_state.page == "Kampdata":
        # Require coach or assistant_coach role
        if not session_manager.require_role(['admin', 'coach', 'assistant_coach']):
            return

        st.header("Kampe")

        # Initialize session state for match recording
        if 'match_step' not in st.session_state:
            st.session_state.match_step = 1
        if 'selected_players' not in st.session_state:
            st.session_state.selected_players = []
        if 'match_date' not in st.session_state:
            st.session_state.match_date = None
        if 'match_time' not in st.session_state:
            st.session_state.match_time = None
        if 'opponent' not in st.session_state:
            st.session_state.opponent = None

        # Step 1: Select match details and players
        if st.session_state.match_step == 1:
            with st.form("select_players"):
                st.subheader("Vælg kampdetaljer og spillere")

                match_date = st.date_input("Dato")
                match_time = st.time_input("Tidspunkt")
                opponent = st.text_input("Modstander (valgfrit)")

                # Pass current_user_id when getting players
                players_df = dm.get_players(current_user_id)
                if not players_df.empty:
                    st.subheader("Vælg spillere der deltog i kampen")

                    # Create checkboxes for player selection
                    selected_players = {}
                    cols = st.columns(3)  # Display checkboxes in 3 columns
                    for idx, player in players_df.iterrows():
                        col_idx = idx % 3
                        with cols[col_idx]:
                            # Pre-select players that were previously selected
                            default_value = player['Name'] in st.session_state.selected_players
                            selected_players[player['Name']] = st.checkbox(player['Name'], value=default_value)

                    if st.form_submit_button("Fortsæt til vurdering"):
                        selected_players_list = [name for name, selected in selected_players.items() if selected]
                        if len(selected_players_list) > 0:
                            st.session_state.selected_players = selected_players_list
                            st.session_state.match_date = match_date
                            st.session_state.match_time = match_time
                            st.session_state.opponent = opponent
                            st.session_state.match_step = 2
                            st.rerun()
                        else:
                            st.error("Vælg mindst én spiller")

        # Step 2: Enter ratings for selected players
        elif st.session_state.match_step == 2:
            with st.form("player_ratings"):
                st.subheader("Spillervurdering")
                st.write(f"Dato: {st.session_state.match_date}")
                st.write(f"Tidspunkt: {st.session_state.match_time}")
                st.write(f"Modstander: {st.session_state.opponent or 'Ikke angivet'}")

                categories = ["Boldholder", "Medspiller", "Presspiller", "Støttespiller"]
                ratings = {}

                # Show ratings input for selected players
                for player_name in st.session_state.selected_players:
                    st.write(f"### {player_name}")
                    cols = st.columns(4)

                    for i, category in enumerate(categories):
                        with cols[i]:
                            ratings[f"{player_name}_{category}"] = st.selectbox(
                                f"{category}",
                                ["A", "B", "C", "D"],
                                key=f"{player_name}_{category}"
                            )

                col1, col2 = st.columns([1, 5])
                with col1:
                    if st.form_submit_button("Tilbage"):
                        st.session_state.match_step = 1
                        # Keep the selected players in session state
                        st.rerun()

                with col2:
                    if st.form_submit_button("Gem Kampdata"):
                        # Prepare player ratings
                        player_ratings = {}
                        for category in categories:
                            player_ratings[category] = {
                                player_name: ratings[f"{player_name}_{category}"]
                                for player_name in st.session_state.selected_players
                            }

                        # Save match record with date and time
                        #Pass current_user_id when getting players
                        players_df = dm.get_players(current_user_id)
                        selected_players_df = players_df[players_df['Name'].isin(st.session_state.selected_players)]
                        dm.add_match_record(
                            st.session_state.match_date,
                            st.session_state.match_time,
                            st.session_state.opponent or "Ikke angivet",
                            selected_players_df,
                            player_ratings,
                            current_user_id
                        )

                        # Reset state and show success message
                        st.session_state.match_step = 1
                        st.session_state.selected_players = []
                        st.session_state.match_date = None
                        st.session_state.match_time = None
                        st.session_state.opponent = None
                        st.success("Kampdata gemt!")
                        st.rerun()

    elif st.session_state.page == "Udviklingsanalyse":
        # All roles can view analysis
        if not session_manager.require_login():
            return

        st.header("Udviklingsanalyse")

        # Add date range filtering
        col1, col2 = st.columns([1, 2])
        with col1:
            analysis_type = st.radio(
                "Vælg analysetype",
                ["Individuel Spilleranalyse", "Holdanalyse", "Spillersammenligning"]
            )

        with col2:
            # Get available seasons
            available_seasons = dm.get_available_seasons(current_user_id)
            if available_seasons:
                selected_season = st.selectbox(
                    "Vælg sæson",
                    ["Alle sæsoner"] + [str(year) for year in available_seasons]
                )

                # Set date range based on selected season
                if selected_season != "Alle sæsoner":
                    year = int(selected_season)
                    start_date = f"{year}-01-01"
                    end_date = f"{year}-12-31"
                else:
                    start_date = None
                    end_date = None
            else:
                st.info("Ingen kampdata tilgængelig")
                start_date = None
                end_date = None

        if analysis_type == "Individuel Spilleranalyse":
            # Pass current_user_id when getting players
            players_df = dm.get_players(current_user_id)
            if not players_df.empty:
                player = st.selectbox("Vælg Spiller", players_df['Name'].tolist())
                category = st.selectbox(
                    "Vælg rolle",
                    ["Alle roller", "Boldholder", "Medspiller", "Presspiller", "Støttespiller"]
                )

                # Pass current_user_id when getting player performance
                player_data = dm.get_player_performance(player, start_date, end_date, current_user_id)
                if not player_data.empty:
                    if category == "Alle roller":
                        fig = viz.plot_player_all_categories(player_data, player)
                    else:
                        fig = viz.plot_player_single_category(player_data, player, category)
                    st.plotly_chart(fig, config={
                        'displayModeBar': False,  # Hide the modebar completely
                        'scrollZoom': False,      # Disable scroll zoom
                        'doubleClick': False,     # Disable double click actions
                        'showTips': False,        # Disable hover tips
                        'displaylogo': False,     # Hide Plotly logo
                        'responsive': True,       # Make the plot responsive to window size
                        'staticPlot': True        # Make the plot completely static
                    }, use_container_width=True)  # Use full container width
                else:
                    st.info("Ingen data tilgængelig for denne spiller")

        elif analysis_type == "Holdanalyse":
            # Pass current_user_id when getting team performance
            team_data = dm.get_team_performance(start_date, end_date, current_user_id)
            if not team_data.empty:
                if category == "Alle roller":
                    fig = viz.plot_team_all_categories(team_data)
                else:
                    fig = viz.plot_team_single_category(team_data, category)
                st.plotly_chart(fig, config={
                    'displayModeBar': False,      # Hide the modebar completely
                    'scrollZoom': False,          # Disable scroll zoom
                    'doubleClick': False,         # Disable double click actions
                    'showTips': False,            # Disable hover tips
                    'displaylogo': False,         # Hide Plotly logo
                    'responsive': True,           # Make the plot responsive to window size
                    'staticPlot': True            # Make the plot completely static
                }, use_container_width=True)  # Use full container width
            else:
                st.info("Ingen holddata tilgængelig")

        else:  # Spillersammenligning
            # Pass current_user_id when getting players for comparison
            players_df = dm.get_players(current_user_id)
            if not players_df.empty:
                st.write("### Vælg spillere at sammenligne")
                st.write("Vælg op til 4 spillere at sammenligne ved at markere afkrydsningsfelterne nedenfor.")

                # Create a grid layout for player selection checkboxes
                cols_per_row = 3
                all_players = players_df['Name'].tolist()

                # Calculate number of rows needed
                num_rows = (len(all_players) + cols_per_row - 1) // cols_per_row

                # Initialize selected players list
                selected_players = []

                # Create checkbox grid
                for row in range(num_rows):
                    cols = st.columns(cols_per_row)
                    for col in range(cols_per_row):
                        player_idx = row * cols_per_row + col
                        if player_idx < len(all_players):
                            player_name = all_players[player_idx]
                            # Only allow selection if less than 4 players are selected
                            disabled = len(selected_players) >= 4 and player_name not in selected_players
                            with cols[col]:
                                if st.checkbox(
                                    player_name,
                                    key=f"player_check_{player_name}",
                                    disabled=disabled
                                ):
                                    selected_players.append(player_name)

                if selected_players:
                    # Get data for all selected players
                    player_data_dict = {}
                    for player_name in selected_players:
                        # Pass current_user_id when getting player performance
                        player_data = dm.get_player_performance(player_name, start_date, end_date, current_user_id)
                        if not player_data.empty:
                            player_data_dict[player_name] = player_data

                    if player_data_dict:
                        fig = viz.plot_player_comparison(player_data_dict)
                        st.plotly_chart(fig, config={
                            'displayModeBar': False,  # Hide the modebar completely
                            'scrollZoom': False,      # Disable scroll zoom
                            'doubleClick': False,     # Disable double click actions
                            'showTips': False,        # Disable hover tips
                            'displaylogo': False,     # Hide Plotly logo
                            'responsive': True,       # Make the plot responsive to window size
                            'staticPlot': True        # Make the plot completely static
                        }, use_container_width=True)  # Use full container width
                    else:
                        st.info("Ingen data tilgængelig for de valgte spillere")
                else:
                    st.info("Vælg mindst én spiller at sammenligne")

if __name__ == "__main__":
    main()