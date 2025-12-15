from uuid import UUID

from schemas import UserCreate, UserUpdate
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from tables import User


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, user_id: UUID) -> User | None:
        result = await self.session.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_filter(
        self, count: int = 10, page: int = 1, **kwargs
    ) -> list[User]:
        offset = (page - 1) * count
        query = select(User)

        if kwargs:
            for key, value in kwargs.items():
                if hasattr(User, key):
                    query = query.where(getattr(User, key) == value)

        query = query.offset(offset).limit(count)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_total_count(self, **kwargs) -> int:
        query = select(User)

        if kwargs:
            for key, value in kwargs.items():
                if hasattr(User, key):
                    query = query.where(getattr(User, key) == value)

        result = await self.session.execute(select(User.id))
        return len(result.scalars().all())

    async def create(self, user_data: UserCreate) -> User:
        user = User(
            username=user_data.username,
            email=user_data.email,
            description=user_data.description,
        )
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def update(self, user_id: UUID, user_data: UserUpdate) -> User:
        user = await self.get_by_id(user_id)
        if not user:
            return None

        update_data = user_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)

        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def delete(self, user_id: UUID) -> bool:
        user = await self.get_by_id(user_id)
        if not user:
            return False

        await self.session.delete(user)
        await self.session.commit()
        return True
