from typing import List, Optional, Protocol

from app.domain.models.provider import Provider


class ProviderRepository(Protocol):
    async def save(self, provider: Provider) -> None:
        ...

    async def find_by_id(self, provider_id: str) -> Optional[Provider]:
        ...

    async def find_by_id_and_user_id(self, provider_id: str, user_id: str) -> Optional[Provider]:
        ...

    async def find_by_user_id(self, user_id: str) -> List[Provider]:
        ...

    async def delete(self, provider_id: str) -> None:
        ...
