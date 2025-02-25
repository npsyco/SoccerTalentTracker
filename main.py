import streamlit as st
import pandas as pd
from data_manager import DataManager
from visualizations import Visualizer
from utils import initialize_session_state
from auth.session import SessionManager
from auth.database import AuthDB
from auth.admin import create_initial_admin
from pages.login import show_login_page, show_logout_button
from datetime import datetime

# Must be the first Streamlit command
st.set_page_config(
    page_title="Sorø-Freja Spiller Udviklingsværktøj",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    # Initialize session state
    initialize_session_state()

    # Initialize session manager
    session_manager = SessionManager()

    # Create initial admin user if needed
    create_initial_admin()

    # Show login page if user is not logged in
    if not session_manager.get_current_user():
        # Hide sidebar for login page
        st.markdown(
            """
            <style>
                [data-testid="stSidebar"][aria-expanded="true"]{
                    display: none;
                }
            </style>
            """,
            unsafe_allow_html=True
        )
        show_login_page()
        return

    # Show navigation and content only after login
    with st.sidebar:
        st.write(f"Logget ind som: {st.session_state.user['username']}")
        show_logout_button()
        st.sidebar.divider()

        # Navigation menu
        page = st.sidebar.selectbox(
            "Navigation",
            ["Spillere", "Kampdata", "Udviklingsanalyse"]
        )

    # Initialize data manager and visualizer
    dm = DataManager()
    viz = Visualizer()

    st.title("Sorø-Freja Spiller Udviklingsværktøj")

    if page == "Spillere":
        # Require coach or admin role
        if not session_manager.require_role(['admin', 'coach']):
            return

        st.header("Spillere")

        col1, col2 = st.columns([1, 2])

        with col1:
            with st.form("add_player"):
                st.subheader("Tilføj spiller")
                player_name = st.text_input("Spiller navn")

                if st.form_submit_button("Tilføj Spiller"):
                    if player_name:
                        # Set a default position as it's hidden for now
                        dm.add_player(player_name, "Not specified")
                        st.success(f"Spiller tilføjet: {player_name}")
                    else:
                        st.error("Indtast venligst et spillernavn")

        with col2:
            st.subheader("Aktive Spillere")
            players_df = dm.get_players()
            if not players_df.empty:
                st.dataframe(players_df[['Name']])  # Only show name column

                # Delete player option
                player_to_delete = st.selectbox("Vælg spiller fra listen der skal slettes", players_df['Name'].tolist())
                if st.button("Slet Spiller"):
                    if st.warning("Advarsel: Hvis du bekræfter slettes denne spiller og alle spillerens data"):
                        dm.delete_player(player_to_delete)
                        st.success(f"Spiller slettet: {player_to_delete}")
                        st.rerun()


    elif page == "Kampdata":
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

                match_date = st.date_input("Dato", datetime.date.today())
                match_time = st.time_input("Tidspunkt", datetime.time(12, 0))
                opponent = st.text_input("Modstander (valgfrit)")

                players_df = dm.get_players()
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
                        players_df = dm.get_players()
                        selected_players_df = players_df[players_df['Name'].isin(st.session_state.selected_players)]
                        dm.add_match_record(
                            st.session_state.match_date,
                            st.session_state.match_time,
                            st.session_state.opponent or "Ikke angivet",
                            selected_players_df,
                            player_ratings
                        )

                        # Reset state and show success message
                        st.session_state.match_step = 1
                        st.session_state.selected_players = []
                        st.session_state.match_date = None
                        st.session_state.match_time = None
                        st.session_state.opponent = None
                        st.success("Kampdata gemt!")
                        st.rerun()

    else:  # Udviklingsanalyse
        # All roles can view analysis
        if not session_manager.require_login():
            return

        st.header("Udviklingsanalyse")

        # Add date range filtering
        col1, col2 = st.columns([1, 2])
        with col1:
            analysis_type = st.radio(
                "Vælg analysetype",
                ["Individuel Spilleranalyse", "Holdanalyse"]
            )

        with col2:
            # Get available seasons
            available_seasons = dm.get_available_seasons()
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
            players_df = dm.get_players()
            if not players_df.empty:
                player = st.selectbox("Vælg Spiller", players_df['Name'].tolist())
                category = st.selectbox(
                    "Vælg rolle",
                    ["Alle roller", "Boldholder", "Medspiller", "Presspiller", "Støttespiller"]
                )

                player_data = dm.get_player_performance(player, start_date, end_date)
                if not player_data.empty:
                    if category == "Alle roller":
                        fig = viz.plot_player_all_categories(player_data, player)
                    else:
                        fig = viz.plot_player_single_category(player_data, player, category)
                    st.plotly_chart(fig)
                else:
                    st.info("Ingen data tilgængelig for denne spiller")

        else:  # Holdanalyse
            category = st.selectbox(
                "Vælg rolle",
                ["Alle roller", "Boldholder", "Medspiller", "Presspiller", "Støttespiller"]
            )

            team_data = dm.get_team_performance(start_date, end_date)
            if not team_data.empty:
                # Temporary debug output
                st.write("Debug: Team Performance Calculation")
                matches_df = pd.read_csv('data/matches.csv')
                st.write("Latest match ratings (Team Delta):")
                st.dataframe(matches_df[matches_df['Opponent'] == 'Team Delta'])
                st.write("Calculated team ratings:")
                st.dataframe(team_data)

                if category == "Alle roller":
                    fig = viz.plot_team_all_categories(team_data)
                else:
                    fig = viz.plot_team_single_category(team_data, category)
                st.plotly_chart(fig)
            else:
                st.info("Ingen holddata tilgængelig")

if __name__ == "__main__":
    main()