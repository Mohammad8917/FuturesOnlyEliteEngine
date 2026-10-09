from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from domain.futures.contract_specification import (
    FuturesContractSpecification,
    QuantityUnit,
)
from domain.futures.exposure import (
    ExposureDenomination,
    ExposureValidationError,
    FuturesExposureSpecification,
)
from contracts.futures.instrument import CanonicalFuturesSymbol, ContractFamily, Market
from contracts.futures.position_side import PositionSide

UTC = timezone.utc


def make_symbol(market: Market, family: ContractFamily) -> CanonicalFuturesSymbol:
    base = "BTC" if market is Market.CRYPTO else "XAU"
    return CanonicalFuturesSymbol(base, "USD", family, "USD")


def make_contract(
    market: Market, family: ContractFamily
) -> FuturesContractSpecification:
    return FuturesContractSpecification(
        market=market,
        symbol=make_symbol(market, family),
        quantity_unit=QuantityUnit.CONTRACTS,
        contract_multiplier=Decimal("100"),
        price_quote_asset="USD",
    )


@pytest.mark.parametrize("market", list(Market))
@pytest.mark.parametrize("family", list(ContractFamily))
def test_scope_is_explicit_for_all_markets_and_families(market, family):
    specification = FuturesExposureSpecification(market, make_symbol(market, family))
    assert specification.market is market
    assert specification.symbol.contract_family is family


def test_linear_base_and_quote_value_are_distinct():
    contract = make_contract(Market.CRYPTO, ContractFamily.LINEAR)
    specification = FuturesExposureSpecification(Market.CRYPTO, contract.symbol)

    assert specification.base_exposure(
        contract=contract, quantity=Decimal("2"), price=Decimal("50")
    ) == Decimal("200")
    assert specification.quote_value(
        contract=contract, quantity=Decimal("2"), reference_price=Decimal("50")
    ) == Decimal("10000")


def test_inverse_base_and_quote_value_are_distinct():
    contract = make_contract(Market.CRYPTO, ContractFamily.INVERSE)
    specification = FuturesExposureSpecification(Market.CRYPTO, contract.symbol)

    assert specification.base_exposure(
        contract=contract, quantity=Decimal("2"), price=Decimal("50")
    ) == Decimal("4")
    assert specification.quote_value(
        contract=contract, quantity=Decimal("2"), reference_price=Decimal("50")
    ) == Decimal("200")


def test_side_only_changes_signed_direction_not_gross_magnitude():
    contract = make_contract(Market.CRYPTO, ContractFamily.LINEAR)
    specification = FuturesExposureSpecification(Market.CRYPTO, contract.symbol)

    long_value = specification.signed_quote_value(
        contract=contract,
        quantity=Decimal("2"),
        reference_price=Decimal("50"),
        position_side=PositionSide.LONG,
    )
    short_value = specification.signed_quote_value(
        contract=contract,
        quantity=Decimal("2"),
        reference_price=Decimal("50"),
        position_side=PositionSide.SHORT,
    )

    assert long_value == Decimal("10000")
    assert short_value == Decimal("-10000")
    assert abs(long_value) == abs(short_value)


def test_explicit_denomination_and_reference_provenance():
    contract = make_contract(Market.CRYPTO, ContractFamily.LINEAR)
    specification = FuturesExposureSpecification(Market.CRYPTO, contract.symbol)

    assert specification.value(
        contract=contract,
        quantity=Decimal("2"),
        reference_price=Decimal("50.123456789"),
        denomination=ExposureDenomination.BASE,
        valuation_source="synthetic-reference",
        observed_at=datetime(2026, 1, 1, 12, tzinfo=UTC),
    ) == Decimal("200")


@pytest.mark.parametrize(
    "value", [True, False, 0, -1, 0.1, float("nan"), Decimal("NaN")]
)
def test_financial_inputs_fail_closed(value):
    contract = make_contract(Market.CRYPTO, ContractFamily.LINEAR)
    specification = FuturesExposureSpecification(Market.CRYPTO, contract.symbol)

    with pytest.raises(ExposureValidationError):
        specification.base_exposure(
            contract=contract, quantity=value, price=Decimal("50")
        )


def test_reference_provenance_and_freshness_fail_closed():
    contract = make_contract(Market.CRYPTO, ContractFamily.LINEAR)
    specification = FuturesExposureSpecification(Market.CRYPTO, contract.symbol)

    with pytest.raises(ExposureValidationError):
        specification.value(
            contract=contract,
            quantity=Decimal("1"),
            reference_price=Decimal("100"),
            denomination=ExposureDenomination.QUOTE,
            valuation_source="",
            observed_at=datetime(2026, 1, 1, 12, tzinfo=UTC),
        )

    specification.validate_reference_freshness(
        as_of=datetime(2026, 1, 1, 12, 30, tzinfo=UTC),
        observed_at=datetime(2026, 1, 1, 12, tzinfo=UTC),
        max_age=timedelta(hours=1),
    )

    with pytest.raises(ExposureValidationError):
        specification.validate_reference_freshness(
            as_of=datetime(2026, 1, 1, 14, tzinfo=UTC),
            observed_at=datetime(2026, 1, 1, 12, tzinfo=UTC),
            max_age=timedelta(hours=1),
        )

    with pytest.raises(ExposureValidationError):
        specification.validate_reference_freshness(
            as_of=datetime(2026, 1, 1, 11, 59, tzinfo=UTC),
            observed_at=datetime(2026, 1, 1, 12, tzinfo=UTC),
            max_age=timedelta(hours=1),
        )


def test_mismatched_contract_and_side_fail_closed():
    contract = make_contract(Market.CRYPTO, ContractFamily.LINEAR)
    other_contract = make_contract(Market.FOREX, ContractFamily.LINEAR)
    specification = FuturesExposureSpecification(Market.CRYPTO, contract.symbol)

    with pytest.raises(ExposureValidationError):
        specification.quote_value(
            contract=other_contract,
            quantity=Decimal("1"),
            reference_price=Decimal("100"),
        )

    with pytest.raises(ExposureValidationError):
        specification.signed_base_exposure(
            contract=contract,
            quantity=Decimal("1"),
            price=Decimal("100"),
            position_side="LONG",
        )


def test_valuation_denomination_and_provenance_are_mandatory():
    contract = make_contract(Market.CRYPTO, ContractFamily.LINEAR)
    specification = FuturesExposureSpecification(Market.CRYPTO, contract.symbol)

    with pytest.raises(ExposureValidationError):
        specification.value(
            contract=contract,
            quantity=Decimal("1"),
            reference_price=Decimal("100"),
            denomination="QUOTE",
            valuation_source="synthetic",
            observed_at=datetime(2026, 1, 1, 12, tzinfo=UTC),
        )

    with pytest.raises(ExposureValidationError):
        specification.value(
            contract=contract,
            quantity=Decimal("1"),
            reference_price=Decimal("100"),
            denomination=ExposureDenomination.QUOTE,
            valuation_source="synthetic",
            observed_at=datetime(2026, 1, 1, 12),
        )


def test_specification_is_immutable():
    specification = FuturesExposureSpecification(
        Market.CRYPTO, make_symbol(Market.CRYPTO, ContractFamily.LINEAR)
    )
    with pytest.raises(AttributeError):
        specification.market = Market.GOLD
