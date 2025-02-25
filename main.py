import streamlit as st
import pandas as pd
from data_manager import DataManager
from visualizations import Visualizer
from utils import initialize_session_state
import datetime

st.set_page_config(page_title="Sorø-Freja Spiller Udviklingsværktøj", layout="wide")

def main():
    # Initialize session state
    initialize_session_state()

    # Initialize data manager
    dm = DataManager()
    viz = Visualizer()

    st.title("Sorø-Freja Spiller Udviklingsværktøj")

    # Sidebar navigation
    page = st.sidebar.selectbox(
        "Navigation",
        ["Spillere", "Kampdata", "Udviklingsanalyse"]
    )

    if page == "Spillere":
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
        st.header("Kampe")

        with st.form("add_match_record"):
            st.subheader("Gem kampdata")

            match_date = st.date_input("Dato", datetime.date.today())
            opponent = st.text_input("Modstander (valgfrit)")

            players_df = dm.get_players()
            if not players_df.empty:
                st.subheader("Spillervurdering")

                categories = ["Boldholder", "Medspiller", "Presspiller", "Støttespiller"]
                ratings = {}

                for _, player in players_df.iterrows():
                    st.write(f"### {player['Name']}")
                    cols = st.columns(4)

                    for i, category in enumerate(categories):
                        with cols[i]:
                            ratings[category] = st.selectbox(
                                f"{category}",
                                ["A", "B", "C", "D"],
                                key=f"{player['Name']}_{category}"
                            )

                if st.form_submit_button("Gem Kampdata"):
                    dm.add_match_record(match_date, opponent or "Ikke angivet", players_df, ratings)
                    st.success("Kampdata gemt!")

    else:  # Udviklingsanalyse
        st.header("Udviklingsanalyse")

        analysis_type = st.radio(
            "Vælg analysetype",
            ["Individuel Spilleranalyse", "Holdanalyse"]
        )

        if analysis_type == "Individuel Spilleranalyse":
            players_df = dm.get_players()
            if not players_df.empty:
                player = st.selectbox("Vælg Spiller", players_df['Name'].tolist())
                category = st.selectbox(
                    "Vælg rolle",
                    ["Alle roller", "Boldholder", "Medspiller", "Presspiller", "Støttespiller"]
                )

                player_data = dm.get_player_performance(player)
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

            team_data = dm.get_team_performance()
            if not team_data.empty:
                if category == "Alle roller":
                    fig = viz.plot_team_all_categories(team_data)
                else:
                    fig = viz.plot_team_single_category(team_data, category)
                st.plotly_chart(fig)
            else:
                st.info("Ingen holddata tilgængelig")

if __name__ == "__main__":
    main()