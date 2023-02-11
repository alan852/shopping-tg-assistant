import logging
import os
from datetime import datetime

from dotenv import find_dotenv, load_dotenv
from telegram import Update
from telegram.constants import ParseMode
from telegram.error import InvalidToken
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes, ApplicationHandlerStop

from firefly_iii import retrieve_transactions, digest_transaction
from env import DEFAULT, ENV
from cal_unit_cost import cal_unit_cost_from_str

load_dotenv(dotenv_path=find_dotenv())

logging.basicConfig(
    format=os.environ.get(ENV.LOG_FORMAT, DEFAULT.LOG_FORMAT),
    level=os.environ.get(ENV.LOG_LEVEL, DEFAULT.LOG_LEVEL)
)
logger = logging.getLogger(__name__)
log_path = os.environ.get(ENV.LOG_PATH, DEFAULT.LOG_PATH)
if not os.path.exists(log_path):
    os.makedirs(log_path)
fileHandler = logging.FileHandler(os.path.join(log_path, f'app-{datetime.today().strftime("%Y%m%d")}.log'))
fileHandler.setLevel(os.environ.get(ENV.LOG_LEVEL, DEFAULT.LOG_LEVEL))
fileHandler.setFormatter(logging.Formatter(os.environ.get(ENV.LOG_FORMAT, DEFAULT.LOG_FORMAT)))
logger.addHandler(fileHandler)

admin_chat_id = os.environ.get(ENV.ADMIN_CHAT_ID)
admin_chat_id = {int(admin_chat_id)} if admin_chat_id is not None and admin_chat_id != '' else set()
allowed_chat_ids = os.environ.get(ENV.ALLOWED_CHAT_IDS)
allowed_chat_ids = {int(_) for _ in allowed_chat_ids.split(',') if _ != ''} \
    if allowed_chat_ids is not None and allowed_chat_ids != '' else set()
allowed_chat_ids |= admin_chat_id
logger.info(f'Allowed Chat IDs: {allowed_chat_ids}')

error_message = os.environ.get(ENV.TELEGRAM_BOT_ERROR_MESSAGE, DEFAULT.TELEGRAM_BOT_ERROR_MESSAGE)
empty_result_message = os.environ.get(ENV.TELEGRAM_BOT_EMPTY_RESULT_MESSAGE, DEFAULT.TELEGRAM_BOT_EMPTY_RESULT_MESSAGE)


async def message_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f'Message "{update.message.text}" from chat id {update.effective_chat.id}')
    if update.effective_chat.id in allowed_chat_ids:
        try:
            unit_cost = cal_unit_cost_from_str(update.message.text)
            if unit_cost is not None:
                response_text = f'{unit_cost["cost"]:.2f}/{unit_cost["unit"]}'
            else:
                items = list()
                unknown = list()
                for transaction in retrieve_transactions(update.message.text):
                    try:
                        items.append(digest_transaction(transaction))
                    except Exception as e:
                        logger.error(f'{e} (Ref: {transaction})')
                        unknown.append(transaction)
                items = sorted(items, key=lambda i: i['unit_cost']['cost'])
                response_text = '\r\n'.join(f'• {_["name"]} {_["size"]:.0f}{_["unit"]}, '
                                            f'{_["unit_cost"]["cost"]:.2f}/{_["unit_cost"]["unit"]}'
                                            f' on {_["date"].strftime("%d/%m/%Y")} at {_["store"]}'
                                            for _ in items)
                if len(unknown) != 0:
                    response_text += '\r\n\r\nUnknown Format\r\n' + '\r\n'.join(f'• {_["description"]}' for _ in unknown)
                response_text = response_text if response_text is not None and response_text != '' \
                    else empty_result_message
        except Exception as e:
            logger.error(e)
            response_text = error_message
        await context.bot.send_message(chat_id=update.effective_chat.id, text=response_text)
    else:
        raise ApplicationHandlerStop


if __name__ == '__main__':
    try:
        application = ApplicationBuilder().token(os.environ.get(ENV.TELEGRAM_BOT_TOKEN)).build()

        message_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), message_response)

        application.add_handler(message_handler)

        application.run_polling()
    except InvalidToken as e:
        logger.error(e)
