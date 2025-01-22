import json

from requests.auth import HTTPBasicAuth

from config import *


def take_token():
    """Функция получения токена"""
    headers = {}
    data = {}
    try:
        response = requests.post(
            URL_AUTH,
            auth=HTTPBasicAuth(API_LOGIN, API_PASSWORD),
            data=data,
            headers=headers
        )
        data = response.json()
        token = data['token']
        LOGGER.info('Получили токен успешно')
        return token
    except Exception as take_token_error:
        send_tg(f'Ошибка получения токена: {take_token_error}')
        raise Exception(take_token_error)


def send_data(call_list, agent_name, selection_name):
    """
    Ввод: json-объект, название агента, название очереди

    Функция отправки POST-запроса с загрузочником.
    """
    LOGGER.info('Попали в send_data')
    params = {
        'agent_uuid': NAMES_UUIDS[agent_name],
        'with_selection': 'true',
        'selection_name': f"{selection_name}"
    }

    payload = json.dumps(call_list)
    headers = {
        "Authorization": f"Bearer {take_token()}",
        "Content-Type": "application/json",
    }
    if CAN_SEND:
        response = requests.request("POST", URL_QUEUE_LOADER, headers=headers, data=payload, params=params)
        status_code = response.status_code
        LOGGER.info(f'Ответ: {response.json()}')
    else:
        LOGGER.info(f'Ответ: тестовый запрос -> не отправляем')
        status_code = 200
    return status_code
