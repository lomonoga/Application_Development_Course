import pytest
from unittest.mock import Mock
from uuid import UUID
from polyfactory.factories.pydantic_factory import ModelFactory
from litestar.status_codes import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT
from litestar.di import Provide
from litestar.testing import create_test_client

from product_controller import ProductController
from product_service import ProductService
from schemas import ProductCreate, ProductUpdate, ProductResponse


class ProductCreateFactory(ModelFactory[ProductCreate]):
    __model__ = ProductCreate


class ProductUpdateFactory(ModelFactory[ProductUpdate]):
    __model__ = ProductUpdate


class ProductResponseFactory(ModelFactory[ProductResponse]):
    __model__ = ProductResponse


@pytest.fixture()
def product_create():
    return ProductCreateFactory.build()


@pytest.fixture()
def product_update():
    return ProductUpdateFactory.build()


@pytest.fixture()
def product_response():
    return ProductResponseFactory.build()


class MockProductService(ProductService):
    def __init__(self):
        super().__init__(repository=Mock())

        self._mock_get_by_id = Mock()
        self._mock_get_by_filter = Mock()
        self._mock_get_total_count = Mock()
        self._mock_create = Mock()
        self._mock_update = Mock()
        self._mock_delete = Mock()

    async def get_by_id(self, product_id: UUID):
        result = self._mock_get_by_id(product_id)
        return result

    async def get_by_filter(self, count: int = 10, page: int = 1, **kwargs):
        result = self._mock_get_by_filter(count, page, **kwargs)
        return result

    async def get_total_count(self, **kwargs):
        return self._mock_get_total_count(**kwargs)

    async def create(self, product_data: ProductCreate):
        return self._mock_create(product_data)

    async def update(self, product_id: UUID, product_data: ProductUpdate):
        return self._mock_update(product_id, product_data)

    async def delete(self, product_id: UUID):
        return self._mock_delete(product_id)


@pytest.mark.asyncio
async def test_get_product_by_id(product_response: ProductResponse):
    mock_service = MockProductService()

    mock_service._mock_get_by_id.return_value = product_response

    with create_test_client(
            route_handlers=[ProductController],
            dependencies={"product_service": Provide(lambda: mock_service, sync_to_thread=False)}
    ) as client:
        response = client.get(f"/products/get_product/{product_response.id}")
        assert response.status_code == HTTP_200_OK
        assert response.json()["id"] == str(product_response.id)


@pytest.mark.asyncio
async def test_get_product_by_id_not_found():
    from uuid import uuid4

    mock_service = MockProductService()

    from litestar.exceptions import NotFoundException
    mock_service._mock_get_by_id.side_effect = NotFoundException(detail="Product not found")

    with create_test_client(
            route_handlers=[ProductController],
            dependencies={"product_service": Provide(lambda: mock_service, sync_to_thread=False)}
    ) as client:
        response = client.get(f"/products/get_product/{uuid4()}")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_get_all_products(product_response: ProductResponse):
    mock_service = MockProductService()

    mock_service._mock_get_by_filter.return_value = [product_response]
    mock_service._mock_get_total_count.return_value = 1

    with create_test_client(
            route_handlers=[ProductController],
            dependencies={"product_service": Provide(lambda: mock_service, sync_to_thread=False)}
    ) as client:
        response = client.get("/products/get_all_products?count=10&page=1")
        assert response.status_code == HTTP_200_OK
        data = response.json()
        assert data["total_count"] == 1
        assert len(data["products"]) == 1
        assert data["products"][0]["id"] == str(product_response.id)
        assert data["page"] == 1
        assert data["count"] == 10


@pytest.mark.asyncio
async def test_get_all_products_with_filters(product_response: ProductResponse):
    mock_service = MockProductService()

    mock_service._mock_get_by_filter.return_value = [product_response]
    mock_service._mock_get_total_count.return_value = 1

    with create_test_client(
            route_handlers=[ProductController],
            dependencies={"product_service": Provide(lambda: mock_service, sync_to_thread=False)}
    ) as client:
        response = client.get(
            "/products/get_all_products?"
            "count=5&page=2&"
            f"category={product_response.category}&"
            "in_stock=true&"
            "price_min=10&"
            "price_max=100"
        )
        assert response.status_code == HTTP_200_OK
        data = response.json()
        assert data["filters"]["category"] == product_response.category
        assert data["filters"]["in_stock"] is True
        assert data["filters"]["price_min"] == 10.0
        assert data["filters"]["price_max"] == 100.0


@pytest.mark.asyncio
async def test_create_product(product_create: ProductCreate, product_response: ProductResponse):
    mock_service = MockProductService()

    mock_service._mock_create.return_value = product_response

    with create_test_client(
            route_handlers=[ProductController],
            dependencies={"product_service": Provide(lambda: mock_service, sync_to_thread=False)}
    ) as client:
        response = client.post("/products/create_product", json=product_create.model_dump())
        assert response.status_code == HTTP_201_CREATED
        assert response.json()["name"] == product_response.name


@pytest.mark.asyncio
async def test_update_product(product_response: ProductResponse, product_update: ProductUpdate):
    mock_service = MockProductService()

    mock_service._mock_update.return_value = product_response

    with create_test_client(
            route_handlers=[ProductController],
            dependencies={"product_service": Provide(lambda: mock_service, sync_to_thread=False)}
    ) as client:
        response = client.put(
            f"/products/update_product/{product_response.id}",
            json=product_update.model_dump()
        )
        assert response.status_code == HTTP_200_OK
        assert response.json()["id"] == str(product_response.id)


@pytest.mark.asyncio
async def test_update_product_not_found(product_update: ProductUpdate):
    from uuid import uuid4

    mock_service = MockProductService()

    from litestar.exceptions import NotFoundException
    mock_service._mock_update.side_effect = NotFoundException(detail="Product not found")

    with create_test_client(
            route_handlers=[ProductController],
            dependencies={"product_service": Provide(lambda: mock_service, sync_to_thread=False)}
    ) as client:
        response = client.put(f"/products/update_product/{uuid4()}", json=product_update.model_dump())
        assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_product(product_response: ProductResponse):
    mock_service = MockProductService()

    from litestar.exceptions import NotFoundException

    def delete_side_effect(product_id):
        if str(product_id) == str(product_response.id):
            return None
        raise NotFoundException(detail="Product not found")

    mock_service._mock_delete.side_effect = delete_side_effect

    with create_test_client(
            route_handlers=[ProductController],
            dependencies={"product_service": Provide(lambda: mock_service, sync_to_thread=False)}
    ) as client:
        response = client.delete(f"/products/delete_product/{product_response.id}")
        assert response.status_code == HTTP_204_NO_CONTENT


@pytest.mark.asyncio
async def test_delete_product_not_found():
    from uuid import uuid4

    mock_service = MockProductService()

    from litestar.exceptions import NotFoundException
    mock_service._mock_delete.side_effect = NotFoundException(detail="Product not found")

    with create_test_client(
            route_handlers=[ProductController],
            dependencies={"product_service": Provide(lambda: mock_service, sync_to_thread=False)}
    ) as client:
        response = client.delete(f"/products/delete_product/{uuid4()}")
        assert response.status_code == 404
