import aio_pika
import os

RABBITMQ_SETTINGS = {
    "host": os.getenv("RABBITMQ_HOST"),
    "port": int(os.getenv("RABBITMQ_PORT")),
    "login": os.getenv("RABBITMQ_USER"),
    "password": os.getenv("RABBITMQ_PASS"),
}
EXCHANGE_NAME = os.getenv("EXCHANGE_NAME")
QUEUE_NAME = os.getenv("QUEUE_NAME")

async def get_connection():
    return await aio_pika.connect_robust(**RABBITMQ_SETTINGS)

async def get_channel():
    connection = await get_connection()
    channel = await connection.channel()
    await channel.set_qos(prefetch_count=10)
    return channel

async def setup_rabbitmq(channel):
    # Объявляем Exchange (fanout)
    exchange = await channel.declare_exchange(
        EXCHANGE_NAME,
        aio_pika.ExchangeType.FANOUT,
        durable=True
    )

    # Объявляем очередь
    queue = await channel.declare_queue(
        QUEUE_NAME,
        durable=True
    )
    # Привязываем очередь к exchange по имени
    await queue.bind(exchange.name)
    return queue
