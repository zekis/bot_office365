import sys
import traceback
import argparse
from datetime import datetime

import asyncio
import threading

from bot_main import openaai_master
from bot_comms import publish, publish_action, publish_actions

import bot_config


async def task_scheduler(bot):
    #publish("Let me check to see if I have any scheduled tasks due today.")
    while True:
        bot.process_task_schedule()
        await asyncio.sleep(ai_config.Todo_PollingIntervalSeconds)

async def email_scheduler(bot):
    #publish("Let me check to see if I have any scheduled tasks due today.")
    while True:
        bot.process_email_schedule()
        await asyncio.sleep(ai_config.Todo_PollingIntervalSeconds / 10)

async def ai_response(bot):
    
    publish(f"Hi {ai_config.FRIENDLY_NAME}, How can I help you today?")
    #publish_action("Get Started", "List available tools", "BOT_RESTART")
    #buttons = [("Check my tasks", "Show me a list of my task folders"),("Check the weather", "Check the weather for my saved location"),("Check emails", "Did I get any emails today?"), ("Book a meeting", "Book a meeting for tomorrow morning"), ("Draft an email", "Draft an email"), ("Research AI news", "Research AI news"), ("Restart BOT", "bot_restart")]
    #publish_actions("How can I help you today?", buttons)
    while True:
        #model_selector()
        bot.model_response()
        await asyncio.sleep(0.5)
        #await asyncio.Event().wait()
    
async def main():
    #Create master bot
    bot = openaai_master()
    await bot.async_init()
    print("bot initilised")
    ai_tasks = []
    ai_tasks.append(asyncio.create_task(ai_response(bot)))
    ai_tasks.append(asyncio.create_task(task_scheduler(bot)))
    ai_tasks.append(asyncio.create_task(email_scheduler(bot)))
    await asyncio.gather(*ai_tasks)


#This bot starts, registers itself with the server, and then waits for a message from a user.
#when bot rescieves message, it will start an instance of itself and parse the message on to the bot.
#the bot will send and recieve messages from the user until the task is complete and then shutdown
#
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Language Chain Bot")
    parser.add_argument("user_id", type=str, help="User ID")
    parser.add_argument("tenant_id", type=str, help="Tenant ID")
    parser.add_argument("user_name", type=str, help="User Name")
    parser.add_argument("email_address", type=str, help="Email Address")
    #parser.add_argument("reset_config", type=bool, help="reset config", default=False, required=False)
    parser.add_argument("--reset_config", action="store_true", help="reset config", default=False)
    args = parser.parse_args()

    print("starting bot...")
    print("user_id: " + args.user_id)
    print("tenant_id: " + args.tenant_id)
    print("user_name: " + args.user_name)
    print("email_address: " + args.email_address)
    print("reset_config: " + str(args.reset_config))


    ai_config.USER_ID = args.user_id
    ai_config.TENANT_ID = args.tenant_id
    ai_config.FRIENDLY_NAME = args.user_name
    ai_config.OFFICE_USER = args.email_address
    ai_config.EMAIL_CACHE_FILE_NAME = "workspace/" + sanitize_subject(args.user_id,1000) + ".txt"
    ai_config.LOCAL_MEMORY_FILE_NAME = "workspace/" + sanitize_subject(args.user_id,1000) + "txt"
    ai_config.RESET_CONFIG = args.reset_config
    # Need to check for GPT API key here and request key before starting bot
    asyncio.run(main())