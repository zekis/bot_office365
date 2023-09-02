import traceback
import pika
import json
import time 
import bot_logging

comms_logger = bot_logging.logging.getLogger('BotComms')
comms_logger.addHandler(bot_logging.file_handler)
"This module handles sending and recieving between server and bots"

def encode_command(bot_id, command: str, data: str) -> str:
    "encode a <prompt> into a dict and return a string to send via rabbitmq to a bot"
    
    response = {
        "bot_id": bot_id,
        "command": command,
        "data": data
    }
    comms_logger.debug(f"ENCODING: {response}")

    return json.dumps(response)


def decode_response(response: dict) -> str:
    "decode a dict <response> into a message and return the prompt as string"
    
    try:
        response = response.decode("utf-8")

        comms_logger.debug(f"DECODING: {response}")

        response_dict = json.loads(response)

        #prompt = response_dict.get('prompt')
        
        return response_dict
    except Exception as e:
        traceback.print_exc()
        return "prompt", f"error: {e}", None


def from_dispatcher(channel_id: str) -> str:
    'consume and decode a message from <channel_id> directed as a specific user'

    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))

    message_channel = connection.channel()
    
    message_channel.queue_declare(queue=channel_id)

    method, properties, body = message_channel.basic_get(queue=channel_id, auto_ack=True)

    message_channel.close()

    if body:
        response = decode_response(body)
        return response
    else:
        return None

def send_to_dispatcher(channel_id: str, bot_id: str, command: str, data: str):
    "encode and send a message directly to a bot using <channel_id>"

    comms_logger.info(f"CHANNEL: {channel_id} - {bot_id} - {command}")

    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))

    message_channel = connection.channel()

    message_channel.queue_declare(queue=channel_id)

    message = encode_command(bot_id, command, data)

    message_channel.basic_publish(exchange='',routing_key=channel_id,body=message)