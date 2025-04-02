from typing import Optional

from bittensor import AsyncSubtensor
from bittensor.core.subtensor import ScaleObj
from bittensor.utils.balance import Balance


class TaoDividendQuerier:
    def __init__(self):
        self._connection = None

    async def _ensure_connection(self):
        if self._connection is None:
            self._connection = AsyncSubtensor(network="test")
        return self._connection

    async def get_tao_dividends_per_subnet(
        self, netuid: int, hotkey: str
    ) -> Optional[Balance]:
        try:
            self.subtensor = await self._ensure_connection()
            result = await self.subtensor.query_module(
                "SubtensorModule",
                "TaoDividendsPerSubnet",
                params=[netuid, hotkey],
            )
            if (
                result is not None
                and isinstance(result, ScaleObj)
                and isinstance(result.value, int)
            ):
                return Balance.from_rao(result.value)
            return None
        except Exception as error:
            raise Exception("Error querying TaoDividendsPerSubnet") from error

    async def close(self):
        if self._connection:
            await self._connection.close()
            self._connection = None


async def main():
    querier = TaoDividendQuerier()
    try:
        test_hotkey = "5GpzQgpiAKHMWNSH3RN4GLf96GVTDct9QxYEFAY7LWcVzTbx"
        result = await querier.get_tao_dividends_per_subnet(
            netuid=4,
            hotkey=test_hotkey,
        )
        print(f"TAO dividends for hotkey {test_hotkey}: {result}")
    finally:
        await querier.close()


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
