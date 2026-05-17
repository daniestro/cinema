LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DEFAULT_HANDLERS = [
    "console",
]

# В логгере настраивается логгирование uvicorn-сервера.
# Про логирование в Python можно прочитать в документации
# https://docs.python.org/3/howto/logging.html
# https://docs.python.org/3/howto/logging-cookbook.html


def get_logging_settings(logging_level: str, console_logging_level: str):
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "verbose": {"format": LOG_FORMAT},
            "default": {
                "()": "uvicorn.logging.DefaultFormatter",
                "fmt": "%(levelprefix)s %(message)s",
                "use_colors": None,
            },
            "access": {
                "()": "uvicorn.logging.AccessFormatter",
                "fmt": "%(levelprefix)s %(client_addr)s - '%(request_line)s' %(status_code)s",
            },
        },
        "handlers": {
            "console": {
                "level": console_logging_level,
                "class": "logging.StreamHandler",
                "formatter": "verbose",
            },
            "default": {
                "formatter": "default",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
            },
            "access": {
                "formatter": "access",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
            },
        },
        "loggers": {
            "": {
                "handlers": LOG_DEFAULT_HANDLERS,
                "level": logging_level,
            },
            "uvicorn.error": {
                "level": logging_level,
            },
            "uvicorn.access": {
                "handlers": ["access"],
                "level": logging_level,
                "propagate": False,
            },
        },
        "root": {
            "level": logging_level,
            "formatter": "verbose",
            "handlers": LOG_DEFAULT_HANDLERS,
        },
    }
