#!/usr/bin/env python3
"""
AWS Cost Optimizer - OAuth Integration
Handles OAuth integration with Google, Microsoft, and AWS SSO
"""

import asyncio
import json
import logging
import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import httpx
import jwt
from urllib.parse import urlencode, parse_qs

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OAuthProvider(Enum):
    """OAuth provider enumeration"""
    GOOGLE = "google"
    MICROSOFT = "microsoft"
    AWS_SSO = "aws_sso"
    GITHUB = "github"

class OAuthScope(Enum):
    """OAuth scope enumeration"""
    PROFILE = "profile"
    EMAIL = "email"
    OPENID = "openid"
    AWS_BILLING = "aws-billing"
    AWS_COST_EXPLORER = "ce:GetCostAndUsage"

@dataclass
class OAuthConfig:
    """OAuth configuration"""
    provider: OAuthProvider
    client_id: str
    client_secret: str
    redirect_uri: str
    scopes: List[str]
    auth_url: str
    token_url: str
    user_info_url: str
    jwks_url: Optional[str] = None

@dataclass
class OAuthUser:
    """OAuth user data"""
    provider: OAuthProvider
    provider_id: str
    email: str
    name: str
    picture: Optional[str]
    verified: bool
    metadata: Dict[str, Any]

@dataclass
class OAuthToken:
    """OAuth token data"""
    access_token: str
    refresh_token: Optional[str]
    token_type: str
    expires_in: int
    scope: str
    expires_at: datetime

class OAuthIntegration:
    """OAuth integration service"""
    
    def __init__(self):
        """Initialize OAuth integration"""
        self.configs = self.load_oauth_configs()
        self.state_store = {}  # In production, use Redis or database
    
    def load_oauth_configs(self) -> Dict[OAuthProvider, OAuthConfig]:
        """Load OAuth configurations"""
        return {
            OAuthProvider.GOOGLE: OAuthConfig(
                provider=OAuthProvider.GOOGLE,
                client_id="your-google-client-id",
                client_secret="your-google-client-secret",
                redirect_uri="https://awscostoptimizer.com/auth/callback/google",
                scopes=["openid", "profile", "email"],
                auth_url="https://accounts.google.com/o/oauth2/v2/auth",
                token_url="https://oauth2.googleapis.com/token",
                user_info_url="https://www.googleapis.com/oauth2/v2/userinfo",
                jwks_url="https://www.googleapis.com/oauth2/v3/certs"
            ),
            OAuthProvider.MICROSOFT: OAuthConfig(
                provider=OAuthProvider.MICROSOFT,
                client_id="your-microsoft-client-id",
                client_secret="your-microsoft-client-secret",
                redirect_uri="https://awscostoptimizer.com/auth/callback/microsoft",
                scopes=["openid", "profile", "email", "User.Read"],
                auth_url="https://login.microsoftonline.com/common/oauth2/v2.0/authorize",
                token_url="https://login.microsoftonline.com/common/oauth2/v2.0/token",
                user_info_url="https://graph.microsoft.com/v1.0/me",
                jwks_url="https://login.microsoftonline.com/common/discovery/v2.0/keys"
            ),
            OAuthProvider.AWS_SSO: OAuthConfig(
                provider=OAuthProvider.AWS_SSO,
                client_id="your-aws-sso-client-id",
                client_secret="your-aws-sso-client-secret",
                redirect_uri="https://awscostoptimizer.com/auth/callback/aws-sso",
                scopes=["openid", "profile", "email", "aws-billing"],
                auth_url="https://your-org.auth.us-east-1.amazoncognito.com/oauth2/authorize",
                token_url="https://your-org.auth.us-east-1.amazoncognito.com/oauth2/token",
                user_info_url="https://your-org.auth.us-east-1.amazoncognito.com/oauth2/userInfo"
            ),
            OAuthProvider.GITHUB: OAuthConfig(
                provider=OAuthProvider.GITHUB,
                client_id="your-github-client-id",
                client_secret="your-github-client-secret",
                redirect_uri="https://awscostoptimizer.com/auth/callback/github",
                scopes=["user:email", "read:user"],
                auth_url="https://github.com/login/oauth/authorize",
                token_url="https://github.com/login/oauth/access_token",
                user_info_url="https://api.github.com/user"
            )
        }
    
    def generate_auth_url(self, provider: OAuthProvider, state: str = None) -> str:
        """Generate OAuth authorization URL"""
        try:
            config = self.configs[provider]
            
            if not state:
                state = secrets.token_urlsafe(32)
                self.state_store[state] = {
                    'provider': provider,
                    'timestamp': datetime.now(),
                    'used': False
                }
            
            params = {
                'client_id': config.client_id,
                'redirect_uri': config.redirect_uri,
                'scope': ' '.join(config.scopes),
                'response_type': 'code',
                'state': state,
                'access_type': 'offline' if provider == OAuthProvider.GOOGLE else None,
                'prompt': 'consent' if provider == OAuthProvider.GOOGLE else None
            }
            
            # Remove None values
            params = {k: v for k, v in params.items() if v is not None}
            
            auth_url = f"{config.auth_url}?{urlencode(params)}"
            
            logger.info(f"Generated auth URL for {provider.value}: {auth_url}")
            return auth_url
            
        except Exception as e:
            logger.error(f"Error generating auth URL for {provider.value}: {e}")
            raise
    
    async def exchange_code_for_token(self, provider: OAuthProvider, code: str, 
                                    state: str = None) -> OAuthToken:
        """Exchange authorization code for access token"""
        try:
            config = self.configs[provider]
            
            # Verify state if provided
            if state and state in self.state_store:
                if self.state_store[state]['used']:
                    raise ValueError("State has already been used")
                if self.state_store[state]['provider'] != provider:
                    raise ValueError("Invalid state for provider")
                self.state_store[state]['used'] = True
            
            # Prepare token request
            data = {
                'client_id': config.client_id,
                'client_secret': config.client_secret,
                'code': code,
                'redirect_uri': config.redirect_uri,
                'grant_type': 'authorization_code'
            }
            
            headers = {
                'Accept': 'application/json',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            # Make token request
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    config.token_url,
                    data=data,
                    headers=headers
                )
                response.raise_for_status()
                
                token_data = response.json()
            
            # Create OAuth token
            oauth_token = OAuthToken(
                access_token=token_data['access_token'],
                refresh_token=token_data.get('refresh_token'),
                token_type=token_data.get('token_type', 'Bearer'),
                expires_in=token_data.get('expires_in', 3600),
                scope=token_data.get('scope', ''),
                expires_at=datetime.now() + timedelta(seconds=token_data.get('expires_in', 3600))
            )
            
            logger.info(f"Token exchanged successfully for {provider.value}")
            return oauth_token
            
        except Exception as e:
            logger.error(f"Error exchanging code for token: {e}")
            raise
    
    async def get_user_info(self, provider: OAuthProvider, oauth_token: OAuthToken) -> OAuthUser:
        """Get user information from OAuth provider"""
        try:
            config = self.configs[provider]
            
            headers = {
                'Authorization': f"{oauth_token.token_type} {oauth_token.access_token}",
                'Accept': 'application/json'
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    config.user_info_url,
                    headers=headers
                )
                response.raise_for_status()
                
                user_data = response.json()
            
            # Parse user data based on provider
            if provider == OAuthProvider.GOOGLE:
                oauth_user = OAuthUser(
                    provider=provider,
                    provider_id=user_data['id'],
                    email=user_data['email'],
                    name=user_data.get('name', ''),
                    picture=user_data.get('picture'),
                    verified=user_data.get('verified_email', False),
                    metadata=user_data
                )
            elif provider == OAuthProvider.MICROSOFT:
                oauth_user = OAuthUser(
                    provider=provider,
                    provider_id=user_data['id'],
                    email=user_data.get('mail') or user_data.get('userPrincipalName', ''),
                    name=user_data.get('displayName', ''),
                    picture=None,  # Microsoft Graph doesn't provide picture in basic profile
                    verified=True,  # Microsoft accounts are verified
                    metadata=user_data
                )
            elif provider == OAuthProvider.AWS_SSO:
                oauth_user = OAuthUser(
                    provider=provider,
                    provider_id=user_data['sub'],
                    email=user_data.get('email', ''),
                    name=user_data.get('name', ''),
                    picture=None,
                    verified=user_data.get('email_verified', False),
                    metadata=user_data
                )
            elif provider == OAuthProvider.GITHUB:
                oauth_user = OAuthUser(
                    provider=provider,
                    provider_id=str(user_data['id']),
                    email=user_data.get('email', ''),
                    name=user_data.get('name', ''),
                    picture=user_data.get('avatar_url'),
                    verified=user_data.get('email_verified', False),
                    metadata=user_data
                )
            else:
                raise ValueError(f"Unsupported provider: {provider}")
            
            logger.info(f"User info retrieved for {provider.value}: {oauth_user.email}")
            return oauth_user
            
        except Exception as e:
            logger.error(f"Error getting user info from {provider.value}: {e}")
            raise
    
    async def refresh_token(self, provider: OAuthProvider, refresh_token: str) -> OAuthToken:
        """Refresh OAuth token"""
        try:
            config = self.configs[provider]
            
            data = {
                'client_id': config.client_id,
                'client_secret': config.client_secret,
                'refresh_token': refresh_token,
                'grant_type': 'refresh_token'
            }
            
            headers = {
                'Accept': 'application/json',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    config.token_url,
                    data=data,
                    headers=headers
                )
                response.raise_for_status()
                
                token_data = response.json()
            
            # Create new OAuth token
            oauth_token = OAuthToken(
                access_token=token_data['access_token'],
                refresh_token=token_data.get('refresh_token', refresh_token),
                token_type=token_data.get('token_type', 'Bearer'),
                expires_in=token_data.get('expires_in', 3600),
                scope=token_data.get('scope', ''),
                expires_at=datetime.now() + timedelta(seconds=token_data.get('expires_in', 3600))
            )
            
            logger.info(f"Token refreshed for {provider.value}")
            return oauth_token
            
        except Exception as e:
            logger.error(f"Error refreshing token for {provider.value}: {e}")
            raise
    
    async def revoke_token(self, provider: OAuthProvider, token: str) -> bool:
        """Revoke OAuth token"""
        try:
            config = self.configs[provider]
            
            # Not all providers support token revocation
            if provider == OAuthProvider.GOOGLE:
                revoke_url = "https://oauth2.googleapis.com/revoke"
                async with httpx.AsyncClient() as client:
                    response = await client.post(revoke_url, data={'token': token})
                    return response.status_code == 200
            elif provider == OAuthProvider.MICROSOFT:
                # Microsoft doesn't have a simple revoke endpoint
                # Token will expire naturally
                return True
            elif provider == OAuthProvider.AWS_SSO:
                # AWS Cognito token revocation
                revoke_url = f"{config.token_url.replace('/token', '/revoke')}"
                async with httpx.AsyncClient() as client:
                    response = await client.post(revoke_url, data={'token': token})
                    return response.status_code == 200
            elif provider == OAuthProvider.GITHUB:
                # GitHub doesn't support token revocation
                return True
            else:
                return False
                
        except Exception as e:
            logger.error(f"Error revoking token for {provider.value}: {e}")
            return False
    
    def validate_state(self, state: str) -> bool:
        """Validate OAuth state parameter"""
        try:
            if state not in self.state_store:
                return False
            
            state_data = self.state_store[state]
            
            # Check if state is expired (5 minutes)
            if datetime.now() - state_data['timestamp'] > timedelta(minutes=5):
                del self.state_store[state]
                return False
            
            # Check if state has been used
            if state_data['used']:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating state: {e}")
            return False
    
    def cleanup_expired_states(self):
        """Clean up expired OAuth states"""
        try:
            current_time = datetime.now()
            expired_states = [
                state for state, data in self.state_store.items()
                if current_time - data['timestamp'] > timedelta(minutes=5)
            ]
            
            for state in expired_states:
                del self.state_store[state]
            
            logger.info(f"Cleaned up {len(expired_states)} expired states")
            
        except Exception as e:
            logger.error(f"Error cleaning up expired states: {e}")
    
    def get_supported_providers(self) -> List[OAuthProvider]:
        """Get list of supported OAuth providers"""
        return list(self.configs.keys())
    
    def is_provider_configured(self, provider: OAuthProvider) -> bool:
        """Check if OAuth provider is properly configured"""
        try:
            config = self.configs[provider]
            return bool(config.client_id and config.client_secret)
        except KeyError:
            return False
    
    def get_provider_config(self, provider: OAuthProvider) -> Optional[OAuthConfig]:
        """Get OAuth provider configuration"""
        return self.configs.get(provider)
    
    async def create_or_update_user_from_oauth(self, oauth_user: OAuthUser) -> Dict[str, Any]:
        """Create or update user from OAuth data"""
        try:
            # This would integrate with your user management system
            # For now, return a mock user creation result
            
            user_data = {
                'id': f"{oauth_user.provider.value}_{oauth_user.provider_id}",
                'email': oauth_user.email,
                'name': oauth_user.name,
                'picture': oauth_user.picture,
                'provider': oauth_user.provider.value,
                'provider_id': oauth_user.provider_id,
                'verified': oauth_user.verified,
                'created_at': datetime.now().isoformat(),
                'metadata': oauth_user.metadata
            }
            
            logger.info(f"User created/updated from OAuth: {oauth_user.email}")
            return user_data
            
        except Exception as e:
            logger.error(f"Error creating/updating user from OAuth: {e}")
            raise

# Example usage
async def main():
    """Example usage of OAuth integration"""
    oauth = OAuthIntegration()
    
    # Generate auth URL for Google
    auth_url = oauth.generate_auth_url(OAuthProvider.GOOGLE)
    print(f"Google auth URL: {auth_url}")
    
    # Simulate token exchange (in real app, this would be done in callback)
    # code = "authorization_code_from_callback"
    # oauth_token = await oauth.exchange_code_for_token(OAuthProvider.GOOGLE, code)
    # user_info = await oauth.get_user_info(OAuthProvider.GOOGLE, oauth_token)
    # print(f"User info: {user_info}")

if __name__ == "__main__":
    asyncio.run(main())
