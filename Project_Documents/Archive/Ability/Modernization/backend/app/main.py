from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta

from app.core.config import settings
from app.core.auth import (
    oauth2_handler,
    create_access_token,
    get_current_user,
    get_current_active_user,
)
from app.db.session import engine, init_db
from app.graphql.schema import graphql_app
from app.schemas.token import Token

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount GraphQL app
app.include_router(
    graphql_app,
    prefix=f"{settings.API_V1_STR}/graphql",
    tags=["GraphQL"],
)

@app.on_event("startup")
async def startup_event():
    await init_db()

@app.post(f"{settings.API_V1_STR}/oauth/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends()
):
    """OAuth2 compatible token login, get an access token for future requests"""
    if not oauth2_handler.verify_client(
        form_data.client_id,
        form_data.client_secret,
        form_data.redirect_uri,
        form_data.scope
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid client credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": form_data.username},
        expires_delta=access_token_expires
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        scope=form_data.scope
    )

@app.get(f"{settings.API_V1_STR}/oauth/authorize")
async def authorize(
    response_type: str,
    client_id: str,
    redirect_uri: str,
    scope: str,
    state: str,
    current_user: User = Depends(get_current_active_user)
):
    """OAuth2 authorization endpoint"""
    if response_type != "code":
        raise HTTPException(
            status_code=400,
            detail="Invalid response type"
        )

    if not oauth2_handler.verify_client(
        client_id,
        None,
        redirect_uri,
        scope
    ):
        raise HTTPException(
            status_code=400,
            detail="Invalid client or redirect URI"
        )

    code = await oauth2_handler.create_authorization_code(
        client_id,
        redirect_uri,
        scope,
        current_user
    )

    return JSONResponse({
        "code": code,
        "state": state
    })

@app.post(f"{settings.API_V1_STR}/oauth/token")
async def token(
    grant_type: str,
    code: str,
    redirect_uri: str,
    client_id: str,
    client_secret: str
):
    """OAuth2 token endpoint"""
    if grant_type != "authorization_code":
        raise HTTPException(
            status_code=400,
            detail="Invalid grant type"
        )

    return await oauth2_handler.exchange_code_for_token(
        code,
        client_id,
        client_secret,
        redirect_uri
    )

@app.get(f"{settings.API_V1_STR}/oauth/userinfo")
async def userinfo(current_user: User = Depends(get_current_active_user)):
    """OAuth2 userinfo endpoint"""
    return current_user

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Global exception handler for HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "type": "error",
            "status": exc.status_code,
        },
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        ws="websockets"
    )
