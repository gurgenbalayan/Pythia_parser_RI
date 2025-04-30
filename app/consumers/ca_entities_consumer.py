import json
import traceback
import aio_pika
from services.html_scraper import fetch_company_data, fetch_company_details
from utils.logger import setup_logger
import os

logger = setup_logger("consumer")

RABBITMQ_SETTINGS = {
    "host": os.getenv("RABBITMQ_HOST"),
    "port": int(os.getenv("RABBITMQ_PORT")),
    "login": os.getenv("RABBITMQ_USER"),
    "password": os.getenv("RABBITMQ_PASS"),
}
RESULTS_QUEUE_NAME = os.getenv("RABBITMQ_RESULTS_QUEUE")
PARSER_ID = os.getenv("PARSER_ID")
STATE = os.getenv("STATE")
async def publish_result(result: dict, channel: aio_pika.Channel):
    await channel.default_exchange.publish(
        aio_pika.Message(
            body=json.dumps(result).encode(),
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT
        ),
        routing_key=RESULTS_QUEUE_NAME
    )
    logger.info(f"Published result to '{RESULTS_QUEUE_NAME}': {json.dumps(result, indent=2, ensure_ascii=False)}")
async def handle_search(payload: dict, channel: aio_pika.Channel):
    query = payload.get("query")
    task_id = payload.get("task_id")
    results = await fetch_company_data(query)
    result_payload = {
        "task_id": task_id,
        "parser_id": PARSER_ID,
        "action": "search",
        "results": results
    }
    await publish_result(result_payload, channel)

async def handle_details(payload: dict, channel: aio_pika.Channel):
    url = payload.get("url")
    task_id = payload.get("task_id")
    results = await fetch_company_details(url)
    result_payload = {
        "task_id": task_id,
        "parser_id": PARSER_ID,
        "action": "details",
        "results": results
    }
    await publish_result(result_payload, channel)
async def handle_message(message: aio_pika.IncomingMessage):
    async with message.process():
        try:
            payload = json.loads(message.body.decode())
            action = payload.get("action")
            states = payload.get("states")
            state = payload.get("state")

            connection = await aio_pika.connect_robust(**RABBITMQ_SETTINGS)
            channel = await connection.channel()
            await channel.declare_queue(RESULTS_QUEUE_NAME, durable=True)

            if action == "search" and (STATE in states or not states):
                await handle_search(payload, channel)
            elif action == "details" and state == STATE:
                await handle_details(payload, channel)
            else:
                logger.warning(f"Unknown action: {action}")

        except json.JSONDecodeError:
            logger.warning("Invalid JSON format in message.")
        except Exception as e:
            logger.error(f"Error handling message: {e}")
            traceback.print_exc()
