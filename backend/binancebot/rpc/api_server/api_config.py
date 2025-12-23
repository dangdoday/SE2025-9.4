"""
API endpoint for updating configuration file
Saves API keys directly to config.json so they persist after restart
"""
import json
import logging
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from binancebot.rpc.api_server.deps import get_config, get_api_config
from binancebot.rpc.api_server.api_auth import http_basic_or_jwt_token
from binancebot.rpc.api_server.api_schemas import ApiProfile, ApiProfileListResponse

logger = logging.getLogger(__name__)

router = APIRouter()


def _get_config_path(config: dict[str, Any]) -> Path:
    """Helper to locate the config.json file on disk."""
    docker_config = Path("/config/config.json")
    if docker_config.exists():
        return docker_config

    config_path = None
    initial_files = config.get("initial_config_files")
    if initial_files and len(initial_files) > 0:
        config_path = Path(initial_files[0])
    
    if not config_path or not config_path.exists():
        orig_path = config.get("original_config_path")
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
            
    return config_path


class ExchangeConfigUpdate(BaseModel):
    """Schema for exchange config update"""
    api_key: str
    api_secret: str
    sandbox: bool = True
    dry_run: bool = True
    trading_mode: str = "spot"


class UserAuthConfig(BaseModel):
    """Schema for user auth update"""
    username: str
    password: str





@router.post("/config/save_exchange", tags=["config"])

def save_exchange_config(
    payload: ExchangeConfigUpdate,
    config: dict[str, Any] = Depends(get_config)
):
    """
    Save exchange API keys to the config file on disk.
    This persists the keys so they survive backend restart.
    """
    try:
        # Try multiple ways to find the config file
        config_path = None

        docker_config = Path("/config/config.json")
        if docker_config.exists():
            config_path = docker_config
            logger.info(f"Using config from docker path: {config_path}")
        
        # Method 1: Use initial_config_files from running config
        initial_files = config.get("initial_config_files")
        if initial_files and len(initial_files) > 0:
            config_path = Path(initial_files[0])
            logger.info(f"Using config from initial_config_files: {config_path}")
        
        # Method 2: Use original_config_path
        if not config_path or not config_path.exists():
            orig_path = config.get("original_config_path")
            if orig_path:
                config_path = Path(orig_path)
                logger.info(f"Using config from original_config_path: {config_path}")
        
        # Method 3: Fallback to common locations
        if not config_path or not config_path.exists():
            # Try to find config.json relative to this file
            current_file = Path(__file__)
            # api_config.py is in: backend/binancebot/rpc/api_server/
            # config.json is in: config/
            # So we need: up 4 levels then into config/
            project_root = current_file.parent.parent.parent.parent.parent
            config_path = project_root / "config" / "config.json"
            logger.info(f"Using fallback config path: {config_path}")
        
        logger.info(f"Final config path: {config_path}")
        
        if not config_path.exists():
            # Try current working directory
            import os
            cwd_config = Path(os.getcwd()) / "config" / "config.json"
            if cwd_config.exists():
                config_path = cwd_config
                logger.info(f"Found config in CWD: {config_path}")
            else:
                raise HTTPException(status_code=404, detail=f"Config file not found: {config_path}")
        
        # Read current config
        with open(config_path, "r", encoding="utf-8") as f:
            current_config = json.load(f)
        
        # Update dry_run
        current_config["dry_run"] = payload.dry_run
        
        # Update exchange section
        if "exchange" not in current_config:
            current_config["exchange"] = {}
        
        current_config["exchange"]["key"] = payload.api_key
        current_config["exchange"]["secret"] = payload.api_secret
        
        # Update sandbox/testnet mode in ccxt configs
        if "ccxt_config" not in current_config["exchange"]:
            current_config["exchange"]["ccxt_config"] = {"options": {"defaultType": "spot"}}
        current_config["exchange"]["ccxt_config"]["sandbox"] = payload.sandbox
        
        if "ccxt_async_config" not in current_config["exchange"]:
            current_config["exchange"]["ccxt_async_config"] = {"options": {"defaultType": "spot"}}
        current_config["exchange"]["ccxt_async_config"]["sandbox"] = payload.sandbox
        
        # Update trading mode
        current_config["trading_mode"] = payload.trading_mode
        
        # Write back to file
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(current_config, f, indent=4, ensure_ascii=False)
        
        logger.info(f"Successfully saved exchange config to {config_path}")
        
        return {
            "status": "success",
            "message": "API keys saved to config file. Restart backend to apply.",
            "config_file": str(config_path),
            "sandbox": payload.sandbox
        }
        
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse config: {e}")
        raise HTTPException(status_code=500, detail="Failed to parse config file")
    except PermissionError as e:
        logger.error(f"Permission denied writing config: {e}")
        raise HTTPException(status_code=500, detail="Permission denied writing to config file")
    except Exception as e:
        logger.error(f"Failed to save config: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/config/save_auth", tags=["config"])
def save_auth_config(
    payload: UserAuthConfig,
    config: dict[str, Any] = Depends(get_config)
):
    """
    Save user authentication (username/password) to the config file on disk.
    Also updates the running configuration in memory (Hot-Reload).
    """
    try:
        from binancebot.rpc.api_server.api_auth import HashPassword
        from binancebot.rpc.api_server.webserver import ApiServer
        
        config_path = None
        docker_config = Path("/config/config.json")
        if docker_config.exists():
            config_path = docker_config

        # ... logic to find config_path ...
        initial_files = config.get("initial_config_files")
        if initial_files and len(initial_files) > 0:
            config_path = Path(initial_files[0])
        
        if not config_path or not config_path.exists():
            orig_path = config.get("original_config_path")
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
                raise HTTPException(status_code=404, detail=f"Config file not found")
        
        with open(config_path, "r", encoding="utf-8") as f:
            current_config = json.load(f)
        
        if "api_server" not in current_config:
            current_config["api_server"] = {}
        
        # Hash new password
        hashed_pwd = HashPassword(payload.password)
        
        current_config["api_server"]["username"] = payload.username
        current_config["api_server"]["password"] = hashed_pwd
        
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(current_config, f, indent=4, ensure_ascii=False)
        
        # Hot-Reload: Update the running config instance
        if ApiServer._config and "api_server" in ApiServer._config:
            ApiServer._config["api_server"]["username"] = payload.username
            ApiServer._config["api_server"]["password"] = hashed_pwd
            logger.info("Hot-Reload: Running configuration updated in memory.")
        
        logger.info(f"Successfully saved auth config to {config_path}")
        
        return {
            "status": "success",
            "message": "Authentication updated and reloaded! You can continue without restart.",
            "username": payload.username
        }
        
    except Exception as e:
        logger.error(f"Failed to save auth config: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/profiles", response_model=ApiProfileListResponse, tags=["profiles"])
def list_profiles(
    config: dict[str, Any] = Depends(get_config),
    user: str = Depends(http_basic_or_jwt_token)
):
    """List API profiles for the current user."""
    api_cfg = config.get("api_server", {})
    profiles = []
    
    # 1. Check Primary Admin
    if user == api_cfg.get("username", "admin"):
        profiles = api_cfg.get("profiles", [])
    else:
        # 2. Check Additional Users
        users = api_cfg.get("users", [])
        for u in users:
            if u.get("username") == user:
                profiles = u.get("profiles", [])
                break

    for profile in profiles:
        profile.setdefault("copy_enabled", False)
        profile.setdefault("allocation_pct", 0.0)
                
    return {"profiles": profiles}


@router.post("/profiles", tags=["profiles"])
def save_profile(
    payload: ApiProfile,
    config: dict[str, Any] = Depends(get_config),
    user: str = Depends(http_basic_or_jwt_token)
):
    """Save an API profile for the current user."""
    try:
        from binancebot.rpc.api_server.webserver import ApiServer
        config_path = _get_config_path(config)
        
        with open(config_path, "r", encoding="utf-8") as f:
            current_config = json.load(f)
            
        api_cfg = current_config.setdefault("api_server", {})
        target_profiles = None
        
        # Determine which user's profiles to update
        if user == api_cfg.get("username", "admin"):
            target_profiles = api_cfg.setdefault("profiles", [])
        else:
            users = api_cfg.setdefault("users", [])
            for u in users:
                if u.get("username") == user:
                    target_profiles = u.setdefault("profiles", [])
                    break
        
        if target_profiles is None:
            raise HTTPException(status_code=404, detail="User not found in config")
            
        # 1. Start Overlap Check
        # Check if this API Key is already used by Admin
        admin_key = api_cfg.get("key")
        if admin_key and payload.api_key == admin_key:
             # If current user is NOT admin, deny
             if user != api_cfg.get("username", "admin"):
                 raise HTTPException(status_code=400, detail="This API Key is already in use by the Main Administrator.")
        
        # Check against Admin Profiles
        admin_profiles = api_cfg.get("profiles", [])
        for p in admin_profiles:
            if p.get("api_key") == payload.api_key:
                # If current user is not admin, deny
                if user != api_cfg.get("username", "admin"):
                    raise HTTPException(status_code=400, detail="This API Key is already in use by the Administrator.")
                # If current user IS admin, allow update (it's their own profile)

        # Check against Other Users
        for u in api_cfg.get("users", []):
            u_name = u.get("username")
            if u_name == user:
                continue # Skip self (we are updating our own list)
            
            for p in u.get("profiles", []):
                if p.get("api_key") == payload.api_key:
                    raise HTTPException(status_code=400, detail=f"This API Key is already in use by user '{u_name}'.")
        # End Overlap Check

        # Add or update profile
        found = False
        for i, p in enumerate(target_profiles):
            if p.get("id") == payload.id:
                target_profiles[i] = payload.model_dump()
                found = True
                break
        if not found:
            target_profiles.append(payload.model_dump())
            
        # Save to file
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(current_config, f, indent=4, ensure_ascii=False)
            
        # Hot-Reload (Update memory)
        if ApiServer._config and "api_server" in ApiServer._config:
            mem_api_cfg = ApiServer._config["api_server"]
            if user == mem_api_cfg.get("username", "admin"):
                mem_api_cfg["profiles"] = target_profiles
            else:
                for u in mem_api_cfg.get("users", []):
                    if u.get("username") == user:
                        u["profiles"] = target_profiles
                        break
                        
        return {"status": "success", "message": f"Profile '{payload.name}' saved."}
        
    except Exception as e:
        logger.error(f"Failed to save profile: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/profiles/{profile_id}", tags=["profiles"])
def delete_profile(
    profile_id: str,
    config: dict[str, Any] = Depends(get_config),
    user: str = Depends(http_basic_or_jwt_token)
):
    """Delete an API profile."""
    try:
        from binancebot.rpc.api_server.webserver import ApiServer
        config_path = _get_config_path(config)
        
        with open(config_path, "r", encoding="utf-8") as f:
            current_config = json.load(f)
            
        api_cfg = current_config.setdefault("api_server", {})
        target_profiles = None
        
        if user == api_cfg.get("username", "admin"):
            target_profiles = api_cfg.get("profiles", [])
        else:
            for u in api_cfg.get("users", []):
                if u.get("username") == user:
                    target_profiles = u.get("profiles", [])
                    break
                    
        if target_profiles is None:
            raise HTTPException(status_code=404, detail="User not found")
            
        # Filter out the profile
        new_profiles = [p for p in target_profiles if p.get("id") != profile_id]
        
        # Update config
        if user == api_cfg.get("username", "admin"):
            api_cfg["profiles"] = new_profiles
        else:
            for u in api_cfg.get("users", []):
                if u.get("username") == user:
                    u["profiles"] = new_profiles
                    break
                    
        # Save
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(current_config, f, indent=4, ensure_ascii=False)
            
        # Hot-Reload
        if ApiServer._config and "api_server" in ApiServer._config:
            mem_api_cfg = ApiServer._config["api_server"]
            if user == mem_api_cfg.get("username", "admin"):
                mem_api_cfg["profiles"] = new_profiles
            else:
                for u in mem_api_cfg.get("users", []):
                    if u.get("username") == user:
                        u["profiles"] = new_profiles
                        break
                        
        return {"status": "success", "message": "Profile deleted."}
        
    except Exception as e:
        logger.error(f"Failed to delete profile: {e}")
        raise HTTPException(status_code=500, detail=str(e))


