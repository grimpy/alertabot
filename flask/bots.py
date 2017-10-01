import telepot
import sys
import time
import random
import telepot
import telepot.helper
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from telepot.delegate import (
    per_chat_id, per_callback_query_origin, create_open, pave_event_space)
import logging
import os
import pytoml
LOG = logging.getLogger('alerta.plugins.gig')
import os
import pytoml
import config
import requests
import json
from alertaclient.api import ApiClient
from alertaclient.alert import Alert
from utils import *

chat_ids = {}
group_chat_ids = {}
CHAT_IDS_PATH = config.CHAT_IDS_PATH # path to dir in which we will save ids
ENV_FILE = config.ENV_FILE # path to dir in which we will save ids
PRIVATE_CHAT_PATH = os.path.join(CHAT_IDS_PATH, "private.toml")
GROUP_CHAT_PATH = os.path.join(CHAT_IDS_PATH, "group.toml")
sent_messages = []
def initialize_chat_ids():
    global chat_ids
    global group_chat_ids

    if not os.path.exists(CHAT_IDS_PATH):
        # dir_path = '/'.join(chat_ids_path.split("/")[:-1])
        os.system("mkdir -p {}".format(CHAT_IDS_PATH))
        os.system("touch {}".format(PRIVATE_CHAT_PATH))
        os.system("touch {}".format(GROUP_CHAT_PATH))

    with open(PRIVATE_CHAT_PATH, 'rb') as f:
        chat_ids = pytoml.load(f)

    with open(GROUP_CHAT_PATH, "rb") as f:
        group_chat_ids = pytoml.load(f)

def get_chat_ids():
    global chat_ids
    if not chat_ids:
        initialize_chat_ids()
    return chat_ids

def get_group_chat_ids():
    global group_chat_ids
    if not group_chat_ids:
        initialize_chat_ids()
    return group_chat_ids




def get_sent_messages():
    global sent_messages
    return sent_messages

class AlertsStarter(telepot.helper.ChatHandler):
    def __init__(self, *args, **kwargs):
        super(AlertsStarter, self).__init__(*args, **kwargs)

    def on_chat_message(self, msg):
        content_type, chat_type, chat_id = telepot.glance(msg)
        LOG.info('incomming message content_type: {}, chat_type {}, chat_id{}'.format(content_type, chat_type, chat_id))
        if content_type == 'text' and msg['text'] == '/start':
            if chat_type == "group":
                group_name = msg['chat']['title']
                #check if we have a defined group with this name or not
                for env_name, env_data in get_envs().items():
                    if group_name in env_data.get('telegrams'):
                        group_chat_ids[group_name] = chat_id
                        with open(GROUP_CHAT_PATH, "w") as f:
                            pytoml.dump(group_chat_ids, f)
                        self.sender.sendMessage('Hey, Get Ready we will start sending you messages')
                        break
                else:
                    self.sender.sendMessage('This group is not a recognized chat group')
            else: # private chat
                chat_ids[msg['chat']['username']] = chat_id
                with open(PRIVATE_CHAT_PATH, "w") as f:
                    pytoml.dump(chat_ids, f)

                LOG.info("Registering a new agent {}".format(chat_id))
                self.sender.sendMessage('Hey, Get Ready, we will start sending you alerts')
                self.close()
        else:
            print(msg)
class Alerter(telepot.helper.CallbackQueryOriginHandler):
    def __init__(self, *args, **kwargs):
        super(Alerter, self).__init__(*args, **kwargs)

    def on_callback_query(self, msg):
        query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')
        if query_data == '/start': # this is /start from a group
            pass
        for message in sent_messages:
            if msg['message']['text'] == message['message_id']:
                sent_messages.remove(message)
                self.editor.editMessageReplyMarkup()
                self.bot.sendMessage(self.id[0], "Thanks... !")
                api = ApiClient(endpoint=config.ALERTA_API_URL, key=config.ALERTA_API_KEY)
                text = "status change via API (Telegram) by {}.".format(msg['message']['chat']['username'])
                api.update_status(alertid=message['data']['id'], status = query_data, text=text)
                break
        else:
            self.editor.editMessageReplyMarkup()
            self.bot.sendMessage(self.id[0], "Oh Sorry, You were too late. You can not ACK this now.")

        self.close()
