from flask import Flask
from bots import Alerter, AlertsStarter
from agent_manager import  AgentChooser
import logging
LOG = logging.getLogger('bots')
import telepot
from telepot.delegate import (
    per_chat_id, per_callback_query_origin, create_open, pave_event_space, per_message, call,
    per_from_id)
import telepot.helper
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from flask import jsonify, request
from bots import get_chat_ids, initialize_chat_ids, get_sent_messages
import json
import time
import asyncio
import threading


app = Flask(__name__)
app.config.from_pyfile("config.py")
TOKEN = app.config['TOKEN']
timeout = app.config['MESSAGE_TIMEOUT']

# this to register new agents on doing /start
initialize_chat_ids()
bot = telepot.DelegatorBot(TOKEN, [
    pave_event_space()(
        per_chat_id(), create_open, AlertsStarter, timeout=3),
    pave_event_space()(
        per_callback_query_origin(), create_open, Alerter, timeout=5),
])

agent_chooser = AgentChooser()
message_loop = MessageLoop(bot)

def check_sent_messages():
    while(1):
        now = time.time()
        messages = get_sent_messages()
        for msg in messages:
            if round(now - msg['timestamp']) > timeout:
                #send the message to the back up agent
                if msg['level'] == "level1":
                    # need to check if this is the period of the back up or not
                    message = send_inline_message(msg['backup'][0], msg['data'])
                    msg['telegram'] = msg['backup'][0]
                    msg['level'] = 'level2'
                    msg['message_id'] = message['message_id']
                    msg['timestamp'] = time.time()

                elif msg['level'] == "level2":
                    message = send_inline_message(msg['reports_into'], msg['data'])
                    # Remove once escalated
                    msg['timestamp'] == time.time()
                    msg['level'] = "level3"
                    msg['message_id'] = message['message_id']
                else:
                    try:
                        # at this point we should delete old messages even if no one picked them
                        messages.remove(message)
                    except Exception as e:
                        # should pass if the user caught it before deleting
                        pass

        time.sleep(20)

message_thread = threading.Thread(name="message_thread", target=check_sent_messages)
message_thread.start()



@app.route('/alerts/', methods=['POST'])
def new_alert():
    data = json.loads(request.data.decode())
    agent = agent_chooser.get_current_agent()
    # chat_id = get_chat_ids().get(agent.telegram)
    message = send_inline_message(agent.telegram, data)
    msg = {}
    msg['telegram'] = agent.telegram
    msg['timestamp'] = time.time()
    msg['data'] = data
    msg['backup'] = agent.backup
    msg['level'] = "level1"
    msg['message_id'] = message['message_id']
    msg['reports_into'] = agent.reports_into
    get_sent_messages().append(msg)
    return jsonify(stats_code=200)

def send_inline_message(telegram, data, call_back="ack"):
    chat_id = get_chat_ids().get(telegram)
    message = bot.sendMessage(chat_id,
        "{}: {}: {}".format(data['text'], data['severity'], data['environment']),
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[[
                InlineKeyboardButton(text='ACK', callback_data=call_back),
            ]]
            )
        )
    return message

if __name__ == "__main__":
    message_loop.run_as_thread()
    app.run(debug=True, use_reloader=False)
