import subprocess
import bot_config
from user_manager import UserManager
import bot_logging
from bot_comms import from_dispatcher, send_to_dispatcher, send_to_user, clear_queue, send_to_instance, send_credentials_to_instance


bot_logger = bot_logging.logging.getLogger('BotManager')
bot_logger.addHandler(bot_logging.file_handler)
"This module handles sending and recieving between server and bots"

class BotManager:
    def __init__(self):
        bot_logger.info("Bot manager initilised")
        self.user_processes = {}

    def handle_instance(self, prompt, user_id):
        bot_instance_channel = bot_config.BOT_ID + user_id

        if user_id in self.user_processes and self.user_processes[user_id].poll() is None:
            #bot_logger.info(f"Bot is already running for user {user_id}", user_id)
            """do nothing"""
            return
        else:
            bot_logger.info(f"Starting bot for user {user_id}...")
            clear_queue(bot_instance_channel)
            process = subprocess.Popen(['python', './bot/bot.py', user_id, bot_config.BOT_ID])
            self.user_processes[user_id] = process
            return



botManager = BotManager()
userManager = UserManager(bot_config.DATA_DIR)

async def process_server_message():
    "process server messages"
    message = from_dispatcher()
    if message:

        bot_logger.debug(f"{message}")

        bot_id = message.get('bot_id')
        command = message.get('command')
        data = message.get('data')
        
        user_id = message.get('user_id')
        prompt = message.get('prompt')
        credentials = message.get('credentials')
        

        # if command:
        #     if command == "registered":
        #         "Do nothing for now"
        #     else:
        #         bot_logger.info(f"{message}")
        # user_id = message.get('user_id')
        # prompt = message.get('prompt')
        if prompt:
            botManager.handle_instance(prompt, user_id)
            bot_instance_channel = bot_config.BOT_ID + user_id
            send_to_instance(bot_instance_channel, user_id, prompt)
            send_credentials_to_instance(bot_instance_channel, user_id, credentials)

            #does the user have a bot_instance
            #spin one up
            # send_to_user(bot_config.DISPATCHER_CHANNEL_ID, bot_config.BOT_ID, user_id, prompt)
            # send_to_dispatcher(bot_config.DISPATCHER_CHANNEL_ID, bot_config.BOT_ID, 'end', user_id)





def register_self():
    "send register message to server"
    "To use this bot, the server must send these values"
    required_credentials = []
    required_credentials.append('openai_api')
    required_credentials.append('tenant_id')
    required_credentials.append('user_name')
    required_credentials.append('email_address')
    register_package = {
        'description': bot_config.BOT_DESCRIPTION,
        'required_credentials': required_credentials
    }
    send_to_dispatcher("register", register_package)
    #send_to_dispatcher(bot_con, bot_id, command, data)






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


    