import traceback
import bot_config
import bot_logging

from datetime import datetime
from typing import Any, Dict, Optional, Type

from bot_comms import publish_event_card, publish_list, send_to_another_bot
from bot_utils import tool_description, tool_error


from langchain.callbacks.manager import AsyncCallbackManagerForToolRun, CallbackManagerForToolRun
from langchain.tools import BaseTool


tool_logger = bot_logging.logging.getLogger('ToolLogger')
tool_logger.addHandler(bot_logging.file_handler)



class Forward(BaseTool):
    parameters = []
    optional_parameters = []
    name = "FORWARD"
    summary = """Useful to forward request on to another bot"""
    parameters.append({"name": "request", "description": "original reqeuest"})
    description = tool_description(name, summary, parameters, optional_parameters)
    return_direct = True

    def _run(self, request: str, publish: str = "True", run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        try:
            send_to_another_bot("",request)
            
        except Exception as e:
            #traceback.print_exc()
            tb = traceback.format_exc()
            return tool_error(e, tb, self.description)
    
    async def _arun(self, query: str, run_manager: Optional[AsyncCallbackManagerForToolRun] = None) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("FORWARD does not support async")
