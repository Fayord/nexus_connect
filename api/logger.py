import os
import logging
import json
from pytz import timezone
from datetime import datetime
import time
from contextvars import ContextVar


LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = os.getenv("LOG_FORMAT", "json")

api_name = "chat_btl"

# Note :
# use correlation_id as contextvar because this api is async, with contextvar correlation_id can seperate by each request
# https://github.com/tiangolo/fastapi/issues/397
# https://docs.python.org/3/library/contextvars.html
correlation_id: ContextVar[str] = ContextVar("correlation_id", default=None)

logging.Formatter.converter = lambda *args: datetime.now(
    tz=timezone("Asia/Bangkok")
).timetuple()


def get_logger_correlation_id():
    return correlation_id.get()


def set_logger_correlation_id(value):
    correlation_id.set(value)


class ContextFilter(logging.Filter):
    def filter(self, record):
        record.correlation_id = get_logger_correlation_id()
        return True


class JsonFormatter:
    def format(self, record):
        formatted_record = dict()
        for key in ["created", "correlation_id", "levelname", "msg"]:
            if key == "created":
                created = getattr(record, key)
                formatted_record["time"] = time.strftime(
                    "%Y-%m-%dT%H:%M:%S", time.localtime(created)
                )

            elif key == "msg":
                msg = getattr(record, key)
                formatted_record[api_name] = {}
                if isinstance(msg, dict):
                    formatted_record[api_name]["data"] = msg
                else:
                    formatted_record[api_name]["msg"] = msg

            else:
                formatted_record[key] = getattr(record, key)

        return json.dumps(formatted_record, ensure_ascii=False)


logger = logging.getLogger(__name__)
logger.setLevel(logging.getLevelName(LOG_LEVEL))
if LOG_FORMAT == "json":
    log_formatter = JsonFormatter()
elif LOG_FORMAT == "str":
    log_formatter = logging.Formatter(
        "[%(asctime)s][%(correlation_id)s][%(levelname)s]: %(message)s"
    )
else:
    raise TypeError(f"LOG_FORMAT: {LOG_FORMAT} not in ['json', 'str']")

console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter)
logger.addHandler(console_handler)
f = ContextFilter()
logger.addFilter(f)
