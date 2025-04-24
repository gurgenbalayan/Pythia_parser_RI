import aiohttp
import logging
import traceback

logger = logging.getLogger("http_client")

# Send to server
async def send_post_request(url, data):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=data) as response:
                if response.status == 200:
                    logger.info(f"Successfully sent data to {url}")
                    return await response.json()
                else:
                    logger.error(f"Failed to send data to {url}, Status Code: {response.status}")
                    return None
    except Exception as e:
        logger.error(f"Error sending POST request: {e}")
        traceback.print_exc()
        return None
