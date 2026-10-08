from decimal import Decimal
from typing import cast

import pytest

from contracts.futures.contract_specification import (
    FuturesContractSpecification,
    QuantityUnit,
)
from contracts.futures.instrument import CanonicalFuturesSymbol, ContractFamily, Market
from contracts.futures.liquidation import (
    FuturesLiquidationSpecification,
    LiquidationDenomination,
    LiquidationValidationError,
)
from contracts.futures.position_side import PositionSide


def make_symbol(market: Market, family: ContractFamily) -> CanonicalFuturesSymbol:
    base = "BTC" if market is Market.CRYPTO else "XAU"
    return CanonicalFuturesSymbol(base, "USD", family, "USD")


def make_contract(market: Market, family: ContractFamily) -> FuturesContractSpecification:
    return FuturesContractSpecification(
        market=market,
        symbol=make_symbol(market, family),
        quantity_unit=QuantityUnit.CONTRACTS,
        contract_multiplier=Decimal("100"),
        price_quote_asset="USD",
    )


@pytest.mark.parametrize("market", list(Market))
@pytest.mark.parametrize("family", list(ContractFamily))
def test_scope_is_explicit_for_all_markets_and_families(market: Market, family: ContractFamily) -> None:
    specification = FuturesLiquidationSpecification(market, make_symbol(market, family))
    assert specification.market is market
    assert specification.symbol.contract_family is family


def test_linear_long_liquidation_price_uses_explicit_margin_and_maintenance():
    contract = make_contract(Market.CRYPTO, ContractFamily.LINEAR)
    specification = FuturesLiquidationSpecification(Market.CRYPTO, contract.symbol)

    price = specification.liquidation_price(
        contract=contract,
        quantity=Decimal("2"),
        entry_price=Decimal("50"),
        margin_amount=Decimal("900"),
        margin_denomination=LiquidationDenomination.QUOTE,
        maintenance_margin_ratio=Decimal("0.05"),
        position_side=PositionSide.LONG,
    )

    assert price == Decimal("9100") / Decimal("190")
    assert price < Decimal("50")


def test_linear_short_liquidation_price_uses_explicit_margin_and_maintenance():
    contract = make_contract(Market.CRYPTO, ContractFamily.LINEAR)
    specification = FuturesLiquidationSpecification(Market.CRYPTO, contract.symbol)

    price = specification.liquidation_price(
        contract=contract,
        quantity=Decimal("2"),
        entry_price=Decimal("50"),
        margin_amount=Decimal("900"),
        margin_denomination=LiquidationDenomination.QUOTE,
        maintenance_margin_ratio=Decimal("0.05"),
        position_side=PositionSide.SHORT,
    )

    assert price == Decimal("10900") / Decimal("210")
    assert price > Decimal("50")


def test_inverse_long_liquidation_price_preserves_inverse_base_denominated_semantics():
    contract = make_contract(Market.CRYPTO, ContractFamily.INVERSE)
    specification = FuturesLiquidationSpecification(Market.CRYPTO, contract.symbol)

    price = specification.liquidation_price(
        contract=contract,
        quantity=Decimal("2"),
        entry_price=Decimal("50"),
        margin_amount=Decimal("1"),
        margin_denomination=LiquidationDenomination.BASE,
        maintenance_margin_ratio=Decimal("0.05"),
        position_side=PositionSide.LONG,
    )

    assert price == Decimal("42")
    assert price < Decimal("50")


def test_inverse_short_liquidation_price_preserves_inverse_base_denominated_semantics():
    contract = make_contract(Market.CRYPTO, ContractFamily.INVERSE)
    specification = FuturesLiquidationSpecification(Market.CRYPTO, contract.symbol)

    price = specification.liquidation_price(
        contract=contract,
        quantity=Decimal("2"),
        entry_price=Decimal("50"),
        margin_amount=Decimal("1"),
        margin_denomination=LiquidationDenomination.BASE,
        maintenance_margin_ratio=Decimal("0.05"),
        position_side=PositionSide.SHORT,
    )

    assert price == Decimal("190") / Decimal("3")
    assert price > Decimal("50")


@pytest.mark.parametrize(
    ("family", "denomination"),
    [
        (ContractFamily.LINEAR, LiquidationDenomination.BASE),
        (ContractFamily.INVERSE, LiquidationDenomination.QUOTE),
    ],
)
def test_wrong_margin_denomination_fails_closed(family: ContractFamily, denomination: LiquidationDenomination) -> None:
    contract = make_contract(Market.CRYPTO, family)
    specification = FuturesLiquidationSpecification(Market.CRYPTO, contract.symbol)

    with pytest.raises(LiquidationValidationError):
        specification.liquidation_price(
            contract=contract,
            quantity=Decimal("2"),
            entry_price=Decimal("50"),
            margin_amount=Decimal("900"),
            margin_denomination=denomination,
            maintenance_margin_ratio=Decimal("0.05"),
            position_side=PositionSide.LONG,
        )


@pytest.mark.parametrize(
    "value",
    [True, False, 0, -1, 0.1, float("nan"), Decimal("NaN")],
)
def test_financial_inputs_fail_closed(value: object) -> None:
    contract = make_contract(Market.CRYPTO, ContractFamily.LINEAR)
    specification = FuturesLiquidationSpecification(Market.CRYPTO, contract.symbol)

    with pytest.raises(LiquidationValidationError):
        specification.liquidation_price(
            contract=contract,
            quantity=cast(Decimal, value),
            entry_price=Decimal("50"),
            margin_amount=Decimal("900"),
            margin_denomination=LiquidationDenomination.QUOTE,
            maintenance_margin_ratio=Decimal("0.05"),
            position_side=PositionSide.LONG,
        )


def test_maintenance_ratio_and_side_are_explicit_and_constrained():
    contract = make_contract(Market.CRYPTO, ContractFamily.LINEAR)
    specification = FuturesLiquidationSpecification(Market.CRYPTO, contract.symbol)

    with pytest.raises(LiquidationValidationError):
        specification.liquidation_price(
            contract=contract,
            quantity=Decimal("2"),
            entry_price=Decimal("50"),
            margin_amount=Decimal("900"),
            margin_denomination=LiquidationDenomination.QUOTE,
            maintenance_margin_ratio=Decimal("1"),
            position_side=PositionSide.LONG,
        )

    with pytest.raises(LiquidationValidationError):
        specification.liquidation_price(
            contract=contract,
            quantity=Decimal("2"),
            entry_price=Decimal("50"),
            margin_amount=Decimal("900"),
            margin_denomination=LiquidationDenomination.QUOTE,
            maintenance_margin_ratio=Decimal("0.05"),
            position_side=cast(PositionSide, "LONG"),
        )


def test_liquidation_price_rejects_nonphysical_direction_and_identity_mismatch():
    contract = make_contract(Market.CRYPTO, ContractFamily.LINEAR)
    specification = FuturesLiquidationSpecification(Market.CRYPTO, contract.symbol)

    with pytest.raises(LiquidationValidationError):
        specification.liquidation_price(
            contract=contract,
            quantity=Decimal("2"),
            entry_price=Decimal("50"),
            margin_amount=Decimal("10000"),
            margin_denomination=LiquidationDenomination.QUOTE,
            maintenance_margin_ratio=Decimal("0.05"),
            position_side=PositionSide.LONG,
        )

    other_contract = make_contract(Market.FOREX, ContractFamily.LINEAR)
    with pytest.raises(LiquidationValidationError):
        specification.liquidation_price(
            contract=other_contract,
            quantity=Decimal("2"),
            entry_price=Decimal("50"),
            margin_amount=Decimal("900"),
            margin_denomination=LiquidationDenomination.QUOTE,
            maintenance_margin_ratio=Decimal("0.05"),
            position_side=PositionSide.LONG,
        )
