import hashlib
import logging
import secrets
from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.security.http import HTTPBasic, HTTPBasicCredentials

from binancebot.rpc.api_server.api_schemas import AccessAndRefreshToken, AccessToken
from binancebot.rpc.api_server.deps import get_api_config, get_config


logger = logging.getLogger(__name__)

ALGORITHM = "HS256"

router_login = APIRouter()


def HashPassword(password: str) -> str:
    """Hash a password for storing."""
    salt = secrets.token_hex(16)
    key = hashlib.pbkdf2_hmac(
        'sha256', 
        password.encode('utf-8'), 
        salt.encode('utf-8'), 
        100000
    ).hex()
    return f"pbkdf2_sha256$100000${salt}${key}"


def VerifyPassword(plain_password: str, hashed_password: str) -> bool:
    """Verify a hashed password."""
    try:
        if not hashed_password.startswith("pbkdf2_sha256$"):
            # Legacy plain text support
            return secrets.compare_digest(plain_password, hashed_password)
            
        algorithm, iterations, salt, key = hashed_password.split('$')
        iterations = int(iterations)
        new_key = hashlib.pbkdf2_hmac(
            'sha256', 
            plain_password.encode('utf-8'), 
            salt.encode('utf-8'), 
            iterations
        ).hex()
        return secrets.compare_digest(key, new_key)
    except Exception:
        return False


def verify_auth(api_config, username: str, password: str):
    """Verify username/password"""
    # 1. Check Primary Admin
    if secrets.compare_digest(username, api_config.get("username", "")):
        stored_password = api_config.get("password", "")
        return VerifyPassword(password, stored_password)
        
    # 2. Check Additional Users (Multi-User Support)
    users = api_config.get("users", [])
    for user in users:
        if secrets.compare_digest(username, user.get("username", "")):
            return VerifyPassword(password, user.get("password", ""))
            
    return False


httpbasic = HTTPBasic(auto_error=False)
security = HTTPBasic()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)


def get_user_from_token(token, secret_key: str, token_type: str = "access") -> str:  # noqa: S107
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, secret_key, algorithms=[ALGORITHM])
        username: str = payload.get("identity", {}).get("u")
        if username is None:
            raise credentials_exception
        if payload.get("type") != token_type:
            raise credentials_exception

    except jwt.PyJWTError:
        raise credentials_exception
    return username


# This should be reimplemented to better realign with the existing tools provided
# by FastAPI regarding API Tokens
# https://github.com/tiangolo/fastapi/blob/master/fastapi/security/api_key.py
async def validate_ws_token(
    ws: WebSocket,
    ws_token: str | None = Query(default=None, alias="token"),
    api_config: dict[str, Any] = Depends(get_api_config),
):
    secret_ws_token = api_config.get("ws_token", None)
    secret_jwt_key = api_config.get("jwt_secret_key", "super-secret")

    # Check if ws_token is/in secret_ws_token
    if ws_token and secret_ws_token:
        is_valid_ws_token = False
        if isinstance(secret_ws_token, str):
            is_valid_ws_token = secrets.compare_digest(secret_ws_token, ws_token)
        elif isinstance(secret_ws_token, list):
            is_valid_ws_token = any(
                [secrets.compare_digest(potential, ws_token) for potential in secret_ws_token]
            )

        if is_valid_ws_token:
            return ws_token

    # Check if ws_token is a JWT
    try:
        user = get_user_from_token(ws_token, secret_jwt_key)
        return user
    # If the token is a jwt, and it's valid return the user
    except HTTPException:
        pass

    # If it doesn't match, close the websocket connection
    await ws.close(code=status.WS_1008_POLICY_VIOLATION)


def create_token(data: dict, secret_key: str, token_type: str = "access") -> str:  # noqa: S107
    to_encode = data.copy()
    if token_type == "access":  # noqa: S105
        expire = datetime.now(UTC) + timedelta(minutes=15)
    elif token_type == "refresh":  # noqa: S105
        expire = datetime.now(UTC) + timedelta(days=30)
    else:
        raise ValueError()
    to_encode.update(
        {
            "exp": expire,
            "iat": datetime.now(UTC),
            "type": token_type,
        }
    )
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=ALGORITHM)
    return encoded_jwt


def http_basic_or_jwt_token(
    form_data: HTTPBasicCredentials = Depends(httpbasic),
    token: str = Depends(oauth2_scheme),
    api_config=Depends(get_api_config),
):
    if token:
        return get_user_from_token(token, api_config.get("jwt_secret_key", "super-secret"))
    elif form_data and verify_auth(api_config, form_data.username, form_data.password):
        return form_data.username

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Unauthorized",
    )


from pydantic import BaseModel

class LoginRequest(BaseModel):
    username: str
    password: str

@router_login.post("/token/login", response_model=AccessAndRefreshToken)
def token_login(
    body: LoginRequest | None = None,
    form_data: HTTPBasicCredentials = Depends(httpbasic), 
    api_config=Depends(get_api_config)
):
    # Try getting from Basic Auth first, then fall back to JSON body
    user = form_data.username if form_data else (body.username if body else None)
    pwd = form_data.password if form_data else (body.password if body else None)
    
    if user and pwd and verify_auth(api_config, user, pwd):
        token_data = {"identity": {"u": user}}
        access_token = create_token(
            token_data,
            api_config.get("jwt_secret_key", "super-secret"),
            token_type="access",  # noqa: S106
        )
        refresh_token = create_token(
            token_data,
            api_config.get("jwt_secret_key", "super-secret"),
            token_type="refresh",  # noqa: S106
        )
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )


@router_login.post("/token/refresh", response_model=AccessToken)
def token_refresh(token: str = Depends(oauth2_scheme), api_config=Depends(get_api_config)):
    # Refresh token
    u = get_user_from_token(token, api_config.get("jwt_secret_key", "super-secret"), "refresh")
    token_data = {"identity": {"u": u}}
    access_token = create_token(
        token_data,
        api_config.get("jwt_secret_key", "super-secret"),
        token_type="access",  # noqa: S106
    )
    return {"access_token": access_token}


@router_login.post("/register", tags=["auth"])
def register_user(
    payload: LoginRequest,
    config: dict[str, Any] = Depends(get_api_config), # Wait, saving needs FULL config
    full_config: dict[str, Any] = Depends(get_config) # Needed for file path
):
    """
    Create a new user account.
    Adds the user to the 'users' list in config.json.
    """
    import json
    from pathlib import Path
    
    try:
        from binancebot.rpc.api_server.webserver import ApiServer
        
        # 1. Locate Config File
        config_path = None
        initial_files = full_config.get("initial_config_files")
        if initial_files and len(initial_files) > 0:
            config_path = Path(initial_files[0])
        
        if not config_path or not config_path.exists():
            orig_path = full_config.get("original_config_path")
            if orig_path:
                config_path = Path(orig_path)
        
        if not config_path or not config_path.exists():
            current_file = Path(__file__)
            project_root = current_file.parent.parent.parent.parent.parent
            config_path = project_root / "config" / "config.json"
        
        if not config_path.exists():
            import os
            cwd_config = Path(os.getcwd()) / "config" / "config.json"
            if cwd_config.exists():
                config_path = cwd_config
            else:
                raise HTTPException(status_code=404, detail="Config file not found")
        
        # 2. Read Config
        with open(config_path, "r", encoding="utf-8") as f:
            current_config = json.load(f)
        
        if "api_server" not in current_config:
            current_config["api_server"] = {}
            
        api_cfg = current_config["api_server"]
        
        # 3. Check for duplicates
        if payload.username == api_cfg.get("username", "admin"):
            raise HTTPException(status_code=400, detail="Username already exists (Admin)")
            
        users = api_cfg.get("users", [])
        if any(u.get("username") == payload.username for u in users):
             raise HTTPException(status_code=400, detail="Username already exists")
        
        # 4. Hash Password & Add User
        hashed_pwd = HashPassword(payload.password)
        
        if "users" not in api_cfg:
            api_cfg["users"] = []
            
        api_cfg["users"].append({
            "username": payload.username,
            "password": hashed_pwd
        })
        
        # 5. Save Config
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(current_config, f, indent=4, ensure_ascii=False)
        
        # 6. Hot-Reload
        if ApiServer._config and "api_server" in ApiServer._config:
            if "users" not in ApiServer._config["api_server"]:
                ApiServer._config["api_server"]["users"] = []
            ApiServer._config["api_server"]["users"].append({
                "username": payload.username,
                "password": hashed_pwd
            })
            logger.info(f"Hot-Reload: New user '{payload.username}' registered.")
        
        return {
            "status": "success",
            "message": f"Account '{payload.username}' created successfully!",
            "username": payload.username
        }
        
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Failed to register user: {e}")
        raise HTTPException(status_code=500, detail=str(e))
