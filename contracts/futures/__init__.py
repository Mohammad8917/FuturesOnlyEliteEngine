"""Canonical Futures domain boundary contracts."""

from .contract_specification import (
    ContractSpecificationValidationError,
    FuturesContractSpecification,
    QuantityUnit,
)
from .settlement import FuturesSettlementSpecification, SettlementUnit, SettlementValidationError
from .margin import FuturesMarginSpecification, MarginUnit, MarginValidationError
from .leverage import FuturesLeverageSpecification, LeverageUnit, LeverageValidationError
from .maintenance_margin import (
    FuturesMaintenanceMarginSpecification,
    MaintenanceMarginUnit,
    MaintenanceMarginValidationError,
)
from .initial_margin import (
    FuturesInitialMarginSpecification,
    InitialMarginUnit,
    InitialMarginValidationError,
)
from .instrument import (
    CanonicalFuturesSymbol,
    ContractFamily,
    FuturesInstrumentIdentity,
    InstrumentStatus,
    InstrumentValidationError,
    Market,
)

__all__ = [
    "CanonicalFuturesSymbol",
    "ContractFamily",
    "ContractSpecificationValidationError",
    "FuturesContractSpecification",
    "FuturesInstrumentIdentity",
    "FuturesSettlementSpecification",
    "FuturesMarginSpecification",
    "FuturesLeverageSpecification",
    "InstrumentStatus",
    "InstrumentValidationError",
    "Market",
    "SettlementUnit",
    "MarginUnit",
    "MarginValidationError",
    "LeverageUnit",
    "LeverageValidationError",
    "FuturesMaintenanceMarginSpecification",
    "MaintenanceMarginUnit",
    "MaintenanceMarginValidationError",
    "FuturesInitialMarginSpecification",
    "InitialMarginUnit",
    "InitialMarginValidationError",
    "SettlementValidationError",
    "QuantityUnit",
]
