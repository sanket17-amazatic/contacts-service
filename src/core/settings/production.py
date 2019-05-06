"""
This file contains production level settings
"""

import os
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'mq=1@_3wwgry$rs8oi&45pxr0_da=4i311d52j(l-a0%_p9(jt'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

DATABASES = {
    # 'default': {
    #     'ENGINE': 'django.db.backends.sqlite3',
    #     'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    # }
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'contact_service',
        'USER': 'sanket',
        'PASSWORD': '',
    }
}
