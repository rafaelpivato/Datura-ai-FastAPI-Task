from unittest.mock import AsyncMock

import pytest
from bittensor.core.subtensor import ScaleObj
from bittensor.utils.balance import Balance

from app.taodiv import TaoDividendQuerier


@pytest.fixture
async def querier():
    querier = TaoDividendQuerier()
    querier._connection = AsyncMock()
    try:
        yield querier
    finally:
        await querier.close()


async def test_get_tao_dividends_success(querier):
    # Mock the query response
    mock_result = ScaleObj(1000000000)
    querier._connection.query_module = AsyncMock(return_value=mock_result)

    result = await querier.get_tao_dividends_per_subnet(netuid=1, hotkey="test_hotkey")

    # Verify the result is a Balance object with correct value
    assert isinstance(result, Balance)
    assert str(result) == "τ1.000000000"

    # Verif query was called with correct parameters
    querier.subtensor.query_module.assert_called_once_with(
        "SubtensorModule",
        "TaoDividendsPerSubnet",
        params=[1, "test_hotkey"],
    )


async def test_get_tao_dividends_no_result(querier):
    querier._connection.query_module = AsyncMock(return_value=None)
    result = await querier.get_tao_dividends_per_subnet(netuid=1, hotkey="test_hotkey")
    querier.subtensor.query_module.assert_called_once()
    assert result is None


async def test_get_tao_dividends_error(querier):
    querier._connection.query_module = AsyncMock(side_effect=Exception("Test error"))
    with pytest.raises(Exception, match="Error querying TaoDividendsPerSubnet"):
        await querier.get_tao_dividends_per_subnet(netuid=1, hotkey="test_hotkey")
    querier.subtensor.query_module.assert_called_once()


async def test_close_connection(querier):
    close_mock = AsyncMock()
    querier._connection = AsyncMock(close=close_mock)
    await querier.close()
    close_mock.assert_called_once()
    assert querier._connection is None
