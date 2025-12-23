from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import ccxt

from binancebot.misc import deep_merge_dicts


logger = logging.getLogger(__name__)


@dataclass
class CopyProfile:
    id: str
    name: str
    api_key: str
    secret_key: str
    trading_mode: str
    margin_mode: str | None
    copy_enabled: bool
    allocation_pct: float


class CopyTradingManager:
    """
    Mirror master trades to enabled follower profiles.
    """

    def __init__(self, config: dict[str, Any], exchange) -> None:
        self._config = config
        self._exchange = exchange
        self._clients: dict[str, dict[str, Any]] = {}
        self._state_path = Path(config.get("datadir", "data")) / "copy_trades.json"
        self._state: dict[str, Any] = self._load_state()
        self._master_key_cache: str | None = None
        self._master_key_ts = 0.0

    def _load_state(self) -> dict[str, Any]:
        if self._state_path.exists():
            try:
                return json.loads(self._state_path.read_text(encoding="utf-8"))
            except Exception as exc:
                logger.warning("Failed to read copy trade state: %s", exc)
        return {"version": 1, "trades": {}}

    def _save_state(self) -> None:
        self._state_path.parent.mkdir(parents=True, exist_ok=True)
        self._state_path.write_text(json.dumps(self._state, indent=2), encoding="utf-8")

    def _read_config_file(self) -> dict[str, Any]:
        for path in (Path("/config/config.json"), Path("config/config.json")):
            if path.exists():
                try:
                    return json.loads(path.read_text(encoding="utf-8"))
                except Exception as exc:
                    logger.warning("Failed to read config file %s: %s", path, exc)
        return self._config

    def _get_master_key(self) -> str | None:
        now = time.time()
        if self._master_key_cache is not None and now - self._master_key_ts < 30:
            return self._master_key_cache
        cfg = self._read_config_file()
        self._master_key_cache = cfg.get("exchange", {}).get("key")
        self._master_key_ts = now
        return self._master_key_cache

    def _get_copy_profiles(self) -> list[CopyProfile]:
        cfg = self._read_config_file()
        api_cfg = cfg.get("api_server", {})
        master_key = cfg.get("exchange", {}).get("key") or self._get_master_key()
        active_profile_id = api_cfg.get("active_profile_id")
        raw_profiles = api_cfg.get("profiles", [])
        profiles: list[CopyProfile] = []

        for p in raw_profiles:
            api_key = p.get("api_key")
            secret_key = p.get("secret_key")
            allocation_pct = float(p.get("allocation_pct") or 0.0)
            copy_enabled = bool(p.get("copy_enabled", False))
            if not copy_enabled or allocation_pct <= 0:
                continue
            if not api_key or not secret_key:
                continue
            if active_profile_id and p.get("id") == active_profile_id:
                continue
            if master_key and api_key == master_key:
                continue
            profiles.append(
                CopyProfile(
                    id=p.get("id", ""),
                    name=p.get("name", "Account"),
                    api_key=api_key,
                    secret_key=secret_key,
                    trading_mode=p.get("trading_mode", "spot"),
                    margin_mode=p.get("margin_mode"),
                    copy_enabled=copy_enabled,
                    allocation_pct=allocation_pct,
                )
            )

        return profiles

    def _build_client(self, profile: CopyProfile):
        exchange_id = self._config.get("exchange", {}).get("name", "binance")
        exchange_cls = getattr(ccxt, exchange_id)

        ccxt_config: dict[str, Any] = {
            "apiKey": profile.api_key,
            "secret": profile.secret_key,
            "enableRateLimit": True,
            "timeout": 30000,
        }

        exchange_cfg = self._config.get("exchange", {})
        ccxt_config = deep_merge_dicts(exchange_cfg.get("ccxt_config", {}), ccxt_config)
        ccxt_config = deep_merge_dicts(exchange_cfg.get("ccxt_sync_config", {}), ccxt_config)

        options = dict(ccxt_config.get("options", {}))
        if profile.trading_mode == "futures":
            options["defaultType"] = "future"
        else:
            options["defaultType"] = "spot"
        ccxt_config["options"] = options

        client = exchange_cls(ccxt_config)
        client.load_markets()
        return client

    def _get_client(self, profile: CopyProfile):
        entry = self._clients.get(profile.id)
        if entry and entry.get("api_key") == profile.api_key:
            return entry["client"]

        if entry:
            try:
                entry["client"].close()
            except Exception:
                pass

        client = self._build_client(profile)
        self._clients[profile.id] = {"api_key": profile.api_key, "client": client}
        return client

    def _get_free_balance(self, balance: dict[str, Any], currency: str) -> float:
        if currency in balance and isinstance(balance[currency], dict):
            return float(balance[currency].get("free") or 0.0)
        free = balance.get("free", {})
        return float(free.get(currency) or 0.0)

    def _record_entry(self, trade_id: int, profile_id: str, pair: str, amount: float) -> None:
        trades = self._state.setdefault("trades", {})
        trade_key = str(trade_id)
        entries = trades.setdefault(trade_key, {})
        entry = entries.get(profile_id, {"pair": pair, "amount": 0.0})
        entry["amount"] = float(entry.get("amount", 0.0)) + float(amount)
        entries[profile_id] = entry
        self._save_state()

    def _consume_entry(self, trade_id: int, profile_id: str) -> dict[str, Any] | None:
        trades = self._state.get("trades", {})
        trade_key = str(trade_id)
        entries = trades.get(trade_key, {})
        entry = entries.pop(profile_id, None)
        if entry is not None and not entries:
            trades.pop(trade_key, None)
        self._save_state()
        return entry

    def mirror_entry(
        self,
        trade_id: int,
        pair: str,
        side: str,
        price: float,
        stake_currency: str,
        mode: str,
    ) -> None:
        if mode not in ("initial", "force_entry"):
            return
        profiles = self._get_copy_profiles()
        if not profiles:
            return
        for profile in profiles:
            if profile.trading_mode != "spot":
                logger.info("Copy trading skip non-spot profile %s", profile.name)
                continue
            try:
                client = self._get_client(profile)
                balance = client.fetch_balance()
                free_quote = self._get_free_balance(balance, stake_currency)
                stake = free_quote * (profile.allocation_pct / 100.0)
                if stake <= 0:
                    continue
                amount = (stake / price) * 0.995
                amount = float(client.amount_to_precision(pair, amount))
                if amount <= 0:
                    continue
                params: dict[str, Any] = {}
                if side == "buy":
                    params["quoteOrderQty"] = stake
                order = client.create_order(pair, "market", side, amount, None, params)
                filled = order.get("filled") or order.get("amount") or amount
                if not filled and order.get("cost") and order.get("average"):
                    filled = order["cost"] / order["average"]
                self._record_entry(trade_id, profile.id, pair, float(filled))
                logger.info(
                    "Copy entry %s %s amount=%s profile=%s",
                    pair,
                    side,
                    filled,
                    profile.name,
                )
            except Exception as exc:
                logger.warning("Copy entry failed for %s: %s", profile.name, exc)

    def mirror_exit(
        self,
        trade_id: int,
        pair: str,
        side: str,
    ) -> None:
        profiles = self._get_copy_profiles()
        if not profiles:
            return
        for profile in profiles:
            if profile.trading_mode != "spot":
                logger.info("Copy trading skip non-spot profile %s", profile.name)
                continue
            entry = self._consume_entry(trade_id, profile.id)
            if not entry:
                continue
            amount = float(entry.get("amount") or 0.0)
            if amount <= 0:
                continue
            try:
                client = self._get_client(profile)
                amount = float(client.amount_to_precision(pair, amount))
                if amount <= 0:
                    continue
                client.create_order(pair, "market", side, amount)
                logger.info(
                    "Copy exit %s %s amount=%s profile=%s",
                    pair,
                    side,
                    amount,
                    profile.name,
                )
            except Exception as exc:
                logger.warning("Copy exit failed for %s: %s", profile.name, exc)

    def close(self) -> None:
        for entry in self._clients.values():
            try:
                entry["client"].close()
            except Exception:
                pass
        self._clients.clear()
