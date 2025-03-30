from typing import Optional

from bittensor import AsyncSubtensor
from bittensor.utils.balance import Balance


class TaoDividendQuerier:
    def __init__(self):
        self._connection = None

    async def _ensure_connection(self):
        if self._connection is None:
            self._connection = AsyncSubtensor()
        return self._connection

    async def get_tao_dividends_per_subnet(
        self, netuid: int, hotkey: str
    ) -> Optional[Balance]:
        try:
            self.subtensor = await self._ensure_connection()
            result = await self.subtensor.query_map(
                "SubtensorModule", "TaoDividendsPerSubnet", netuid, hotkey
            )
            if result:
                return Balance.from_rao(int(str(result)))
            return None
        except Exception as e:
            print(f"Error querying TaoDividendsPerSubnet: {str(e)}")
            return None

    async def close(self):
        if self._connection:
            await self._connection.close()
            self._connection = None


async def main():
    querier = TaoDividendQuerier()
    try:
        # Example using testnet with netuid 1 and a test hotkey
        test_hotkey = "5FFApaS75bv5pJHfAp2FVLBj9ZaXuFDjEypsaBNc1wCfe52v"
        result = await querier.get_tao_dividends_per_subnet(
            netuid=18, hotkey=test_hotkey
        )
        print(f"TAO dividends for hotkey {test_hotkey}: {result}")
    finally:
        await querier.close()


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
