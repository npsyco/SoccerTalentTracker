import pandas as pd
import os
from datetime import datetime

class DataManager:
    def __init__(self):
        self.players_file = "data/players.csv"
        self.matches_file = "data/matches.csv"
        self._initialize_data_files()

    def _initialize_data_files(self):
        """Initialize CSV files if they don't exist"""
        if not os.path.exists("data"):
            os.makedirs("data")

        if not os.path.exists(self.players_file):
            pd.DataFrame(columns=['Name', 'Position']).to_csv(self.players_file, index=False)

        if not os.path.exists(self.matches_file):
            columns = ['Date', 'Opponent', 'Player', 'Technical', 'Tactical', 'Physical', 'Mental']
            pd.DataFrame(columns=columns).to_csv(self.matches_file, index=False)

    def add_player(self, name, position):
        """Add a new player to the system"""
        players_df = pd.read_csv(self.players_file)
        if name not in players_df['Name'].values:
            new_player = pd.DataFrame({'Name': [name], 'Position': [position]})
            players_df = pd.concat([players_df, new_player], ignore_index=True)
            players_df.to_csv(self.players_file, index=False)

    def delete_player(self, name):
        """Delete a player from the system"""
        players_df = pd.read_csv(self.players_file)
        players_df = players_df[players_df['Name'] != name]
        players_df.to_csv(self.players_file, index=False)

        # Also remove player's match records
        matches_df = pd.read_csv(self.matches_file)
        matches_df = matches_df[matches_df['Player'] != name]
        matches_df.to_csv(self.matches_file, index=False)

    def get_players(self):
        """Get list of all players"""
        return pd.read_csv(self.players_file)

    def add_match_record(self, date, opponent, players_df, ratings):
        """Add match performance records for all players"""
        matches_df = pd.read_csv(self.matches_file)

        new_records = []
        for _, player in players_df.iterrows():
            record = {
                'Date': date.strftime('%Y-%m-%d'),
                'Opponent': opponent,
                'Player': player['Name'],
                'Technical': ratings['Technical'],
                'Tactical': ratings['Tactical'],
                'Physical': ratings['Physical'],
                'Mental': ratings['Mental']
            }
            new_records.append(record)

        new_records_df = pd.DataFrame(new_records)
        matches_df = pd.concat([matches_df, new_records_df], ignore_index=True)
        matches_df.to_csv(self.matches_file, index=False)

    def get_player_performance(self, player_name):
        """Get performance history for a specific player"""
        matches_df = pd.read_csv(self.matches_file)
        return matches_df[matches_df['Player'] == player_name].sort_values('Date')

    def get_team_performance(self):
        """Get team's overall performance history"""
        matches_df = pd.read_csv(self.matches_file)
        if matches_df.empty:
            return pd.DataFrame()

        # Convert rating columns to numeric
        numeric_columns = ['Technical', 'Tactical', 'Physical', 'Mental']
        for col in numeric_columns:
            matches_df[col] = pd.to_numeric(matches_df[col], errors='coerce')

        # Group by date and calculate mean of only numeric columns
        return matches_df.groupby('Date')[numeric_columns].mean()