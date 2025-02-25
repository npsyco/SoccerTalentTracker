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
            WITH valid_matches AS (
                -- First get only valid matches
                SELECT m.* 
                FROM matches m
                JOIN players p ON m.player_id = p.id
                WHERE p.name = %s
                AND m.date IS NOT NULL 
                AND m.date != '1970-01-01'
                AND EXTRACT(YEAR FROM m.date) >= 2000
                AND EXTRACT(YEAR FROM m.date) <= EXTRACT(YEAR FROM CURRENT_DATE)
            )
            SELECT 
                date::date as date, 
                time::time as time,
                opponent,
                boldholder as "Boldholder",
                medspiller as "Medspiller",
                presspiller as "Presspiller",
                stottespiller as "Støttespiller"
            FROM valid_matches
            ORDER BY date, time
        """
        params = [player_name]

        if start_date:
            query = query.replace("ORDER BY date, time", "AND date >= %s ORDER BY date, time")
            params.append(start_date)
        if end_date:
            query = query.replace("ORDER BY date, time", "AND date <= %s ORDER BY date, time")
            params.append(end_date)

        try:
            with psycopg2.connect(self.conn_string) as conn:
                df = pd.read_sql_query(query, conn, params=params)
                if not df.empty:
                    # Ensure date and time are properly formatted
                    df['Date'] = pd.to_datetime(df['date']).dt.date
                    df['Time'] = pd.to_datetime(df['time'], format='%H:%M:%S').dt.time
                    # Drop the original date/time columns
                    df = df.drop(['date', 'time'], axis=1)
                    # Convert rating columns to numeric values
                    for category in ['Boldholder', 'Medspiller', 'Presspiller', 'Støttespiller']:
                        df[category] = df[category].map(self.rating_map)
                return df
        except psycopg2.Error as e:
            print(f"Error getting player performance: {e}")
            return pd.DataFrame()

    def get_team_performance(self, start_date=None, end_date=None):
        """Get team's overall performance history within date range"""
        query = """
            WITH match_dates AS (
                -- First get only valid match dates
                SELECT DISTINCT date::date as date, time::time as time
                FROM matches
                WHERE date IS NOT NULL 
                AND date != '1970-01-01'
                AND EXTRACT(YEAR FROM date) >= 2000
                AND EXTRACT(YEAR FROM date) <= EXTRACT(YEAR FROM CURRENT_DATE)
            ),
            match_ratings AS (
                SELECT 
                    m.date,
                    m.time,
                    -- Convert ratings to numeric values with explicit casting
                    CASE m.boldholder 
                        WHEN 'A' THEN 4.0 
                        WHEN 'B' THEN 3.0 
                        WHEN 'C' THEN 2.0 
                        WHEN 'D' THEN 1.0 
                    END::numeric as boldholder_val,
                    CASE m.medspiller 
                        WHEN 'A' THEN 4.0 
                        WHEN 'B' THEN 3.0 
                        WHEN 'C' THEN 2.0 
                        WHEN 'D' THEN 1.0 
                    END::numeric as medspiller_val,
                    CASE m.presspiller 
                        WHEN 'A' THEN 4.0 
                        WHEN 'B' THEN 3.0 
                        WHEN 'C' THEN 2.0 
                        WHEN 'D' THEN 1.0 
                    END::numeric as presspiller_val,
                    CASE m.stottespiller 
                        WHEN 'A' THEN 4.0 
                        WHEN 'B' THEN 3.0 
                        WHEN 'C' THEN 2.0 
                        WHEN 'D' THEN 1.0 
                    END::numeric as stottespiller_val
                FROM matches m
                JOIN match_dates d ON m.date::date = d.date AND 
                                    (m.time::time = d.time OR (m.time IS NULL AND d.time IS NULL))
            ),
            match_averages AS (
                SELECT 
                    date,
                    time,
                    ROUND(AVG(boldholder_val)::numeric, 2) as "Boldholder",
                    ROUND(AVG(medspiller_val)::numeric, 2) as "Medspiller",
                    ROUND(AVG(presspiller_val)::numeric, 2) as "Presspiller",
                    ROUND(AVG(stottespiller_val)::numeric, 2) as "Støttespiller",
                    COUNT(*) as player_count
                FROM match_ratings
                GROUP BY date, time
                HAVING COUNT(*) > 0
            )
            SELECT * FROM match_averages
            ORDER BY date, time
        """
        params = []

        if start_date:
            query = query + " WHERE date >= %s"
            params.append(start_date)
        if end_date:
            query += " AND date <= %s" if start_date else " WHERE date <= %s"
            params.append(end_date)

        try:
            with psycopg2.connect(self.conn_string) as conn:
                df = pd.read_sql_query(query, conn, params=params)
                if not df.empty:
                    # Set date as index
                    df.set_index(['date', 'time'], inplace=True)
                    # Drop the player_count column as it's no longer needed
                    df = df.drop('player_count', axis=1)
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