"""
OAuth Handler Module
Manages Google OAuth2 authentication.
"""
from typing import Dict, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2AuthorizationCodeBearer
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from sqlalchemy.ext.asyncio import AsyncSession
from ..database.session import get_session
from ..repositories.user_repository import UserRepository

oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl="https://accounts.google.com/o/oauth2/v2/auth",
    tokenUrl="https://oauth2.googleapis.com/token"
)

class OAuthHandler:
    """Handler for OAuth2 operations."""
    
    SCOPES = ['https://www.googleapis.com/auth/calendar']
    
    def __init__(self, session: AsyncSession):
        """Initialize with database session."""
        self.session = session
        self.user_repository = UserRepository(session)

    async def get_current_user(
        self,
        token: str = Depends(oauth2_scheme)
    ) -> Dict[str, str]:
        """Get current user from token."""
        try:
            # Get credentials from database
            user_creds = await self.user_repository.get_user_credentials(token)
            if not user_creds:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Could not validate credentials",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            # Validate credentials
            credentials = Credentials.from_authorized_user_info(
                user_creds,
                self.SCOPES
            )
            
            if not credentials or not credentials.valid:
                if credentials and credentials.expired and credentials.refresh_token:
                    credentials.refresh(Request())
                    # Update stored credentials
                    await self.user_repository.update_user_credentials(
                        token,
                        credentials.to_json()
                    )
                else:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid credentials",
                        headers={"WWW-Authenticate": "Bearer"},
                    )
            
            return credentials.to_json()
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(e),
                headers={"WWW-Authenticate": "Bearer"},
            )

    async def create_credentials_flow(self) -> InstalledAppFlow:
        """Create OAuth2 flow for new credentials."""
        return InstalledAppFlow.from_client_secrets_file(
            'client_secrets.json',
            self.SCOPES
        )

async def get_oauth_handler(
    session: AsyncSession = Depends(get_session)
) -> OAuthHandler:
    """Dependency provider for OAuthHandler."""
    return OAuthHandler(session)

async def get_current_user(
    oauth_handler: OAuthHandler = Depends(get_oauth_handler),
    token: str = Depends(oauth2_scheme)
) -> Dict[str, str]:
    """Dependency for getting current user."""
    return await oauth_handler.get_current_user(token)
