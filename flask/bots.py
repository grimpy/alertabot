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
from agent_manager import AgentChooser
LOG = logging.getLogger('alerta.plugins.gig')
import os
import pytoml
import config
chat_ids = {}
chat_ids_path = config.CHAT_IDS_PATH #, "/opt/chat_ids.toml")
sent_messages = []
def initialize_chat_ids():
    global chat_ids
    if not os.path.exists(chat_ids_path):
        dir_path = '/'.join(chat_ids_path.split("/")[:-1])
        os.system("mkdir -p {}".format(dir_path))
        os.system('touch {}'.format(chat_ids_path))
    with open(chat_ids_path, 'rb') as f:
        chat_ids = pytoml.load(f)

def get_chat_ids():
    global chat_ids
    if not chat_ids:
        initialize_chat_ids()
    return chat_ids

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
            chat_ids[msg['chat']['username']] = chat_id
            with open(chat_ids_path, "w") as f:
                pytoml.dump(chat_ids, f)

            LOG.info("Registering a new agent {}".format(chat_id))
            self.sender.sendMessage('Hey, Get Ready, we will start sending you alerts')
        self.close()
    def get_chat_ids(self):
        with open(self.chat_ids_path, 'rb') as f:
            chat_ids = pytoml.load(f)



class Alerter(telepot.helper.CallbackQueryOriginHandler):
    def __init__(self, *args, **kwargs):
        self.agent_chooser = AgentChooser()
        super(Alerter, self).__init__(*args, **kwargs)

    def on_callback_query(self, msg):
        query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')
        if query_data == 'ack':
            # Current Agent ack the message
            for message in sent_messages:
                if msg['message']['message_id'] == message['message_id']:
                    sent_messages.remove(message)
                    self.bot.sendMessage(self.id[0], "Thanks... !")
                    break
            else:
                self.bot.sendMessage(self.id[0], "Oh Sorry, You were too late. You can not ACK this now.")

            self.close()

    def on__idle(self, event):
        # if this is the current Agent (i.e not the backup) send to the backup
        time.sleep(5)
        self.editor.deleteMessage()
        self.close()
