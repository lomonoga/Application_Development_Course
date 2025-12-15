from litestar import Controller, get, post, put, delete
from litestar.params import Parameter, Body
from uuid import UUID

from address_service import AddressService
from schemas import AddressCreate, AddressUpdate, AddressResponse


class AddressController(Controller):
    path = "/addresses"
    tags = ["Address Management"]

    @get("/get_address/{address_id:uuid}")
    async def get_address_by_id(
            self,
            address_service: AddressService,
            address_id: UUID
    ) -> AddressResponse:
        """Get address by ID"""
        return await address_service.get_by_id(address_id)

    @get("/get_user_addresses/{user_id:uuid}")
    async def get_addresses_by_user_id(
            self,
            address_service: AddressService,
            user_id: UUID
    ) -> list[AddressResponse]:
        """Get all addresses for a specific user"""
        return await address_service.get_by_user_id(user_id)

    @get("/get_all_addresses")
    async def get_all_addresses(
            self,
            address_service: AddressService,
            count: int = Parameter(gt=0, le=100, default=10),
            page: int = Parameter(gt=0, default=1),
            user_id: UUID | None = Parameter(default=None),
            city: str | None = Parameter(default=None),
            country: str | None = Parameter(default=None),
            is_primary: bool | None = Parameter(default=None)
    ) -> dict:
        """Get all addresses with pagination and filtering"""
        filters = {}
        if user_id:
            filters['user_id'] = user_id
        if city:
            filters['city'] = city
        if country:
            filters['country'] = country
        if is_primary is not None:
            filters['is_primary'] = is_primary

        addresses = await address_service.get_by_filter(
            count=count,
            page=page,
            **filters
        )
        total_count = await address_service.get_total_count(**filters)

        return {
            "addresses": addresses,
            "total_count": total_count,
            "page": page,
            "count": count
        }

    @post("/create_address")
    async def create_address(
            self,
            address_service: AddressService,
            data: AddressCreate = Body(media_type="application/json")
    ) -> AddressResponse:
        """Create a new address"""
        return await address_service.create(data)

    @put("/update_address/{address_id:uuid}")
    async def update_address(
            self,
            address_service: AddressService,
            address_id: UUID,
            data: AddressUpdate = Body(media_type="application/json")
    ) -> AddressResponse:
        """Update address"""
        return await address_service.update(address_id, data)

    @delete("/delete_address/{address_id:uuid}")
    async def delete_address(
            self,
            address_service: AddressService,
            address_id: UUID
    ) -> None:
        """Delete address"""
        await address_service.delete(address_id)
