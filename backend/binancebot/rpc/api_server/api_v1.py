import logging
from copy import deepcopy
from typing import Annotated, Any

from fastapi import APIRouter, Depends, Query
from fastapi.exceptions import HTTPException

from binancebot import __version__
from binancebot.data.history import get_datahandler
from binancebot.enums import CandleType, RunMode, State, TradingMode
from binancebot.exceptions import OperationalException
from binancebot.rpc import RPC
from binancebot.rpc.api_server.api_pairlists import handleExchangePayload
from binancebot.rpc.api_server.api_schemas import (
    AvailablePairs,
    Balances,
    BlacklistPayload,
    BlacklistResponse,
    Count,
    DailyWeeklyMonthly,
    DeleteLockRequest,
    DeleteTrade,
    Entry,
    ExchangeListResponse,
    Exit,
    ForceEnterPayload,
    ForceEnterResponse,
    ForceExitPayload,
    AIMLModelListResponse,
    Health,
    HyperoptLossListResponse,
    ListCustomData,
    Locks,
    LocksPayload,
    Logs,
    MarketRequest,
    MarketResponse,
    MixTag,
    OpenTradeSchema,
    PairCandlesRequest,
    PairHistory,
    PerformanceEntry,
    Ping,
    PlotConfig,
    Profit,
    ProfitAll,
    ResultMsg,
    ShowConfig,
    Stats,
    StatusMsg,
    StrategyListResponse,
    StrategyResponse,
    SysInfo,
    Version,
    WhitelistResponse,
    ExchangeConfigPayload,
)
from binancebot.rpc.api_server.deps import get_config, get_exchange, get_rpc, get_rpc_optional
from binancebot.rpc.api_server.api_auth import http_basic_or_jwt_token
from binancebot.rpc.rpc import RPCException


logger = logging.getLogger(__name__)

# API version
# Pre-1.1, no version was provided
# Version increments should happen in "small" steps (1.1, 1.12, ...) unless big changes happen.
# 1.11: forcebuy and forcesell accept ordertype
# 1.12: add blacklist delete endpoint
# 1.13: forcebuy supports stake_amount
# versions 2.xx -> futures/short branch
# 2.14: Add entry/exit orders to trade response
# 2.15: Add backtest history endpoints
# 2.16: Additional daily metrics
# 2.17: Forceentry - leverage, partial force_exit
# 2.20: Add websocket endpoints
# 2.21: Add new_candle messagetype
# 2.22: Add AIML to backtesting
# 2.23: Allow plot config request in webserver mode
# 2.24: Add cancel_open_order endpoint
# 2.25: Add several profit values to /status endpoint
# 2.26: increase /balance output
# 2.27: Add /trades/<id>/reload endpoint
# 2.28: Switch reload endpoint to Post
# 2.29: Add /exchanges endpoint
# 2.30: new /pairlists endpoint
# 2.31: new /backtest/history/ delete endpoint
# 2.32: new /backtest/history/ patch endpoint
# 2.33: Additional weekly/monthly metrics
# 2.34: new entries/exits/mix_tags endpoints
# 2.35: pair_candles and pair_history endpoints as Post variant
# 2.40: Add hyperopt-loss endpoint
# 2.41: Add download-data endpoint
# 2.42: Add /pair_history endpoint with live data
# 2.43: Add /profit_all endpoint
API_VERSION = 2.43

# Public API, requires no auth.
router_public = APIRouter()
# Private API, protected by authentication
router = APIRouter()


def check_api_ownership(
    config: dict[str, Any] = Depends(get_config),
    user: str = Depends(http_basic_or_jwt_token)
) -> bool:
    """Check if the current user owns the active API key."""
    import json
    from pathlib import Path
    
    # Read directly from config.json file (runtime config may not have exchange.key)
    config_path = Path("config/config.json")
    if not config_path.exists():
        config_path = Path("../config/config.json")
    
    try:
        with open(config_path, 'r') as f:
            file_config = json.load(f)
    except Exception as e:
        logger.error(f"[check_api_ownership] Failed to read config file: {e}")
        return True  # Allow on error to not break functionality
    
    active_key = file_config.get("exchange", {}).get("key")
    logger.info(f"[check_api_ownership] User: {user}, Active Key Prefix: {active_key[:10] if active_key else 'None'}...")
    
    if not active_key:
        # If no key is active, allow (nothing to leak from exchange)
        logger.info("[check_api_ownership] No active key in config file, allowing access")
        return True
        
    api_cfg = file_config.get("api_server", {})
    
    # 1. Check Primary Admin
    primary_admin = api_cfg.get("username", "admin")
    if user == primary_admin:
        # If active key matches admin's direct config keys
        if active_key == api_cfg.get("key"):
            logger.info("[check_api_ownership] User is admin, key matches direct config")
            return True
        # Or matches one of admin's profiles
        profiles = api_cfg.get("profiles", [])
        if any(p.get("api_key") == active_key for p in profiles):
            logger.info("[check_api_ownership] User is admin, key matches admin's profile")
            return True
        logger.info(f"[check_api_ownership] User is admin but key doesn't match any profile")
    else:
        # 2. Check Additional Users
        logger.info(f"[check_api_ownership] User {user} is not primary admin ({primary_admin}), checking users list")
        found_user = False
        for u in api_cfg.get("users", []):
            if u.get("username") == user:
                found_user = True
                profiles = u.get("profiles", [])
                logger.info(f"[check_api_ownership] Found user {user} with {len(profiles)} profiles")
                if any(p.get("api_key") == active_key for p in profiles):
                    logger.info("[check_api_ownership] Key matches user's profile")
                    return True
                break
        if not found_user:
            logger.info(f"[check_api_ownership] User {user} not found in users list")
                
    logger.info(f"[check_api_ownership] DENYING access for user {user}")
    return False


@router_public.get("/ping", response_model=Ping)
def ping():
    """simple ping"""
    return {"status": "pong"}


@router.get("/version", response_model=Version, tags=["info"])
def version():
    """Bot Version info"""
    return {"version": __version__}


@router.get("/balance", response_model=Balances, tags=["info"])
def balance(
    rpc: RPC = Depends(get_rpc), 
    config=Depends(get_config),
    is_owner: bool = Depends(check_api_ownership)
):
    """Account Balances"""
    if not is_owner:
        raise HTTPException(status_code=403, detail="Active account belongs to another user")
    return rpc._rpc_balance(
        config["stake_currency"],
        config.get("fiat_display_currency", ""),
    )


@router.get("/count", response_model=Count, tags=["info"])
def count(rpc: RPC = Depends(get_rpc)):
    return rpc._rpc_count()


@router.get("/entries", response_model=list[Entry], tags=["info"])
def entries(pair: str | None = None, rpc: RPC = Depends(get_rpc)):
    return rpc._rpc_enter_tag_performance(pair)


@router.get("/exits", response_model=list[Exit], tags=["info"])
def exits(pair: str | None = None, rpc: RPC = Depends(get_rpc)):
    return rpc._rpc_exit_reason_performance(pair)


@router.get("/mix_tags", response_model=list[MixTag], tags=["info"])
def mix_tags(pair: str | None = None, rpc: RPC = Depends(get_rpc)):
    return rpc._rpc_mix_tag_performance(pair)


@router.get("/performance", response_model=list[PerformanceEntry], tags=["info"])
def performance(rpc: RPC = Depends(get_rpc), is_owner: bool = Depends(check_api_ownership)):
    if not is_owner:
        return []
    return rpc._rpc_performance()


@router.get("/profit", response_model=Profit, tags=["info"])
def profit(
    rpc: RPC = Depends(get_rpc), 
    config=Depends(get_config),
    is_owner: bool = Depends(check_api_ownership)
):
    if not is_owner:
        raise HTTPException(status_code=403, detail="Active account belongs to another user")
    return rpc._rpc_trade_statistics(config["stake_currency"], config.get("fiat_display_currency"))


@router.get("/profit_all", response_model=ProfitAll, tags=["info"])
def profit_all(
    rpc: RPC = Depends(get_rpc), 
    config=Depends(get_config),
    is_owner: bool = Depends(check_api_ownership)
):
    if not is_owner:
        raise HTTPException(status_code=403, detail="Active account belongs to another user")
    response = {
        "all": rpc._rpc_trade_statistics(
            config["stake_currency"], config.get("fiat_display_currency")
        ),
    }
    if config.get("trading_mode", TradingMode.SPOT) != TradingMode.SPOT:
        response["long"] = rpc._rpc_trade_statistics(
            config["stake_currency"], config.get("fiat_display_currency"), direction="long"
        )
        response["short"] = rpc._rpc_trade_statistics(
            config["stake_currency"], config.get("fiat_display_currency"), direction="short"
        )

    return response


@router.get("/stats", response_model=Stats, tags=["info"])
def stats(rpc: RPC = Depends(get_rpc), is_owner: bool = Depends(check_api_ownership)):
    if not is_owner:
        raise HTTPException(status_code=403, detail="Active account belongs to another user")
    return rpc._rpc_stats()


@router.get("/daily", response_model=DailyWeeklyMonthly, tags=["info"])
def daily(
    timescale: int = Query(7, ge=1, description="Number of days to fetch data for"),
    rpc: RPC = Depends(get_rpc),
    config=Depends(get_config),
    is_owner: bool = Depends(check_api_ownership)
):
    if not is_owner:
        raise HTTPException(status_code=403, detail="Active account belongs to another user")
    return rpc._rpc_timeunit_profit(
        timescale, config["stake_currency"], config.get("fiat_display_currency", "")
    )


@router.get("/weekly", response_model=DailyWeeklyMonthly, tags=["info"])
def weekly(
    timescale: int = Query(4, ge=1, description="Number of weeks to fetch data for"),
    rpc: RPC = Depends(get_rpc),
    config=Depends(get_config),
    is_owner: bool = Depends(check_api_ownership)
):
    if not is_owner:
        raise HTTPException(status_code=403, detail="Active account belongs to another user")
    return rpc._rpc_timeunit_profit(
        timescale, config["stake_currency"], config.get("fiat_display_currency", ""), "weeks"
    )


@router.get("/monthly", response_model=DailyWeeklyMonthly, tags=["info"])
def monthly(
    timescale: int = Query(3, ge=1, description="Number of months to fetch data for"),
    rpc: RPC = Depends(get_rpc),
    config=Depends(get_config),
    is_owner: bool = Depends(check_api_ownership)
):
    if not is_owner:
        raise HTTPException(status_code=403, detail="Active account belongs to another user")
    return rpc._rpc_timeunit_profit(
        timescale, config["stake_currency"], config.get("fiat_display_currency", ""), "months"
    )


@router.get("/status", response_model=list[OpenTradeSchema], tags=["info"])
def status(rpc: RPC = Depends(get_rpc), is_owner: bool = Depends(check_api_ownership)):
    if not is_owner:
        return []
    try:
        return rpc._rpc_trade_status()
    except RPCException:
        return []


# Using the responsemodel here will cause a ~100% increase in response time (from 1s to 2s)
# on big databases. Correct response model: response_model=TradeResponse,
@router.get("/trades", tags=["info", "trading"])
def trades(
    limit: int = Query(500, ge=1, description="Maximum number of different trades to return data"),
    offset: int = Query(0, ge=0, description="Number of trades to skip for pagination"),
    order_by_id: bool = Query(
        True, description="Sort trades by id (default: True). If False, sorts by latest timestamp"
    ),
    rpc: RPC = Depends(get_rpc),
    is_owner: bool = Depends(check_api_ownership)
):
    if not is_owner:
        return {"trades": [], "trades_count": 0, "offset": offset, "total_trades": 0}
    return rpc._rpc_trade_history(limit, offset=offset, order_by_id=order_by_id)


@router.get("/trade/{tradeid}", response_model=OpenTradeSchema, tags=["info", "trading"])
def trade(tradeid: int = 0, rpc: RPC = Depends(get_rpc)):
    try:
        return rpc._rpc_trade_status([tradeid])[0]
    except (RPCException, KeyError):
        raise HTTPException(status_code=404, detail="Trade not found.")


@router.delete("/trades/{tradeid}", response_model=DeleteTrade, tags=["info", "trading"])
def trades_delete(tradeid: int, rpc: RPC = Depends(get_rpc)):
    return rpc._rpc_delete(tradeid)


@router.delete("/trades/{tradeid}/open-order", response_model=OpenTradeSchema, tags=["trading"])
def trade_cancel_open_order(tradeid: int, rpc: RPC = Depends(get_rpc)):
    rpc._rpc_cancel_open_order(tradeid)
    return rpc._rpc_trade_status([tradeid])[0]


@router.post("/trades/{tradeid}/reload", response_model=OpenTradeSchema, tags=["trading"])
def trade_reload(tradeid: int, rpc: RPC = Depends(get_rpc)):
    rpc._rpc_reload_trade_from_exchange(tradeid)
    return rpc._rpc_trade_status([tradeid])[0]


@router.get("/trades/open/custom-data", response_model=list[ListCustomData], tags=["trading"])
def list_open_trades_custom_data(
    key: str | None = Query(None, description="Optional key to filter data"),
    limit: int = Query(100, ge=1, description="Maximum number of different trades to return data"),
    offset: int = Query(0, ge=0, description="Number of trades to skip for pagination"),
    rpc: RPC = Depends(get_rpc),
):
    """
    Fetch custom data for all open trades.
    If a key is provided, it will be used to filter data accordingly.
    Pagination is implemented via the `limit` and `offset` parameters.
    """
    try:
        return rpc._rpc_list_custom_data(key=key, limit=limit, offset=offset)
    except RPCException as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/trades/{trade_id}/custom-data", response_model=list[ListCustomData], tags=["trading"])
def list_custom_data(trade_id: int, key: str | None = Query(None), rpc: RPC = Depends(get_rpc)):
    """
    Fetch custom data for a specific trade.
    If a key is provided, it will be used to filter data accordingly.
    """
    try:
        return rpc._rpc_list_custom_data(trade_id, key=key)
    except RPCException as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/show_config", response_model=ShowConfig, tags=["info"])
def show_config(rpc: RPC | None = Depends(get_rpc_optional), config=Depends(get_config)):
    state: State | str = ""
    strategy_version = None
    if rpc:
        state = rpc._binancebot.state
        strategy_version = rpc._binancebot.strategy.version()
    resp = RPC._rpc_show_config(config, state, strategy_version)
    resp["api_version"] = API_VERSION
    return resp


# /forcebuy is deprecated with short addition. use /forceentry instead
@router.post("/forceenter", response_model=ForceEnterResponse, tags=["trading"])
@router.post("/forcebuy", response_model=ForceEnterResponse, tags=["trading"])
def force_entry(payload: ForceEnterPayload, rpc: RPC = Depends(get_rpc)):
    ordertype = payload.ordertype.value if payload.ordertype else None

    trade = rpc._rpc_force_entry(
        payload.pair,
        payload.price,
        order_side=payload.side,
        order_type=ordertype,
        stake_amount=payload.stakeamount,
        enter_tag=payload.entry_tag or "force_entry",
        leverage=payload.leverage,
    )

    if trade:
        return ForceEnterResponse.model_validate(trade.to_json())
    else:
        return ForceEnterResponse.model_validate(
            {"status": f"Error entering {payload.side} trade for pair {payload.pair}."}
        )


# /forcesell is deprecated with short addition. use /forceexit instead
@router.post("/forceexit", response_model=ResultMsg, tags=["trading"])
@router.post("/forcesell", response_model=ResultMsg, tags=["trading"])
def forceexit(payload: ForceExitPayload, rpc: RPC = Depends(get_rpc)):
    ordertype = payload.ordertype.value if payload.ordertype else None
    return rpc._rpc_force_exit(str(payload.tradeid), ordertype, amount=payload.amount)


@router.get("/blacklist", response_model=BlacklistResponse, tags=["info", "pairlist"])
def blacklist(rpc: RPC = Depends(get_rpc)):
    return rpc._rpc_blacklist()


@router.post("/blacklist", response_model=BlacklistResponse, tags=["info", "pairlist"])
def blacklist_post(payload: BlacklistPayload, rpc: RPC = Depends(get_rpc)):
    return rpc._rpc_blacklist(payload.blacklist)


@router.delete("/blacklist", response_model=BlacklistResponse, tags=["info", "pairlist"])
def blacklist_delete(pairs_to_delete: list[str] = Query([]), rpc: RPC = Depends(get_rpc)):
    """Provide a list of pairs to delete from the blacklist"""

    return rpc._rpc_blacklist_delete(pairs_to_delete)


@router.get("/whitelist", response_model=WhitelistResponse, tags=["info", "pairlist"])
def whitelist(rpc: RPC = Depends(get_rpc)):
    return rpc._rpc_whitelist()


@router.get("/locks", response_model=Locks, tags=["info", "locks"])
def locks(rpc: RPC = Depends(get_rpc)):
    return rpc._rpc_locks()


@router.delete("/locks/{lockid}", response_model=Locks, tags=["info", "locks"])
def delete_lock(lockid: int, rpc: RPC = Depends(get_rpc)):
    return rpc._rpc_delete_lock(lockid=lockid)


@router.post("/locks/delete", response_model=Locks, tags=["info", "locks"])
def delete_lock_pair(payload: DeleteLockRequest, rpc: RPC = Depends(get_rpc)):
    return rpc._rpc_delete_lock(lockid=payload.lockid, pair=payload.pair)


@router.post("/locks", response_model=Locks, tags=["info", "locks"])
def add_locks(payload: list[LocksPayload], rpc: RPC = Depends(get_rpc)):
    for lock in payload:
        rpc._rpc_add_lock(lock.pair, lock.until, lock.reason, lock.side)
    return rpc._rpc_locks()


@router.get("/logs", response_model=Logs, tags=["info"])
def logs(
    limit: int | None = None,
    is_owner: bool = Depends(check_api_ownership)
):
    if not is_owner:
        return {"log_count": 0, "logs": []}
    return RPC._rpc_get_logs(limit)


@router.post("/start", response_model=StatusMsg, tags=["botcontrol"])
def start(rpc: RPC = Depends(get_rpc)):
    return rpc._rpc_start()


@router.post("/stop", response_model=StatusMsg, tags=["botcontrol"])
def stop(rpc: RPC = Depends(get_rpc)):
    return rpc._rpc_stop()


@router.post("/pause", response_model=StatusMsg, tags=["botcontrol"])
@router.post("/stopentry", response_model=StatusMsg, tags=["botcontrol"])
@router.post("/stopbuy", response_model=StatusMsg, tags=["botcontrol"])
def pause(rpc: RPC = Depends(get_rpc)):
    return rpc._rpc_pause()


@router.post("/reload_config", response_model=StatusMsg, tags=["botcontrol"])
def reload_config(rpc: RPC = Depends(get_rpc)):
    return rpc._rpc_reload_config()


@router.get("/pair_candles", response_model=PairHistory, tags=["candle data"])
def pair_candles(pair: str, timeframe: str, limit: int | None = None, rpc: RPC = Depends(get_rpc)):
    return rpc._rpc_analysed_dataframe(pair, timeframe, limit, None)


@router.post("/pair_candles", response_model=PairHistory, tags=["candle data"])
def pair_candles_filtered(payload: PairCandlesRequest, rpc: RPC = Depends(get_rpc)):
    # Advanced pair_candles endpoint with column filtering
    return rpc._rpc_analysed_dataframe(
        payload.pair, payload.timeframe, payload.limit, payload.columns
    )


@router.get("/plot_config", response_model=PlotConfig, tags=["candle data"])
def plot_config(
    strategy: str | None = None,
    config=Depends(get_config),
    rpc: RPC | None = Depends(get_rpc_optional),
):
    if not strategy:
        if not rpc:
            raise RPCException("Strategy is mandatory in webserver mode.")
        return PlotConfig.model_validate(rpc._rpc_plot_config())
    else:
        config1 = deepcopy(config)
        config1.update({"strategy": strategy})
    try:
        return PlotConfig.model_validate(RPC._rpc_plot_config_with_strategy(config1))
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


@router.get("/strategies", response_model=StrategyListResponse, tags=["strategy"])
def list_strategies(config=Depends(get_config)):
    from binancebot.resolvers.strategy_resolver import StrategyResolver

    strategies = StrategyResolver.search_all_objects(
        config, False, config.get("recursive_strategy_search", False)
    )
    strategies = sorted(strategies, key=lambda x: x["name"])

    return {"strategies": [x["name"] for x in strategies]}


@router.get("/strategy/{strategy}", response_model=StrategyResponse, tags=["strategy"])
def get_strategy(strategy: str, config=Depends(get_config)):
    if ":" in strategy:
        raise HTTPException(status_code=500, detail="base64 encoded strategies are not allowed.")

    config_ = deepcopy(config)
    from binancebot.resolvers.strategy_resolver import StrategyResolver

    try:
        strategy_obj = StrategyResolver._load_strategy(
            strategy, config_, extra_dir=config_.get("strategy_path")
        )
    except OperationalException:
        raise HTTPException(status_code=404, detail="Strategy not found")
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))
    return {
        "strategy": strategy_obj.get_strategy_name(),
        "code": strategy_obj.__source__,
        "timeframe": getattr(strategy_obj, "timeframe", None),
    }


@router.get("/exchanges", response_model=ExchangeListResponse, tags=[])
def list_exchanges(config=Depends(get_config)):
    from binancebot.exchange import list_available_exchanges

    exchanges = list_available_exchanges(config)
    return {
        "exchanges": exchanges,
    }


@router.get(
    "/hyperoptloss", response_model=HyperoptLossListResponse, tags=["hyperopt", "webserver"]
)
def list_hyperoptloss(
    config=Depends(get_config),
):
    import textwrap

    from binancebot.resolvers.hyperopt_resolver import HyperOptLossResolver

    loss_functions = HyperOptLossResolver.search_all_objects(config, False)
    loss_functions = sorted(loss_functions, key=lambda x: x["name"])

    return {
        "loss_functions": [
            {
                "name": x["name"],
                "description": textwrap.dedent((x["class"].__doc__ or "").strip()),
            }
            for x in loss_functions
        ]
    }


@router.get("/AIMLmodels", response_model=AIMLModelListResponse, tags=["AIML"])
def list_AIMLmodels(config=Depends(get_config)):
    from binancebot.resolvers.AIMLmodel_resolver import AIMLModelResolver

    models = AIMLModelResolver.search_all_objects(config, False)
    models = sorted(models, key=lambda x: x["name"])

    return {"AIMLmodels": [x["name"] for x in models]}


@router.get("/available_pairs", response_model=AvailablePairs, tags=["candle data"])
def list_available_pairs(
    timeframe: str | None = None,
    stake_currency: str | None = None,
    candletype: CandleType | None = None,
    config=Depends(get_config),
):
    dh = get_datahandler(config["datadir"], config.get("dataformat_ohlcv"))
    trading_mode: TradingMode = config.get("trading_mode", TradingMode.SPOT)
    pair_interval = dh.ohlcv_get_available_data(config["datadir"], trading_mode)

    if timeframe:
        pair_interval = [pair for pair in pair_interval if pair[1] == timeframe]
    if stake_currency:
        pair_interval = [pair for pair in pair_interval if pair[0].endswith(stake_currency)]
    if candletype:
        pair_interval = [pair for pair in pair_interval if pair[2] == candletype]
    else:
        candle_type = CandleType.get_default(trading_mode)
        pair_interval = [pair for pair in pair_interval if pair[2] == candle_type]

    pair_interval = sorted(pair_interval, key=lambda x: x[0])

    pairs = list({x[0] for x in pair_interval})
    pairs.sort()
    result = {
        "length": len(pairs),
        "pairs": pairs,
        "pair_interval": pair_interval,
    }
    return result


@router.get("/markets", response_model=MarketResponse, tags=["candle data", "webserver"])
def markets(
    query: Annotated[MarketRequest, Query()],
    config=Depends(get_config),
    rpc: RPC | None = Depends(get_rpc_optional),
):
    if not rpc or config["runmode"] == RunMode.WEBSERVER:
        # webserver mode
        config_loc = deepcopy(config)
        handleExchangePayload(query, config_loc)
        exchange = get_exchange(config_loc)
    else:
        exchange = rpc._binancebot.exchange

    return {
        "markets": exchange.get_markets(
            base_currencies=[query.base] if query.base else None,
            quote_currencies=[query.quote] if query.quote else None,
        ),
        "exchange_id": exchange.id,
    }


@router.get("/sysinfo", response_model=SysInfo, tags=["info"])
def sysinfo():
    return RPC._rpc_sysinfo()


@router.get("/health", response_model=Health, tags=["info"])
def health(rpc: RPC = Depends(get_rpc)):
    return rpc.health()


@router.post("/set_exchange_config", response_model=StatusMsg, tags=["botcontrol"])
def set_exchange_config(
    payload: ExchangeConfigPayload, 
    rpc: RPC = Depends(get_rpc), 
    config=Depends(get_config),
    user: str = Depends(http_basic_or_jwt_token)
):
    """Update exchange API credentials and trading mode at runtime.
    
    This allows the frontend to configure the exchange connection
    with user-provided API keys and trading mode (spot/futures).
    """
    import json
    import os
    
    # SECURITY: Verify that the user owns the API key they are trying to activate
    api_cfg = config.get("api_server", {})
    user_profiles = []
    if user == api_cfg.get("username", "admin"):
        # Explicitly allow the primary admin to set the hardcoded keys if they match
        if payload.api_key == api_cfg.get("key"):
             pass # Allowed
        else:
             user_profiles = api_cfg.get("profiles", [])
    else:
        for u in api_cfg.get("users", []):
            if u.get("username") == user:
                user_profiles = u.get("profiles", [])
                break
    
    is_owner = any(p.get("api_key") == payload.api_key for p in user_profiles)
    if not is_owner and not (user == api_cfg.get("username", "admin") and payload.api_key == api_cfg.get("key")):
         raise HTTPException(status_code=403, detail="You do not own this API profile.")

    try:
        # Get config file path - use hardcoded path since config dict doesn't store path as string
        config_path = 'config/config.json'
        
        # Try to find config path from command line args if available
        original_config = config.get('original_config')
        if isinstance(original_config, str) and os.path.exists(original_config):
            config_path = original_config
        elif not os.path.exists(config_path):
            # Try alternative paths
            for try_path in ['config/config.json', './config.json', 'user_data/config.json']:
                if os.path.exists(try_path):
                    config_path = try_path
                    break
        
        # Read current config
        with open(config_path, 'r') as f:
            file_config = json.load(f)
        
        # Update exchange credentials
        if 'exchange' not in file_config:
            file_config['exchange'] = {}
        
        # Set active keys
        file_config['exchange']['key'] = payload.api_key
        file_config['exchange']['secret'] = payload.secret_key
        
        # Update trading mode
        file_config['trading_mode'] = payload.trading_mode
        if payload.trading_mode == 'futures' and payload.margin_mode:
            file_config['margin_mode'] = payload.margin_mode
        elif 'margin_mode' in file_config and payload.trading_mode == 'spot':
            # Remove margin_mode if switching to spot
            file_config.pop('margin_mode', None)
        
        # Ensure sandbox is false as we only use Live Trading
        file_config['exchange']['ccxt_config'] = file_config['exchange'].get('ccxt_config', {})
        file_config['exchange']['ccxt_async_config'] = file_config['exchange'].get('ccxt_async_config', {})
        file_config['exchange']['ccxt_config']['sandbox'] = False
        file_config['exchange']['ccxt_async_config']['sandbox'] = False
        
        # Remove any legacy testnet URLs
        if 'urls' in file_config['exchange']['ccxt_config']:
            file_config['exchange']['ccxt_config'].pop('urls', None)
        if 'urls' in file_config['exchange']['ccxt_async_config']:
            file_config['exchange']['ccxt_async_config'].pop('urls', None)

        # Update database URL if provided (for multi-account isolation)
        if payload.db_url:
            logger.info(f"Updating DB URL to: {payload.db_url}")
            file_config['db_url'] = payload.db_url
        else:
             logger.info("No DB URL provided in payload.")
        
        # Write updated config
        with open(config_path, 'w') as f:
            json.dump(file_config, f, indent=4)
        
        logger.info(f"Exchange config updated: trading_mode={payload.trading_mode}")
        
        # Trigger bot reconfiguration to apply changes immediately
        try:
            rpc._rpc_reload_config()
            logger.info("Bot reconfiguration triggered - changes will apply shortly")
            return {"status": f"Config updated and bot reloading. Mode: {payload.trading_mode}"}
        except Exception as reload_err:
            logger.warning(f"Could not trigger reload: {reload_err}. Restart backend manually.")
            return {"status": f"Config updated. Mode: {payload.trading_mode}. Restart backend to apply."}
        
    except Exception as e:
        logger.error(f"Failed to update exchange config: {e}")
        raise HTTPException(status_code=500, detail=str(e))


