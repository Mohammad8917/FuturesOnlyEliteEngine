"""Canonical Futures instrument identity contract.

This module contains deterministic, exchange-independent boundary vocabulary.
Exchange-specific symbols and transport metadata must be mapped to this contract
at the infrastructure boundary; they are not part of the canonical identity.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from enum import StrEnum
import re


_ASSET_RE = re.compile(r"^[A-Z][A-Z0-9]{0,15}$")
_INSTRUMENT_ID_RE = re.compile(r"^FUTURES\|(CRYPTO|FOREX|GOLD)\|.+$")
_CANONICAL_RE = re.compile(
    r"^(?P<base>[A-Z][A-Z0-9]{0,15})/"
    r"(?P<quote>[A-Z][A-Z0-9]{0,15})\."
    r"(?P<family>LINEAR|INVERSE)\."
    r"(?P<settlement>[A-Z][A-Z0-9]{0,15})"
    r"(?:\.(?P<expiry>[0-9]{8}))?$"
)


class InstrumentValidationError(ValueError):
    """Raised when a Futures instrument identity is invalid or ambiguous."""


class Market(StrEnum):
    CRYPTO = "CRYPTO"
    FOREX = "FOREX"
    GOLD = "GOLD"


class ContractFamily(StrEnum):
    LINEAR = "LINEAR"
    INVERSE = "INVERSE"


class InstrumentStatus(StrEnum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    EXPIRED = "EXPIRED"
    DELISTED = "DELISTED"


def _asset(value: str, field: str) -> str:
    if not isinstance(value, str):
        raise InstrumentValidationError(f"{field} must be a string")
    normalized = value.strip().upper()
    if not _ASSET_RE.fullmatch(normalized):
        raise InstrumentValidationError(f"{field} is not a valid canonical asset")
    if normalized.startswith("SPOT"):
        raise InstrumentValidationError(f"{field} contains forbidden Spot semantics")
    return normalized


@dataclass(frozen=True, slots=True)
class CanonicalFuturesSymbol:
    """Exchange-independent canonical symbol for one Futures contract.

    Format:
      BASE/QUOTE.FAMILY.SETTLEMENT
      BASE/QUOTE.FAMILY.SETTLEMENT.YYYYMMDD

    Missing expiry means perpetual Futures; a supplied expiry identifies a
    dated/expiring Futures contract. The family and settlement are always
    explicit and never inferred from an exchange-specific symbol.
    """

    base_asset: str
    quote_asset: str
    contract_family: ContractFamily
    settlement_asset: str
    expiry: date | None = None

    def __post_init__(self) -> None:
        base = _asset(self.base_asset, "base_asset")
        quote = _asset(self.quote_asset, "quote_asset")
        settlement = _asset(self.settlement_asset, "settlement_asset")

        if base == quote:
            raise InstrumentValidationError("base_asset and quote_asset must differ")
        if base == settlement and self.contract_family is ContractFamily.LINEAR:
            raise InstrumentValidationError(
                "Linear settlement must be explicit and cannot equal base asset"
            )
        if self.expiry is not None and not isinstance(self.expiry, date):
            raise InstrumentValidationError("expiry must be a date or None")

        object.__setattr__(self, "base_asset", base)
        object.__setattr__(self, "quote_asset", quote)
        object.__setattr__(self, "settlement_asset", settlement)

    def as_text(self) -> str:
        value = (
            f"{self.base_asset}/{self.quote_asset}."
            f"{self.contract_family.value}.{self.settlement_asset}"
        )
        if self.expiry is not None:
            value += f".{self.expiry:%Y%m%d}"
        return value

    @classmethod
    def parse(cls, value: str) -> "CanonicalFuturesSymbol":
        if not isinstance(value, str):
            raise InstrumentValidationError("canonical symbol must be a string")
        normalized = value.strip().upper()
        match = _CANONICAL_RE.fullmatch(normalized)
        if not match:
            raise InstrumentValidationError(
                "invalid canonical Futures symbol; expected "
                "BASE/QUOTE.LINEAR|INVERSE.SETTLEMENT[.YYYYMMDD]"
            )

        expiry_text = match.group("expiry")
        expiry = None
        if expiry_text is not None:
            try:
                expiry = date(
                    int(expiry_text[0:4]),
                    int(expiry_text[4:6]),
                    int(expiry_text[6:8]),
                )
            except ValueError as exc:
                raise InstrumentValidationError("invalid Futures expiry date") from exc

        return cls(
            base_asset=match.group("base"),
            quote_asset=match.group("quote"),
            contract_family=ContractFamily(match.group("family")),
            settlement_asset=match.group("settlement"),
            expiry=expiry,
        )


@dataclass(frozen=True, slots=True)
class FuturesInstrumentIdentity:
    """Validated, stable identity for a Futures instrument.

    The identity is derived only from canonical Futures semantics and market
    scope. Exchange-specific symbols are deliberately excluded.
    """

    instrument_id: str
    market: Market
    symbol: CanonicalFuturesSymbol
    margin_asset: str
    status: InstrumentStatus = InstrumentStatus.ACTIVE

    def __post_init__(self) -> None:
        if not isinstance(self.market, Market):
            raise InstrumentValidationError("market must be a supported Futures market")
        if not isinstance(self.symbol, CanonicalFuturesSymbol):
            raise InstrumentValidationError("symbol must be CanonicalFuturesSymbol")
        if not isinstance(self.status, InstrumentStatus):
            raise InstrumentValidationError("status must be a known instrument status")

        margin = _asset(self.margin_asset, "margin_asset")
        expected_id = self.build_id(self.market, self.symbol)
        if self.instrument_id != expected_id:
            raise InstrumentValidationError(
                "instrument_id must equal the deterministic canonical Futures identity"
            )

        object.__setattr__(self, "margin_asset", margin)

    @staticmethod
    def build_id(market: Market, symbol: CanonicalFuturesSymbol) -> str:
        if not isinstance(market, Market):
            raise InstrumentValidationError("market must be a supported Futures market")
        return f"FUTURES|{market.value}|{symbol.as_text()}"

    @classmethod
    def create(
        cls,
        *,
        market: Market,
        symbol: CanonicalFuturesSymbol,
        margin_asset: str,
        status: InstrumentStatus = InstrumentStatus.ACTIVE,
    ) -> "FuturesInstrumentIdentity":
        return cls(
            instrument_id=cls.build_id(market, symbol),
            market=market,
            symbol=symbol,
            margin_asset=margin_asset,
            status=status,
        )

    @classmethod
    def parse_id(
        cls,
        instrument_id: str,
        *,
        margin_asset: str,
        status: InstrumentStatus = InstrumentStatus.ACTIVE,
    ) -> "FuturesInstrumentIdentity":
        if not isinstance(instrument_id, str) or not _INSTRUMENT_ID_RE.fullmatch(instrument_id):
            raise InstrumentValidationError("invalid canonical Futures instrument_id")

        _, market_text, symbol_text = instrument_id.split("|", 2)
        market = Market(market_text)
        symbol = CanonicalFuturesSymbol.parse(symbol_text)
        return cls.create(
            market=market,
            symbol=symbol,
            margin_asset=margin_asset,
            status=status,
        )
