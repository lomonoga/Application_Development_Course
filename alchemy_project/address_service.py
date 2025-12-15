from uuid import UUID
from typing import List, Optional
from address_repository import AddressRepository
from schemas import AddressCreate, AddressUpdate, AddressResponse
from litestar.exceptions import NotFoundException


class AddressService:
    def __init__(self, repository: AddressRepository):
        self.repository = repository

    async def get_by_id(self, address_id: UUID) -> AddressResponse:
        """Получить адрес по ID"""
        address = await self.repository.get_by_id(address_id, include_user=True)
        if not address:
            raise NotFoundException(detail=f"Address with ID {address_id} not found")
        return AddressResponse.model_validate(address)

    async def get_by_user_id(self, user_id: UUID) -> List[AddressResponse]:
        """Получить все адреса пользователя"""
        addresses = await self.repository.get_by_user_id(user_id, include_user=True)
        return [AddressResponse.model_validate(addr) for addr in addresses]

    async def get_by_filter(
            self,
            count: int = 10,
            page: int = 1,
            **kwargs
    ) -> List[AddressResponse]:
        """Получить адреса с фильтрацией"""
        addresses = await self.repository.get_by_filter(count=count, page=page, **kwargs)
        return [AddressResponse.model_validate(addr) for addr in addresses]

    async def get_total_count(self, **kwargs) -> int:
        """Получить общее количество адресов"""
        return await self.repository.get_total_count(**kwargs)

    async def create(self, address_data: AddressCreate) -> AddressResponse:
        """Создать новый адрес"""
        address = await self.repository.create(address_data)
        return AddressResponse.model_validate(address)

    async def update(self, address_id: UUID, address_data: AddressUpdate) -> AddressResponse:
        """Обновить адрес"""
        address = await self.repository.update(address_id, address_data)
        if not address:
            raise NotFoundException(detail=f"Address with ID {address_id} not found")
        return AddressResponse.model_validate(address)

    async def delete(self, address_id: UUID) -> None:
        """Удалить адрес"""
        success = await self.repository.delete(address_id)
        if not success:
            raise NotFoundException(detail=f"Address with ID {address_id} not found")
