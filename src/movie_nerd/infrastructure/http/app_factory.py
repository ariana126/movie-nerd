from __future__ import annotations

from typing import Any

from fastapi import Depends, FastAPI, HTTPException, Request, Response
from pydantic import BaseModel
from starlette.middleware.base import BaseHTTPMiddleware

from ddd import Identity

from movie_nerd.application.auth.auth_service import AuthService
from movie_nerd.application.auth.errors import (
    InvalidCredentials,
    InvalidToken,
    UserAlreadyExists,
)
from movie_nerd.domain import User


class CredentialsRequest(BaseModel):
    email: str
    password: str


class RegistrationRequest(BaseModel):
    email: str
    password: str
    first_name: str
    last_name: str


class TokenResponse(BaseModel):
    token: str


class UserMeResponse(BaseModel):
    email: str
    first_name: str
    last_name: str


def _require_authenticated_user(request: Request) -> User:
    user = getattr(request.state, "user", None)
    if user is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user


class AuthenticationMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: FastAPI, *, auth_service: AuthService) -> None:
        super().__init__(app)
        self._auth_service = auth_service

    async def dispatch(self, request: Request, call_next) -> Response:
        request.state.user = None

        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.lower().startswith("bearer "):
            token = auth_header.split(" ", 1)[1].strip()
            if token:
                try:
                    request.state.user = self._auth_service.get_user_from_token(token=token)
                except InvalidToken:
                    request.state.user = None
                except Exception:
                    # Keep middleware permissive: invalid tokens simply result
                    # in an unauthenticated request.
                    request.state.user = None

        return await call_next(request)


def create_app(*, auth_service: AuthService) -> FastAPI:
    app = FastAPI()
    app.add_middleware(AuthenticationMiddleware, auth_service=auth_service)

    @app.get("/health", status_code=204)
    def health() -> None:
        return None

    @app.post("/auth/register", status_code=201)
    def register(payload: RegistrationRequest) -> Any:
        try:
            auth_service.register(
                email=payload.email,
                password=payload.password,
                first_name=payload.first_name,
                last_name=payload.last_name,
            )
            return Response(status_code=201)
        except UserAlreadyExists:
            raise HTTPException(status_code=409, detail="User already exists")

    @app.post("/auth/login", response_model=TokenResponse)
    def login(payload: CredentialsRequest) -> TokenResponse:
        try:
            token = auth_service.login(email=payload.email, password=payload.password)
            return TokenResponse(token=token)
        except InvalidCredentials:
            raise HTTPException(status_code=401, detail="Invalid credentials")

    @app.get("/me", response_model=UserMeResponse)
    def me(current_user: User = Depends(_require_authenticated_user)) -> UserMeResponse:
        return UserMeResponse(email=current_user.email, first_name=current_user.first_name, last_name=current_user.last_name)

    return app

