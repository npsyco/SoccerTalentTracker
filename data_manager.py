from postgres_data_manager import PostgresDataManager

class DataManager:
    def __init__(self):
        self.db = PostgresDataManager()
        self.rating_order = ['D', 'C', 'B', 'A']
        self.rating_map = {'A': 4, 'B': 3, 'C': 2, 'D': 1}
        self.reverse_rating_map = {4: 'A', 3: 'B', 2: 'C', 1: 'D'}

    def add_player(self, name, position="Not specified"):
        """Add a new player to the system"""
        return self.db.add_player(name, position)

    def delete_player(self, name):
        """Delete a player from the system"""
        return self.db.delete_player(name)

    def get_players(self):
        """Get list of all players"""
        return self.db.get_players()

    def add_match_record(self, date, time, opponent, players_df, ratings):
        """Add match performance records for selected players"""
        return self.db.add_match_record(date, time, opponent, players_df, ratings)

    def get_player_performance(self, player_name, start_date=None, end_date=None):
        """Get performance history for a specific player within date range"""
        return self.db.get_player_performance(player_name, start_date, end_date)

    def get_team_performance(self, start_date=None, end_date=None):
        """Get team's overall performance history within date range"""
        return self.db.get_team_performance(start_date, end_date)

    def get_available_seasons(self):
        """Get list of available seasons (years) from match data"""
        return self.db.get_available_seasons()

    def generate_test_data(self, username):
        """Generate test data for a specific user"""
        return self.db.generate_test_data(username)

    def reset_data(self):
        """Reset all data in the system"""
        return self.db.reset_data()

    def _convert_to_numeric(self, rating):
        """Convert letter rating to numeric value"""
        return self.rating_map.get(rating, 1)  # Default to 1 (D) if invalid

    def _convert_to_letter(self, numeric_value):
        """Convert numeric value back to letter rating"""
        # Round to nearest integer and ensure it's in range 1-4
        numeric_value = max(1, min(4, round(numeric_value)))
        return self.reverse_rating_map.get(numeric_value, 'D')