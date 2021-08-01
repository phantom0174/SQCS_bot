import logging
from dotenv import load_dotenv
from bot import SQCSBot, keep_alive

# load all secrets from .env
load_dotenv()

Format = (
    '%(asctime)s %(levelname)s: %(message)s, '
    'via line: %(lineno)d, '
    'in func: %(funcName)s, '
    'of file: %(pathname)s\n'
)

logging.basicConfig(
    filename='./bot/buffer/bot.log',
    level=logging.WARNING,
    format=Format
)
logging.captureWarnings(True)

if __name__ == '__main__':
    keep_alive()

    bot = SQCSBot()
    bot.run()
