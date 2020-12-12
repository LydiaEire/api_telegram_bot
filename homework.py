import os
import time

import logging
import requests
import telegram
from dotenv import load_dotenv

load_dotenv()

PRAKTIKUM_TOKEN = os.getenv("PRAKTIKUM_TOKEN")
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
URL = 'https://praktikum.yandex.ru/api/user_api/homework_statuses/'


def parse_homework_status(homework):
    if not isinstance(homework, dict):
        logging.error('Invalid homework variable %s' % homework)
        raise ValueError('Invalid homework variable %s' % homework)

    homework_name = homework.get('homework_name')
    if homework_name is None:
        logging.error('"homework_name" is not found')
        raise KeyError('"homework_name" is not found')

    homework_status = homework.get('status')
    if homework_status is None:
        logging.error('"homework_status" is not found')
        raise KeyError('"homework_status" is not found')

    verdict = 'Статус проверки неизвестен'
    if homework_status == 'rejected':
        verdict = 'К сожалению в работе нашлись ошибки.'
    if homework_status == 'approved':
        verdict = 'Ревьюеру всё понравилось, можно приступать к следующему уроку.'
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homework_statuses(current_timestamp):
    headers = {'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'}
    if current_timestamp is None:
        current_timestamp = int(time.time())
    date = {'from_date': current_timestamp}
    try:
        homework_statuses = requests.get(URL, params=date, headers=headers)
    except requests.exceptions.RequestException as e:
        logging.error(e)
        raise SystemExit(e)
    return homework_statuses.json()


def send_message(message, bot_client):
    return bot_client.send_message(chat_id=CHAT_ID, text=message)


def main():
    print('Инициализируем бота')
    bot = telegram.Bot(token=TELEGRAM_TOKEN)  # проинициализировать бота здесь
    current_timestamp = int(time.time())  # начальное значение timestamp
    while True:
        try:
            print('Проверяем домашку')
            new_homework = get_homework_statuses(current_timestamp)
            if new_homework.get('homeworks'):
                send_message(parse_homework_status(new_homework.get('homeworks')[0]), bot)
            current_timestamp = new_homework.get('current_date', current_timestamp)  # обновить timestamp
            time.sleep(600)

        except Exception as e:
            print(f'Бот столкнулся с ошибкой: {e}')
            time.sleep(5)


if __name__ == '__main__':
    main()
