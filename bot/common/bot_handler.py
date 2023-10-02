import traceback
import re
import json
import bot_config
import common.bot_logging

from langchain.callbacks.base import BaseCallbackHandler
from typing import Any, Dict, List, Optional, Union
from uuid import UUID
from langchain.input import print_text
from langchain.schema import AgentAction, AgentFinish, LLMResult

# import pika
handler_logger = common.bot_logging.logging.getLogger('BotHandler')
handler_logger.addHandler(common.bot_logging.file_handler)
"This module handles sending and recieving between server and bots"

from common.bot_comms import send_to_user


class RabbitHandler(BaseCallbackHandler):

    #message_channel = pika.BlockingConnection()


    def __init__(self, color: Optional[str] = None, ) -> None:
        """Initialize callback handler."""
    
        

    def on_agent_finish(
        self,
        finish: AgentFinish,
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any,
    ) -> Any:
        try:
            handler_logger.info(f"on_agent_finish Callback {finish}")
            #print(f"on_agent_finish Callback {finish.log}")
            message = finish
            if message:
                #message = encode_message(config.USER_ID,'on_agent_finish', message)
                #self.message_channel.basic_publish(exchange='',routing_key='notify',body=message)
                handler_logger.info(f"Agent Finish: {message}")
        except Exception as e:
            traceback.print_exc()

    def on_chain_end(
        self,
        outputs: Dict[str, Any],
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any,
    ) -> Any:
        try:
            handler_logger.info(f"on_chain_end Callback {outputs}")
            #response = outputs.get("output")
            #look for output

            #look for text
            if outputs:

                # Convert the string to dictionary
                #dict_str = eval(outputs)

                # Extract 'text' content
                text_content = outputs.get("text")
                output_content = outputs.get("output")

                if text_content:
                    # Extract text part without JSON string
                    text_without_json = text_content.split('```')[0].strip()
                    text_without_prefixes = text_without_json.replace('Thought: ','').replace('Action:', '').replace('\n','')
                    if bot_config.VERBOSE:
                        """Turn off"""
                        #publish(f"VERBOSE: {text_without_prefixes}")
                
                if output_content:
                    send_to_user(f"{output_content}")
                    #buttons = [("Creating an Email", f"Create an email with the following: {output_content}"),("Creating a Task", f"Create a task with the following: {output_content}"),("Creating a Meeting", f"Create a meeting to discuss the following: {output_content}")]
                    #buttons = generate_commands(output_content)
                    #feedback = f"""{output_content}. Is there anything else I can do?"""
                    #publish_actions(feedback, buttons)
        except Exception as e:
            traceback.print_exc()
            #return e

    def on_chain_error(
        self,
        error: Union[Exception, KeyboardInterrupt],
        *,
        run_id: UUID,
        parent_run_id: Optional[UUID] = None,
        **kwargs: Any,
    ) -> Any:
        """Run when chain errors."""
        if error:
            #message = encode_message(config.USER_ID,'prompt', message)
            #self.message_channel.basic_publish(exchange='',routing_key='notify',body=message)
            handler_logger.error(f"Chain Error: {error}")
            send_to_user(f"{error}")
            return str(error)