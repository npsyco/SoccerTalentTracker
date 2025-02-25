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

    def add_player(self, name, position="Not specified", user_id=None):
        """Add a new player to the system"""
        try:
            with psycopg2.connect(self.conn_string) as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO players (name, position, user_id)
                        VALUES (%s, %s, %s)
                        ON CONFLICT (name, user_id) DO NOTHING
                        RETURNING id
                    """, (name, position, user_id))
                    conn.commit()
                    return cur.fetchone() is not None
        except psycopg2.Error as e:
            print(f"Error adding player: {e}")
            return False

    def delete_player(self, name, user_id=None):
        """Delete a player and their matches"""
        try:
            with psycopg2.connect(self.conn_string) as conn:
                with conn.cursor() as cur:
                    # Only delete if the player belongs to the user
                    cur.execute("""
                        DELETE FROM players 
                        WHERE name = %s AND user_id = %s
                    """, (name, user_id))
                    conn.commit()
                    return True
        except psycopg2.Error as e:
            print(f"Error deleting player: {e}")
            return False

    def get_players(self, user_id=None):
        """Get list of all players for a specific user"""
        try:
            with psycopg2.connect(self.conn_string) as conn:
                query = """
                    SELECT name, position 
                    FROM players 
                    WHERE user_id = %s
                    ORDER BY name
                """
                df = pd.read_sql_query(query, conn, params=[user_id])
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

    def get_player_performance(self, player_name, start_date=None, end_date=None, user_id=None):
        """Get performance history for a specific player within date range"""
        query = """
            SELECT 
                m.date::date as date,
                m.time::time as time,
                m.opponent,
                m.boldholder as "Boldholder",
                m.medspiller as "Medspiller",
                m.presspiller as "Presspiller",
                m.stottespiller as "Støttespiller"
            FROM matches m
            JOIN players p ON m.player_id = p.id
            WHERE p.name = %s
            AND p.user_id = %s
            AND m.date IS NOT NULL 
            AND m.date != '1970-01-01'::date
            AND m.boldholder IN ('A', 'B', 'C', 'D')
            AND m.medspiller IN ('A', 'B', 'C', 'D')
            AND m.presspiller IN ('A', 'B', 'C', 'D')
            AND m.stottespiller IN ('A', 'B', 'C', 'D')
            ORDER BY m.date::date, m.time::time
        """
        params = [player_name, user_id]

        if start_date:
            query = query.replace("ORDER BY m.date::date, m.time::time", 
                                "AND m.date >= %s ORDER BY m.date::date, m.time::time")
            params.append(start_date)
        if end_date:
            query = query.replace("ORDER BY m.date::date, m.time::time", 
                                "AND m.date <= %s ORDER BY m.date::date, m.time::time")
            params.append(end_date)

        try:
            with psycopg2.connect(self.conn_string) as conn:
                df = pd.read_sql_query(query, conn, params=params)
                if not df.empty:
                    # Convert ratings to numeric values
                    for category in ['Boldholder', 'Medspiller', 'Presspiller', 'Støttespiller']:
                        df[category] = df[category].map(self.rating_map)
                    # Keep date and time as is since they're already properly formatted by Postgres
                    df['Date'] = df['date']
                    df['Time'] = df['time']
                    df = df.drop(['date', 'time'], axis=1)
                return df
        except psycopg2.Error as e:
            print(f"Error getting player performance: {e}")
            return pd.DataFrame()

    def get_team_performance(self, start_date=None, end_date=None, user_id=None):
        """Get team's overall performance history within date range for a specific user"""
        query = """
            WITH valid_matches AS (
                SELECT 
                    date::date as date,
                    time::time as time,
                    boldholder,
                    medspiller,
                    presspiller,
                    stottespiller
                FROM matches m
                JOIN players p ON m.player_id = p.id
                WHERE p.user_id = %s
                AND date IS NOT NULL 
                AND date != '1970-01-01'::date
                AND boldholder IN ('A', 'B', 'C', 'D')
                AND medspiller IN ('A', 'B', 'C', 'D')
                AND presspiller IN ('A', 'B', 'C', 'D')
                AND stottespiller IN ('A', 'B', 'C', 'D')
            )
            SELECT 
                v.date,
                v.time,
                ROUND(AVG(
                    CASE v.boldholder 
                        WHEN 'A' THEN 4.0 
                        WHEN 'B' THEN 3.0 
                        WHEN 'C' THEN 2.0 
                        WHEN 'D' THEN 1.0 
                    END)::numeric, 2) as "Boldholder",
                ROUND(AVG(
                    CASE v.medspiller 
                        WHEN 'A' THEN 4.0 
                        WHEN 'B' THEN 3.0 
                        WHEN 'C' THEN 2.0 
                        WHEN 'D' THEN 1.0 
                    END)::numeric, 2) as "Medspiller",
                ROUND(AVG(
                    CASE v.presspiller 
                        WHEN 'A' THEN 4.0 
                        WHEN 'B' THEN 3.0 
                        WHEN 'C' THEN 2.0 
                        WHEN 'D' THEN 1.0 
                    END)::numeric, 2) as "Presspiller",
                ROUND(AVG(
                    CASE v.stottespiller 
                        WHEN 'A' THEN 4.0 
                        WHEN 'B' THEN 3.0 
                        WHEN 'C' THEN 2.0 
                        WHEN 'D' THEN 1.0 
                    END)::numeric, 2) as "Støttespiller"
            FROM valid_matches v
            GROUP BY v.date, v.time
            HAVING COUNT(*) > 0
            ORDER BY v.date, v.time
        """
        params = [user_id]

        if start_date:
            query = query.replace("ORDER BY v.date, v.time", "AND v.date >= %s ORDER BY v.date, v.time")
            params.append(start_date)
        if end_date:
            query = query.replace("ORDER BY v.date, v.time", "AND v.date <= %s ORDER BY v.date, v.time")
            params.append(end_date)

        try:
            with psycopg2.connect(self.conn_string) as conn:
                df = pd.read_sql_query(query, conn, params=params)
                if not df.empty:
                    df.set_index(['date', 'time'], inplace=True)
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
            self.add_player(player, "Not specified", username) #Added user_id

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

        players_df = self.get_players(username) #Added user_id

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