# main.py
import asyncio
from consumers.ca_entities_consumer import handle_message
from rabbitmq_connection import get_channel, setup_rabbitmq
from utils.logger import setup_logger
import os

logger = setup_logger("main")
QUEUE_NAME = os.getenv("QUEUE_NAME")

async def main():
    channel = await get_channel()
    queue = await setup_rabbitmq(channel)

    logger.info(f" [*] Waiting for messages in queue '{QUEUE_NAME}'")
    await queue.consume(handle_message)

    try:
        await asyncio.Event().wait()
    except KeyboardInterrupt:
        logger.info(" [x] Shutdown requested")

if __name__ == "__main__":
    asyncio.run(main())
