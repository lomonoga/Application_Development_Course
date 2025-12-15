from typing import List, Optional
from uuid import UUID

from schemas import AddressCreate, AddressUpdate
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from tables import Address


class AddressRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(
        self, address_id: UUID, include_user: bool = False
    ) -> Optional[Address]:
        query = select(Address)
        if include_user:
            query = query.options(joinedload(Address.user))
        query = query.where(Address.id == address_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_user_id(
        self, user_id: UUID, include_user: bool = False
    ) -> List[Address]:
        query = select(Address).where(Address.user_id == user_id)
        if include_user:
            query = query.options(joinedload(Address.user))
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_by_filter(
        self, count: int = 10, page: int = 1, **kwargs
    ) -> List[Address]:
        offset = (page - 1) * count
        query = select(Address)

        if kwargs:
            for key, value in kwargs.items():
                if hasattr(Address, key):
                    query = query.where(getattr(Address, key) == value)

        query = query.offset(offset).limit(count)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_total_count(self, **kwargs) -> int:
        query = select(Address)

        if kwargs:
            for key, value in kwargs.items():
                if hasattr(Address, key):
                    query = query.where(getattr(Address, key) == value)

        result = await self.session.execute(query)
        return len(result.scalars().all())

    async def create(self, address_data: AddressCreate) -> Address:
        address = Address(
            user_id=address_data.user_id,
            street=address_data.street,
            city=address_data.city,
            state=address_data.state,
            zip_code=address_data.zip_code,
            country=address_data.country,
            is_primary=address_data.is_primary,
        )

        # Если это основной адрес, снимаем флаг is_primary у других адресов пользователя
        if address_data.is_primary:
            await self._unset_primary_for_user(address_data.user_id)

        self.session.add(address)
        await self.session.commit()
        await self.session.refresh(address)
        return address

    async def update(
        self, address_id: UUID, address_data: AddressUpdate
    ) -> Optional[Address]:
        address = await self.get_by_id(address_id)
        if not address:
            return None

        update_data = address_data.model_dump(exclude_unset=True)

        # Если устанавливаем is_primary=True, снимаем флаг у других адресов пользователя
        if update_data.get("is_primary", False):
            await self._unset_primary_for_user(address.user_id)

        for field, value in update_data.items():
            setattr(address, field, value)

        await self.session.commit()
        await self.session.refresh(address)
        return address

    async def delete(self, address_id: UUID) -> bool:
        address = await self.get_by_id(address_id)
        if not address:
            return False

        await self.session.delete(address)
        await self.session.commit()
        return True

    async def _unset_primary_for_user(self, user_id: UUID) -> None:
        """Снимает флаг is_primary у всех адресов пользователя"""
        result = await self.session.execute(
            select(Address).where(
                (Address.user_id == user_id) & (Address.is_primary == True)
            )
        )
        addresses = result.scalars().all()

        for addr in addresses:
            addr.is_primary = False

        if addresses:
            await self.session.commit()
