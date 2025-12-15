import asyncio
import aio_pika
import json

import aiohttp


async def get_products_from_api():
    """Получение всех продуктов через API"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get('http://localhost:8001/products/get_all_products') as response:
                if response.status == 200:
                    data = await response.json()
                    products = data.get('products', [])

                    product_ids = [product['id'] for product in products]
                    print(f"Получено {len(product_ids)} продуктов из API: {product_ids}")
                    return product_ids
                else:
                    print(f"Ошибка: {response.status}")
                    return []
    except Exception as e:
        print(f"Ошибка подключения к API: {str(e)}")
        return []


async def send_messages():
    connection = await aio_pika.connect_robust(
        "amqp://guest:guest@localhost:5672/local"
    )

    async with connection:
        channel = await connection.channel()

        for i in range(5):
            message = {
                "action": "create",
                "data": {
                    "name": f"Product_{i + 1}",
                    "description": f"Description {i + 1}",
                    "price": 100.0 * (i + 1),
                    "category": ["electronics", "books", "clothing", "food", "tools"][i],
                    "in_stock": True
                }
            }

            await channel.default_exchange.publish(
                aio_pika.Message(body=json.dumps(message).encode()),
                routing_key="product"
            )
            print(f"Отправлен продукт {i + 1}")

        await asyncio.sleep(2)

        product_ids = await get_products_from_api()
        if not product_ids:
            raise Exception("Не удалось получить продукты из API")

        for i in range(min(3, len(product_ids))):
            order = {
                "action": "create",
                "data": {
                    "status": "pending",
                    "items": [
                        {
                            "product_id": product_ids[i],
                            "quantity": i + 1,
                            "unit_price": 100.0 * (i + 1)
                        }
                    ]
                }
            }

            await channel.default_exchange.publish(
                aio_pika.Message(body=json.dumps(order).encode()),
                routing_key="order"
            )
            print(f"Отправлен заказ {i + 1} с product_id: {product_ids[i]}")

    print("Все сообщения отправлены")


if __name__ == "__main__":
    asyncio.run(send_messages())
