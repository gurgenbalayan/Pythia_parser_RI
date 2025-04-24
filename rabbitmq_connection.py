import aio_pika
import os
from dotenv import load_dotenv

load_dotenv()

RABBITMQ_URL = os.getenv("RABBITMQ_URL")

async def get_connection():
    return await aio_pika.connect_robust(RABBITMQ_URL)

async def get_channel():
    connection = await get_connection()
    channel = await connection.channel()
    await channel.set_qos(prefetch_count=10)
    return channel
