import os
from datetime import datetime
import bot_logging
import bot_config
from bot_handler import RabbitHandler
from bot_comms import from_bot_manager, send_to_user, get_input, send_prompt, from_bot_to_bot_manager
import sys

from loaders.todo import MSGetTasks, MSGetTaskFolders, MSGetTaskDetail, MSSetTaskComplete, MSCreateTask, MSDeleteTask, MSCreateTaskFolder, MSUpdateTask
from loaders.calendar import MSGetCalendarEvents, MSGetCalendarEvent, MSCreateCalendarEvent
from loaders.todo import scheduler_get_task_due_today, scheduler_get_bots_unscheduled_task
from loaders.outlook import scheduler_check_emails
from loaders.outlook import (
    MSSearchEmailsId,
    MSGetEmailDetail,
    MSDraftEmail,
    MSSendEmail,
    MSReplyToEmail,
    MSForwardEmail,
    MSDraftForwardEmail,
    MSDraftReplyToEmail
)

from langchain.chat_models import ChatOpenAI
from langchain.agents import initialize_agent
from langchain.agents import AgentType
from langchain.agents import load_tools, Tool
from langchain.agents import ZeroShotAgent, AgentExecutor
from langchain.memory import ConversationBufferMemory, ConversationBufferWindowMemory
from langchain.prompts import MessagesPlaceholder


class aiBot:

    def __init__(self):
        self.logger = bot_logging.logging.getLogger('BotInstance') 
        self.logger.addHandler(bot_logging.file_handler)
        self.logger.info(f"Init Bot Instance")
        self.credentials = []
        self.initialised = False

    def bot_init(self):
        #Init AI
        if not self.initialised:
            os.environ["OPENAI_API_KEY"] = bot_config.OPENAI_API_KEY
            self.llm = ChatOpenAI(model_name=bot_config.MAIN_AI, temperature=0, verbose=True)
            self.handler = RabbitHandler()
            self.tools = self.load_tools(self.llm)

            #Initate Agent Executor
            self.chat_history = MessagesPlaceholder(variable_name="chat_history")
            self.memory = ConversationBufferWindowMemory(memory_key="chat_history", k=2, return_messages=True)
            self.memory.buffer.clear()

            self.agent_executor = initialize_agent(
                tools=self.tools,
                llm=self.llm,
                agent=AgentType.OPENAI_FUNCTIONS,
                verbose=True,
                max_iterations=5, 
                agent_kwargs = {
                    "memory_prompts": [self.chat_history],
                    "input_variables": ["input", "agent_scratchpad", "chat_history"]
                })
            self.initialised = True

    #Main Loop
    def process_messages(self):
        "loop"
        message = from_bot_manager()
        if message:
        
            incoming_credentials = message.get('credentials')
            prompt = message.get('prompt')

            if incoming_credentials:
                self.credentials = incoming_credentials
                bot_config.OPENAI_API_KEY = self.get_credential('openai_api')
                bot_config.TENANT_ID = self.get_credential('tenant_id')
                bot_config.FRIENDLY_NAME = self.get_credential('user_name')
                bot_config.OFFICE_USER = self.get_credential('email_address')
                self.bot_init()

            if prompt == "ping":
                send_to_user(f'PID:{os.getpid()} - pong')
                return
            
            if prompt == "kill":
                send_to_user(f'PID:{os.getpid()} - Shutting Down')
                sys.exit()
                return

            if prompt and self.initialised:
                #AI goes here
                self.process_model(prompt)

    def process_model(self, question):
        current_date_time = datetime.now()
        #inital_prompt = f"Previous conversation: {self.memory.buffer_as_str}" + f''', Thinking step by step and With only the tools provided and with the current date and time of {current_date_time} help the human with the following request, Request: {question} '''
        inital_prompt = f'''With the current date and time of {current_date_time} help the human with the following request, Request: {question} '''
        response = self.agent_executor.run(input=inital_prompt, callbacks=[self.handler])
        self.logger.info(response)

    def process_task_schedule(self):
        if self.initialised:
            "check tasks"
            while True:
                task = scheduler_get_task_due_today(bot_config.Todo_BotsTaskFolder)
                if task:
                    #self.logger.info(task)
                    self.logger.info(task.subject)
                    send_to_user(f"Looks like one of my tasks is due - {task.subject}")
                    current_date_time = datetime.now() 
                    try:
                        inital_prompt = f'''With only the tools provided and with the current date and time of {current_date_time}, help the human with the following request, Request: {task.subject} - {task.body}'''
                        response = self.agent_executor.run(input=inital_prompt, callbacks=[self.handler])
                        task.body = response
                        task.mark_completed()
                        task.save()
                    except Exception as e:
                        send_to_user( f"An exception occurred: {e}")
                else:
                    break

            while True:
                task = scheduler_get_bots_unscheduled_task(bot_config.Todo_BotsTaskFolder)
                if task:
                    #self.logger.info(task)
                    self.logger.info(task.subject)
                    send_to_user(f"Looks like one of my tasks is due - {task.subject}")
                    bot_logging.info(task.subject)
                    current_date_time = datetime.now() 
                    try:
                        inital_prompt = f'''With only the tools provided and with the current date and time of {current_date_time}, help the human with the following request, Request: {task.subject} - {task.body}'''
                        response = self.agent_executor.run(input=inital_prompt, callbacks=[self.handler])
                        task.body = response
                        task.mark_completed()
                        task.save()
                    except Exception as e:
                        send_to_user( f"An exception occurred: {e}")
                else:
                    break

    def process_email_schedule(self):
        if self.initialised:
            "check emails"
            scheduler_check_emails()

    def heartbeat(self):
        from_bot_to_bot_manager('heartbeat', os.getpid())

    def load_tools(self, llm) -> list():
        
        tools = load_tools(["human"], input_func=get_input, prompt_func=send_prompt, llm=llm)
        
        tools.append(MSGetTaskFolders())
        tools.append(MSGetTasks())
        tools.append(MSGetTaskDetail())
        tools.append(MSSetTaskComplete())
        tools.append(MSCreateTask())
        tools.append(MSDeleteTask())
        tools.append(MSCreateTaskFolder())
        
        tools.append(MSSearchEmailsId())
        tools.append(MSGetEmailDetail())
        tools.append(MSDraftEmail())
        tools.append(MSSendEmail())
        tools.append(MSReplyToEmail())
        tools.append(MSForwardEmail())
        tools.append(MSDraftReplyToEmail())
        tools.append(MSDraftForwardEmail())

        tools.append(MSGetCalendarEvents())
        tools.append(MSGetCalendarEvent())
        tools.append(MSCreateCalendarEvent())

        return tools
    
    def get_credential(self, name):
        self.logger.info(f"Fetching credential for: {name}")
        for credential in self.credentials:
            if name in credential:
                self.logger.debug(credential[name])
                return credential[name]
        return False