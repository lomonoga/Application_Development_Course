import pytest
from unittest.mock import Mock, AsyncMock, patch
from uuid import uuid4
from datetime import datetime

from litestar.exceptions import NotFoundException

from product_service import ProductService
from schemas import ProductUpdate, ProductCreate


class TestProductService:
    @pytest.mark.asyncio
    async def test_get_by_id(self):
        mock_repo = AsyncMock()
        product_data = {
            "id": uuid4(),
            "name": "Test Product",
            "description": "Test description",
            "price": 100.0,
            "category": "Electronics",
            "in_stock": True,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        mock_product = Mock(**product_data)
        mock_repo.get_by_id.return_value = mock_product

        with patch('schemas.ProductResponse.model_validate') as mock_validate:
            mock_response = Mock()
            for key, value in product_data.items():
                setattr(mock_response, key, value)
            mock_validate.return_value = mock_response

            service = ProductService(repository=mock_repo)
            result = await service.get_by_id(product_data["id"])

            assert result.id == product_data["id"]
            mock_repo.get_by_id.assert_called_once_with(product_data["id"])

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self):
        mock_repo = AsyncMock()
        mock_repo.get_by_id.return_value = None

        service = ProductService(repository=mock_repo)

        with pytest.raises(NotFoundException):
            await service.get_by_id(uuid4())

    @pytest.mark.asyncio
    async def test_get_by_filter(self):
        mock_repo = AsyncMock()
        products_data = [
            {
                "id": uuid4(),
                "name": "Product 1",
                "price": 50.0,
                "category": "Books",
                "in_stock": True
            },
            {
                "id": uuid4(),
                "name": "Product 2",
                "price": 75.0,
                "category": "Books",
                "in_stock": False
            }
        ]
        mock_products = [Mock(**data) for data in products_data]
        mock_repo.get_by_filter.return_value = mock_products

        with patch('schemas.ProductResponse.model_validate') as mock_validate:
            mock_responses = []
            for data in products_data:
                mock_response = Mock()
                for key, value in data.items():
                    setattr(mock_response, key, value)
                mock_responses.append(mock_response)

            mock_validate.side_effect = mock_responses

            service = ProductService(repository=mock_repo)
            result = await service.get_by_filter(category="Books")

            assert len(result) == 2
            mock_repo.get_by_filter.assert_called_once_with(count=10, page=1, category="Books")

    @pytest.mark.asyncio
    async def test_get_total_count(self):
        mock_repo = AsyncMock()
        mock_repo.get_total_count.return_value = 25

        service = ProductService(repository=mock_repo)
        result = await service.get_total_count(category="Clothing")

        assert result == 25
        mock_repo.get_total_count.assert_called_once_with(category="Clothing")

    @pytest.mark.asyncio
    async def test_create(self):
        mock_repo = AsyncMock()
        product_data_dict = {
            "id": uuid4(),
            "name": "New Product",
            "price": 200.0,
            "category": "Home",
            "in_stock": True
        }
        mock_product = Mock(**product_data_dict)
        mock_repo.create.return_value = mock_product

        with patch('schemas.ProductResponse.model_validate') as mock_validate:
            mock_response = Mock()
            for key, value in product_data_dict.items():
                setattr(mock_response, key, value)
            mock_validate.return_value = mock_response

            service = ProductService(repository=mock_repo)
            product_data = ProductCreate(
                name="New Product",
                price=200.0,
                category="Home"
            )
            result = await service.create(product_data)

            assert result.name == "New Product"
            mock_repo.create.assert_called_once_with(product_data)

    @pytest.mark.asyncio
    async def test_update(self):
        mock_repo = AsyncMock()
        product_id = uuid4()
        product_data_dict = {
            "id": product_id,
            "name": "Updated Product",
            "price": 150.0,
            "category": "Updated",
            "in_stock": False
        }
        mock_product = Mock(**product_data_dict)
        mock_repo.update.return_value = mock_product

        with patch('schemas.ProductResponse.model_validate') as mock_validate:
            mock_response = Mock()
            for key, value in product_data_dict.items():
                setattr(mock_response, key, value)
            mock_validate.return_value = mock_response

            service = ProductService(repository=mock_repo)
            product_data = ProductUpdate(price=150.0)
            result = await service.update(product_id, product_data)

            assert result.price == 150.0
            mock_repo.update.assert_called_once_with(product_id, product_data)

    @pytest.mark.asyncio
    async def test_update_not_found(self):
        mock_repo = AsyncMock()
        mock_repo.update.return_value = None

        service = ProductService(repository=mock_repo)

        with pytest.raises(NotFoundException):
            await service.update(uuid4(), ProductUpdate(name="Test"))

    @pytest.mark.asyncio
    async def test_delete(self):
        mock_repo = AsyncMock()
        mock_repo.delete.return_value = True

        service = ProductService(repository=mock_repo)
        product_id = uuid4()
        await service.delete(product_id)

        mock_repo.delete.assert_called_once_with(product_id)

    @pytest.mark.asyncio
    async def test_delete_not_found(self):
        mock_repo = AsyncMock()
        mock_repo.delete.return_value = False

        service = ProductService(repository=mock_repo)

        with pytest.raises(NotFoundException):
            await service.delete(uuid4())
