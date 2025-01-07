import logging
import logging.config

LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

logging_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": LOG_FORMAT
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
            "level": "DEBUG"
        },
        "file": {
            "class": "logging.FileHandler",
            "filename": "app.log",
            "formatter": "default",
            "level": "DEBUG"
        }
    },
    "root": {
        "handlers": ["console", "file"],
        "level": "DEBUG"
    }
}

logging.config.dictConfig(logging_config)
