from datetime import datetime
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field, field_validator, ConfigDict

class Holding(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    
    isin: str
    name: str
    quantity: float
    fifo_price: float = Field(alias="fifo_price")
    valuation: float
    valuation_currency: str
    quote_mid_price: float
    quote_currency: str
    quote_timestamp_utc: datetime
    quote_is_outdated: bool
    security_type: str
    blocked_quantity: float
    pending_quantity: float

    def __repr__(self) -> str:
        ts = self.quote_timestamp_utc.strftime("%Y-%m-%d %H:%M")
        return f"{ts} | [HOLDING] {self.isin:12} | {self.name[:30]:30} | {self.quantity:10.2f}x @ {self.quote_mid_price:8.2f} {self.quote_currency:3} | VAL: {self.valuation:10.2f} {self.valuation_currency:3}"
    
    __str__ = __repr__

class HoldingsResponse(BaseModel):
    account_id: str
    portfolio_id: str
    items: List[Holding]
    count: int

    def __repr__(self) -> str:
        return f"HoldingsResponse(count={self.count}, portfolio='{self.portfolio_id}')"
    
    __str__ = __repr__

class Transaction(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    type: str  # SECURITY_TRANSACTION | CASH_TRANSACTION
    status: str
    amount: float
    currency: str
    description: str
    timestamp: datetime = Field(alias="last_event_datetime")
    custodian: str
    is_cancellation: bool
    
    # Security transaction specific
    isin: Optional[str] = None
    side: Optional[str] = None  # BUY | SELL
    quantity: Optional[float] = None
    security_transaction_type: Optional[str] = None
    limit_price: Optional[float] = None
    stop_price: Optional[float] = None
    
    # Cash transaction specific
    cash_transaction_type: Optional[str] = None
    related_isin: Optional[str] = None

    def __repr__(self) -> str:
        ts = self.timestamp.strftime("%Y-%m-%d %H:%M")
        details = ""
        if self.type == "SECURITY_TRANSACTION":
            side = self.side or ""
            isin = self.isin or ""
            quantity = self.quantity or 0.0
            details = f"{side:4} {quantity:8.2f}x {isin:12}"
        elif self.type == "CASH_TRANSACTION":
            ctype = self.cash_transaction_type or "CASH"
            isin = self.related_isin or ""
            details = f"{ctype[:15]:15}"
            if isin:
                details += f" ({isin:12})"
        
        return f"{ts} | [TRANS   ] {self.amount:10.2f} {self.currency:3} | {self.type[:15]:15} | {details} | {self.description[:40]}"

    __str__ = __repr__

class TransactionsResponse(BaseModel):
    items: List[Transaction]
    count: int

class UserInfo(BaseModel):
    first_name: str = Field(alias="firstName")
    last_name: str = Field(alias="lastName")

    def __repr__(self) -> str:
        return f"UserInfo(name='{self.first_name} {self.last_name}')"

    __str__ = __repr__

class TradeResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    confirmation_id: Optional[str] = Field(None, alias="confirmationId")
    order_id: Optional[str] = Field(None, alias="orderId")
    status: Optional[str] = None

    def __repr__(self) -> str:
        return f"TradeResponse(status='{self.status}', order_id='{self.order_id}', confirmation_id='{self.confirmation_id}')"

    __str__ = __repr__

class PerformanceMetric(BaseModel):
    timeframe: str
    performance: float
    simple_absolute_return: float = Field(alias="simpleAbsoluteReturn")
    currency: str = "EUR"

    def __repr__(self) -> str:
        return f"{self.timeframe:10} | {self.performance:6.2f}% | {self.simple_absolute_return:10.2f} {self.currency:3}"

    __str__ = __repr__

class Overview(BaseModel):
    account_id: str
    portfolio_id: str
    total: float
    securities: float
    crypto: float
    inventory_timestamp_utc: datetime
    valuation_timestamp_utc: datetime
    performance: List[PerformanceMetric]

    @classmethod
    def from_api_dict(cls, data: Dict[str, Any]) -> "Overview":
        # The overview JSON is particularly nested, so we help Pydantic a bit
        result = data.get("data", {}).get("result", data)
        val = result.get("valuation", {})
        ts = result.get("timestamps", {})
        
        return cls(
            account_id=result.get("account_id", ""),
            portfolio_id=result.get("portfolio_id", ""),
            total=val.get("total", 0),
            securities=val.get("securities", 0),
            crypto=val.get("crypto", 0),
            inventory_timestamp_utc=ts.get("inventory_timestamp_utc") or datetime.min,
            valuation_timestamp_utc=ts.get("valuation_timestamp_utc") or datetime.min,
            performance=result.get("performance", []),
        )

    def __repr__(self) -> str:
        ts = self.valuation_timestamp_utc.strftime("%Y-%m-%d %H:%M")
        return f"{ts} | [OVERVIEW] TOTAL: {self.total:10.2f} | SEC: {self.securities:10.2f} | CRYPTO: {self.crypto:10.2f}"

    __str__ = __repr__

class Security(BaseModel):
    isin: str
    name: str
    quote_currency: str
    quote_is_outdated: bool
    quote_mid_price: float
    quote_timestamp_utc: datetime
    security_type: str

    def __repr__(self) -> str:
        ts = self.quote_timestamp_utc.strftime("%Y-%m-%d %H:%M")
        return f"{ts} | [SECURITY] {self.isin:12} | {self.name[:30]:30} | PRICE: {self.quote_mid_price:8.2f} {self.quote_currency:3} | {self.security_type:10}"

    __str__ = __repr__

class SearchResponse(BaseModel):
    items: List[Security]
    count: int
    portfolio_id: str
    query: str