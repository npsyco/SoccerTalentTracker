import pandas as pd
import os
from datetime import datetime

class DataManager:
    def __init__(self):
        self.players_file = "data/players.csv"
        self.matches_file = "data/matches.csv"
        self._initialize_data_files()
        self.rating_order = ['D', 'C', 'B', 'A']

    def _initialize_data_files(self):
        """Initialize CSV files if they don't exist"""
        if not os.path.exists("data"):
            os.makedirs("data")

        if not os.path.exists(self.players_file):
            pd.DataFrame(columns=['Name', 'Position']).to_csv(self.players_file, index=False)

        if not os.path.exists(self.matches_file):
            columns = ['Date', 'Opponent', 'Player', 'Technical', 'Tactical', 'Physical', 'Mental', 'Boldholder', 'Medspiller', 'Presspiller', 'Støttespiller']
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
        """Add match performance records for selected players"""
        matches_df = pd.read_csv(self.matches_file)

        new_records = []
        for _, player in players_df.iterrows():
            player_name = player['Name']
            record = {
                'Date': date.strftime('%Y-%m-%d'),
                'Opponent': opponent,
                'Player': player_name,
                'Boldholder': ratings['Boldholder'][player_name],
                'Medspiller': ratings['Medspiller'][player_name],
                'Presspiller': ratings['Presspiller'][player_name],
                'Støttespiller': ratings['Støttespiller'][player_name]
            }
            new_records.append(record)

        new_records_df = pd.DataFrame(new_records)
        matches_df = pd.concat([matches_df, new_records_df], ignore_index=True)
        matches_df.to_csv(self.matches_file, index=False)

    def get_player_performance(self, player_name, start_date=None, end_date=None):
        """Get performance history for a specific player within date range"""
        matches_df = pd.read_csv(self.matches_file)
        player_data = matches_df[matches_df['Player'] == player_name].copy()

        if not player_data.empty:
            player_data['Date'] = pd.to_datetime(player_data['Date'])
            if start_date:
                player_data = player_data[player_data['Date'] >= start_date]
            if end_date:
                player_data = player_data[player_data['Date'] <= end_date]

        return player_data.sort_values('Date')

    def get_available_seasons(self):
        """Get list of available seasons (years) from match data"""
        matches_df = pd.read_csv(self.matches_file)
        if not matches_df.empty:
            matches_df['Date'] = pd.to_datetime(matches_df['Date'])
            years = sorted(matches_df['Date'].dt.year.unique())
            return years
        return []

    def get_team_performance(self, start_date=None, end_date=None):
        """Get team's overall performance history within date range"""
        matches_df = pd.read_csv(self.matches_file)
        if matches_df.empty:
            return pd.DataFrame()

        # Convert date and filter by date range
        matches_df['Date'] = pd.to_datetime(matches_df['Date'])
        if start_date:
            matches_df = matches_df[matches_df['Date'] >= start_date]
        if end_date:
            matches_df = matches_df[matches_df['Date'] <= end_date]

        if matches_df.empty:
            return pd.DataFrame()

        categories = ['Boldholder', 'Medspiller', 'Presspiller', 'Støttespiller']
        team_performance = pd.DataFrame()

        # Process each date separately
        for date in matches_df['Date'].unique():
            date_data = matches_df[matches_df['Date'] == date].copy()
            date_ratings = {}

            # Calculate mode (most common rating) for each category
            for category in categories:
                # Convert to categorical with proper ordering first
                date_data.loc[:, category] = pd.Categorical(
                    date_data[category],
                    categories=self.rating_order,
                    ordered=True
                )
                ratings = date_data[category].value_counts()
                # If there's a tie, take the lower rating
                date_ratings[category] = ratings.index[0] if not ratings.empty else 'D'

            # Add to team performance dataframe
            team_performance = pd.concat([
                team_performance,
                pd.DataFrame([date_ratings], index=[date])
            ])

        # Ensure categorical type for all columns
        for category in categories:
            team_performance[category] = pd.Categorical(
                team_performance[category],
                categories=self.rating_order,
                ordered=True
            )

        return team_performance.sort_index()