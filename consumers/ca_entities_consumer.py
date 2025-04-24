import json
import traceback
import aio_pika
from services.html_scraper import fetch_company_data, fetch_company_details
from utils.logger import setup_logger
from http_client import send_post_request
import os
from dotenv import load_dotenv
load_dotenv()

POST_URL = os.getenv("POST_URL")
logger = setup_logger("consumer")

async def handle_message(message: aio_pika.IncomingMessage):
    async with message.process():
        try:
            payload = json.loads(message.body.decode())
            action = payload.get("action")

            if action == "search":
                query = payload.get("query")
                results = await fetch_company_data(query)
                logger.info(f"Search results for '{query}': {json.dumps(results, indent=2, ensure_ascii=False)}")
                # response = await send_post_request(POST_URL, results)
                # if response:
                #     logger.info(f"Search results successfully sent to {POST_URL}")
                # else:
                #     logger.error(f"Failed to send search results to {POST_URL}")
            elif action == "details":
                company_url = payload.get("url")
                results = await fetch_company_details(company_url)
                logger.info(f"Received request for details of company: {company_url}: {json.dumps(results, indent=2, ensure_ascii=False)}")
                # response = await send_post_request(POST_URL, results)
                # if response:
                #     logger.info(f"Company details successfully sent to {POST_URL}")
                # else:
                #     logger.error(f"Failed to send company details to {POST_URL}")
            else:
                logger.warning(f"Unknown action: {action}")
        except json.JSONDecodeError:
            logger.warning("Invalid JSON format in message.")
        except Exception as e:
            logger.error(f"Error handling message: {e}")
            traceback.print_exc()
