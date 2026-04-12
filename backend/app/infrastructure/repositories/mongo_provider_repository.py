from typing import List, Optional

from app.domain.models.provider import Provider
from app.domain.repositories.provider_repository import ProviderRepository
from app.infrastructure.models.documents import ProviderDocument


class MongoProviderRepository(ProviderRepository):
    async def save(self, provider: Provider) -> None:
        document = await ProviderDocument.find_one(ProviderDocument.provider_id == provider.id)
        if not document:
            document = ProviderDocument.from_domain(provider)
            await document.save()
            return
        document.update_from_domain(provider)
        await document.save()

    async def find_by_id(self, provider_id: str) -> Optional[Provider]:
        document = await ProviderDocument.find_one(ProviderDocument.provider_id == provider_id)
        return document.to_domain() if document else None

    async def find_by_id_and_user_id(self, provider_id: str, user_id: str) -> Optional[Provider]:
        document = await ProviderDocument.find_one(
            ProviderDocument.provider_id == provider_id,
            ProviderDocument.user_id == user_id,
        )
        return document.to_domain() if document else None

    async def find_by_user_id(self, user_id: str) -> List[Provider]:
        documents = await ProviderDocument.find(ProviderDocument.user_id == user_id).to_list()
        return [document.to_domain() for document in documents]

    async def delete(self, provider_id: str) -> None:
        document = await ProviderDocument.find_one(ProviderDocument.provider_id == provider_id)
        if document:
            await document.delete()
