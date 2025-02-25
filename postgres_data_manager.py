import psycopg2
from psycopg2.extras import DictCursor
import os
from datetime import datetime
import pandas as pd

class PostgresDataManager:
    def __init__(self):
        self.conn_string = os.environ['DATABASE_URL']
        self.rating_order = ['D', 'C', 'B', 'A']
        self.rating_map = {'A': 4, 'B': 3, 'C': 2, 'D': 1}
        self.reverse_rating_map = {4: 'A', 3: 'B', 2: 'C', 1: 'D'}

    def add_player(self, name, position="Not specified"):
        """Add a new player to the system"""
        try:
            with psycopg2.connect(self.conn_string) as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO players (name, position)
                        VALUES (%s, %s)
                        ON CONFLICT (name) DO NOTHING
                        RETURNING id
                    """, (name, position))
                    conn.commit()
                    return cur.fetchone() is not None
        except psycopg2.Error as e:
            print(f"Error adding player: {e}")
            return False

    def delete_player(self, name):
        """Delete a player and their matches"""
        try:
            with psycopg2.connect(self.conn_string) as conn:
                with conn.cursor() as cur:
                    # Player's matches will be deleted automatically due to CASCADE
                    cur.execute("DELETE FROM players WHERE name = %s", (name,))
                    conn.commit()
                    return True
        except psycopg2.Error as e:
            print(f"Error deleting player: {e}")
            return False

    def get_players(self):
        """Get list of all players"""
        try:
            with psycopg2.connect(self.conn_string) as conn:
                df = pd.read_sql_query("SELECT name, position FROM players ORDER BY name", conn)
                # Rename columns to match expected format
                df = df.rename(columns={'name': 'Name', 'position': 'Position'})
                return df
        except psycopg2.Error as e:
            print(f"Error getting players: {e}")
            return pd.DataFrame(columns=['Name', 'Position'])

    def add_match_record(self, date, time, opponent, players_df, ratings):
        """Add match performance records for selected players"""
        try:
            with psycopg2.connect(self.conn_string) as conn:
                with conn.cursor() as cur:
                    for _, player in players_df.iterrows():
                        player_name = player['Name']
                        # Get player ID
                        cur.execute("SELECT id FROM players WHERE name = %s", (player_name,))
                        player_id = cur.fetchone()[0]

                        # Insert match record
                        cur.execute("""
                            INSERT INTO matches 
                            (date, time, opponent, player_id, 
                             boldholder, medspiller, presspiller, stottespiller)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        """, (
                            date,
                            time,
                            opponent,
                            player_id,
                            ratings['Boldholder'][player_name],
                            ratings['Medspiller'][player_name],
                            ratings['Presspiller'][player_name],
                            ratings['Støttespiller'][player_name]
                        ))
                    conn.commit()
                    return True
        except psycopg2.Error as e:
            print(f"Error adding match record: {e}")
            return False

    def get_player_performance(self, player_name, start_date=None, end_date=None):
        """Get performance history for a specific player within date range"""
        query = """
            SELECT 
                m.date, 
                m.time,
                m.opponent,
                m.boldholder as "Boldholder",
                m.medspiller as "Medspiller",
                m.presspiller as "Presspiller",
                m.stottespiller as "Støttespiller"
            FROM matches m
            JOIN players p ON m.player_id = p.id
            WHERE p.name = %s
        """
        params = [player_name]

        if start_date:
            query += " AND m.date >= %s"
            params.append(start_date)
        if end_date:
            query += " AND m.date <= %s"
            params.append(end_date)

        query += " ORDER BY m.date, m.time"

        try:
            with psycopg2.connect(self.conn_string) as conn:
                df = pd.read_sql_query(query, conn, params=params)
                if not df.empty:
                    df['Date'] = pd.to_datetime(df['date'])
                    df['Time'] = pd.to_datetime(df['time'], format='%H:%M:%S').dt.time
                    # Drop the original date/time columns
                    df = df.drop(['date', 'time'], axis=1)
                    # Ensure proper categorical ordering for rating columns
                    for category in ['Boldholder', 'Medspiller', 'Presspiller', 'Støttespiller']:
                        df[category] = pd.Categorical(
                            df[category],
                            categories=self.rating_order,
                            ordered=True
                        )
                return df
        except psycopg2.Error as e:
            print(f"Error getting player performance: {e}")
            return pd.DataFrame()

    def get_team_performance(self, start_date=None, end_date=None):
        """Get team's overall performance history within date range"""
        query = """
            WITH daily_ratings AS (
                SELECT 
                    date,
                    time,
                    AVG(CASE boldholder 
                        WHEN 'A' THEN 4 
                        WHEN 'B' THEN 3 
                        WHEN 'C' THEN 2 
                        WHEN 'D' THEN 1 
                    END) as boldholder_avg,
                    AVG(CASE medspiller 
                        WHEN 'A' THEN 4 
                        WHEN 'B' THEN 3 
                        WHEN 'C' THEN 2 
                        WHEN 'D' THEN 1 
                    END) as medspiller_avg,
                    AVG(CASE presspiller 
                        WHEN 'A' THEN 4 
                        WHEN 'B' THEN 3 
                        WHEN 'C' THEN 2 
                        WHEN 'D' THEN 1 
                    END) as presspiller_avg,
                    AVG(CASE stottespiller 
                        WHEN 'A' THEN 4 
                        WHEN 'B' THEN 3 
                        WHEN 'C' THEN 2 
                        WHEN 'D' THEN 1 
                    END) as stottespiller_avg
                FROM matches
                GROUP BY date, time
            )
            SELECT 
                date,
                time,
                CASE 
                    WHEN boldholder_avg >= 3.5 THEN 'A'
                    WHEN boldholder_avg >= 2.5 THEN 'B'
                    WHEN boldholder_avg >= 1.5 THEN 'C'
                    ELSE 'D'
                END as "Boldholder",
                CASE 
                    WHEN medspiller_avg >= 3.5 THEN 'A'
                    WHEN medspiller_avg >= 2.5 THEN 'B'
                    WHEN medspiller_avg >= 1.5 THEN 'C'
                    ELSE 'D'
                END as "Medspiller",
                CASE 
                    WHEN presspiller_avg >= 3.5 THEN 'A'
                    WHEN presspiller_avg >= 2.5 THEN 'B'
                    WHEN presspiller_avg >= 1.5 THEN 'C'
                    ELSE 'D'
                END as "Presspiller",
                CASE 
                    WHEN stottespiller_avg >= 3.5 THEN 'A'
                    WHEN stottespiller_avg >= 2.5 THEN 'B'
                    WHEN stottespiller_avg >= 1.5 THEN 'C'
                    ELSE 'D'
                END as "Støttespiller"
            FROM daily_ratings
        """
        params = []

        if start_date:
            query += " WHERE date >= %s"
            params.append(start_date)
        if end_date:
            query += " AND date <= %s" if start_date else " WHERE date <= %s"
            params.append(end_date)

        query += " ORDER BY date, time"

        try:
            with psycopg2.connect(self.conn_string) as conn:
                df = pd.read_sql_query(query, conn, params=params)
                if not df.empty:
                    # Set date as index
                    df.set_index(['date', 'time'], inplace=True)
                    # Ensure proper categorical ordering
                    for category in ['Boldholder', 'Medspiller', 'Presspiller', 'Støttespiller']:
                        df[category] = pd.Categorical(
                            df[category],
                            categories=self.rating_order,
                            ordered=True
                        )
                return df
        except psycopg2.Error as e:
            print(f"Error getting team performance: {e}")
            return pd.DataFrame()

    def get_available_seasons(self):
        """Get list of available seasons (years) from match data"""
        try:
            with psycopg2.connect(self.conn_string) as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT DISTINCT EXTRACT(YEAR FROM date) FROM matches ORDER BY 1")
                    return [int(year[0]) for year in cur.fetchall()]
        except psycopg2.Error as e:
            print(f"Error getting available seasons: {e}")
            return []

    def generate_test_data(self, username):
        """Generate test data for a specific user"""
        # Generate 10 test players
        test_players = [f"Test{i}" for i in range(1, 11)]
        for player in test_players:
            self.add_player(player, "Not specified")

        # Generate 5 matches
        match_data = [
            # Two matches on the same day
            (datetime(2025, 2, 25, 9, 0), "Morning Team"),
            (datetime(2025, 2, 25, 15, 0), "Afternoon Team"),
            # Three matches on different days
            (datetime(2025, 2, 23, 12, 0), "Team Alpha"),
            (datetime(2025, 2, 24, 14, 0), "Team Beta"),
            (datetime(2025, 2, 26, 10, 0), "Team Gamma")
        ]

        # Performance ratings (A, B, C, D) for each role
        roles = ['Boldholder', 'Medspiller', 'Presspiller', 'Støttespiller']
        ratings = ['A', 'B', 'C', 'D']

        players_df = self.get_players()

        for match_date, opponent in match_data:
            # Generate random ratings for each player
            player_ratings = {}
            for role in roles:
                player_ratings[role] = {
                    player: ratings[hash(f"{player}{role}{match_date}") % len(ratings)]
                    for player in test_players[:5]  # Use 5 players per match
                }

            # Add match record
            self.add_match_record(
                match_date.date(),
                match_date.time(),
                opponent,
                players_df[players_df['Name'].isin(test_players[:5])],
                player_ratings
            )

    def reset_data(self):
        """Reset all data in the system"""
        try:
            with psycopg2.connect(self.conn_string) as conn:
                with conn.cursor() as cur:
                    cur.execute("TRUNCATE TABLE matches CASCADE")
                    cur.execute("TRUNCATE TABLE players CASCADE")
                    conn.commit()
                    return True
        except psycopg2.Error as e:
            print(f"Error resetting data: {e}")
            return False