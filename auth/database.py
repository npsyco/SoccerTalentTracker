import os
import psycopg2
from psycopg2.extras import DictCursor
from datetime import datetime, timedelta
from passlib.context import CryptContext
from jose import JWTError, jwt
from typing import Optional, Dict
import streamlit as st

# Password hashing configuration
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT configuration
SECRET_KEY = os.environ.get("SECRET_KEY", "your-secret-key")  # In production, use a proper secret key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

class AuthDB:
    def __init__(self):
        self.conn_string = os.environ['DATABASE_URL']
        self._initialize_tables()

    def _initialize_tables(self):
        """Create necessary tables if they don't exist"""
        with psycopg2.connect(self.conn_string) as conn:
            with conn.cursor() as cur:
                # Create roles table without using sequence
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS roles (
                        id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
                        name VARCHAR(50) UNIQUE NOT NULL
                    )
                """)

                # Create users table without using sequence
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
                        username VARCHAR(100) UNIQUE NOT NULL,
                        password_hash VARCHAR(200) NOT NULL,
                        email VARCHAR(100) UNIQUE NOT NULL,
                        role_id INTEGER REFERENCES roles(id),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                # Insert default roles if they don't exist
                roles = ['admin', 'coach', 'assistant_coach', 'observer']
                for role in roles:
                    cur.execute("""
                        INSERT INTO roles (name)
                        VALUES (%s)
                        ON CONFLICT (name) DO NOTHING
                    """, (role,))

                conn.commit()

    def create_user(self, username: str, password: str, email: str, role: str) -> bool:
        """Create a new user"""
        try:
            # Create password hash
            password_hash = pwd_context.hash(password)
            st.write(f"Debug - Creating user '{username}' with role '{role}'")
            st.write(f"Debug - Generated password hash: {password_hash[:20]}...")

            with psycopg2.connect(self.conn_string) as conn:
                with conn.cursor() as cur:
                    # Get role ID
                    cur.execute("SELECT id FROM roles WHERE name = %s", (role,))
                    role_id = cur.fetchone()
                    if not role_id:
                        st.error(f"Role '{role}' not found")
                        return False

                    # For admin user, use ON CONFLICT DO UPDATE to ensure correct hash
                    if role == 'admin':
                        cur.execute("""
                            INSERT INTO users (username, password_hash, email, role_id)
                            VALUES (%s, %s, %s, %s)
                            ON CONFLICT (username) 
                            DO UPDATE SET password_hash = EXCLUDED.password_hash,
                                        email = EXCLUDED.email,
                                        role_id = EXCLUDED.role_id
                            RETURNING id
                        """, (username, password_hash, email, role_id[0]))
                        user_id = cur.fetchone()
                        st.write(f"Debug - Admin user created/updated with ID: {user_id[0]}")
                    else:
                        cur.execute("""
                            INSERT INTO users (username, password_hash, email, role_id)
                            VALUES (%s, %s, %s, %s)
                        """, (username, password_hash, email, role_id[0]))

                    conn.commit()
                    st.success(f"User '{username}' created successfully")
                    return True

        except psycopg2.Error as e:
            st.error(f"Database error creating user: {str(e)}")
            return False

    def verify_user(self, username: str, password: str) -> Optional[Dict]:
        """Verify user credentials and return user info if valid"""
        try:
            st.write(f"Debug - Verifying user '{username}'")

            with psycopg2.connect(self.conn_string) as conn:
                with conn.cursor(cursor_factory=DictCursor) as cur:
                    cur.execute("""
                        SELECT u.*, r.name as role_name
                        FROM users u
                        JOIN roles r ON u.role_id = r.id
                        WHERE u.username = %s
                    """, (username,))
                    user = cur.fetchone()

                    if user:
                        st.write("Debug - User found in database")
                        is_valid = pwd_context.verify(password, user['password_hash'])
                        st.write(f"Debug - Password verification result: {is_valid}")
                        if is_valid:
                            return dict(user)
                    else:
                        st.write("Debug - User not found in database")
                    return None

        except psycopg2.Error as e:
            st.error(f"Database error during verification: {str(e)}")
            return None

    def create_access_token(self, data: dict) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    def verify_token(self, token: str) -> Optional[Dict]:
        """Verify JWT token and return payload if valid"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except JWTError:
            return None

    def get_user_role(self, username: str) -> Optional[str]:
        """Get user's role"""
        try:
            with psycopg2.connect(self.conn_string) as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT r.name
                        FROM users u
                        JOIN roles r ON u.role_id = r.id
                        WHERE u.username = %s
                    """, (username,))
                    role = cur.fetchone()
                    return role[0] if role else None
        except psycopg2.Error:
            return None