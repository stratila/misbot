from typing import Annotated

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

from misbot.config import get_settings

settings = get_settings()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=settings.auth.token_url)
jwks_client = jwt.PyJWKClient(settings.auth.jwks_url)


async def verify_token(token: Annotated[str, Depends(oauth2_scheme)]) -> dict:
    try:
        signing_key = jwks_client.get_signing_key_from_jwt(token)
        return jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            issuer=settings.auth.issuer,
            audience=settings.auth.audience,
        )
    except jwt.InvalidTokenError:
        raise HTTPException(401, detail="Invalid token")


def require_scope(required: str):
    def checker(payload: Annotated[dict, Depends(verify_token)]) -> dict:
        if required not in payload.get("scope", "").split():
            raise HTTPException(403, detail="Insufficient scope")
        return payload

    return checker
