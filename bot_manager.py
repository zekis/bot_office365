import subprocess
import os
import signal
import bot_config
import datetime
import bot_logging
from bot_comms import from_dispatcher, send_to_dispatcher, send_to_user, clear_queue, send_to_instance, send_credentials_to_instance


bot_logger = bot_logging.logging.getLogger('BotManager')
bot_logger.addHandler(bot_logging.file_handler)
"This module handles sending and recieving between server and bots"

class BotManager:
    def __init__(self):
        bot_logger.info("Bot manager initilised")
        self.user_processes = {}

    def handle_instance(self, user_id):
        bot_instance_channel = bot_config.BOT_ID + user_id
        current_path = os.getcwd()
        if user_id in self.user_processes and self.user_processes[user_id].poll() is None:
            bot_logger.info(f"Bot is already running for user {user_id}")
            """do nothing"""
            return
        else:
            bot_logger.info(f"Starting bot for user {user_id}...")
            clear_queue(bot_instance_channel)
            process = subprocess.Popen([f'{current_path}/.venv/bin/python', f'./bot/bot.py', user_id, bot_config.BOT_ID])
            self.user_processes[user_id] = process
            return

    def stop_all_processes(self):
        """Stop all running bots."""
        for key, process in self.user_processes.items():
            if process.poll() is None:  # Check if the process is running
                bot_logger.warn(f"Stopping bots")
                process.terminate()
                process.wait()
                bot_logger.warn(f"Bots stopped")

        # Clear the dictionary after stopping all processes
        self.user_processes.clear()

    """stop the bot"""
    def stop_instance(self, user_id):
        bot_logger.warn(f"Stopping bot.")
        if user_id in self.user_processes:
            self.user_processes[user_id].terminate()
            self.user_processes[user_id].wait()
            del self.user_processes[user_id]
            bot_logger.warn(f"Bot stopped.")
        else:
            bot_logger.warn(f"No bot to stop.")




botManager = BotManager()
# userManager = UserManager(bot_config.DATA_DIR)
last_server_contact = datetime.datetime.now()
server_contact = False

async def process_server_message():
    # Declare server_contact and last_server_contact as global
    global server_contact, last_server_contact


    "process server messages"
    message = from_dispatcher()
    current_time = datetime.datetime.now()


    if message:
        

        bot_logger.debug(f"{message}")
        

        bot_id = message.get('bot_id')
        command = message.get('command')
        data = message.get('data')
        
        user_id = message.get('user_id')
        prompt = message.get('prompt')
        credentials = message.get('credentials')
        
        

        if command:
            if command == "registered":
                if not server_contact:
                    bot_logger.info(f"Server connection restored")
                server_contact = True
                last_server_contact = current_time
                bot_config.HEARTBEAT_SEC = bot_config.HEARTBEAT_NORMAL_SEC
            
            if command == "unknown_bot_id":
                server_contact = True
                register_self()
            
        
            if command == "heartbeat":
                # Update the last_bot_contact time for known bots
                is_my_process = False
                
                for pid, process in botManager.user_processes.items():
                    # Depending on what type `process` is, you might need to adjust this
                    if process.pid == data:  
                        process.last_bot_contact = current_time
                        is_my_process = True
                        break

                if not is_my_process:
                    # Bot is not known to the manager
                    bot_logger.warn(f"Received heartbeat from unknown bot with process ID: {data}.")
                    # Kill process using ID in data
                    try:
                        os.kill(data, signal.SIGTERM)
                        bot_logger.info(f"Killed unknown bot process with ID: {data}.")
                    except ProcessLookupError:
                        bot_logger.error(f"Process with ID {data} not found.")




        if prompt:
            if prompt == 'stop':
                send_to_user(user_id, f"stopping bot instance...")
                botManager.stop_instance(user_id)
                return False
            if prompt == 'stop_all':
                send_to_user(user_id, f"stopping all bot instances...")
                botManager.stop_all_processes()
                return False

            if prompt == 'status':
                if user_id in botManager.user_processes:
                    last_bot_contact = botManager.user_processes[user_id].last_bot_contact
                    process_id = botManager.user_processes[user_id].pid
                    send_to_user(user_id, f"Current Instance PID: {process_id}, Last Reported Healthy {last_bot_contact}")
                else:
                    send_to_user(user_id, f"No running bot instance")
                
                return False
            if prompt == 'ping':
                send_to_user(user_id, f"pinging instances")
                send_to_instance(user_id, 'ping')
                return False
            if prompt == 'start':
                send_to_user(user_id, f"starting bot instance...")
                botManager.handle_instance(user_id)
                send_credentials_to_instance(user_id, credentials)
                return False
            if prompt == 'restart':
                send_to_user(user_id, f"stopping bot instance...")
                botManager.stop_instance(user_id)
                
                send_to_user(user_id, f"starting bot instance...")
                botManager.handle_instance(user_id)
                send_credentials_to_instance(user_id, credentials)
                return False

            if prompt == 'heartbeat':
                return False


            #send_to_user(user_id, f"thinking...")
            botManager.handle_instance(user_id)
            #always send credentials first
            send_credentials_to_instance(user_id, credentials)
            send_to_instance(user_id, prompt)

           
    # if (current_time - last_server_contact).total_seconds() > float(bot_config.SERVER_TIMOUT_SEC) and server_contact == True:
    #     bot_logger.warn(f"Server connection lost")
    #     server_contact = False
    #     #register every second until True (Server clears messages on startup)
    #     bot_config.HEARTBEAT_SEC = bot_config.HEARTBEAT_RETRY_SEC
    #     #kill all bots
    #     botManager.stop_all_processes()
                
    # for process in user_processes:
    #     if (current_time - process.last_bot_contact).total_seconds() > float(bot_config.BOT_TIMEOUT_SEC):
    #         #kill process
    #         self.user_processes[user_id].terminate()
    #         self.user_processes[user_id].wait()
    #         del self.user_processes[user_id]
    #         bot_logger.warn(f"Bot stopped.")

def clear_heartbeats():
    clear_queue(bot_config.BOT_ID)

def register_self():
    "send register message to server"
    "To use this bot, the server must send these values"
    required_credentials = []
    required_credentials.append(('openai_api', 'This is your OpenAI API key'))
    required_credentials.append(('tenant_id', 'Microsoft Application tenant ID'))
    required_credentials.append(('user_name', 'Your office username. Usually this is firstname.lastname'))
    required_credentials.append(('email_address', 'Your office EMAIL address, this is used to determine if emails are addressed to you'))
    required_credentials.append(('app_id', 'The Microsoft Application ID. This app must be given permission to access emails and tasks'))
    required_credentials.append(('app_secret', 'The Microsoft Application secrect key'))
    required_credentials.append(('folder_to_monitor', 'This is the folder that the bot will monitor for incoming emails, If you are not sure, just enter inbox'))
    required_credentials.append(('ignore_domains', 'This a comma seperated list of domains to ignore'))
    required_credentials.append(('auto_draft_reply', 'yes/no setting determines if the bot automatically creates drafts for emails received'))
    required_credentials.append(('time_zone', "Country/City. example, Australia/Perth"))
    required_credentials.append(('bots_todo_folder', 'This is the MS todo task folder that the bot will monitor for jobs'))
    required_credentials.append(('auto_read_emails', 'yes/no setting determines if the bot automatically monitors your inbox'))
    
    register_package = {
        'description': bot_config.BOT_DESCRIPTION,
        'required_credentials': required_credentials
    }
    send_to_dispatcher("register", register_package)
    # send_to_dispatcher(bot_con, bot_id, command, data)


def heartbeat():
    send_to_dispatcher("heartbeat", None)
    # send_to_dispatcher(bot_con, bot_id, command, data)




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


    