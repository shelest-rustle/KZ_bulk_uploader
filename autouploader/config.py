import requests
import logging
import os

from dotenv import load_dotenv

load_dotenv()

LOGGER = logging.getLogger(__name__)
HANDLER = logging.StreamHandler()
LOGGER.addHandler(HANDLER)

logging.basicConfig(filename='kz_uploader.log', level=logging.INFO)

# две переменные TEST - выставляет тестовые настройки (юиды, type_call и т.д.)
# CAN_SEND разрешает отправлять на агентов
TEST = False
# TEST = True

CAN_SEND = True
# CAN_SEND = False


API_LOGIN = os.environ.get('API_LOGIN')
API_PASSWORD = os.environ.get('API_PASSWORD')
URL_BASE = os.environ.get('URL_BASE')
URL_AUTH = URL_BASE + os.environ.get('URL_AUTH')
URL_GENERAL = URL_BASE + os.environ.get('URL_GENERAL')
TG_ADRESSES = os.environ.get('TG_ADRESSES')

URL_QUEUE_LOADER = os.environ.get('URL_QUEUE_LOADER')


if not TEST:
    NAMES_UUIDS = {
        'Agent1': os.environ.get('Agent1_uuid'),
        'Agent2': os.environ.get('Agent2_uuid'),
        'Agent3': os.environ.get('Agent3_uuid'),
        'Agent4': os.environ.get('Agent4_uuid'),
        'Agent5': os.environ.get('Agent5_uuid'),
    }
else:
    # тестовые
    NAMES_UUIDS = {
        'Agent1': os.environ.get('Agent1_uuid_test'),
        'Agent2': os.environ.get('Agent2_uuid_test'),
        'Agent3': os.environ.get('Agent3_uuid_test'),
        'Agent4': os.environ.get('Agent4_uuid_test'),
        'Agent5': os.environ.get('Agent5_uuid_test'),
    }

AGENTS = (
    'Agent1', 'Agent2', 'Agent3', 'Agent4', 'Agent5'
)


def send_tg(AGENT_NAME, message):
    LOGGER.info('Попали в send_tg')
    if TEST:
        to_send = os.environ.get('TG_ADRESSES_DEV')
    else:
        to_send = TG_ADRESSES
    for dev_id in to_send:
        send_message = ('KZ_Uploader\n'
                        f'Агент {AGENT_NAME}: \n'
                        f'{message}')
        url = ('https://api.telegram.org/'
               f'{os.environ.get("TG_BOT_TOKEN")}/'
               f'sendMessage?chat_id={dev_id}&text={send_message}')
        payloads = {}
        headers = {}
        try:
            requests.get(url=url, headers=headers, data=payloads)
        except Exception as send_tg_reponse_error:
            LOGGER.info(send_tg_reponse_error)
    return
