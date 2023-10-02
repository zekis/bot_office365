import traceback
import bot_config
import common.bot_logging

from datetime import datetime
from typing import Any, Dict, Optional, Type

from common.bot_comms import publish_event_card, publish_list, send_to_another_bot, publish_error
from common.bot_utils import tool_description, tool_error


from langchain.callbacks.manager import AsyncCallbackManagerForToolRun, CallbackManagerForToolRun
from langchain.tools import BaseTool


tool_logger = common.bot_logging.logging.getLogger('ToolLogger')
tool_logger.addHandler(common.bot_logging.file_handler)



class Forward(BaseTool):
    parameters = []
    optional_parameters = []
    name = "FORWARD"
    summary = """Useful to forward request on to another bot"""
    parameters.append({"name": "to", "description": "rough description of the the bot that needs to take over"})
    parameters.append({"name": "task", "description": "original reqeuest"})
    description = tool_description(name, summary, parameters, optional_parameters)
    return_direct = True

    def _run(self, to: str, request: str, publish: str = "True", run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        try:
            send_to_another_bot("",f"{to} Task: {request}")
            
        except Exception as e:
            #traceback.print_exc()
            tb = traceback.format_exc()
            publish_error(e, tb)
            return tool_error(e, tb, self.description)
    
    async def _arun(self, query: str, run_manager: Optional[AsyncCallbackManagerForToolRun] = None) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("FORWARD does not support async")