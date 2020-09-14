import logging
import os
import time

import requests
import telegram
from dotenv import load_dotenv

load_dotenv()


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
url_yapraktikum = 'https://praktikum.yandex.ru/api/user_api/homework_statuses/'


def set_logger():
    logger = logging.getLogger('telegramBot')
    logger.setLevel(logging.INFO)
    fh = logging.FileHandler('telegram_bot.log')
    formatter = logging.Formatter('%(asctime)s - %(name)s - '
                                  '%(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    logger.info('Program started')
    return logger


def parse_homework_status(homework):
    global logger
    try:
        homework_name = homework.get('homework_name')
        if homework_name is not None:
            if homework['status'] != 'approved':
                verdict = 'К сожалению в работе нашлись ошибки.'
            else:
                verdict = ('Ревьюеру всё понравилось, '
                           'можно приступать к следующему уроку.')
            return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'
        else:
            raise TypeError
    except TypeError:
        logger.info('None homework, trouble with server')


def get_homework_statuses(current_timestamp):
    if current_timestamp is None:
        current_timestamp = int(time.time())
    headers = {'Authorization': f'OAuth {PRACTICUM_TOKEN}',
               }
    params = {'from_date': current_timestamp}
    try:
        homework_statuses = requests.get(
            url_yapraktikum,
            headers=headers,
            params=params,)
        return homework_statuses.json()
    except requests.exceptions.RequestException as e:
        logger.info(f'Errors on server: {e}')


def send_message(message):
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    return bot.send_message(chat_id=CHAT_ID, text=message)


def main():
    logger = set_logger()
    current_timestamp = int(time.time())
    send_message(f'Бот запущен {time.ctime(current_timestamp)}')
    while True:
        try:
            new_homework = get_homework_statuses(current_timestamp)
            if new_homework.get('homeworks'):
                logger.info(f'debug!, {new_homework.get("homeworks")[0]}')
                send_message(
                    parse_homework_status(new_homework.get('homeworks')[0])
                )
            current_timestamp = new_homework.get('current_date')
            time.sleep(600)
        except Exception as e:
            print(f'Бот упал с ошибкой: {e}')
            logger.exception(f'Exeption!, {e}')
            time.sleep(5)
            continue


if __name__ == '__main__':
    main()
