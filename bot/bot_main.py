import bot_logging
import bot_config
import bot_handler
from bot_comms import from_bot_manager, send_to_user

class aiBot:

    def __init__(self):
        self.logger = bot_logging.logging.getLogger('BotInstance') 
        self.logger.addHandler(bot_logging.file_handler)
        self.logger.info(f"Init Bot Instance")

    async def async_init(self):
        #Init AI
        self.llm = ChatOpenAI(model_name=ai_config.MAIN_AI, temperature=0, verbose=True)
        self.handler = RabbitHandler()
        self.tools = self.load_chads_tools(self.llm)

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

    #Main Loop
    def model_response(self):
        "loop"
        message = from_bot_manager()
        if message:
        
            credentials = message.get('credentials')
            prompt = message.get('prompt')

            if prompt:
                send_to_user(prompt)

            if credentials:
                send_to_user(f"Credentials Received: {credentials}")

    def process_task_schedule(self):
        "check tasks"

    def process_email_schedule(self):
        "check emails"