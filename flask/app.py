from flask import Flask
from bots import *
import logging

LOG = logging.getLogger()
import telepot
from telepot.delegate import (
    per_chat_id, per_callback_query_origin, create_open, pave_event_space, per_message, call,
    per_from_id)
import telepot.helper
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from flask import jsonify, request
import json
import time
import threading
import config
from utils import *
from spread_sheet_agent_manager import AgentManager
from gspread.exceptions import CellNotFound
import base64
import datetime
import utils
from toml_manager import TomlManager


app = Flask(__name__)
app.config.from_pyfile("config.py")
TOKEN = app.config['TOKEN']
timeout = app.config['MESSAGE_TIMEOUT']

# this to register new agents on doing /start
initialize_chat_ids()
bot = telepot.DelegatorBot(TOKEN, [
    pave_event_space()(
        per_chat_id(), create_open, AlertsStarter, timeout=100),
    pave_event_space()(
        per_callback_query_origin(), create_open, Alerter, timeout=5),
])
agent_manager = AgentManager()
message_loop = MessageLoop(bot)
toml_manager = TomlManager()
def pull_repo():

    utils.pull_repo()
    toml_manager.load_envs()
    time.sleep(app.config.get("PULL_REPO_PERIOD", 1800))

agent_thread = threading.Thread(name="pull_repo", target=pull_repo)
agent_thread.start()


def check_sent_messages():
    while(1):
        now = time.time()
        messages = get_sent_messages()
        for msg in messages:
            if round(now - msg['timestamp']) > timeout:
                #send the message to the back up agent
                if msg['level'] == "level1":
                    # need to check if this is the period of the back up or not
                    first_oncalls = agent_manager.get_current_first_oncalls()
                    text = construct_message_text(msg['data'])
                    for agent in first_oncalls:
                        send_message(agent['telegram'], text, callback=True)
                    msg['level'] = 'level2'
                    msg['timestamp'] = time.time()

                elif msg['level'] == "level2":
                    text = construct_message_text(msg['data'])
                    second_oncalls = agent_manager.get_current_second_oncalls()
                    for agent in second_oncalls:
                        send_message(agent['telegram'], text, callback=True)
                    msg['timestamp'] == time.time()
                    msg['level'] = "level3"
                else:
                    try:
                        # at this point we should delete old messages even if no one picked them
                        messages.remove(msg)
                    except Exception as e:
                        # should pass if the user caught it before deleting
                        pass

        time.sleep(app.config.get("MESSAGE_TIMEOUT", 1000))

message_thread = threading.Thread(name="message_thread", target=check_sent_messages)
message_thread.start()



@app.route('/alerts', methods=['POST'])
def new_alert():
    notify_flag = True
    data = json.loads(request.data.decode())
    data['text'] = data['text'].replace('_', '-')
    LOG.debug("Alert received: {}".format(data))
    now = datetime.datetime.now()
    date = "{}/{}".format(now.month, now.day)
    if agent_manager.last_updated != date:
        try:
            agent_manager.update()
        except CellNotFound as e :
            text = 'date %s not found in the spreadsheet' % date
            notify_flag = False
    if notify_flag:
        monitors = agent_manager.get_current_monitors()
        text = construct_message_text(data)
        message_id = None
        for agent in monitors:
            message = send_message(agent['telegram'], text, callback=True)
            if message and not message_id:
                message_id = message['text']

        # Add message to sent message to do escalation for it
        msg = {}
        msg['timestamp'] = time.time()
        msg['data'] = data
        msg['level'] = "level1"
        msg['message_id'] = message_id
        get_sent_messages().append(msg)

        #send message to specified telegram groups and email
        # envs = get_envs()
        for env, env_data in toml_manager.envs.items():
            if 'all' in list(map(lambda x: x.lower(), env_data.get('envs'))) or data['environment'] in env_data.get('envs'):
                    for group in env_data.get("telegrams"):
                        send_message(group, text, callback=False, group=True)
                    for email in env_data.get("emails"):
                        send_email(email, text)
    else:
        for env, env_data in toml_manager.envs.items():
            for group in env_data.get("telegrams"):
                send_message(group, text, callback=False, group=True)

    return jsonify(stats_code=200)

def send_email(to, data):
    try:
        s = MailService()
        body = utils.body_as_html(data)
        s.send(to, body)
    except Exception as e:
        print(e)

def construct_message_text(data):
    text = '[%s](%s) %s: %s - %s on %s\n%s' % (
    data['short_id'],
    '%s/#/alert/%s' % (config.ALERTA_DASHBOARD_URL, data['id']),
    data['environment'],
    data['severity'],
    data['event'],
    data['service'],
    data['text']
    )
    return text

def send_message(telegram, text, callback=False, group=False):
    message = None
    if callback:
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[[
                {'text':'ack', 'callback_data': 'ack'},
                {'text':'close', 'callback_data': 'close'},

            ]]
            )
    else:
        keyboard = None
    try:
        if group:
            chat_id = get_group_chat_ids().get(telegram)
        else:
            chat_id = get_chat_ids().get(telegram)
        message = bot.sendMessage(chat_id, text, parse_mode='Markdown', reply_markup=keyboard)
    except Exception as e:
        # this agent is not registered yet so skip sending message
        LOG.debug(e)
        pass
    return message

if __name__ == "__main__":
    message_loop.run_as_thread()
    app.run(debug=True, use_reloader=False)

