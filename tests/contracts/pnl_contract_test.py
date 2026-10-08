from datetime import datetime,timedelta,timezone
from decimal import Decimal
import pytest
from contracts.futures.pnl import FuturesPnLSpecification,PnLDenomination,PnLUnit,PnLValidationError
from contracts.futures.instrument import CanonicalFuturesSymbol,ContractFamily,Market
from contracts.futures.position_side import PositionSide
UTC=timezone.utc
def spec(family: ContractFamily) -> FuturesPnLSpecification: return FuturesPnLSpecification(Market.CRYPTO,CanonicalFuturesSymbol("BTC","USD",family,"USD"),PnLUnit.REALIZED_OR_UNREALIZED)
@pytest.mark.parametrize("family,denom",[(ContractFamily.LINEAR,PnLDenomination.QUOTE),(ContractFamily.INVERSE,PnLDenomination.BASE)])
@pytest.mark.parametrize("market",list(Market))
def test_scope(family: ContractFamily, denom: PnLDenomination, market: Market) -> None:
    base="BTC" if market is Market.CRYPTO else "XAU"
    s=FuturesPnLSpecification(market,CanonicalFuturesSymbol(base,"USD",family,"USD"),PnLUnit.REALIZED_OR_UNREALIZED)
    assert s.denomination is denom
def test_linear_long_short():
    s=spec(ContractFamily.LINEAR)
    assert s.calculate_realized(quantity=Decimal("10"),multiplier=Decimal("0.001"),entry_price=Decimal("100"),exit_price=Decimal("120"),position_side=PositionSide.LONG)==Decimal("0.2")
    assert s.calculate_realized(quantity=Decimal("10"),multiplier=Decimal("0.001"),entry_price=Decimal("100"),exit_price=Decimal("120"),position_side=PositionSide.SHORT)==Decimal("-0.2")
def test_inverse_long_short():
    s=spec(ContractFamily.INVERSE)
    assert s.calculate_realized(quantity=Decimal("10"),multiplier=Decimal("100"),entry_price=Decimal("100"),exit_price=Decimal("200"),position_side=PositionSide.LONG)==Decimal("5")
    assert s.calculate_realized(quantity=Decimal("10"),multiplier=Decimal("100"),entry_price=Decimal("100"),exit_price=Decimal("200"),position_side=PositionSide.SHORT)==Decimal("-5")
def test_unrealized_exact():
    assert spec(ContractFamily.LINEAR).calculate_unrealized(quantity=Decimal("3"),multiplier=Decimal("0.1"),entry_price=Decimal("100.00"),valuation_price=Decimal("100.123456789"),position_side=PositionSide.LONG,valuation_source="synthetic",observed_at=datetime(2026,1,1,12,tzinfo=UTC))==Decimal("0.0370370367")
def test_zero_pnl():
    assert spec(ContractFamily.LINEAR).calculate_unrealized(quantity=Decimal("1"),multiplier=Decimal("1"),entry_price=Decimal("100"),valuation_price=Decimal("100"),position_side=PositionSide.LONG,valuation_source="synthetic",observed_at=datetime(2026,1,1,12,tzinfo=UTC))==Decimal("0")
@pytest.mark.parametrize("v",[True,False,0,-1,0.1,float("nan"),Decimal("NaN")])
def test_invalid(v: object) -> None:
    with pytest.raises(PnLValidationError): spec(ContractFamily.LINEAR).calculate_realized(quantity=v,multiplier=Decimal("1"),entry_price=Decimal("100"),exit_price=Decimal("101"),position_side=PositionSide.LONG)
def test_utc_source_and_freshness():
    with pytest.raises(PnLValidationError): spec(ContractFamily.LINEAR).calculate_unrealized(quantity=Decimal("1"),multiplier=Decimal("1"),entry_price=Decimal("100"),valuation_price=Decimal("101"),position_side=PositionSide.LONG,valuation_source="",observed_at=datetime(2026,1,1,12))
    s=spec(ContractFamily.LINEAR); s.validate_valuation_freshness(as_of=datetime(2026,1,1,12,30,tzinfo=UTC),observed_at=datetime(2026,1,1,12,tzinfo=UTC),max_age=timedelta(hours=1))
    with pytest.raises(PnLValidationError): s.validate_valuation_freshness(as_of=datetime(2026,1,1,14,tzinfo=UTC),observed_at=datetime(2026,1,1,12,tzinfo=UTC),max_age=timedelta(hours=1))
def test_immutable():
    s=spec(ContractFamily.LINEAR)
    with pytest.raises(AttributeError): s.pnl_unit=PnLUnit.REALIZED_OR_UNREALIZED
