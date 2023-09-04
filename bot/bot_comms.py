import traceback
import bot_config
import pika
import json
import time 
import bot_logging


from bot_cards import (
    create_draft_email_card, 
    create_draft_forward_email_card, 
    create_draft_reply_email_card, 
    create_email_card, 
    create_event_card, 
    create_list_card,
    create_folder_list_card, 
    create_media_card,
    create_todo_card,
    create_input_card
)

comms_logger = bot_logging.logging.getLogger('BotComms')
comms_logger.addHandler(bot_logging.file_handler)
"This module handles sending and recieving between server and bots"


def encode_response(bot_id, user_id, prompt: str, type=None, actions=None) -> str:
    "encode a <prompt> into a dict and return a string to send via rabbitmq to a bot"
    
    response = {
        "bot_id": bot_id,
        "user_id": user_id,
        "type": type,
        "prompt": prompt,
        "actions": actions
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

def encode_instance_message(user_id, prompt: str) -> str:
    "encode a <prompt> into a dict and return a string to send via rabbitmq to a bot"
    
    response = {
        "user_id": user_id,
        "prompt": prompt
    }
    comms_logger.debug(f"ENCODING: {response}")

    return json.dumps(response)


def send_to_user(prompt: str):
    "encode and send a message directly to a bot using <channel_id>"
    channel_id = bot_config.DISPATCHER_CHANNEL_ID
    bot_id = bot_config.BOT_ID
    user_id = bot_config.USER_ID

    comms_logger.debug(f"CHANNEL: {channel_id} - {user_id} - {prompt}")

    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))

    message_channel = connection.channel()

    message_channel.queue_declare(queue=channel_id)

    message = encode_response(bot_id, user_id, prompt)

    message_channel.basic_publish(exchange='',routing_key=channel_id,body=message)

def send_to_me(prompt: str):
    "encode and send a message directly to a bot using <channel_id>"
    user_id = bot_config.USER_ID
    bot_instance_channel = bot_config.BOT_ID + bot_config.USER_ID
    

    comms_logger.debug(f"CHANNEL: {bot_instance_channel} - {user_id} - {prompt}")

    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))

    message_channel = connection.channel()

    message_channel.queue_declare(queue=bot_instance_channel)

    message = encode_instance_message(user_id, prompt)

    message_channel.basic_publish(exchange='',routing_key=bot_instance_channel,body=message)

def from_bot_manager() -> str:
    'consume and decode a message from <channel_id> directed as a specific user'
    channel_id = bot_config.BOT_ID + bot_config.USER_ID

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





# def publish_system_message(command, parameters, override_id=None):
#     connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
#     if not override_id:
#         message = encode_message(ai_config.USER_ID, 'prompt', command, parameters)
#     else:
#         message = encode_message(override_id, 'prompt', command, parameters)
#     notify_channel = connection.channel()
#     notify_channel.basic_publish(exchange='',
#                       routing_key='notify',
#                       body=message)
#     #print(message)
#     notify_channel.close()



# def publish_action(message, button1, button2, override_id=None):
#     connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
#     actions = [CardAction(
#         type=ActionTypes.im_back,
#         title=button1,
#         value=button1,
#     ),
#     CardAction(
#         type=ActionTypes.im_back,
#         title=button2,
#         value=button2,
#     )]
#     actions = [action.__dict__ for action in actions] if actions else []
#     if not override_id:
#         message = encode_message(ai_config.USER_ID, 'action', message, actions)
#     else:
#         message = encode_message(override_id, 'action', message, actions)
    
#     notify_channel = connection.channel()
#     notify_channel.basic_publish(exchange='',
#                       routing_key='notify',
#                       body=message)
#     #print(message)
#     notify_channel.close()

# def publish_actions(message, buttons, override_id=None):
#     connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))

#     actions = [CardAction(
#         type=ActionTypes.im_back,
#         title=button[0],
#         value=button[1],
#         mode="secondary"
#     ) for button in buttons]

#     actions = [action.__dict__ for action in actions] if actions else []

#     if not override_id:
#         message = encode_message(ai_config.USER_ID, 'action', message, actions)
#     else:
#         message = encode_message(override_id, 'action', message, actions)

#     notify_channel = connection.channel()
#     notify_channel.basic_publish(exchange='',
#                       routing_key='notify',
#                       body=message)
#     #print(message)
#     notify_channel.close()


def publish_list(message,strings_values):
    
    channel_id = bot_config.DISPATCHER_CHANNEL_ID
    bot_id = bot_config.BOT_ID
    user_id = bot_config.USER_ID

    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))

    message_channel = connection.channel()

    message_channel.queue_declare(queue=channel_id)

    comms_logger.info(f"CHANNEL: {channel_id} - {user_id} - {message} - {strings_values}")


    #convert string to dict (hopefully our AI has formatted it correctly)
    try:
        cards = create_list_card(message,strings_values)
        #cards = create_list_card("Choose an option:", [("Option 1", "1"), ("Option 2", "2"), ("Option 3", "3")])
    except Exception as e:
        traceback.print_exc()
        cards = None
    
    message = encode_response(bot_id, user_id, message, "cards", cards)

    message_channel.basic_publish(exchange='',routing_key=channel_id,body=message)




def publish_folder_list(message,strings_values):
    channel_id = bot_config.DISPATCHER_CHANNEL_ID
    bot_id = bot_config.BOT_ID
    user_id = bot_config.USER_ID

    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))

    message_channel = connection.channel()

    message_channel.queue_declare(queue=channel_id)

    comms_logger.info(f"CHANNEL: {channel_id} - {user_id} - {message} - {strings_values}")

    #convert string to dict (hopefully our AI has formatted it correctly)
    try:
        cards = create_folder_list_card(message,strings_values)
        #cards = create_list_card("Choose an option:", [("Option 1", "1"), ("Option 2", "2"), ("Option 3", "3")])
    except Exception as e:
        traceback.print_exc()
        cards = None
    
    message = encode_response(bot_id, user_id, message, "cards", cards)

    message_channel.basic_publish(exchange='',routing_key=channel_id,body=message)

def publish_event_card(message,event):
    channel_id = bot_config.DISPATCHER_CHANNEL_ID
    bot_id = bot_config.BOT_ID
    user_id = bot_config.USER_ID

    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))

    message_channel = connection.channel()

    message_channel.queue_declare(queue=channel_id)

    comms_logger.info(f"CHANNEL: {channel_id} - {user_id} - {message} - {event}")
    
    #convert string to dict (hopefully our AI has formatted it correctly)
    try:
        cards = create_event_card(message,event)
    except Exception as e:
        traceback.print_exc()
        cards = None
    
    message = encode_response(bot_id, user_id, message, "cards", cards)

    message_channel.basic_publish(exchange='',routing_key=channel_id,body=message)

def publish_todo_card(message,task):
    channel_id = bot_config.DISPATCHER_CHANNEL_ID
    bot_id = bot_config.BOT_ID
    user_id = bot_config.USER_ID

    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))

    message_channel = connection.channel()

    message_channel.queue_declare(queue=channel_id)

    comms_logger.info(f"CHANNEL: {channel_id} - {user_id} - {message} - {task}")

    #convert string to dict (hopefully our AI has formatted it correctly)
    try:
        cards = create_todo_card(message,task)
    except Exception as e:
        traceback.print_exc()
        cards = None
    
    message = encode_response(bot_id, user_id, message, "cards", cards)

    message_channel.basic_publish(exchange='',routing_key=channel_id,body=message)
    
def publish_email_card(message,email,summary):
    channel_id = bot_config.DISPATCHER_CHANNEL_ID
    bot_id = bot_config.BOT_ID
    user_id = bot_config.USER_ID

    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))

    message_channel = connection.channel()

    message_channel.queue_declare(queue=channel_id)

    comms_logger.info(f"CHANNEL: {channel_id} - {user_id} - {message} - {email}")
    
    #convert string to dict (hopefully our AI has formatted it correctly)
    try:
        cards = create_email_card(message,email,summary)
    except Exception as e:
        traceback.print_exc()
        cards = None
    
    message = encode_response(bot_id, user_id, message, "cards", cards)

    message_channel.basic_publish(exchange='',routing_key=channel_id,body=message)

def publish_draft_card(message,email,response, reply=False):
    channel_id = bot_config.DISPATCHER_CHANNEL_ID
    bot_id = bot_config.BOT_ID
    user_id = bot_config.USER_ID

    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))

    message_channel = connection.channel()

    message_channel.queue_declare(queue=channel_id)

    comms_logger.info(f"CHANNEL: {channel_id} - {user_id} - {message} - {response}")
    
    #convert string to dict (hopefully our AI has formatted it correctly)
    try:
        if reply:
            cards = create_draft_reply_email_card(message,email,response)
        else:
            cards = create_draft_email_card(message,email,response)
    except Exception as e:
        traceback.print_exc()
        cards = None
    
    message = encode_response(bot_id, user_id, message, "cards", cards)

    message_channel.basic_publish(exchange='',routing_key=channel_id,body=message)

def publish_draft_forward_card(message,email,response):
    channel_id = bot_config.DISPATCHER_CHANNEL_ID
    bot_id = bot_config.BOT_ID
    user_id = bot_config.USER_ID

    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))

    message_channel = connection.channel()

    message_channel.queue_declare(queue=channel_id)

    comms_logger.info(f"CHANNEL: {channel_id} - {user_id} - {message} - {response}")
    
    #convert string to dict (hopefully our AI has formatted it correctly)
    try:
        cards = create_draft_forward_email_card(message,email,response)
    except Exception as e:
        traceback.print_exc()
        cards = None
    
    message = encode_response(bot_id, user_id, message, "cards", cards)

    message_channel.basic_publish(exchange='',routing_key=channel_id,body=message)

# def publish_input_card(intro,parameters):
#     connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
#     notify_channel = connection.channel()
#     notify_channel.queue_declare(queue='notify')
    
#     try:
#         card = create_input_card(intro, parameters)
#     except Exception as e:
#         traceback.print_exc()
#         cards = None
    
#     message = encode_message(ai_config.USER_ID, "cards", intro, card)
#     notify_channel.basic_publish(exchange='',routing_key='notify',body=message)

# #Consume bot messages
# def consume(override_id=None):
#     connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
#     message_channel = connection.channel()
#     if not override_id:
#         message_channel.queue_declare(queue=ai_config.USER_ID)
#         method, properties, body = message_channel.basic_get(queue=ai_config.USER_ID, auto_ack=True)
#     else:
#         message_channel.queue_declare(queue=override_id)
#         method, properties, body = message_channel.basic_get(queue=override_id, auto_ack=True)
#     message_channel.close()
#     if body:
#         response = decode_response(body)
#         return response
#     else:
#         return None



# #clear bots messages (do this on start)
# def clear_queue(id):
#     print("Clearing message queue")
#     connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
#     message_channel = connection.channel()
#     message_channel.queue_delete(id)
#     message_channel.queue_declare(id)


# def receive_from_bot():
#     connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
#     notify_channel = connection.channel()
#     method, properties, body = notify_channel.basic_get(queue='notify',auto_ack=True)
#     if body:
#         user_id, type, body, data = decode_message(body)
#         return user_id, type, body, data
#     else:
#         return None, None,None, None

#callbacks
async def get_input(timeout_minutes=1):
    timeout = time.time() + 60*timeout_minutes   # x minutes from now
    #print("Insert your text. Press Ctrl-D (or Ctrl-Z on Windows) to end.")
    #contents = []
    comms_logger.info("Waiting for response...")
    while True:
        msg = from_bot_manager()
        if msg:
            comms_logger.info("Response recieved: " + msg)
            question = msg
            break
        elif timeout_minutes > 0:
            if time.time() > timeout:
                comms_logger.info("Timeout")
                question = "timeout"
                break
        #time.sleep(0.5)
        #await asyncio.sleep(0.5)
    return question

def send_prompt(query):
        send_to_user(query + "?")
