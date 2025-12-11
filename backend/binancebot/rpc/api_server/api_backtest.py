import asyncio
import logging
from copy import deepcopy
from datetime import datetime
from pathlib import Path
from typing import Any

from fastapi import APIRouter, BackgroundTasks, Depends
from fastapi.exceptions import HTTPException

from binancebot.configuration import remove_exchange_credentials
from binancebot.configuration.config_validation import validate_config_consistency
from binancebot.constants import Config
from binancebot.data.btanalysis import (
    delete_backtest_result,
    get_backtest_market_change,
    get_backtest_result,
    get_backtest_resultlist,
    load_and_merge_backtest_result,
    update_backtest_metadata,
)
from binancebot.enums import BacktestState
from binancebot.exceptions import ConfigurationError, DependencyException, OperationalException
from binancebot.ft_types import get_BacktestResultType_default
from binancebot.misc import deep_merge_dicts, is_file_in_dir
from binancebot.rpc.api_server.api_schemas import (
    BacktestHistoryEntry,
    BacktestMarketChange,
    BacktestMetadataUpdate,
    BacktestRequest,
    BacktestResponse,
)
from binancebot.rpc.api_server.deps import get_config
from binancebot.rpc.api_server.webserver_bgwork import ApiBG
from binancebot.rpc.rpc import RPCException


logger = logging.getLogger(__name__)

# Private API, protected by authentication and webserver_mode dependency
router = APIRouter()


