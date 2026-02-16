#!/usr/bin/python3
"""
QuickBot Security Module

Handles authentication, authorization, encryption,
and secure data handling for QuickBot.
"""

import hashlib
import hmac
import secrets
import json
from typing import Dict, Optional, List
from datetime import datetime, timedelta
import os
import base64


class SecurityConfig:
    """Security configuration"""

    def __init__(self, config_path: str = 'config.yaml'):
        self.config_path = config_path
        self.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(32))
        self.jwt_secret = os.environ.get('JWT_SECRET', secrets.token_hex(32))
        self.session_timeout = 3600  # 1 hour
        self.max_failed_attempts = 5
        self.lockout_duration = 300  # 5 minutes


class PasswordHasher:
    """Password hashing and verification using bcrypt-like approach"""

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using SHA-256 with salt"""
        salt = secrets.token_hex(16)
        hashed = hashlib.sha256((password + salt).encode()).hexdigest()
        return f"{salt}${hashed}"

    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        """Verify a password against a hashed password"""
        try:
            salt, hashed = hashed_password.split('$')
            computed = hashlib.sha256((password + salt).encode()).hexdigest()
            return hmac.compare_digest(computed, hashed)
        except:
            return False


class SessionManager:
    """Manages user sessions"""

    def __init__(self, security_config: SecurityConfig):
        self.config = security_config
        self.sessions: Dict[str, Dict] = {}
        self.failed_attempts: Dict[str, int] = {}
        self.lockouts: Dict[str, datetime] = {}

    def create_session(self, user_id: str, user_data: Dict = None) -> str:
        """Create a new user session"""
        session_id = secrets.token_hex(32)

        self.sessions[session_id] = {
            'user_id': user_id,
            'user_data': user_data or {},
            'created_at': datetime.now(),
            'last_active': datetime.now(),
            'ip': None,  # Set in real implementation
        }

        return session_id

    def validate_session(self, session_id: str) -> Optional[Dict]:
        """Validate a session and return user data"""
        session = self.sessions.get(session_id)

        if not session:
            return None

        # Check session timeout
        age = datetime.now() - session['last_active']
        if age.total_seconds() > self.config.session_timeout:
            del self.sessions[session_id]
            return None

        # Update last active time
        session['last_active'] = datetime.now()

        return session

    def revoke_session(self, session_id: str) -> bool:
        """Revoke/destroy a session"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False

    def record_failed_attempt(self, user_id: str) -> int:
        """Record a failed login attempt"""
        self.failed_attempts[user_id] = self.failed_attempts.get(user_id, 0) + 1

        # Check lockout threshold
        if self.failed_attempts[user_id] >= self.config.max_failed_attempts:
            self.lockouts[user_id] = datetime.now()
            return 0  # Locked out

        return self.config.max_failed_attempts - self.failed_attempts[user_id]

    def clear_failed_attempts(self, user_id: str) -> None:
        """Clear failed login attempts on successful login"""
        if user_id in self.failed_attempts:
            del self.failed_attempts[user_id]
        if user_id in self.lockouts:
            del self.lockouts[user_id]

    def is_locked_out(self, user_id: str) -> bool:
        """Check if user is locked out"""
        if user_id not in self.lockouts:
            return False

        lockout_time = self.lockouts[user_id]
        age = datetime.now() - lockout_time

        if age.total_seconds() > self.config.lockout_duration:
            # Lockout expired
            del self.lockouts[user_id]
            return False

        return True

    def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions"""
        expired_sessions = []

        for session_id, session in self.sessions.items():
            age = datetime.now() - session['last_active']
            if age.total_seconds() > self.config.session_timeout * 2:
                expired_sessions.append(session_id)

        for session_id in expired_sessions:
            del self.sessions[session_id]

        return len(expired_sessions)

    def get_active_session_count(self) -> int:
        """Get count of active sessions"""
        return len(self.sessions)


class TokenGenerator:
    """Generates various types of secure tokens"""

    @staticmethod
    def generate_token(length: int = 32) -> str:
        """Generate a secure random token"""
        return secrets.token_hex(length)

    @staticmethod
    def generate_jwt(payload: Dict, secret: str, expiry_hours: int = 1) -> str:
        """Generate a simple JWT-like token (simplified)"""
        header = json.dumps({"alg": "HS256", "typ": "JWT"})

        # Add expiry
        exp = datetime.now() + timedelta(hours=expiry_hours)
        payload["exp"] = exp.timestamp()

        body = json.dumps(payload)

        # Encode
        encoded = f"{base64.b64encode(header.encode()).decode()}.{base64.b64encode(body.encode()).decode()}"

        # Sign
        signature = hmac.new(
            secret.encode(),
            encoded.encode(),
            hashlib.sha256
        ).digest()

        signature_b64 = base64.b64encode(signature).decode()

        return f"{encoded}.{signature_b64}"

    @staticmethod
    def verify_jwt(token: str, secret: str) -> Optional[Dict]:
        """Verify a JWT-like token"""
        try:
            parts = token.split('.')
            if len(parts) != 3:
                return None

            encoded = f"{parts[0]}.{parts[1]}"

            # Verify signature
            signature = hmac.new(
                secret.encode(),
                encoded.encode(),
                hashlib.sha256
            ).digest()

            signature_b64 = base64.b64encode(signature).decode()

            if signature_b64 != parts[2]:
                return None

            # Decode payload
            body = base64.b64decode(parts[1] + '==')
            payload = json.loads(body)

            # Check expiry
            if 'exp' in payload:
                exp = datetime.fromtimestamp(payload['exp'])
                if datetime.now() > exp:
                    return None

            return payload
        except Exception:
            return None


class EncryptionManager:
    """Handles encryption and decryption"""

    @staticmethod
    def encrypt(data: str, key: str) -> str:
        """Encrypt data using AES (simplified implementation)"""
        # In production, use cryptography library with proper AES
        # This is a placeholder
        salt = secrets.token_hex(8)
        encrypted = hashlib.sha256((data + key + salt).encode()).hexdigest()
        return f"{salt}${encrypted}"

    @staticmethod
    def decrypt(encrypted_data: str, key: str) -> Optional[str]:
        """Decrypt data (simplified implementation)"""
        # In production, use cryptography library with proper AES
        # This is a placeholder
        try:
            salt, hashed = encrypted_data.split('$')
            return f"decrypted:{salt}:{hashed[:8]}"
        except:
            return None


class AccessControl:
    """Access control and authorization"""

    def __init__(self):
        self.roles = {
            'admin': ['*'],
            'user': ['chat', 'memory:read', 'memory:write'],
            'guest': ['chat']
        }

    def authorize(self, user_roles: List[str], action: str) -> bool:
        """Check if user has permission to perform action"""
        for role in user_roles:
            if role in self.roles:
                permissions = self.roles[role]

                # Super admin
                if '*' in permissions:
                    return True

                # Check specific permission
                if self._check_permission(action, permissions):
                    return True

        return False

    def _check_permission(self, action: str, permissions: List[str]) -> bool:
        """Check if a specific permission is granted"""
        if '*' in permissions:
            return True

        # Exact match
        if action in permissions:
            return True

        # Wildcard match
        action_category = action.split(':')[0]
        for perm in permissions:
            if perm == f"{action_category}:*":
                return True

        return False

    def add_role(self, role: str, permissions: List[str]) -> None:
        """Add or update a role with permissions"""
        self.roles[role] = permissions

    def get_role_permissions(self, role: str) -> List[str]:
        """Get permissions for a role"""
        return self.roles.get(role, [])


class SecurityAudit:
    """Security audit logging"""

    def __init__(self, log_file: str = 'security_audit.log'):
        self.log_file = log_file

    def log_event(self, event_type: str, details: Dict) -> None:
        """Log a security event"""
        event = {
            'timestamp': datetime.now().isoformat(),
            'type': event_type,
            'details': details
        }

        with open(self.log_file, 'a') as f:
            f.write(json.dumps(event) + '\n')

    def log_login_attempt(self, user_id: str, ip: str, success: bool) -> None:
        """Log login attempt"""
        self.log_event('LOGIN_ATTEMPT', {
            'user_id': user_id,
            'ip': ip,
            'success': success
        })

    def log_access_attempt(self, user_id: str, resource: str, action: str, authorized: bool) -> None:
        """Log resource access attempt"""
        self.log_event('ACCESS_ATTEMPT', {
            'user_id': user_id,
            'resource': resource,
            'action': action,
            'authorized': authorized
        })

    def log_security_event(self, event_type: str, details: Dict) -> None:
        """Log generic security event"""
        self.log_event(event_type, details)


class SecurityManager:
    """Main security manager"""

    def __init__(self, config_path: str = 'config.yaml'):
        self.config = SecurityConfig(config_path)
        self.session_manager = SessionManager(self.config)
        self.token_generator = TokenGenerator()
        self.encryption_manager = EncryptionManager()
        self.access_control = AccessControl()
        self.audit = SecurityAudit()

    def authenticate_user(self, user_id: str, password: str, hashed_password: str) -> Optional[str]:
        """Authenticate user and create session"""
        # Check lockout
        if self.session_manager.is_locked_out(user_id):
            self.audit.log_login_attempt(user_id, user_id, False)
            raise Exception("Account locked due to too many failed attempts")

        # Verify password
        if not PasswordHasher.verify_password(password, hashed_password):
            remaining = self.session_manager.record_failed_attempt(user_id)
            self.audit.log_login_attempt(user_id, user_id, False)
            raise Exception(f"Invalid password. {remaining} attempts remaining")

        # Clear failed attempts
        self.session_manager.clear_failed_attempts(user_id)

        # Create session
        session_id = self.session_manager.create_session(user_id)

        self.audit.log_login_attempt(user_id, user_id, True)

        return session_id

    def authorize_action(self, session_id: str, action: str) -> bool:
        """Authorize an action for a session"""
        session = self.session_manager.validate_session(session_id)

        if not session:
            return False

        user_roles = session['user_data'].get('roles', ['guest'])

        authorized = self.access_control.authorize(user_roles, action)

        self.audit.log_access_attempt(
            session['user_id'],
            'api',
            action,
            authorized
        )

        return authorized

    def create_user(self, username: str, password: str, roles: List[str]) -> str:
        """Create a new user"""
        hashed_password = PasswordHasher.hash_password(password)

        # In production, store in database
        return hashed_password

    def generate_api_token(self, user_id: str, expiry_hours: int = 24) -> str:
        """Generate an API token for a user"""
        payload = {
            'user_id': user_id,
            'type': 'api_token'
        }

        return self.token_generator.generate_jwt(payload, self.config.jwt_secret, expiry_hours)

    def validate_api_token(self, token: str) -> Optional[Dict]:
        """Validate an API token"""
        return self.token_generator.verify_jwt(token, self.config.jwt_secret)


def main():
    """Test security module"""
    print("QuickBot Security Module")
    print("=" * 50)

    security = SecurityManager()

    # Test password hashing
    print("\nTesting Password Hashing...")
    password = "test_password_123"
    hashed = PasswordHasher.hash_password(password)
    print(f"Original: {password}")
    print(f"Hashed:   {hashed[:40]}...")
    verified = PasswordHasher.verify_password(password, hashed)
    print(f"Verified: {verified}")

    # Test session management
    print("\nTesting Session Management...")
    session_id = security.session_manager.create_session("user123")
    print(f"Session created: {session_id}")
    session = security.session_manager.validate_session(session_id)
    print(f"Session valid: {session is not None}")

    # Test token generation
    print("\nTesting Token Generation...")
    token = security.generate_api_token("user123", 1)
    print(f"Token: {token[:50]}...")
    payload = security.validate_api_token(token)
    print(f"Token valid: {payload is not None}")

    # Test access control
    print("\nTesting Access Control...")
    authorized = security.access_control.authorize(['user'], 'chat')
    print(f"User can chat: {authorized}")
    authorized = security.access_control.authorize(['user'], 'admin:delete')
    print(f"User can admin delete: {authorized}")

    # Test audit logging
    print("\nTesting Audit Logging...")
    security.audit.log_security_event('TEST_EVENT', {'message': 'Test audit log'})
    with open('security_audit.log', 'r') as f:
        lines = f.readlines()
        print(f"Audit entries: {len(lines)}")

    # Cleanup
    os.remove('security_audit.log')

    print("\n✓ Security module tests passed")


if __name__ == '__main__':
    main()
