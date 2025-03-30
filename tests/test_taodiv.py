from unittest.mock import AsyncMock

import pytest
from bittensor.utils.balance import Balance

from app.taodiv import TaoDividendQuerier


@pytest.fixture
async def querier():
    querier = TaoDividendQuerier()
    querier.subtensor = AsyncMock()
    try:
        yield querier
    finally:
        await querier.close()


@pytest.mark.asyncio
async def test_get_tao_dividends_success(querier):
    # Mock the query_map response
    mock_result = "1000000000"
    querier.subtensor.query_map = AsyncMock(return_value=mock_result)

    result = await querier.get_tao_dividends_per_subnet(netuid=1, hotkey="test_hotkey")

    # Verify the result is a Balance object with correct value
    assert isinstance(result, Balance)
    assert str(result) == "1.0"

    # Verify query_map was called with correct parameters
    querier.subtensor.query_map.assert_called_once_with(
        "SubtensorModule", "TaoDividendsPerSubnet", 1, "test_hotkey"
    )


@pytest.mark.asyncio
async def test_get_tao_dividends_no_result(querier):
    # Mock query_map to return None
    querier.subtensor.query_map = AsyncMock(return_value=None)

    result = await querier.get_tao_dividends_per_subnet(netuid=1, hotkey="test_hotkey")

    assert result is None


@pytest.mark.asyncio
async def test_get_tao_dividends_error(querier):
    # Mock query_map to raise an exception
    querier.subtensor.query_map = AsyncMock(side_effect=Exception("Test error"))

    result = await querier.get_tao_dividends_per_subnet(netuid=1, hotkey="test_hotkey")

    assert result is None


@pytest.mark.asyncio
async def test_close_connection(querier):
    # Mock the close method
    querier.subtensor.close = AsyncMock()

    await querier.close()

    # Verify close was called
    querier.subtensor.close.assert_called_once()
