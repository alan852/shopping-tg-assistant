class ENV:
    TELEGRAM_BOT_TOKEN = 'TELEGRAM_BOT_TOKEN'
    TELEGRAM_BOT_ERROR_MESSAGE = 'TELEGRAM_BOT_ERROR_MESSAGE'
    ADMIN_CHAT_ID = 'ADMIN_CHAT_ID'
    ALLOWED_CHAT_IDS = 'ALLOWED_CHAT_IDS'
    LOG_FORMAT = 'LOG_FORMAT'
    LOG_LEVEL = 'LOG_LEVEL'
    LOG_PATH = 'LOG_PATH'
    CAL_UNIT_COST_REGEX = 'CAL_UNIT_COST_CMD_REGEX'
    UNITS = 'UNITS'
    FIREFLY_III_DOMAIN = 'FIREFLY_III_DOMAIN'
    FIREFLY_III_TOKEN = 'FIREFLY_III_TOKEN'
    FIREFLY_III_TRAN_DESC_REGEX = 'FIREFLY_III_TRAN_DESC_REGEX'


class DEFAULT:
    TELEGRAM_BOT_ERROR_MESSAGE = 'Sorry! Internal error.'
    LOG_FORMAT = '%(name)-12s %(asctime)s %(levelname)-8s %(filename)s:%(funcName)s %(message)s'
    LOG_LEVEL = 'INFO'
    LOG_PATH = '/var/log/app'
    CAL_UNIT_COST_REGEX = '(?P<cost>\d+(?:\.\d+)?)\/(?P<size>\d+(?:\.\d+)?)(?P<unit>{units})'
    UNITS = 'm|g|kg|ml|l|pack|each'
