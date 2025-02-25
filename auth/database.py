import os
import psycopg2
from psycopg2.extras import DictCursor
from datetime import datetime, timedelta
from passlib.context import CryptContext
from jose import JWTError, jwt
from typing import Optional, Dict, List
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
                # Create roles table
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS roles (
                        id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
                        name VARCHAR(50) UNIQUE NOT NULL
                    )
                """)

                # Create users table
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
                        username VARCHAR(100) UNIQUE NOT NULL,
                        password_hash VARCHAR(200) NOT NULL,
                        email VARCHAR(100) UNIQUE NOT NULL,
                        role_id INTEGER REFERENCES roles(id),
                        status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'active', 'inactive')),
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
        """Create a new user with active status"""
        try:
            password_hash = pwd_context.hash(password)

            with psycopg2.connect(self.conn_string) as conn:
                with conn.cursor() as cur:
                    # Get role ID
                    cur.execute("SELECT id FROM roles WHERE name = %s", (role,))
                    role_id = cur.fetchone()
                    if not role_id:
                        return False

                    # Insert new user with active status
                    cur.execute("""
                        INSERT INTO users (username, password_hash, email, role_id, status)
                        VALUES (%s, %s, %s, %s, 'active')
                    """, (username, password_hash, email, role_id[0]))

                    conn.commit()
                    return True

        except psycopg2.Error:
            return False

    def register_user(self, username: str, password: str, email: str, role: str) -> bool:
        """Register a new user with pending status"""
        try:
            password_hash = pwd_context.hash(password)

            with psycopg2.connect(self.conn_string) as conn:
                with conn.cursor() as cur:
                    # Get role ID
                    cur.execute("SELECT id FROM roles WHERE name = %s", (role,))
                    role_id = cur.fetchone()
                    if not role_id:
                        return False

                    # Insert new user with pending status
                    cur.execute("""
                        INSERT INTO users (username, password_hash, email, role_id, status)
                        VALUES (%s, %s, %s, %s, 'pending')
                    """, (username, password_hash, email, role_id[0]))

                    conn.commit()
                    return True

        except psycopg2.Error:
            return False

    def get_pending_users(self) -> List[Dict]:
        """Get list of users pending approval"""
        try:
            with psycopg2.connect(self.conn_string) as conn:
                with conn.cursor(cursor_factory=DictCursor) as cur:
                    cur.execute("""
                        SELECT u.username, u.email, u.created_at, r.name as role_name
                        FROM users u
                        JOIN roles r ON u.role_id = r.id
                        WHERE u.status = 'pending'
                        ORDER BY u.created_at DESC
                    """)
                    return [dict(row) for row in cur.fetchall()]
        except psycopg2.Error:
            return []

    def approve_user(self, username: str) -> bool:
        """Approve a pending user"""
        try:
            with psycopg2.connect(self.conn_string) as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        UPDATE users
                        SET status = 'active'
                        WHERE username = %s AND status = 'pending'
                    """, (username,))
                    conn.commit()
                    return True
        except psycopg2.Error:
            return False

    def reject_user(self, username: str) -> bool:
        """Reject a pending user"""
        try:
            with psycopg2.connect(self.conn_string) as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        DELETE FROM users
                        WHERE username = %s AND status = 'pending'
                    """, (username,))
                    conn.commit()
                    return True
        except psycopg2.Error:
            return False

    def verify_user(self, username: str, password: str) -> Optional[Dict]:
        """Verify user credentials and return user info if valid"""
        try:
            with psycopg2.connect(self.conn_string) as conn:
                with conn.cursor(cursor_factory=DictCursor) as cur:
                    cur.execute("""
                        SELECT u.*, r.name as role_name
                        FROM users u
                        JOIN roles r ON u.role_id = r.id
                        WHERE u.username = %s AND u.status = 'active'
                    """, (username,))
                    user = cur.fetchone()

                    if user and pwd_context.verify(password, user['password_hash']):
                        return dict(user)
                    return None

        except psycopg2.Error:
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