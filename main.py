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
        ["Player Management", "Match Records", "Performance Analysis"]
    )

    if page == "Player Management":
        st.header("Player Management")
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            with st.form("add_player"):
                st.subheader("Add New Player")
                player_name = st.text_input("Player Name")
                position = st.selectbox("Position", ["Forward", "Midfielder", "Defender", "Goalkeeper"])
                
                if st.form_submit_button("Add Player"):
                    if player_name:
                        dm.add_player(player_name, position)
                        st.success(f"Added player: {player_name}")
                    else:
                        st.error("Please enter a player name")

        with col2:
            st.subheader("Current Players")
            players_df = dm.get_players()
            if not players_df.empty:
                st.dataframe(players_df)
                
                # Delete player option
                player_to_delete = st.selectbox("Select player to delete", players_df['Name'].tolist())
                if st.button("Delete Player"):
                    dm.delete_player(player_to_delete)
                    st.success(f"Deleted player: {player_to_delete}")
                    st.rerun()

    elif page == "Match Records":
        st.header("Match Records")
        
        with st.form("add_match_record"):
            st.subheader("Add Match Performance")
            
            match_date = st.date_input("Match Date", datetime.date.today())
            opponent = st.text_input("Opponent Team")
            
            players_df = dm.get_players()
            if not players_df.empty:
                st.subheader("Player Ratings")
                
                for _, player in players_df.iterrows():
                    st.write(f"### {player['Name']}")
                    cols = st.columns(4)
                    
                    categories = ["Technical", "Tactical", "Physical", "Mental"]
                    ratings = {}
                    
                    for i, category in enumerate(categories):
                        with cols[i]:
                            ratings[category] = st.slider(
                                f"{category}",
                                1, 10, 5,
                                key=f"{player['Name']}_{category}"
                            )
                
                if st.form_submit_button("Save Match Records"):
                    if opponent:
                        dm.add_match_record(match_date, opponent, players_df, ratings)
                        st.success("Match records saved successfully!")
                    else:
                        st.error("Please enter opponent team name")

    else:  # Performance Analysis
        st.header("Performance Analysis")
        
        analysis_type = st.radio(
            "Select Analysis Type",
            ["Individual Player Analysis", "Team Analysis"]
        )
        
        if analysis_type == "Individual Player Analysis":
            players_df = dm.get_players()
            if not players_df.empty:
                player = st.selectbox("Select Player", players_df['Name'].tolist())
                category = st.selectbox(
                    "Select Category",
                    ["All Categories", "Technical", "Tactical", "Physical", "Mental"]
                )
                
                player_data = dm.get_player_performance(player)
                if not player_data.empty:
                    if category == "All Categories":
                        fig = viz.plot_player_all_categories(player_data, player)
                    else:
                        fig = viz.plot_player_single_category(player_data, player, category)
                    st.plotly_chart(fig)
                else:
                    st.info("No performance data available for this player")
        
        else:  # Team Analysis
            category = st.selectbox(
                "Select Category",
                ["All Categories", "Technical", "Tactical", "Physical", "Mental"]
            )
            
            team_data = dm.get_team_performance()
            if not team_data.empty:
                if category == "All Categories":
                    fig = viz.plot_team_all_categories(team_data)
                else:
                    fig = viz.plot_team_single_category(team_data, category)
                st.plotly_chart(fig)
            else:
                st.info("No team performance data available")

if __name__ == "__main__":
    main()