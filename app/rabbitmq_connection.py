import aio_pika
import os

RABBITMQ_SETTINGS = {
    "host": os.getenv("RABBITMQ_HOST", "rabbitmq"),
    "port": int(os.getenv("RABBITMQ_PORT", 5672)),
    "login": os.getenv("RABBITMQ_USER", "guest"),
    "password": os.getenv("RABBITMQ_PASS", "guest"),
}
async def get_connection():
    return await aio_pika.connect_robust(**RABBITMQ_SETTINGS)

async def get_channel():
    connection = await get_connection()
    channel = await connection.channel()
    await channel.set_qos(prefetch_count=10)
    return channel
