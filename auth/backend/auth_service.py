#!/usr/bin/env python3
"""
AWS Cost Optimizer - Authentication Service
Comprehensive authentication system with MFA, OAuth, and security features
"""

import asyncio
import json
import logging
import hashlib
import secrets
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import jwt
import bcrypt
import pyotp
import qrcode
from io import BytesIO
import base64
import boto3
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import sqlite3
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UserRole(Enum):
    """User role enumeration"""
    ADMIN = "admin"
    MANAGER = "manager"
    ANALYST = "analyst"
    VIEWER = "viewer"
    GUEST = "guest"

class AuthStatus(Enum):
    """Authentication status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING_VERIFICATION = "pending_verification"
    LOCKED = "locked"

class MFAMethod(Enum):
    """MFA method enumeration"""
    TOTP = "totp"
    SMS = "sms"
    EMAIL = "email"
    BIOMETRIC = "biometric"
    HARDWARE_KEY = "hardware_key"

@dataclass
class User:
    """User data structure"""
    id: str
    email: str
    username: str
    password_hash: str
    role: UserRole
    status: AuthStatus
    mfa_enabled: bool
    mfa_methods: List[MFAMethod]
    totp_secret: Optional[str]
    phone_number: Optional[str]
    created_at: datetime
    last_login: Optional[datetime]
    failed_login_attempts: int
    locked_until: Optional[datetime]
    email_verified: bool
    phone_verified: bool
    metadata: Dict[str, Any]

@dataclass
class Session:
    """Session data structure"""
    id: str
    user_id: str
    token: str
    refresh_token: str
    expires_at: datetime
    created_at: datetime
    ip_address: str
    user_agent: str
    is_active: bool
    mfa_verified: bool

@dataclass
class MFASetup:
    """MFA setup data structure"""
    user_id: str
    method: MFAMethod
    secret: str
    qr_code: str
    backup_codes: List[str]
    created_at: datetime

class AuthenticationService:
    """Comprehensive authentication service"""
    
    def __init__(self, secret_key: str, db_path: str = "auth.db"):
        """Initialize authentication service"""
        self.secret_key = secret_key
        self.db_path = db_path
        self.jwt_algorithm = "HS256"
        self.token_expiry = 3600  # 1 hour
        self.refresh_token_expiry = 7 * 24 * 3600  # 7 days
        
        # External services
        self.ses_client = boto3.client('ses')
        self.sns_client = boto3.client('sns')
        
        # Initialize database
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database for authentication"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    email TEXT UNIQUE NOT NULL,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    role TEXT NOT NULL,
                    status TEXT NOT NULL,
                    mfa_enabled BOOLEAN DEFAULT FALSE,
                    mfa_methods TEXT DEFAULT '[]',
                    totp_secret TEXT,
                    phone_number TEXT,
                    created_at TEXT NOT NULL,
                    last_login TEXT,
                    failed_login_attempts INTEGER DEFAULT 0,
                    locked_until TEXT,
                    email_verified BOOLEAN DEFAULT FALSE,
                    phone_verified BOOLEAN DEFAULT FALSE,
                    metadata TEXT DEFAULT '{}'
                )
            ''')
            
            # Create sessions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sessions (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    token TEXT NOT NULL,
                    refresh_token TEXT NOT NULL,
                    expires_at TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    ip_address TEXT,
                    user_agent TEXT,
                    is_active BOOLEAN DEFAULT TRUE,
                    mfa_verified BOOLEAN DEFAULT FALSE,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            # Create mfa_setups table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS mfa_setups (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    method TEXT NOT NULL,
                    secret TEXT NOT NULL,
                    qr_code TEXT,
                    backup_codes TEXT,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            # Create login_attempts table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS login_attempts (
                    id TEXT PRIMARY KEY,
                    user_id TEXT,
                    email TEXT,
                    ip_address TEXT,
                    user_agent TEXT,
                    success BOOLEAN NOT NULL,
                    failure_reason TEXT,
                    timestamp TEXT NOT NULL
                )
            ''')
            
            # Create password_resets table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS password_resets (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    token TEXT NOT NULL,
                    expires_at TEXT NOT NULL,
                    used BOOLEAN DEFAULT FALSE,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            conn.commit()
            conn.close()
            
            logger.info("Authentication database initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing authentication database: {e}")
    
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        try:
            salt = bcrypt.gensalt()
            hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
            return hashed.decode('utf-8')
        except Exception as e:
            logger.error(f"Error hashing password: {e}")
            raise
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash"""
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
        except Exception as e:
            logger.error(f"Error verifying password: {e}")
            return False
    
    def generate_jwt_token(self, user_id: str, role: str, expires_in: int = None) -> str:
        """Generate JWT token"""
        try:
            if expires_in is None:
                expires_in = self.token_expiry
            
            payload = {
                'user_id': user_id,
                'role': role,
                'exp': datetime.utcnow() + timedelta(seconds=expires_in),
                'iat': datetime.utcnow(),
                'iss': 'aws-cost-optimizer'
            }
            
            token = jwt.encode(payload, self.secret_key, algorithm=self.jwt_algorithm)
            return token
        except Exception as e:
            logger.error(f"Error generating JWT token: {e}")
            raise
    
    def verify_jwt_token(self, token: str) -> Dict[str, Any]:
        """Verify JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.jwt_algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise ValueError("Token has expired")
        except jwt.InvalidTokenError:
            raise ValueError("Invalid token")
        except Exception as e:
            logger.error(f"Error verifying JWT token: {e}")
            raise
    
    def generate_refresh_token(self) -> str:
        """Generate refresh token"""
        return secrets.token_urlsafe(32)
    
    def create_user(self, email: str, username: str, password: str, 
                   role: UserRole = UserRole.VIEWER) -> User:
        """Create new user"""
        try:
            # Check if user already exists
            if self.get_user_by_email(email):
                raise ValueError("User with this email already exists")
            
            if self.get_user_by_username(username):
                raise ValueError("User with this username already exists")
            
            # Hash password
            password_hash = self.hash_password(password)
            
            # Create user
            user = User(
                id=str(uuid.uuid4()),
                email=email,
                username=username,
                password_hash=password_hash,
                role=role,
                status=AuthStatus.PENDING_VERIFICATION,
                mfa_enabled=False,
                mfa_methods=[],
                totp_secret=None,
                phone_number=None,
                created_at=datetime.now(),
                last_login=None,
                failed_login_attempts=0,
                locked_until=None,
                email_verified=False,
                phone_verified=False,
                metadata={}
            )
            
            # Store in database
            self.store_user(user)
            
            # Send verification email
            self.send_verification_email(user)
            
            logger.info(f"User created: {user.email}")
            return user
            
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            raise
    
    def authenticate_user(self, email: str, password: str, 
                         ip_address: str = None, user_agent: str = None) -> Tuple[User, Session]:
        """Authenticate user with email and password"""
        try:
            # Get user
            user = self.get_user_by_email(email)
            if not user:
                self.log_login_attempt(None, email, ip_address, user_agent, False, "User not found")
                raise ValueError("Invalid credentials")
            
            # Check if user is locked
            if user.locked_until and datetime.now() < user.locked_until:
                self.log_login_attempt(user.id, email, ip_address, user_agent, False, "Account locked")
                raise ValueError("Account is locked")
            
            # Check if user is active
            if user.status != AuthStatus.ACTIVE:
                self.log_login_attempt(user.id, email, ip_address, user_agent, False, "Account not active")
                raise ValueError("Account is not active")
            
            # Verify password
            if not self.verify_password(password, user.password_hash):
                # Increment failed attempts
                user.failed_login_attempts += 1
                
                # Lock account after 5 failed attempts
                if user.failed_login_attempts >= 5:
                    user.locked_until = datetime.now() + timedelta(minutes=30)
                
                self.update_user(user)
                self.log_login_attempt(user.id, email, ip_address, user_agent, False, "Invalid password")
                raise ValueError("Invalid credentials")
            
            # Reset failed attempts on successful login
            user.failed_login_attempts = 0
            user.locked_until = None
            user.last_login = datetime.now()
            self.update_user(user)
            
            # Create session
            session = self.create_session(user, ip_address, user_agent)
            
            # Log successful login
            self.log_login_attempt(user.id, email, ip_address, user_agent, True, "Login successful")
            
            logger.info(f"User authenticated: {user.email}")
            return user, session
            
        except Exception as e:
            logger.error(f"Error authenticating user: {e}")
            raise
    
    def create_session(self, user: User, ip_address: str = None, 
                      user_agent: str = None) -> Session:
        """Create user session"""
        try:
            # Generate tokens
            access_token = self.generate_jwt_token(user.id, user.role.value)
            refresh_token = self.generate_refresh_token()
            
            # Create session
            session = Session(
                id=str(uuid.uuid4()),
                user_id=user.id,
                token=access_token,
                refresh_token=refresh_token,
                expires_at=datetime.now() + timedelta(seconds=self.token_expiry),
                created_at=datetime.now(),
                ip_address=ip_address,
                user_agent=user_agent,
                is_active=True,
                mfa_verified=not user.mfa_enabled  # MFA not required if not enabled
            )
            
            # Store session
            self.store_session(session)
            
            return session
            
        except Exception as e:
            logger.error(f"Error creating session: {e}")
            raise
    
    def refresh_session(self, refresh_token: str) -> Session:
        """Refresh user session"""
        try:
            # Get session by refresh token
            session = self.get_session_by_refresh_token(refresh_token)
            if not session or not session.is_active:
                raise ValueError("Invalid refresh token")
            
            # Check if session is expired
            if datetime.now() > session.expires_at:
                session.is_active = False
                self.update_session(session)
                raise ValueError("Session expired")
            
            # Get user
            user = self.get_user_by_id(session.user_id)
            if not user:
                raise ValueError("User not found")
            
            # Generate new tokens
            new_access_token = self.generate_jwt_token(user.id, user.role.value)
            new_refresh_token = self.generate_refresh_token()
            
            # Update session
            session.token = new_access_token
            session.refresh_token = new_refresh_token
            session.expires_at = datetime.now() + timedelta(seconds=self.token_expiry)
            session.mfa_verified = not user.mfa_enabled
            
            self.update_session(session)
            
            return session
            
        except Exception as e:
            logger.error(f"Error refreshing session: {e}")
            raise
    
    def setup_mfa_totp(self, user_id: str) -> MFASetup:
        """Setup TOTP MFA for user"""
        try:
            # Generate TOTP secret
            secret = pyotp.random_base32()
            
            # Create TOTP object
            totp = pyotp.TOTP(secret)
            
            # Generate QR code
            qr_code = self.generate_qr_code(user.email, secret)
            
            # Generate backup codes
            backup_codes = [secrets.token_hex(4).upper() for _ in range(10)]
            
            # Create MFA setup
            mfa_setup = MFASetup(
                id=str(uuid.uuid4()),
                user_id=user_id,
                method=MFAMethod.TOTP,
                secret=secret,
                qr_code=qr_code,
                backup_codes=backup_codes,
                created_at=datetime.now()
            )
            
            # Store MFA setup
            self.store_mfa_setup(mfa_setup)
            
            return mfa_setup
            
        except Exception as e:
            logger.error(f"Error setting up TOTP MFA: {e}")
            raise
    
    def verify_mfa_totp(self, user_id: str, token: str) -> bool:
        """Verify TOTP MFA token"""
        try:
            # Get user's TOTP secret
            user = self.get_user_by_id(user_id)
            if not user or not user.totp_secret:
                return False
            
            # Create TOTP object
            totp = pyotp.TOTP(user.totp_secret)
            
            # Verify token
            return totp.verify(token, valid_window=1)
            
        except Exception as e:
            logger.error(f"Error verifying TOTP token: {e}")
            return False
    
    def generate_qr_code(self, email: str, secret: str) -> str:
        """Generate QR code for TOTP setup"""
        try:
            # Create TOTP URI
            totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
                name=email,
                issuer_name="AWS Cost Optimizer"
            )
            
            # Generate QR code
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(totp_uri)
            qr.make(fit=True)
            
            # Create image
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Convert to base64
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            img_str = base64.b64encode(buffer.getvalue()).decode()
            
            return f"data:image/png;base64,{img_str}"
            
        except Exception as e:
            logger.error(f"Error generating QR code: {e}")
            raise
    
    def send_verification_email(self, user: User):
        """Send email verification"""
        try:
            # Generate verification token
            verification_token = secrets.token_urlsafe(32)
            
            # Create verification link
            verification_link = f"https://awscostoptimizer.com/verify-email?token={verification_token}"
            
            # Create email content
            subject = "Verify Your Email - AWS Cost Optimizer"
            body = f"""
            Hello {user.username},
            
            Please verify your email address by clicking the link below:
            
            {verification_link}
            
            This link will expire in 24 hours.
            
            If you didn't create an account, please ignore this email.
            
            Best regards,
            AWS Cost Optimizer Team
            """
            
            # Send email via SES
            self.ses_client.send_email(
                Source='noreply@awscostoptimizer.com',
                Destination={'ToAddresses': [user.email]},
                Message={
                    'Subject': {'Data': subject},
                    'Body': {'Text': {'Data': body}}
                }
            )
            
            logger.info(f"Verification email sent to {user.email}")
            
        except Exception as e:
            logger.error(f"Error sending verification email: {e}")
    
    def send_password_reset_email(self, user: User):
        """Send password reset email"""
        try:
            # Generate reset token
            reset_token = secrets.token_urlsafe(32)
            
            # Store reset token
            self.store_password_reset_token(user.id, reset_token)
            
            # Create reset link
            reset_link = f"https://awscostoptimizer.com/reset-password?token={reset_token}"
            
            # Create email content
            subject = "Reset Your Password - AWS Cost Optimizer"
            body = f"""
            Hello {user.username},
            
            You requested to reset your password. Click the link below to reset it:
            
            {reset_link}
            
            This link will expire in 1 hour.
            
            If you didn't request this, please ignore this email.
            
            Best regards,
            AWS Cost Optimizer Team
            """
            
            # Send email via SES
            self.ses_client.send_email(
                Source='noreply@awscostoptimizer.com',
                Destination={'ToAddresses': [user.email]},
                Message={
                    'Subject': {'Data': subject},
                    'Body': {'Text': {'Data': body}}
                }
            )
            
            logger.info(f"Password reset email sent to {user.email}")
            
        except Exception as e:
            logger.error(f"Error sending password reset email: {e}")
    
    def store_user(self, user: User):
        """Store user in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO users 
                (id, email, username, password_hash, role, status, mfa_enabled, 
                 mfa_methods, totp_secret, phone_number, created_at, last_login, 
                 failed_login_attempts, locked_until, email_verified, phone_verified, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user.id, user.email, user.username, user.password_hash, 
                user.role.value, user.status.value, user.mfa_enabled,
                json.dumps([m.value for m in user.mfa_methods]), user.totp_secret,
                user.phone_number, user.created_at.isoformat(), 
                user.last_login.isoformat() if user.last_login else None,
                user.failed_login_attempts, user.locked_until.isoformat() if user.locked_until else None,
                user.email_verified, user.phone_verified, json.dumps(user.metadata)
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error storing user: {e}")
            raise
    
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return self.row_to_user(row)
            return None
            
        except Exception as e:
            logger.error(f"Error getting user by ID: {e}")
            return None
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return self.row_to_user(row)
            return None
            
        except Exception as e:
            logger.error(f"Error getting user by email: {e}")
            return None
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return self.row_to_user(row)
            return None
            
        except Exception as e:
            logger.error(f"Error getting user by username: {e}")
            return None
    
    def row_to_user(self, row) -> User:
        """Convert database row to User object"""
        return User(
            id=row[0],
            email=row[1],
            username=row[2],
            password_hash=row[3],
            role=UserRole(row[4]),
            status=AuthStatus(row[5]),
            mfa_enabled=bool(row[6]),
            mfa_methods=[MFAMethod(m) for m in json.loads(row[7])],
            totp_secret=row[8],
            phone_number=row[9],
            created_at=datetime.fromisoformat(row[10]),
            last_login=datetime.fromisoformat(row[11]) if row[11] else None,
            failed_login_attempts=row[12],
            locked_until=datetime.fromisoformat(row[13]) if row[13] else None,
            email_verified=bool(row[14]),
            phone_verified=bool(row[15]),
            metadata=json.loads(row[16])
        )
    
    def update_user(self, user: User):
        """Update user in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE users SET 
                email = ?, username = ?, password_hash = ?, role = ?, status = ?,
                mfa_enabled = ?, mfa_methods = ?, totp_secret = ?, phone_number = ?,
                last_login = ?, failed_login_attempts = ?, locked_until = ?,
                email_verified = ?, phone_verified = ?, metadata = ?
                WHERE id = ?
            ''', (
                user.email, user.username, user.password_hash, user.role.value,
                user.status.value, user.mfa_enabled, 
                json.dumps([m.value for m in user.mfa_methods]), user.totp_secret,
                user.phone_number, user.last_login.isoformat() if user.last_login else None,
                user.failed_login_attempts, user.locked_until.isoformat() if user.locked_until else None,
                user.email_verified, user.phone_verified, json.dumps(user.metadata), user.id
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error updating user: {e}")
            raise
    
    def store_session(self, session: Session):
        """Store session in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO sessions 
                (id, user_id, token, refresh_token, expires_at, created_at, 
                 ip_address, user_agent, is_active, mfa_verified)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                session.id, session.user_id, session.token, session.refresh_token,
                session.expires_at.isoformat(), session.created_at.isoformat(),
                session.ip_address, session.user_agent, session.is_active, session.mfa_verified
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error storing session: {e}")
            raise
    
    def get_session_by_token(self, token: str) -> Optional[Session]:
        """Get session by token"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM sessions WHERE token = ? AND is_active = TRUE', (token,))
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return self.row_to_session(row)
            return None
            
        except Exception as e:
            logger.error(f"Error getting session by token: {e}")
            return None
    
    def get_session_by_refresh_token(self, refresh_token: str) -> Optional[Session]:
        """Get session by refresh token"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM sessions WHERE refresh_token = ? AND is_active = TRUE', (refresh_token,))
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return self.row_to_session(row)
            return None
            
        except Exception as e:
            logger.error(f"Error getting session by refresh token: {e}")
            return None
    
    def row_to_session(self, row) -> Session:
        """Convert database row to Session object"""
        return Session(
            id=row[0],
            user_id=row[1],
            token=row[2],
            refresh_token=row[3],
            expires_at=datetime.fromisoformat(row[4]),
            created_at=datetime.fromisoformat(row[5]),
            ip_address=row[6],
            user_agent=row[7],
            is_active=bool(row[8]),
            mfa_verified=bool(row[9])
        )
    
    def update_session(self, session: Session):
        """Update session in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE sessions SET 
                token = ?, refresh_token = ?, expires_at = ?, is_active = ?, mfa_verified = ?
                WHERE id = ?
            ''', (
                session.token, session.refresh_token, session.expires_at.isoformat(),
                session.is_active, session.mfa_verified, session.id
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error updating session: {e}")
            raise
    
    def log_login_attempt(self, user_id: str, email: str, ip_address: str, 
                         user_agent: str, success: bool, failure_reason: str = None):
        """Log login attempt"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO login_attempts 
                (id, user_id, email, ip_address, user_agent, success, failure_reason, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                str(uuid.uuid4()), user_id, email, ip_address, user_agent,
                success, failure_reason, datetime.now().isoformat()
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error logging login attempt: {e}")
    
    def store_mfa_setup(self, mfa_setup: MFASetup):
        """Store MFA setup in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO mfa_setups 
                (id, user_id, method, secret, qr_code, backup_codes, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                mfa_setup.id, mfa_setup.user_id, mfa_setup.method.value,
                mfa_setup.secret, mfa_setup.qr_code, 
                json.dumps(mfa_setup.backup_codes), mfa_setup.created_at.isoformat()
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error storing MFA setup: {e}")
            raise
    
    def store_password_reset_token(self, user_id: str, token: str):
        """Store password reset token"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO password_resets 
                (id, user_id, token, expires_at, created_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                str(uuid.uuid4()), user_id, token,
                (datetime.now() + timedelta(hours=1)).isoformat(),
                datetime.now().isoformat()
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error storing password reset token: {e}")
            raise

# Example usage
if __name__ == "__main__":
    # Create authentication service
    auth_service = AuthenticationService(secret_key="your-secret-key-here")
    
    # Create user
    user = auth_service.create_user(
        email="admin@example.com",
        username="admin",
        password="password123",
        role=UserRole.ADMIN
    )
    
    print(f"User created: {user.email}")
    
    # Authenticate user
    user, session = auth_service.authenticate_user("admin@example.com", "password123")
    print(f"User authenticated: {user.email}")
    print(f"Session token: {session.token[:20]}...")
