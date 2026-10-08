from contracts.futures.funding import FundingRateUnit

def test_funding_rate_unit_is_explicit():
    assert FundingRateUnit.INTERVAL_RATE.value == "INTERVAL_RATE"
