from datetime import datetime, timedelta
import httpx
from typing import Dict, Optional
from app.core.config import Settings

settings = Settings()

class PocketBaseClient:
    _instance = None
    _token: Optional[str] = None
    _token_expiry: Optional[datetime] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PocketBaseClient, cls).__new__(cls)
        return cls._instance

    @classmethod
    async def get_token(cls) -> str:
        """
        Returns a valid auth token. 
        Logs in if token is missing or expired.
        """
        # Simple expiry check (refresh 5 mins before actual expiry if we knew it, 
        # but PB tokens are long-lived, so we mostly care if it's None)
        if cls._token is None:
            await cls._login()
        return cls._token

    @classmethod
    async def get_headers(cls) -> Dict[str, str]:
        """Returns headers with Authorization token."""
        token = await cls.get_token()
        return {"Authorization": token}

    @classmethod
    async def _login(cls):
        """Authenticates with PocketBase as Admin."""
        async with httpx.AsyncClient() as client:
            try:
                # Auth as email/pass (Superuser)
                # Note: Endpoint handles both admins and superusers in newer PB versions via collection auth
                # Try specific superuser collection first (PB v0.23+)
                url = f"{settings.PB_URL}/api/collections/_superusers/auth-with-password"
                payload = {
                    "identity": settings.ADMIN_EMAIL,
                    "password": settings.ADMIN_PASSWORD
                }
                
                response = await client.post(url, json=payload, timeout=5.0)
                
                # If 404, maybe it's an older PB version using /api/admins/auth-with-password
                if response.status_code == 404:
                     url = f"{settings.PB_URL}/api/admins/auth-with-password"
                     response = await client.post(url, json=payload, timeout=5.0)

                response.raise_for_status()
                data = response.json()
                cls._token = data["token"]
                # print(f"Successfully authenticated as {settings.ADMIN_EMAIL}")

            except Exception as e:
                print(f"Failed to authenticate with PocketBase: {e}")
                # We don't raise here to avoid crashing app startup, 
                # but subsequent calls will fail or retry.
                cls._token = None
                raise e

pb_client = PocketBaseClient()
