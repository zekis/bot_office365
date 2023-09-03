# Copyright (c) Tierney Morris
#This bot starts, registers itself with the server, and then waits for a message from a user.
#when bot rescieves message, it will start an instance of itself and parse the message on to the bot.
#the bot will send and recieve messages from the user until the task is complete and then shutdown

import bot_config
import sys
import traceback
import uuid
import bot_logging


from datetime import datetime
from http import HTTPStatus

from typing import Dict


import asyncio
import threading
#from aiohttp import web
#from botbuilder.core.integration import aiohttp_error_middleware

from bot_manager import process_server_message, register_self

async def main_loop():
    #logger.info("Start message processing")
    register_self()

    while True:
        await process_server_message()
        await asyncio.sleep(0.5)

async def heartbeat_loop():
    #logger.info("Start message processing")
    while True:
        await asyncio.sleep(float(bot_config.HEARTBEAT_SEC))
        register_self()
        

async def main():
    bot_config.BOT_ID = "office365"
    bot_config.BOT_DESCRIPTION = "office 365 emails, tasks, and calander manager"
    

    logger = bot_logging.logging.getLogger('Bot_365') 
    logger.addHandler(bot_logging.file_handler)
    logger.info(f"Init Bot")

    tasks = []
    tasks.append(asyncio.create_task(main_loop()))
    tasks.append(asyncio.create_task(heartbeat_loop()))
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())

