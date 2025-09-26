import logging


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

file_log = logging.FileHandler("app.log", encoding='utf-8')
console_log = logging.StreamHandler()

formatter = logging.Formatter(
    '%(asctime)s %(levelname)s %(filename)s:%(lineno)s %(message)s',
    '%d-%m-%Y %H:%M:%S'
)

file_log.setFormatter(formatter)
console_log.setFormatter(formatter)

logger.addHandler(file_log)
logger.addHandler(console_log)