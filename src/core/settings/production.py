"""
This file contains production level settings
"""

import os
import json
import dj_database_url

DEBUG = True if (os.environ.get("DEBUG", "false").lower() == "true") else False

DEFAULT_CONNECTION = dj_database_url.parse(os.environ.get("DATABASE_URL"))
DEFAULT_CONNECTION.update({"CONN_MAX_AGE": 600})
DATABASES = {"default": DEFAULT_CONNECTION}

ALLOWED_HOSTS = json.loads(os.environ.get("ALLOWED_HOSTS", "[\"*\"]"))
