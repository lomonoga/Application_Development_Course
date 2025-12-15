import pytest
from faststream import FastStream
from faststream.rabbit import RabbitBroker
import asyncio

broker = RabbitBroker("amqp://guest:guest@localhost:5672/local")
app = FastStream(broker)

@broker.subscriber("order")
async def handle(msg):
    print(msg)

@pytest.mark.asyncio
@app.after_startup
async def test_publish():
    async with broker:
        await broker.publish("message", "order")

async def main():
    await app.run()

if __name__ == "__main__":
    asyncio.run(main())