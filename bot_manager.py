import subprocess
import bot_config
#from teams.rabbit_comms import publish, clear_queue
import bot_logging
from bot_comms import from_dispatcher, send_to_dispatcher


bot_logger = bot_logging.logging.getLogger('BotManager')
bot_logger.addHandler(bot_logging.file_handler)
"This module handles sending and recieving between server and bots"


async def process_server_message():
    "process server messages"
    message = from_dispatcher(bot_config.BOT_ID)
    if message:
        bot_logger.info("Message received")
        
        bot_logger.info(f"{message}")
        # user_id = message.get('user_id')
        # prompt = message.get('prompt')

def process_user_message():
    "process user message"

def register_self():
    "send register message to server"
    send_to_dispatcher(bot_config.DISPATCHER_CHANNEL_ID, bot_config.BOT_ID, "register", bot_config.BOT_DESCRIPTION)

def send_to_server():
    "send message to server"



# class BotManager:
#     def __init__(self):
#         server_logging.logger.info("Bot manager initilised")
#         self.user_processes = {}

#     def handle_command(self, command, user_id=None, tenant_id=None, user_name=None, email_address=None):
#         if user_id:
#             if command.lower() == "start":
#                 #start the bot
#                 """start the bot"""
#                 publish(f"Starting bot for user {user_id}...", user_id)
#                 if user_id in self.user_processes and self.user_processes[user_id].poll() is None:
#                     publish(f"Bot is already running for user {user_id}", user_id)
#                 else:
#                     clear_queue(user_id)
#                     process = subprocess.Popen(['python', 'ai.py', user_id, tenant_id, user_name, email_address])
#                     self.user_processes[user_id] = process

#             elif command.lower() == "quiet_start":
#                 #start the bot
#                 """start the bot"""
#                 if user_id in self.user_processes and self.user_processes[user_id].poll() is None:
#                     #publish(f"Bot is already running for user {user_id}", user_id)
#                     """do nothing"""
#                     return
#                 else:
#                     publish(f"Starting bot for user {user_id}...", user_id)
#                     clear_queue(user_id)
#                     process = subprocess.Popen(['python', 'ai.py', user_id, tenant_id, user_name, email_address])
#                     self.user_processes[user_id] = process
#                     return

#             elif command.lower() == "stop":
#                 #stop the bot
#                 """stop the bot"""
#                 publish(f"Stopping bot.", user_id)
#                 if user_id in self.user_processes:
#                     self.user_processes[user_id].terminate()
#                     self.user_processes[user_id].wait()
#                     del self.user_processes[user_id]
#                     publish(f"Bot stopped.", user_id)
#                 else:
#                     publish(f"No bot to stop.", user_id)

#             elif command.lower() == "restart":
#                 #stop the bot
#                 """restart the bot"""
#                 clear_queue(user_id)
#                 publish(f"Restarting bot for {user_name}.{user_id}", user_id)
#                 if user_id in self.user_processes:
#                     self.user_processes[user_id].terminate()
#                     self.user_processes[user_id].wait()
#                     del self.user_processes[user_id]
#                 process = subprocess.Popen(['python', 'ai.py', user_id, tenant_id, user_name, email_address])
#                 self.user_processes[user_id] = process
#                 publish(f"Bot restarted.", user_id)
            

#             elif command.lower() == "config":
#                 #stop the bot
#                 """restart the bot"""
#                 clear_queue(user_id)
#                 publish(f"Entering config mode for {user_name}. {user_id}", user_id)
#                 if user_id in self.user_processes:
#                     self.user_processes[user_id].terminate()
#                     self.user_processes[user_id].wait()
#                     del self.user_processes[user_id]
#                 process = subprocess.Popen(['python', 'ai.py', user_id, tenant_id, user_name, email_address, '--reset_config'])
#                 self.user_processes[user_id] = process
#                 #publish(f"Bot restarted.", user_id)

#             elif command.lower() == "list_bots":
                
#                 for process in self.user_processes:
#                     publish(f"Instances: {process} for {user_id}", user_id)
                
#             elif command.lower() == "stop_bots":
#                 self.stop_all_processes(user_id)
#                 publish(f"All bots stopped", user_id)
#                 print("all bots stopped")

#     def stop_all_processes(self, request_user_id):
#         """Stop all running bots."""
#         for user_id, process in self.user_processes.items():
#             if process.poll() is None:  # Check if the process is running
#                 publish(f"Stopping bot for user {user_id}...", request_user_id)
#                 process.terminate()
#                 process.wait()
#                 publish(f"Bot stopped for user {user_id}", request_user_id)

#         # Clear the dictionary after stopping all processes
#         self.user_processes.clear()


    