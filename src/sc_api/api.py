import logging
import json
from typing import List, Optional, Dict, Any
from .cli_manager import CLIManager
from .runner import ScalableRunner
from .models import (
    Holding, HoldingsResponse, Transaction, TransactionsResponse, 
    UserInfo, TradeResponse, Overview, Security, SearchResponse
)

logger = logging.getLogger(__name__)

class ScalableAPIError(Exception):
    """Custom exception for API errors."""
    pass

class ScalableNotLoggedInError(ScalableAPIError):
    """Custom exception for when the user is not logged in."""
    pass

class Broker:
    """
    Sub-api representing 'sc broker' commands.
    Requires an authenticated session to be initialized.
    """
    
    def __init__(self, api: "ScalableAPI", info: UserInfo):
        self._api = api
        self.user = User(info)

    def get_holdings(self) -> List[Holding]:
        """Returns the current portfolio holdings."""
        res = self._api._call(["broker", "holdings"])
        data = res.get("data", {}).get("result", {})
        return HoldingsResponse.model_validate(data).items

    def trade_buy(self, isin: str, amount: float, order_type: str = "market", confirm_id: Optional[str] = None) -> TradeResponse:
        """
        Executes a buy order in two phases.
        Phase 1 (preview): Call without confirm_id.
        Phase 2 (submit): Call with confirm_id.
        """
        args = ["broker", "trade", "buy", "--isin", isin, "--amount", str(amount), "--order-type", order_type]
        if confirm_id:
            args.extend(["--confirm", confirm_id])
            
        res = self._api._call(args)
        data = res.get("data", {}).get("result", res)
        return TradeResponse.model_validate(data)

    def trade_sell(self, isin: str, amount: float, order_type: str = "market", confirm_id: Optional[str] = None) -> TradeResponse:
        """
        Executes a sell order in two phases.
        Phase 1 (preview): Call without confirm_id.
        Phase 2 (submit): Call with confirm_id.
        """
        args = ["broker", "trade", "sell", "--isin", isin, "--amount", str(amount), "--order-type", order_type]
        if confirm_id:
            args.extend(["--confirm", confirm_id])
            
        res = self._api._call(args)
        data = res.get("data", {}).get("result", res)
        return TradeResponse.model_validate(data)

    def get_transactions(self) -> List[Transaction]:
        """Returns the current portfolio transactions."""
        res = self._api._call(["broker", "transactions"])
        data = res.get("data", {}).get("result", {})
        return TransactionsResponse.model_validate(data).items

    def get_overview(self) -> Overview:
        """Returns the current portfolio overview."""
        res = self._api._call(["broker", "overview"])
        return Overview.from_api_dict(res)

    def search(self, query: str) -> List[Security]:
        """Returns a list of securities matching the query (authenticated)."""
        res = self._api._call(["broker", "search", query])
        data = res.get("data", {}).get("result", {})
        return SearchResponse.model_validate(data).items

class User:
    """
    Represents an authenticated Scalable user session details.
    """
    
    def __init__(self, info: UserInfo):
        self.info = info

    @property
    def first_name(self) -> str:
        return self.info.first_name

    @property
    def last_name(self) -> str:
        return self.info.last_name

    def __repr__(self) -> str:
        return f"User(name='{self.first_name} {self.last_name}')"

    __str__ = __repr__

class ScalableAPI:
    """
    Main entry point for the Scalable CLI Python wrapper.
    Handles authentication and session management.
    """
    
    def __init__(self, manager: Optional[CLIManager] = None):
        self.manager = manager or CLIManager()
        self._runner: Optional[ScalableRunner] = None
        self._broker: Optional[Broker] = None
        
    @property
    def runner(self) -> ScalableRunner:
        """Lazily initializes and returns the runner."""
        if self._runner is None:
            if not self.manager.is_installed():
                raise ScalableAPIError(
                    "CLI binary not found. Please install it using "
                    "CLIManager().download_and_install()"
                )
            bin_path = self.manager.get_bin_path()
            if not bin_path:
                raise ScalableAPIError("CLI binary path could not be resolved.")
            self._runner = ScalableRunner(bin_path)
        return self._runner

    def _call(self, args: List[str], use_json: bool = True, capture_output: bool = True) -> Dict[str, Any]:
        """Internal helper to call the runner and handle global errors."""
        result = self.runner.run(args, use_json=use_json, capture_output=capture_output)
        
        if result.get("ok") is False:
            raw_err = result.get("error", "Unknown error")
            
            # Try to parse JSON error if present
            try:
                err_data = json.loads(str(raw_err))
                msg = err_data.get("error", {}).get("message", raw_err)
                code = err_data.get("error", {}).get("code", "")
            except (json.JSONDecodeError, TypeError, AttributeError):
                msg = raw_err
                code = ""

            if "not logged in" in str(msg).lower() or code == "no_session":
                 raise ScalableNotLoggedInError(msg)
            
            raise ScalableAPIError(f"Command failed: {msg}")
            
        return result

    def login(self, interactive: bool = True) -> Broker:
        """
        Smart login: Checks if already authenticated.
        Returns a Broker object for authenticated commands.
        """
        try:
            return self.whoami()
        except ScalableNotLoggedInError:
            if not interactive:
                raise ScalableNotLoggedInError(
                    "No active session and interactive login is disabled. Please run `sc login`."
                )
            
            logger.info("Starting interactive login flow...")
            self._call(["login"], use_json=False, capture_output=False)
            return self.whoami()

    def logout(self) -> None:
        """Logs out and clears the session."""
        self._call(["logout"], use_json=False)
        self._broker = None

    def whoami(self) -> Broker:
        """Returns the current Broker session (cached)."""
        if self._broker:
            return self._broker

        res = self._call(["whoami"])
        result = res.get("data", {}).get("result", {})
        details = result.get("personOverview", {}).get("personalDetails", {})
        info = UserInfo.model_validate(details)
        self._broker = Broker(self, info)
        return self._broker

    def get_installation_code(self) -> str:
        """Returns the installation code (top-level command)."""
        res = self._call(["installation-code"])
        return res["data"]["installation_code"]